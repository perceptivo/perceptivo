"""
Networking between objects and computers
"""

from perceptivo.data.types import Socket



CLINICIAN = (
    Socket('PUB', 'tcp', 5000, 'command'),
)

AUDIO = (
    Socket('SUB', 'tcp', )
)