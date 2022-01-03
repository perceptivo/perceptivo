"""
Additional environmental/system setup routines post python package install

Uses some autopilot scripts, see https://docs.auto-pi-lot.com/en/latest/setup/scripts.html
"""
import typing
import argparse
import subprocess
from autopilot.setup.run_script import run_scripts, call_series

hifiberry_dacplus = [
    {'command': 'sudo adduser pi i2c', 'optional': True},
    'sudo sed -i \'s/^dtparam=audio=on/#dtparam=audio=on/g\' /boot/config.txt',
    'sudo sed -i \'$s/$/\\ndtoverlay=hifiberry-dacplusadcpro\\ndtoverlay=i2s-mmap\\ndtoverlay=i2c-mmap\\ndtparam=i2c1=on\\ndtparam=i2c_arm=on/\' /boot/config.txt',
    'echo -e \'pcm.!default {\\n type hw card 0\\n}\\nctl.!default {\\n type hw card 0\\n}\' | sudo tee /etc/asound.conf'
]
"""
Script used by :func:`autopilot.setup.run_script.call_series` to setup hifiberry dac/adc pro

See also: https://wiki.auto-pi-lot.com/index.php/HiFiBerry_DAC%2B_ADC_pro
"""

apt_requirements = {
    'patient': [
        'libsamplerate0-dev',
        'libsndfile1-dev',
        'libreadline-dev',
        'libasound-dev',
        'liblo-dev'
    ]
}
"""
System-level packages required for different runtimes

TODO: move these into the runtime classes
"""

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
    run_scripts(['jackd_source', 'performance'])
    call_series(hifiberry_dacplus, 'hifiberry dacplus')


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




