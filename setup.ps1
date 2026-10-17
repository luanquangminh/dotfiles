# Windows bootstrap for minhnhb1304/dotfiles
# Usage (run in a NON-admin PowerShell):
#   irm https://raw.githubusercontent.com/minhnhb1304/dotfiles/master/setup.ps1 | iex
$ErrorActionPreference = "Stop"

function Test-Cmd($name) {
    return [bool](Get-Command $name -ErrorAction SilentlyContinue)
}

# Scoop installs to user scope and REFUSES to run elevated; warn early so the
# (otherwise cryptic) abort is understandable.
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if ($isAdmin) {
    Write-Host "[setup] WARNING: this PowerShell is elevated. Scoop refuses to install as admin — please re-run in a NON-admin PowerShell." -ForegroundColor Yellow
}

Write-Host "[setup] dotfiles for Windows"

# 1) Install chezmoi (prefer winget, then scoop, else bootstrap scoop).
if (-not (Test-Cmd chezmoi)) {
    Write-Host "[setup] installing chezmoi..."
    if (Test-Cmd winget) {
        winget install --id twpayne.chezmoi --exact --source winget --silent `
            --accept-package-agreements --accept-source-agreements --disable-interactivity
        # winget portable installs land here and update only the registry PATH, not this
        # session — add it so `chezmoi` resolves below.
        $wingetLinks = Join-Path $env:LOCALAPPDATA 'Microsoft\WinGet\Links'
        if ((Test-Path $wingetLinks) -and ($env:PATH -notlike "*$wingetLinks*")) {
            $env:PATH = "$wingetLinks;$env:PATH"
        }
    }
    elseif (Test-Cmd scoop) {
        scoop install chezmoi
    }
    else {
        try { Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force } catch {}
        Invoke-RestMethod -Uri "https://get.scoop.sh" | Invoke-Expression
        scoop install chezmoi
    }
}

# Confirm chezmoi resolves in THIS session before using it (a freshly installed CLI's
# PATH entry is often only in the registry, not the current process).
if (-not (Test-Cmd chezmoi)) {
    throw "chezmoi was installed but is not on PATH in this session. Open a NEW PowerShell window and re-run: irm https://raw.githubusercontent.com/minhnhb1304/dotfiles/master/setup.ps1 | iex"
}

# 2) Initialize from this repo and apply.
#    chezmoi prompts for git name/email; Windows-only targeting is handled by .chezmoiignore.
chezmoi init --apply minhnhb1304

Write-Host "[setup] done. Open a new PowerShell session to load your profile."
