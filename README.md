# Dotfiles Setup

A comprehensive dotfiles setup that configures development environments for macOS, Linux, and Windows.

## Quick Install

Basic installation:
```bash
curl -L https://raw.githubusercontent.com/minhnhb1304/dotfiles/master/setup.sh | bash
```

With command line options:
```bash
curl -L https://raw.githubusercontent.com/minhnhb1304/dotfiles/master/setup.sh | bash -s -- [OPTIONS]
```

## Installation Options

- `-m, --minimal`: Minimal installation with fewer packages and tools
- `-n, --no-sudo`: Install without sudo privileges
- `-h, --help`: Display help message

Examples:
```bash
# Minimal installation
curl -L https://raw.githubusercontent.com/minhnhb1304/dotfiles/master/setup.sh | bash -s -- -m

# Installation without sudo
curl -L https://raw.githubusercontent.com/minhnhb1304/dotfiles/master/setup.sh | bash -s -- -n

# Minimal installation without sudo
curl -L https://raw.githubusercontent.com/minhnhb1304/dotfiles/master/setup.sh | bash -s -- -m -n
```

## Windows (native)

In PowerShell (no admin required):

```powershell
irm https://raw.githubusercontent.com/minhnhb1304/dotfiles/master/setup.ps1 | iex
```

This installs chezmoi + [Scoop](https://scoop.sh), applies the cross-platform configs
(git, neovim, mise, Claude/ccp, ideavim), installs CLI tools (neovim, fzf, ripgrep, fd,
bat, eza, zoxide, starship, jq, mise) and PowerShell 7, then writes a PowerShell profile
(mise activation, starship prompt, aliases). Unix-only configs (zsh, tmux, kitty, rofi,
terminator, ranger) are skipped automatically via `.chezmoiignore`.

> For Windows + WSL2, use the Linux instructions above inside your WSL distro instead.

## Features

### Core Setup
- XDG base directory structure
- Git configuration
- ZSH as default shell (Linux)
- Homebrew (macOS)
- Rosetta 2 (macOS ARM)

### Tools & Utilities
- [chezmoi](https://chezmoi.io) for dotfiles management
- [fzf](https://github.com/junegunn/fzf) for fuzzy finding
- [mise](https://mise.run) for runtime version management
- [tmux](https://github.com/tmux/tmux) with plugin manager (full installation)
- [Miniconda](https://docs.conda.io/en/latest/miniconda.html) for Python environment management (full installation)

### Additional Features in Full Installation
- Development tools and build essentials
- Python pip and related packages
- FiraCode Nerd Font (Linux)
- Additional system utilities

## System Requirements
- macOS, Linux (Debian/Ubuntu-based), or Windows 10/11
- Internet connection
- macOS/Linux: Git + curl
- Windows: PowerShell 5.1+ (PowerShell 7 is installed automatically)

## Note
The script automatically detects your operating system and installs the appropriate packages and configurations. Use the minimal installation option (-m) for a lighter setup or the no-sudo option (-n) when you don't have sudo privileges.
