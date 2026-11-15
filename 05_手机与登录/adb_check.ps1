$ErrorActionPreference = 'Stop'
$adb = Join-Path $PSScriptRoot 'platform-tools\adb.exe'
if (-not (Test-Path -LiteralPath $adb)) { throw "ADB not found: $adb" }
& $adb kill-server | Out-Null
& $adb start-server | Out-Null
$lines = & $adb devices -l
$lines | Write-Output
$devices = @($lines | Where-Object { $_ -match '\tdevice$' })
$unauthorized = @($lines | Where-Object { $_ -match '\tunauthorized$' })
if ($devices.Count -gt 0) {
  Write-Host "`nDEVICE_OK" -ForegroundColor Green
  & $adb shell getprop ro.product.manufacturer
  & $adb shell getprop ro.product.model
  & $adb shell getprop ro.build.version.release
} elseif ($unauthorized.Count -gt 0) {
  Write-Host "`nDEVICE_UNAUTHORIZED" -ForegroundColor Yellow
  Write-Host "Unlock the phone and tap 'Allow USB debugging'. Check 'Always allow from this computer'."
  Write-Host "If no prompt appears, go to Developer options -> Revoke USB debugging authorizations, then reconnect."
} else {
  Write-Host "`nNO_DEVICE" -ForegroundColor Red
  Write-Host "1. Use a data-capable USB cable, not a charge-only cable."
  Write-Host "2. On the phone, open Developer options and enable USB debugging."
  Write-Host "3. Pull down the USB notification and choose File transfer / MTP."
  Write-Host "4. Unlock the phone and reconnect; accept the RSA fingerprint prompt."
  Write-Host "5. If Windows still sees no device, install the phone vendor's USB driver."
  Write-Host "6. Run this script again."
}