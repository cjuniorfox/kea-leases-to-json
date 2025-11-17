from .core import kea_leases_to_json
from .cli import main

__all__ = ["main", "kea_leases_to_json"]
__version__ = "0.1.0"

def get_version():
    return __version__