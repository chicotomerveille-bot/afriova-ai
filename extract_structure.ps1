$c = Get-Content limova_home.html -Raw
# Find all top-level-ish tags with class attributes
$matches = [System.Text.RegularExpressions.Regex]::Matches($c, '<(?<tag>\w+)(?<rest>[^>]*?)>')
$groups = @{}
foreach ($m in $matches) {
  $tag = $m.Groups['tag'].Value
  $rest = $m.Groups['rest'].Value
  if ($rest -match 'class="([^"]*)"') {
    $cls = $matches[1]
    if (-not $groups[$tag]) { $groups[$tag] = @{} }
    if (-not $groups[$tag][$cls]) { $groups[$tag][$cls] = 0 }
    $groups[$tag][$cls]++
  }
}
foreach ($tag in $groups.Keys | Sort-Object) {
  Write-Host "`n== $tag ==" -ForegroundColor Yellow
  foreach ($cls in $groups[$tag].Keys | Sort-Object) {
    Write-Host "  .{0}  ({1}x)" -f $cls, $groups[$tag][$cls]
  }
}