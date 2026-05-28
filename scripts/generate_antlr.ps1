$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Jar = Join-Path $Root "antlr-4.13.2-complete.jar"
$Grammar = Join-Path $Root "grammar\KunsamuLang.g4"
$Output = Join-Path $Root "generated"

if (!(Test-Path $Jar)) {
    Write-Host "Descargando ANTLR 4.13.2..."
    Invoke-WebRequest -Uri "https://www.antlr.org/download/antlr-4.13.2-complete.jar" -OutFile $Jar
}

java -jar $Jar -Dlanguage=Python3 -visitor -Xexact-output-dir -o $Output $Grammar
Write-Host "Lexer, Parser y Visitor generados en $Output"
