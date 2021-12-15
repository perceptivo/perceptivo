# Installation

## Imaging RaspiOS

## Shared

On all raspberry pis, after installing the operating system you should...

### Basic Configuration

* Change the password using `passwd`
* Update and upgrade system packages with `sudo apt update && sudo apt upgrade -y`
* Use `sudo raspi-config` to configure
    * localization settings and timezone
    * enable SSH access
    * enable WiFi access (if needed)
* If enabling SSH, install an RSA key and disable password access - see https://wiki.auto-pi-lot.com/index.php/SSH

### Install system packages

Install the following system packages from apt:

```bash
sudo apt install -y \
  git \
  python3-pip \
  openssl \
  build-essential \
  libssl-dev \
  libffi-dev \
  libjpeg-dev \
  zlib1g-dev \
  libatlas-base-dev 
  
```

Install rust (needed to install poetry):
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.bashrc
```

Install poetry:
```bash
pip install poetry
```

You may need to add the local bin folder to PATH
```bash
echo 'export PATH=/home/pi/.local/bin:$PATH' >> ~/.bashrc
```

### Install perceptivo

Clone the repository
```bash
git clone https://github.com/perceptivo/perceptivo
```

install perceptivo
```
cd perceptivo
poetry shell
```

Depending on which raspi this is, you need to specify some additional, optional packages:

**patient**

```bash
poetry install -E patient
```

**Clinician**

```bash
poetry install -E clinician
```

## Patient

Install additional post-install dependencies using perceptivo & autopilot scripts

* Install jackd audio from source using `jackd_source` script
* Do performance-enhancing tweaks using `performance`
* Enable hifiberry DAC / ADC Pro 

```bash
python -m perceptivo.setup --patient
```
