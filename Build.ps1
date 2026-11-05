param([string]$FmodCli = 'E:\DCC\FMOD Studio 2.03.06\fmodstudiocl.exe')
$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    & $FmodCli -build -banks 'HK_Emiya_SFX,HK_Emiya_Music,HK_Emiya_VoidHeart' -export-guids HollowKnightAudio.fspro
    if ($LASTEXITCODE -ne 0) { throw "FMOD build failed: $LASTEXITCODE" }
    & $FmodCli -script ValidateProject.js HollowKnightAudio.fspro
    if ($LASTEXITCODE -ne 0) { throw "FMOD validation failed: $LASTEXITCODE" }
    New-Item -ItemType Directory -Force Package | Out-Null
    Copy-Item Build\desktop\HK_Emiya_SFX.bank,Build\desktop\HK_Emiya_Music.bank,Build\desktop\HK_Emiya_VoidHeart.bank Package -Force
    Get-Content Build\GUIDs.txt | Where-Object { $_ -match ' (event:/(sfx|music)/hollow_knight/|bank:/HK_Emiya_)' } | Set-Content Package\GUIDs.txt -Encoding utf8
    if (@(Get-Content Package\GUIDs.txt).Count -ne 66) { throw 'Expected 63 event mappings and 3 bank mappings.' }
    Write-Output 'Build and validation passed. Package is ready.'
} finally { Pop-Location }
