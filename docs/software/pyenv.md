# Installing Python with Pyenv

## Install Prerequisites

```bash
sudo apt-get update && sudo apt-get install -y 
    make \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    wget \
    curl \
    llvm \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libxml2-dev \
    libxmlsec1-dev \
    libffi-dev \
    liblzma-dev
```

## Build pyenv

```bash
mkdir ~/git; cd ~/git
https://github.com/pyenv/pyenv.git
cd pyenv && src/configure && make -C src
```

## Configure pyenv

add this to `~/.bashrc`

```bash
export PYENV_ROOT="$HOME/git/pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
```

and then source it so it works

```bash
source ~/.bashrc
```

## Install Python

Use pyenv to install python, for example let's use `3.8.12`

```bash
pyenv install 3.8.12
```

Then set the pyenv version in your `~/.bashrc` file

```angular2html
echo "export PYENV_VERSION=\"3.8.12\"" >> ~/.bashrc
source ~/.bashrc
```



