#!/usr/bin/env node
const fs = require('fs');
const http = require('http');
const https = require('https');
const path = require('path');
const { loadFactors, resolveSpec, specOf } = require('./factors');

const DEFAULT_MCP_URL = 'https://skillhub.csc108.com/api/mcp/v1/servers/csc-ecomm-ras-ypstocktools/mcp';
const DEFAULT_MCP_TOOL = 'csc-ecomm-ras-ypstocktools_tools_getStockByFactor';
const CALLING_SKILL_ID = 'stock-pick';
const API_KEY_ENV = 'CSC_SKILLHUB_API_KEY';
const APPLY_URL = 'https://skillhub.csc108.com/finly/?channelCode=workbuddy';
const MISSING_API_KEY_MESSAGE = `您好,需要 API Key 才能使用本功能。请前往 ${APPLY_URL} 申请并配置 API Key 后重试。`;
const BUFFER_LIMIT_HINT = 'Exceeded limit on max bytes to buffer';
// 单次最多返回 3000 只。超出时按 oversize 处理，不截断后当成全部结果。
const MAX_STOCKS = 3000;
const PREVIEW_WHEN_ALL = 10;

const BASE_COLUMNS = [
  { key: 'code', header: '股票代码', aliases: [] },
  { key: 'name', header: '股票名称', aliases: [] },
  { key: 'price', header: '最新价', aliases: ['最新价', '股价'] },
  { key: 'changeRate', header: '涨跌幅', aliases: ['涨跌幅'] },
  { key: 'volume', header: '成交量', aliases: ['成交量'] },
  { key: 'amount', header: '成交金额', aliases: ['成交金额', '成交额'] },
];

function fail(message, extra) {
  const payload = { ok: false, error: message, ...(extra || {}) };
  process.stdout.write(`${JSON.stringify(payload, null, 2)}\n`);
  process.exit(1);
}

function parseArgs(argv) {
  const factors = [];
  let limit = null;
  let all = false;
  let outDir = process.cwd();

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--factor') {
      if (!argv[i + 1]) throw new Error('--factor 缺少值，例如 涨跌幅/大于5%');
      factors.push(argv[i + 1]);
      i += 1;
    } else if (arg === '--limit') {
      if (!argv[i + 1]) throw new Error('--limit 缺少数字');
      const n = Number(argv[i + 1]);
      if (!Number.isInteger(n) || n < 1) throw new Error('--limit 必须是正整数');
      limit = n;
      i += 1;
    } else if (arg === '--all') {
      all = true;
    } else if (arg === '--out-dir') {
      if (!argv[i + 1]) throw new Error('--out-dir 缺少路径');
      outDir = path.resolve(argv[i + 1]);
      i += 1;
    } else if (arg === '--help' || arg === '-h') {
      return { help: true };
    } else {
      throw new Error(`未知参数: ${arg}`);
    }
  }

  return { factorSpecs: factors, limit, all, outDir };
}

function mcpConfig() {
  return {
    url: process.env.MCP_URL || DEFAULT_MCP_URL,
    apiKey: String(process.env[API_KEY_ENV] || '').trim(),
    skillId: process.env.MCP_CALLING_SKILL_ID || CALLING_SKILL_ID,
    tool: process.env.MCP_TOOL_NAME || DEFAULT_MCP_TOOL,
  };
}

// API Key 缺失：立即终止，不发任何请求，不做任何降级或绕过。
function abortMissingApiKey(detail) {
  const payload = {
    ok: false,
    needApiKey: true,
    terminated: true,
    error: MISSING_API_KEY_MESSAGE,
    envVar: API_KEY_ENV,
    applyUrl: APPLY_URL,
    ...(detail ? { detail } : {}),
  };
  process.stdout.write(`${JSON.stringify(payload, null, 2)}\n`);
  process.exit(2);
}

function postJson(url, headers, body) {
  const u = new URL(url);
  const mod = u.protocol === 'https:' ? https : http;
  const data = Buffer.from(JSON.stringify(body), 'utf8');
  return new Promise((resolve, reject) => {
    const req = mod.request(
      {
        hostname: u.hostname,
        port: u.port || (u.protocol === 'https:' ? 443 : 80),
        path: `${u.pathname}${u.search}`,
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Content-Length': data.length,
          ...headers,
        },
      },
      (res) => {
        const chunks = [];
        res.on('data', (chunk) => chunks.push(chunk));
        res.on('end', () => {
          const text = Buffer.concat(chunks).toString('utf8');
          resolve({ status: res.statusCode, text });
        });
      },
    );
    req.on('error', reject);
    req.setTimeout(60000, () => req.destroy(new Error('请求超时')));
    req.write(data);
    req.end();
  });
}

function parseRpcBody(text) {
  const trimmed = String(text || '').trim();
  if (!trimmed) throw new Error('响应为空');
  if (trimmed.startsWith('{') || trimmed.startsWith('[')) return JSON.parse(trimmed);
  const data = trimmed
    .split(/\r?\n/)
    .filter((line) => line.startsWith('data:'))
    .map((line) => line.slice(5).trim())
    .filter(Boolean);
  if (data.length) return JSON.parse(data[data.length - 1]);
  throw new Error(`无法识别的响应格式: ${trimmed.slice(0, 200)}`);
}

