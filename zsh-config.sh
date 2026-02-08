# Personal shell setup
export PATH="$HOME/.local/bin:$PATH"
plugins=(
	git 
	zsh-autosuggestions 
	zsh-syntax-highlighting
)

# ======================================= Setups ========================================

# Setup oh-my-zsh
export ZSH="$HOME/.oh-my-zsh"
source $ZSH/oh-my-zsh.sh

# =================================== Optional setups ===================================

# Setup zoxide
command -v zoxide 1> /dev/null && eval "$(zoxide init zsh)"

# Setup oh-my-posh, terminal prompt
OMP_THEME_REPO=https://github.com/GeoffreyCoulaud/omp-theme-yellow-frey
OMP_THEME=$OMP_THEME_REPO/raw/main/yellow-frey.omp.json
command -v oh-my-posh 1> /dev/null && eval "$(oh-my-posh init zsh --config $OMP_THEME)"

# Setup Sdkman
# THIS MUST BE AT THE END OF THE FILE FOR SDKMAN TO WORK!!!
SDKMAN_INIT="$HOME/.sdkman/bin/sdkman-init.sh"
export SDKMAN_DIR="$HOME/.sdkman"
[[ -s "$SDKMAN_INIT" ]] && source "$SDKMAN_INIT"
