param([int]$Chapter = 0, [switch]$CheckOnly)
# 《提瓦特通史》Windows 遊戲畫面素材下載
# PowerShell 5.1+ 內建可執行；不需要安裝 Python 或套件。
$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$manifest = Get-Content -LiteralPath (Join-Path $root 'assets\game-media\sources.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$items = @($manifest.images | Where-Object { $Chapter -eq 0 -or $_.chapter -eq $Chapter })
$total = $items.Count
$done = 0
Write-Host "準備下載 $total 張《原神》遊戲素材（只下載有對應形象的圖）"

function IsPicture([string]$file) {
  if (!(Test-Path -LiteralPath $file)) { return $false }
  $bytes = [System.IO.File]::ReadAllBytes($file)
  if ($bytes.Length -lt 4096) { return $false }
  $jpeg = $bytes[0] -eq 255 -and $bytes[1] -eq 216 -and $bytes[2] -eq 255
  $png = $bytes[0] -eq 137 -and $bytes[1] -eq 80 -and $bytes[2] -eq 78 -and $bytes[3] -eq 71
  $webp = $bytes[0] -eq 82 -and $bytes[1] -eq 73 -and $bytes[2] -eq 70 -and $bytes[3] -eq 70 -and $bytes[8] -eq 87 -and $bytes[9] -eq 69 -and $bytes[10] -eq 66 -and $bytes[11] -eq 80
  return ($jpeg -or $png -or $webp)
}

foreach ($item in $items) {
  $target = Join-Path $root ($item.local -replace '/', '\')
  $parent = Split-Path -Parent $target
  if (!(Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
  if (IsPicture $target) {
    Write-Host "[已存在] $($item.id)"
    $done++
    continue
  }
  if ($CheckOnly) { Write-Host "[缺少] $($item.id)"; continue }
  $ok = $false
  foreach ($url in $item.urls) {
    $temp = "$target.part"
    if (Test-Path -LiteralPath $temp) { Remove-Item -LiteralPath $temp -Force }
    try {
      $headers = @{'User-Agent'='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36';'Accept'='image/webp,image/png,image/jpeg,image/*,*/*;q=0.8'}
      if ($url -match 'hoyolab|hoyoverse') { $headers['Referer']='https://www.hoyolab.com/' }
      Invoke-WebRequest -Uri $url -OutFile $temp -Headers $headers -UseBasicParsing -TimeoutSec 20 -ErrorAction Stop
      if (!(IsPicture $temp)) { throw '取得非圖片資料' }
      Move-Item -LiteralPath $temp -Destination $target -Force
      $site = Join-Path $root ("_site/" + $item.local)
      if (Test-Path (Join-Path $root "_site")) { New-Item -ItemType Directory -Force -Path (Split-Path $site -Parent) | Out-Null; Copy-Item -LiteralPath $target -Destination $site -Force }
      Write-Host "[成功] $($item.id)"
      $done++
      $ok = $true
      break
    } catch {
      Write-Host "[略過來源] $($item.id): $($_.Exception.Message)"
      if (Test-Path -LiteralPath $temp) { Remove-Item -LiteralPath $temp -Force }
    }
  }
  if (!$ok) { if ($item.fallback_only) { Write-Host "[尚未取得，保留提示卡] $($item.id)" } else { Write-Host "[保留原創示意] $($item.id)" } }
}
Write-Host "完成：$done / $total。成功下載的圖片可供日後完全離線閱讀。"
if ($done -ne $total) { Write-Host '站台拒絕直接下載的素材，可依 assets\game-media\sources.json 所載來源頁自行另存。' }

if ($done -ne $total) { exit 1 } else { exit 0 }
