# Anatomy Lab local launcher (Windows). Serves the app folder on http://localhost and opens your browser.
# Uses only what ships with Windows (PowerShell + .NET HttpListener); no Python or Node needed.
# Close this window to stop the app.
$ErrorActionPreference = 'Stop'
$root = Join-Path $PSScriptRoot 'app'
if (-not (Test-Path (Join-Path $root 'index.html'))) { Write-Host "Can't find the app folder next to this script: $root" -ForegroundColor Red; Read-Host 'Press Enter to close'; exit 1 }
$root = (Resolve-Path $root).Path.TrimEnd('\', '/')
$types = @{ '.html' = 'text/html; charset=utf-8'; '.js' = 'application/javascript; charset=utf-8'; '.mjs' = 'application/javascript; charset=utf-8'
  '.json' = 'application/json; charset=utf-8'; '.txt' = 'text/plain; charset=utf-8'; '.css' = 'text/css; charset=utf-8'; '.png' = 'image/png'
  '.jpg' = 'image/jpeg'; '.svg' = 'image/svg+xml'; '.ico' = 'image/x-icon'; '.wasm' = 'application/wasm'; '.md' = 'text/plain; charset=utf-8' }
$listener = $null; $port = 0
foreach ($p in 8259..8299) {
  try { $l = New-Object System.Net.HttpListener; $l.Prefixes.Add("http://localhost:$p/"); $l.Start(); $listener = $l; $port = $p; break } catch { }
}
if (-not $listener) { Write-Host 'No free port between 8259 and 8299.' -ForegroundColor Red; Read-Host 'Press Enter to close'; exit 1 }
$url = "http://localhost:$port/"
$Host.UI.RawUI.WindowTitle = "Anatomy Lab - $url (close this window to stop)"
Write-Host ''
Write-Host "  Anatomy Lab is running at $url" -ForegroundColor Green
Write-Host '  Your browser should open by itself. Keep this window open while you study;'
Write-Host '  close it to stop the app.'
Write-Host ''
try { Start-Process $url } catch { Write-Host "  Open $url in your browser." }
while ($listener.IsListening) {
  try { $ctx = $listener.GetContext() } catch { break }
  $res = $ctx.Response
  try {
    $rel = [Uri]::UnescapeDataString($ctx.Request.Url.AbsolutePath).TrimStart('/')
    if ($rel -eq '') { $rel = 'index.html' }
    $full = [IO.Path]::GetFullPath((Join-Path $root $rel))
    if (-not $full.StartsWith($root + [IO.Path]::DirectorySeparatorChar) -or -not (Test-Path -LiteralPath $full -PathType Leaf)) {
      $res.StatusCode = 404; $b = [Text.Encoding]::UTF8.GetBytes('Not found'); $res.OutputStream.Write($b, 0, $b.Length)
    } else {
      $ext = [IO.Path]::GetExtension($full).ToLower(); $ct = $types[$ext]; if (-not $ct) { $ct = 'application/octet-stream' }
      $res.ContentType = $ct; $res.AddHeader('Cache-Control', 'no-cache')
      $fs = [IO.File]::OpenRead($full)
      try { $res.ContentLength64 = $fs.Length; if ($ctx.Request.HttpMethod -ne 'HEAD') { $fs.CopyTo($res.OutputStream) } } finally { $fs.Dispose() }
    }
  } catch { try { $res.StatusCode = 500 } catch { } }
  finally { try { $res.OutputStream.Close() } catch { } }
}
