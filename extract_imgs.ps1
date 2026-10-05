$c = Get-Content limova_home.html -Raw
$imgs = [System.Text.RegularExpressions.Regex]::Matches($c, 'https://cdn\.prod\.website-files\.com/6a00594a6766c689a1d88ada/[^"'' ]+\.(avif|png|jpg|jpeg|webp)')
$seen = @{}
foreach ($m in $imgs) {
  $u = $m.Value
  if (-not $seen[$u]) { $seen[$u] = $true; Write-Host $u }
}
Write-Host "---TOTAL UNIQUE: $($seen.Count)"