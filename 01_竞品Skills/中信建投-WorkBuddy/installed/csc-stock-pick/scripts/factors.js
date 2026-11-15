#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const CSV_PATH = path.join(__dirname, '..', 'data', 'stock-select-factor.csv');

function loadFactors() {
  const text = fs.readFileSync(CSV_PATH, 'utf8').replace(/^\uFEFF/, '');
  const items = [];
  for (const rawLine of text.split(/\r?\n/)) {
    let line = rawLine.trim();
    if (!line) continue;
    if (line.startsWith('"') && line.endsWith('"')) {
      line = line.slice(1, -1).replace(/""/g, '"');
    }
    items.push(JSON.parse(line));
  }
  return items;
}

function findFactor(factors, sName, sSubName) {
  const sub = sSubName == null ? '' : String(sSubName);
  return factors.find((item) => item.sName === sName && String(item.sSubName || '') === sub) || null;
}

function listByName(factors, sName) {
  return factors.filter((item) => item.sName === sName);
}

function parseSpec(spec) {
  const text = String(spec || '').trim();
  if (!text) throw new Error('因子规格为空');
  const idx = text.indexOf('/');
  if (idx === -1) return { sName: text, sSubName: null };
  return { sName: text.slice(0, idx).trim(), sSubName: text.slice(idx + 1).trim() };
}

function resolveSpec(factors, spec) {
  const { sName, sSubName } = parseSpec(spec);
  if (sSubName === null) {
    const hits = listByName(factors, sName);
    if (hits.length === 1) return hits[0];
    if (hits.length === 0) {
      throw new Error(`因子表中没有「${sName}」`);
    }
    const subs = hits.map((item) => item.sSubName || '(空)').join(' | ');
    throw new Error(`「${sName}」有多个子档，请写成 名称/子档。可选：${subs}`);
  }
  const found = findFactor(factors, sName, sSubName);
  if (!found) {
    const hits = listByName(factors, sName);
    if (hits.length === 0) throw new Error(`因子表中没有「${sName}/${sSubName}」`);
    const subs = hits.map((item) => item.sSubName || '(空)').join(' | ');
    throw new Error(`因子表中没有「${sName}/${sSubName}」。「${sName}」可选子档：${subs}`);
  }
  return found;
}

function catalogText(factors) {
  const grouped = new Map();
  for (const item of factors) {
    const name = item.sName;
    if (!grouped.has(name)) grouped.set(name, []);
    grouped.get(name).push(item.sSubName || '(空)');
  }
  const lines = [`共 ${factors.length} 条，${grouped.size} 个因子`];
  for (const [name, subs] of grouped) {
    lines.push(`${name}\t${subs.join(' | ')}`);
  }
  return lines.join('\n');
}

function searchFactors(factors, keyword) {
  const q = String(keyword || '').trim();
  if (!q) return [];
  return factors.filter((item) => {
    const name = String(item.sName || '');
    const sub = String(item.sSubName || '');
    return name.includes(q) || sub.includes(q);
  });
}

function specOf(item) {
  return item.sSubName ? `${item.sName}/${item.sSubName}` : item.sName;
}

function main(argv) {
  const cmd = argv[0] || 'help';
  const factors = loadFactors();

  if (cmd === 'catalog') {
    process.stdout.write(`${catalogText(factors)}\n`);
    return;
  }

  if (cmd === 'search') {
    const keyword = argv.slice(1).join(' ').trim();
    if (!keyword) {
      console.error('用法: node factors.js search <关键词>');
      process.exit(1);
    }
    const hits = searchFactors(factors, keyword);
    if (!hits.length) {
      process.stdout.write(`未找到包含「${keyword}」的因子\n`);
      return;
    }
    const lines = hits.map((item) => specOf(item));
    process.stdout.write(`${lines.join('\n')}\n`);
    return;
  }

  if (cmd === 'get') {
    const spec = argv.slice(1).join(' ').trim();
    if (!spec) {
      console.error('用法: node factors.js get 涨跌幅/大于5%');
      process.exit(1);
    }
    const item = resolveSpec(factors, spec);
    process.stdout.write(`${JSON.stringify(item, null, 2)}\n`);
    return;
  }

  console.error(`用法:
  node factors.js catalog
  node factors.js search <关键词>
  node factors.js get 涨跌幅/大于5%`);
  process.exit(1);
}

if (require.main === module) {
  try {
    main(process.argv.slice(2));
  } catch (err) {
    console.error(err.message || err);
    process.exit(1);
  }
}

module.exports = {
  loadFactors,
  findFactor,
  listByName,
  parseSpec,
  resolveSpec,
  searchFactors,
  specOf,
  CSV_PATH,
};
