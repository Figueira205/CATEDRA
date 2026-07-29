# Ensambla las páginas: sustituye los marcadores por las particiones.
# Equivalente estático a get_header()/get_footer() de WordPress.
$root = $PSScriptRoot
$head = Get-Content "$root\_partials\head-common.html" -Raw -Encoding UTF8
$header = Get-Content "$root\_partials\header.html" -Raw -Encoding UTF8
$footer = Get-Content "$root\_partials\footer.html" -Raw -Encoding UTF8

Get-ChildItem "$root\*.html" | ForEach-Object {
  $c = Get-Content $_.FullName -Raw -Encoding UTF8
  if ($c -match '<!--@(HEADCOMMON|HEADER|FOOTER)-->') {
    $c = $c -replace '<!--@HEADCOMMON-->', $head
    $c = $c -replace '<!--@HEADER-->', $header
    $c = $c -replace '<!--@FOOTER-->', $footer
    [System.IO.File]::WriteAllText($_.FullName, $c, (New-Object System.Text.UTF8Encoding $false))
    Write-Host "Ensamblada: $($_.Name)"
  }
}
