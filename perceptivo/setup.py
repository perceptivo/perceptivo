"""
Additional environmental/system setup routines post python package install

Uses some autopilot scripts, see https://docs.auto-pi-lot.com/en/latest/setup/scripts.html
"""

from autopilot.setup.run_script import run_script

def setup_patient():
    # install jackd audio
    run_script('jackd_source')