function oversizeError() {
  const err = new Error(
    '符合条件的股票过多，超出单次返回上限（3000 只）。请增加收敛条件后重试。',
  );
  err.oversize = true;
  return err;
}

const API_KEY_ERROR_CODES = ['MISSING_API_KEY', 'INVALID_API_KEY'];

async function fetchByFactor(conditions) {
  const cfg = mcpConfig();
  if (!cfg.apiKey) abortMissingApiKey(`运行环境中未配置环境变量 ${API_KEY_ENV}`);

  const { status, text } = await postJson(
    cfg.url,
    {
      Accept: 'application/json, text/event-stream',
      'X-API-Key': cfg.apiKey,
      'X-Calling-Skill-Id': cfg.skillId,
    },
    {
      jsonrpc: '2.0',
      id: 1,
      method: 'tools/call',
      params: { name: cfg.tool, arguments: { condition: conditions } },
    },
  );

  let envelope;
  try {
    envelope = parseRpcBody(text);
  } catch (err) {
    if (text.includes(BUFFER_LIMIT_HINT)) throw oversizeError();
    throw new Error(`响应解析失败（HTTP ${status}）: ${err.message}`);
  }

  if (envelope.error) {
    const raw = String(envelope.error.message || '');
    const code = (envelope.error.data && envelope.error.data.error_code) || '';
    if (raw.includes(BUFFER_LIMIT_HINT)) throw oversizeError();
    if (API_KEY_ERROR_CODES.includes(code) || status === 401) {
      abortMissingApiKey(raw || `HTTP ${status} ${code}`);
    }
    throw new Error(`MCP 工具调用失败: ${raw || JSON.stringify(envelope.error)}`);
  }

  const content = (envelope.result && envelope.result.content) || [];
  const first = content.find((item) => item && item.type === 'text') || content[0];
  if (!first || typeof first.text !== 'string') throw new Error('MCP 未返回文本内容');

  let payload;
  try {
    payload = unwrapPayload(JSON.parse(first.text));
  } catch {
    throw new Error(`MCP 返回内容不是 JSON: ${first.text.slice(0, 200)}`);
  }

  if (!payload || !Array.isArray(payload.vStock)) {
    if (payload && payload.code) throw new Error(`选股接口返回错误: code=${payload.code}`);
    throw new Error('MCP 未返回 vStock');
  }

  return payload;
}

function unwrapPayload(payload) {
  if (!payload || typeof payload !== 'object') return payload;
  if (typeof payload.response === 'string') {
    try {
      return JSON.parse(payload.response);
    } catch {
      return payload;
    }
  }
  return payload;
}

function normalizeName(name) {
  return String(name || '')
    .replace(/（.*?）/g, '')
    .replace(/\(.*?\)/g, '')
    .replace(/\s+/g, '')
    .trim();
}

function extractTimeSpan(subName) {
  const text = String(subName || '');
  const match = text.match(/近[一二三四五六七八九十\d]+[日天月年周]|\d+日内|\d+个交易日|连续\d+日/);
  return match ? match[0] : '';
}

function fieldValue(field) {
  if (!field) return '';
  if (field.iType === 2) return '是';
  if (field.sValue == null || field.sValue === '') return '';
  return String(field.sValue);
}

function formatNumber(value, digits) {
  if (value == null || value === '') return '';
  const n = Number(value);
  if (!Number.isFinite(n)) return String(value);
  if (digits == null) return n;
  return Number(n.toFixed(digits));
}

function columnHeader(sName, sSubName, sUnit) {
  const span = extractTimeSpan(sSubName);
  if (span) return `${sName}（${span}）`;
  if (sUnit) return `${sName}（${sUnit}）`;
  return sName;
}

function findBaseColumn(sName) {
  const normalized = normalizeName(sName);
  return BASE_COLUMNS.find((col) => col.aliases.includes(normalized) || col.header === normalized) || null;
}

function buildLayout(conditions, sampleFields) {
  const byFactor = new Map(conditions.map((item) => [item.eFactor, item]));
  const replacements = {};
  const extras = [];
  const usedExtraLabels = new Set();

  (sampleFields || []).forEach((field, index) => {
    const cond = byFactor.get(field.eType);
    const sName = field.sName || '';
    const sSubName = cond ? cond.sSubName : '';
    let header = columnHeader(sName, sSubName, field.sUnit);
    const base = findBaseColumn(sName);

    if (base && !replacements[base.key]) {
      replacements[base.key] = { index, header };
      return;
    }

    if (usedExtraLabels.has(header) && sSubName) {
      header = `${sName}（${sSubName}）`;
    }
    usedExtraLabels.add(header);
    extras.push({ index, header });
  });

  const columns = [];
  for (const col of BASE_COLUMNS) {
    if (col.key === 'price') {
      extras.forEach((extra) => columns.push({ kind: 'field', ...extra }));
    }
    if (replacements[col.key]) {
      columns.push({ kind: 'field', key: col.key, ...replacements[col.key] });
    } else {
      columns.push({ kind: 'base', key: col.key, header: col.header });
    }
  }
  return columns;
}

