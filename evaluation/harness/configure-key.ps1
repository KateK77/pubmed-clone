$ErrorActionPreference = 'Stop'
$privateDir = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../private'))
[IO.Directory]::CreateDirectory($privateDir) | Out-Null
$keyFile = Join-Path $privateDir 'openai-api-key.local'
$configuredKey = [Environment]::GetEnvironmentVariable('OPENAI_API_KEY', 'User')
if ([string]::IsNullOrWhiteSpace($configuredKey)) {
    $secureInput = Read-Host 'OpenAI API key (hidden input)' -AsSecureString
    $secretPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureInput)
    try { $configuredKey = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($secretPointer) }
    finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($secretPointer) }
}
if ([string]::IsNullOrWhiteSpace($configuredKey)) { throw 'No key supplied; nothing written.' }
try {
    [IO.File]::WriteAllText($keyFile, $configuredKey.Trim(), (New-Object Text.UTF8Encoding($false)))
    Write-Output 'Local API key configured. No API request made. The private directory is ignored by Git.'
} finally {
    Remove-Variable configuredKey, secureInput, secretPointer -ErrorAction SilentlyContinue
}
