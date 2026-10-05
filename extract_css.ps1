$c = Get-Content limova_home.html -Raw
if ($c -match '(?s)<style[^>]*>(.*?)</style>') {
  [System.IO.File]::WriteAllText('limova_styles.css', $matches[1])
  Write-Host "CSS saved: $($matches[1].Length) chars"
} else { Write-Host 'no style found' }