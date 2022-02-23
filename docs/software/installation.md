# Installation

## Imaging RaspiOS

* Download the RaspiOS image from the [Download Page](https://www.raspberrypi.com/software/operating-systems/)
  * For Patient, download Raspi OS Lite - [HTTP](https://downloads.raspberrypi.org/raspios_lite_arm64/images/raspios_lite_arm64-2022-01-28/2022-01-28-raspios-bullseye-arm64-lite.zip), [.torrent](https://downloads.raspberrypi.org/raspios_lite_arm64/images/raspios_lite_arm64-2022-01-28/2022-01-28-raspios-bullseye-arm64-lite.zip.torrent)
  * For Clinician, download Raspi OS with Desktop - [HTTP](https://downloads.raspberrypi.org/raspios_armhf/images/raspios_armhf-2021-11-08/2021-10-30-raspios-bullseye-armhf.zip), [.torrent](https://downloads.raspberrypi.org/raspios_armhf/images/raspios_armhf-2021-11-08/2021-10-30-raspios-bullseye-armhf.zip.torrent)


### Mac

* Find the name of the SD card using `sudo diskutil list`, will be something like `/dev/disk2`
* Unmount disk with `sudo diskutil unmountDisk /dev/disk2` (but replacing the name/number of your disk)
* Use `dd` to copy the image, note the use of `rdisk` (with same number) rather than `disk`. You can check the status of the transfer with `ctrl+t`:
```bash
sudo dd if=/path/to/raspios-image.img of=/dev/rdisk2 bs=1m
```

### Imager

You can also use the raspberry pi imager, available for windows, mac, and ubuntu:

[https://www.raspberrypi.org/downloads.../](https://www.raspberrypi.org/downloads.../)

## Shared

On all raspberry pis, after installing the operating system you should...

### Basic Configuration

* Change the password using `passwd`
* Update and upgrade system packages with `sudo apt update && sudo apt upgrade -y`
* Use `sudo raspi-config` to configure
    * localization settings and timezone
    * enable SSH access
    * enable WiFi access (if needed)
* If enabling SSH, install an RSA key and disable password access - see [https://wiki.auto-pi-lot.com/index.php/SSH](https://wiki.auto-pi-lot.com/index.php/SSH)

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
  libatlas-base-dev \
  gfortran \
  libhdf5-dev \
  cmake \
  ninja-build \
  libopenjp2-7 \
  libtiff5
```

Install rust (needed to install poetry):
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.bashrc
```

You may need to add the local bin folder to PATH
```bash
echo 'export PATH=/home/pi/.local/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

Install poetry:
```bash
pip install --upgrade pip
pip install poetry
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

Call

```bash
python -m perceptivo.setup --patient
```

and then restart. 

### Audio

Depending on the raspberry pi, you might need some additional configuration to tell alsa
which sound card to use.  By default, autopilot creates an alsa configuration file
that points to the 0th card.

To tell which card to use...

```bash
>>> aplay -l

**** List of PLAYBACK Hardware Devices ****
card 0: vc4hdmi0 [vc4-hdmi-0], device 0: MAI PCM i2s-hifi-0 [MAI PCM i2s-hifi-0]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
card 1: vc4hdmi1 [vc4-hdmi-1], device 0: MAI PCM i2s-hifi-0 [MAI PCM i2s-hifi-0]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
card 2: sndrpihifiberry [snd_rpi_hifiberry_dacplusadcpro], device 0: HiFiBerry DAC+ADC Pro HiFi multicodec-0 [HiFiBerry DAC+ADC Pro HiFi multicodec-0]
  Subdevices: 0/1
  Subdevice #0: subdevice #0
```

in this case we want to use card 2, so we replace that number in `/etc/asound.conf`

```

```