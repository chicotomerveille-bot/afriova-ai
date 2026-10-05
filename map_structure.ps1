$c = Get-Content limova_home.html -Raw
$c2 = [System.Text.RegularExpressions.Regex]::Replace($c, '(?s)<script.*?</script>', '')
$c2 = [System.Text.RegularExpressions.Regex]::Replace($c2, '(?s)<style.*?</style>', '')
$secPat = [System.Text.RegularExpressions.Regex]::new('(?s)<section\b[^>]*class="([^"]*)"[^>]*>(.*?)(?=<section\b|</main>|</body>)')
$matches = $secPat.Matches($c2)
$i = 0
foreach ($m in $matches) {
  $cls = $m.Groups[1].Value
  $body = $m.Groups[2].Value
  $bodyClean = [System.Text.RegularExpressions.Regex]::Replace($body, '<[^>]+>', ' ')
  $bodyClean = [System.Text.RegularExpressions.Regex]::Replace($bodyClean, '\s+', ' ').Trim()
  $h = [System.Text.RegularExpressions.Regex]::Matches($body, '<h[12][^>]*>(.*?)</h[12]>') | ForEach-Object { ($_.Groups[1].Value -replace '<[^>]+>','').Trim() }
  Write-Host "=== SECTION $i : .$cls ==="
  Write-Host "  H: $h"
  Write-Host "  BODY: $($bodyClean.Substring(0, [Math]::Min(400, $bodyClean.Length)))"
  Write-Host "  LEN: $($body.Length)"
  $i++
}