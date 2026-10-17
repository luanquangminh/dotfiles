# PowerShell profile managed by chezmoi (minhnhb1304/dotfiles).
# Mirrors the zsh setup: mise activation, starship prompt, and common aliases.
# Edit the source at .chezmoitemplates/powershell-profile.ps1, then `chezmoi apply`.

$env:EDITOR = "nvim"

# mise: tool versions + project env
if (Get-Command mise -ErrorAction SilentlyContinue) {
    # mise's directory-change hook needs PowerShell 7; silence the per-session warning on 5.1.
    if ($PSVersionTable.PSVersion.Major -lt 7) { $env:MISE_PWSH_CHPWD_WARNING = '0' }
    (& mise activate pwsh) | Out-String | Invoke-Expression
}

# starship prompt
if (Get-Command starship -ErrorAction SilentlyContinue) {
    Invoke-Expression (& starship init powershell)
}

# zoxide: smarter cd (use `z <dir>`)
if (Get-Command zoxide -ErrorAction SilentlyContinue) {
    Invoke-Expression (& { (zoxide init powershell | Out-String) })
}

# Aliases / functions mirroring the zsh config
if (Get-Command eza -ErrorAction SilentlyContinue) {
    function ll { eza -la --git --icons @args }
    function la { eza -a  --icons @args }
    function ls { eza      --icons @args }
}
if (Get-Command bat -ErrorAction SilentlyContinue) {
    function cat { bat @args }
}
if (Get-Command nvim -ErrorAction SilentlyContinue) {
    function vim { nvim @args }
}
Set-Alias -Name g -Value git
