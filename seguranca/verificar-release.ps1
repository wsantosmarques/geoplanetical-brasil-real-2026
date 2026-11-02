param(
  [Parameter(Mandatory=$true)][ValidatePattern('^v[0-9]+\.[0-9]+\.[0-9]+-experimental$')][string]$Tag,
  [Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$')][string]$Repository
)
$ErrorActionPreference='Stop'
$reportDir=Join-Path $PSScriptRoot 'resultado-ci'
New-Item -ItemType Directory -Force -Path $reportDir | Out-Null
$packagesDir=Join-Path $env:RUNNER_TEMP ('meb-packages-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $packagesDir | Out-Null
$report=[ordered]@{ tag=$Tag; repository=$Repository; engine='Microsoft Defender Antivirus'; files=@(); result='not_run'; installerExecuted=$false }
try {
  gh release download $Tag --repo $Repository --dir $packagesDir --pattern '*.exe' --pattern '*.zip' --pattern 'SHA256SUMS.txt'
  if ($LASTEXITCODE -ne 0) {throw 'Falha ao baixar os pacotes da release'}
  $expected=@{}
  Get-Content -LiteralPath (Join-Path $packagesDir 'SHA256SUMS.txt') | ForEach-Object {
    if ($_ -match '^([a-fA-F0-9]{64})\s+([A-Za-z0-9_.-]+)$') { $expected[$Matches[2]]=$Matches[1].ToLowerInvariant() }
  }
  $files=@(Get-ChildItem -LiteralPath $packagesDir -File | Where-Object Extension -in '.exe','.zip')
  if ($files.Count -lt 2) {throw 'Pacotes incompletos'}
  foreach ($file in $files) {
    $hash=(Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    if (-not $expected.ContainsKey($file.Name) -or $hash -ne $expected[$file.Name]) {throw ('SHA-256 divergente: '+$file.Name)}
    $report.files+=@{ file=$file.Name; bytes=$file.Length; sha256=$hash }
  }
  try { Update-MpSignature -ErrorAction Stop } catch { $report.signatureUpdateError=$_.Exception.Message }
  $status=Get-MpComputerStatus -ErrorAction Stop
  if (-not $status -or -not $status.AntivirusEnabled -or -not $status.AntivirusSignatureVersion) {
    $report.result='scanner_unavailable'
    throw 'Defender indisponível ou sem assinaturas neste runner; análise não realizada'
  }
  $report.signatureVersion=$status.AntivirusSignatureVersion
  $report.signatureUpdatedAt=if ($status.AntivirusSignatureLastUpdated) { $status.AntivirusSignatureLastUpdated.ToUniversalTime().ToString('o') } else { $null }
  $candidate=Join-Path $env:ProgramData 'Microsoft\Windows Defender\Platform\CurrentVersion\MpCmdRun.exe'
  if (-not (Test-Path -LiteralPath $candidate)) {
    $candidate=Get-ChildItem (Join-Path $env:ProgramData 'Microsoft\Windows Defender\Platform') -Filter MpCmdRun.exe -Recurse -File | Sort-Object LastWriteTime -Descending | Select-Object -First 1 -ExpandProperty FullName
  }
  if (-not $candidate) {throw 'MpCmdRun não localizado'}
  & $candidate -Scan -ScanType 3 -File $packagesDir -DisableRemediation 2>&1 | Tee-Object -FilePath (Join-Path $reportDir 'scanner.log')
  $scanExit=$LASTEXITCODE; $report.exitCode=$scanExit
  if ($scanExit -ne 0) { $report.result='scan_failed_or_detection';throw ('Scanner terminou com código '+$scanExit) }
  $report.result='no_threats_detected'
  $report.limits='Resultado desta análise, sem garantia absoluta de segurança; não substitui revisão e atualização.'
} catch {
  $report.error=$_.Exception.Message
  throw
} finally {
  $report.finishedAt=[datetime]::UtcNow.ToString('o')
  $report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $reportDir 'relatorio.json') -Encoding utf8
  if ($env:GITHUB_STEP_SUMMARY) {
    @("## Verificação antivírus", "Release: $Tag", "Resultado: $($report.result)", "O instalador não foi executado.", "Relatório e hashes no artefato deste job.") | Add-Content -LiteralPath $env:GITHUB_STEP_SUMMARY
  }
}
