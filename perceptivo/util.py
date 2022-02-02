"""
Utility functions! everyone's favorite!
"""

import typing
from typing import Union
from pathlib import Path

import requests

def download(url:str, output:Union[str, Path], mode:str='wb') -> bool:
    """
    Download a file! with ``requests`` !

    Args:
        url (str): URL to download
        output (str, Path): Place to download it to
        mode (str): Mode to open ``output`` with

    Returns:
        ``True`` if successful, otherwise ``False``
    """

    response = requests.get(url)
    with open(output, mode) as ofile:
        ofile.write(response.content)

    if output.exists():
        return True
    else:
        return False