function baseValue(stock, key) {
  const hq = stock.stStockHq || {};
  const ext = stock.stStockHqExt || {};
  if (key === 'code') return String((stock.stStockId || {}).sCode || '');
  if (key === 'name') return hq.sName || '';
  if (key === 'price') return formatNumber(hq.dPrice);
  if (key === 'changeRate') return formatNumber(hq.dChangeRate, 2);
  if (key === 'volume') return ext.lVolume == null ? '' : ext.lVolume;
  if (key === 'amount') return ext.fAmount == null ? '' : ext.fAmount;
  return '';
}

function rowFromStock(stock, columns) {
  const fields = stock.vField || [];
  const row = {};
  for (const col of columns) {
    if (col.kind === 'field') {
      row[col.header] = fieldValue(fields[col.index]);
    } else {
      row[col.header] = baseValue(stock, col.key);
    }
  }
  return row;
}

function csvEscape(value) {
  const text = value == null ? '' : String(value);
  if (/[",\r\n]/.test(text)) return `"${text.replace(/"/g, '""')}"`;
  return text;
}

function stamp() {
  const d = new Date();
  const p = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}-${p(d.getHours())}${p(d.getMinutes())}${p(d.getSeconds())}`;
}

function writeCsv(filePath, columns, rows) {
  const headers = columns.map((col) => col.header);
  const lines = [headers.map(csvEscape).join(',')];
  for (const row of rows) {
    lines.push(headers.map((header) => csvEscape(row[header])).join(','));
  }
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, `\uFEFF${lines.join('\r\n')}\r\n`, 'utf8');
}

async function main() {
  let args;
  try {
    args = parseArgs(process.argv.slice(2));
  } catch (err) {
    fail(err.message);
  }

  if (args.help) {
    process.stdout.write(`用法:
  node pick.js --factor 涨跌幅/大于5% [--factor 成交额/大于10亿] [--limit 3]
  node pick.js --factor 涨跌幅/大于5% --all

  未指定 --limit 时等同 --all：返回全部；超过 10 条时 stdout 只给前 10 条，并写出完整 CSV。

  数据来源：SkillHub MCP 服务（JSON-RPC over HTTPS）
            默认 ${DEFAULT_MCP_URL}
  鉴权：请求头 X-API-Key 取自环境变量 ${API_KEY_ENV}；
        未配置时立即终止并提示申请，不做任何降级或绕过。
        请求头 X-Calling-Skill-Id 固定为 ${CALLING_SKILL_ID}
  可用环境变量覆盖：MCP_URL / MCP_CALLING_SKILL_ID / MCP_TOOL_NAME
  注意：单次最多返回 3000 只。超出时会失败（oversize），需叠加收敛条件。
`);
    return;
  }

  if (!args.factorSpecs.length) {
    fail('至少需要一个 --factor，例如 --factor 涨跌幅/大于5%');
  }

  const table = loadFactors();
  let conditions;
  try {
    conditions = args.factorSpecs.map((spec) => resolveSpec(table, spec));
  } catch (err) {
    fail(err.message);
  }

  let payload;
  try {
    payload = await fetchByFactor(conditions);
  } catch (err) {
    if (err.oversize) {
      fail(err.message, {
        oversize: true,
        conditions: args.factorSpecs,
        hint: '可叠加 --factor 成交额/大于10亿、--factor 总市值/大于100亿 等条件收窄结果集',
      });
    }
    fail(`MCP 调用失败: ${err.message}`);
  }

  if (payload.vStock.length > MAX_STOCKS) {
    fail('符合条件的股票过多，超出单次返回上限（3000 只）。请增加收敛条件后重试。', {
      oversize: true,
      conditions: args.factorSpecs,
      hint: '可叠加 --factor 成交额/大于10亿、--factor 总市值/大于100亿 等条件收窄结果集',
    });
  }

  const stocks = payload.vStock;
  const columns = stocks.length ? buildLayout(conditions, stocks[0].vField || []) : BASE_COLUMNS.map((col) => ({ kind: 'base', key: col.key, header: col.header }));
  const allRows = stocks.map((stock) => rowFromStock(stock, columns));
  const headers = columns.map((col) => col.header);

  const wantAll = args.limit == null || args.all;
  let shownRows;
  let file = null;

  if (!wantAll) {
    shownRows = allRows.slice(0, args.limit);
  } else if (allRows.length > PREVIEW_WHEN_ALL) {
    shownRows = allRows.slice(0, PREVIEW_WHEN_ALL);
    const filePath = path.join(args.outDir, `选股结果-${stamp()}.csv`);
    writeCsv(filePath, columns, allRows);
    file = filePath;
  } else {
    shownRows = allRows;
  }

  const result = {
    ok: true,
    total: allRows.length,
    shown: shownRows.length,
    file,
    columns: headers,
    conditions: conditions.map((item) => ({
      spec: specOf(item),
      sName: item.sName,
      sSubName: item.sSubName,
    })),
    stocks: shownRows,
  };
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
}

main().catch((err) => fail(err.message || String(err)));
