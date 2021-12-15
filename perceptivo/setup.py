"""
Additional environmental/system setup routines post python package install

Uses some autopilot scripts, see https://docs.auto-pi-lot.com/en/latest/setup/scripts.html
"""

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

def setup_patient():
    # install jackd audio and do performance tweaks
    run_scripts(['jackd_source', 'performance'])
    call_series(hifiberry_dacplus, 'hifiberry dacplus')



