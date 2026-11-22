@echo off
title Anatomy Lab installer
echo.
echo   Installing Anatomy Lab (KNES 259) to your Desktop...
echo.
powershell -NoProfile -ExecutionPolicy Bypass -Command "$s = Get-Content -LiteralPath '%~f0' -Raw; $i = $s.IndexOf('#' + 'PS-BEGIN'); Invoke-Expression $s.Substring($i)"
echo.
pause
exit /b

#PS-BEGIN
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
try {
  [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
  $repo = '2004Kunj/learnAutonomy'
  $desk = [Environment]::GetFolderPath('Desktop')          # follows OneDrive Desktop redirection
  $dest = Join-Path $desk 'Anatomy Lab'
  $tmp = Join-Path $env:TEMP ('anatomylab-' + [guid]::NewGuid().ToString('N'))
  New-Item -ItemType Directory -Path $tmp | Out-Null
  Write-Host "  Downloading from github.com/$repo (about 90 MB, this can take a minute)..."
  $zip = Join-Path $tmp 'lab.zip'
  Invoke-WebRequest -Uri "https://codeload.github.com/$repo/zip/refs/heads/main" -OutFile $zip -UseBasicParsing
  Write-Host '  Unpacking...'
  Expand-Archive -LiteralPath $zip -DestinationPath $tmp -Force
  $src = Get-ChildItem -LiteralPath $tmp -Directory | Select-Object -First 1
  if (-not (Test-Path (Join-Path $src.FullName 'app\index.html'))) { throw 'The download did not contain the app.' }
  if (Test-Path -LiteralPath (Join-Path $dest 'app')) { Remove-Item -LiteralPath (Join-Path $dest 'app') -Recurse -Force }   # update in place
  New-Item -ItemType Directory -Path $dest -Force | Out-Null
  Copy-Item -LiteralPath (Join-Path $src.FullName 'app') -Destination $dest -Recurse -Force
  foreach ($f in 'install\Start-AnatomyLab.ps1', 'README.md', 'LICENSE', 'LICENSE-DATA.md') {
    $p = Join-Path $src.FullName $f; if (Test-Path -LiteralPath $p) { Copy-Item -LiteralPath $p -Destination $dest -Force }
  }
  $launcher = Join-Path $dest 'Start-AnatomyLab.ps1'
  $sh = (New-Object -ComObject WScript.Shell).CreateShortcut((Join-Path $desk 'Anatomy Lab.lnk'))
  $sh.TargetPath = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
  $sh.Arguments = '-NoProfile -ExecutionPolicy Bypass -WindowStyle Minimized -File "' + $launcher + '"'
  $sh.WorkingDirectory = $dest
  $sh.IconLocation = (Join-Path $env:SystemRoot 'System32\SHELL32.dll') + ',13'
  $sh.Description = 'Open Anatomy Lab (KNES 259)'
  $sh.Save()
  Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue
  Write-Host ''
  Write-Host "  Done. Installed to: $dest" -ForegroundColor Green
  Write-Host '  Double-click "Anatomy Lab" on your Desktop any time to open it.'
  Write-Host '  Run this installer again later to update to the newest version.'
  Write-Host '  Starting it now...'
  Start-Process -FilePath $sh.TargetPath -ArgumentList $sh.Arguments -WorkingDirectory $dest -WindowStyle Minimized
} catch {
  Write-Host ''
  Write-Host ('  Install failed: ' + $_.Exception.Message) -ForegroundColor Red
  Write-Host '  Check your internet connection and try again.'
}
