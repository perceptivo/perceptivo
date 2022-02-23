"""
Additional environmental/system setup routines post python package install

Uses some autopilot scripts, see https://docs.auto-pi-lot.com/en/latest/setup/scripts.html
"""
import typing
import argparse
import subprocess
from pathlib import Path
from autopilot.setup.run_script import run_scripts, call_series
from autopilot import prefs

hifiberry_dacplus = [
    {'command': 'sudo adduser pi i2c', 'optional': True},
    'sudo sed -i \'s/^dtparam=audio=on/#dtparam=audio=on/g\' /boot/config.txt',
    'sudo sed -i \'$s/$/\\ndtoverlay=hifiberry-dacplusadcpro\\ndtoverlay=i2s-mmap\\ndtoverlay=i2c-mmap\\ndtparam=i2c1=on\\ndtparam=i2c_arm=on/\' /boot/config.txt',
    'echo -e \'pcm.!default {\\n type hw card 2\\n}\\nctl.!default {\\n type hw card 2\\n}\' | sudo tee /etc/asound.conf'
]
"""
Script used by :func:`autopilot.setup.run_script.call_series` to setup hifiberry dac/adc pro

See also: https://wiki.auto-pi-lot.com/index.php/HiFiBerry_DAC%2B_ADC_pro
"""

pulseaudio_service = """
[Unit]
Description=PulseAudio Sound System
Before=sound.target

[Service]
User=pi
BusName=org.pulseaudio.Server
ExecStart=/usr/bin/pulseaudio
Restart=always  

[Install]
WantedBy=session.target
"""

pulseaudio_command = [
    {'command': 'mkdir ~/.config/systemd', 'optional': True},
    {'command': 'mkdir ~/.config/systemd/user', 'optional': True},
    'echo '
    'echo -e'
]

apt_requirements = {
    'patient': [
        'libsamplerate0-dev',
        'libsndfile1-dev',
        'libreadline-dev',
        'libasound2-dev',
        'liblo-dev',
        'libavformat-dev',
        'libswscale-dev',
        'pulseaudio'
    ]
}
"""
System-level packages required for different runtimes

TODO: move these into the runtime classes
"""

def pulse_systemd(location='/lib/systemd/system/pulseaudio.service'):
    """
    Make a systemd service to launch pulse audio
    """

    location = Path(location)
    try:
        # make unit file
        subprocess.call(f'sudo sh -c \"echo \'{pulseaudio_service}\' > {str(location)}\"', shell=True)
        # enable service
        subprocess.call(['sudo', 'systemctl', 'daemon-reload'])
        sysd_result = subprocess.call(['sudo', 'systemctl', 'enable', location.name])

        if sysd_result != 0:
            message = "Could not enable pulseaudio systemd service!"
        else:
            message = "Systemd service for pulseudio successfully enabled"

    except PermissionError:
        message = "systemd service could not be installed due to a permissions error.\n" + \
                  "create a unit file containing the following at {}\n\n{}".format(location, pulseaudio_service)

    print(message)


def install_apt(packages: typing.List[str]) -> bool:
    """
    Install packages from apt (updating first)

    Args:
        packages (list): A list of pacakge (strings) to install

    Returns:
        bool: ``True`` if successful
    """

    # construct call string
    apt_str = "sudo apt update && sudo apt install -y " + ' '.join(packages)

    result = subprocess.run(apt_str, shell=True, executable='/bin/bash')
    status = False
    if result.returncode == 0:
        status = True

    return status



def setup_patient():
    # install jackd audio and do performance tweaks
    install_apt(apt_requirements['patient'])
    run_scripts(['performance', 'picamera'])
    call_series(hifiberry_dacplus, 'hifiberry dacplus')
    pulse_systemd()


parser = argparse.ArgumentParser(description="Do additional setup for perceptivo")
parser.add_argument('--patient', help="Install additional requirements for patient runtime", action="store_true")
parser.add_argument('--clinician', help="Install additional requirements for clinician runtime", action="store_true")

if __name__ == "__main__":
    args = parser.parse_args()

    if args.patient:
        print('installing patient requirements')
        setup_patient()
    if args.clinician:
        print('installing clinician requirements')
        raise NotImplementedError('Clinician requirements not implemented yet!')




