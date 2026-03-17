"""
Creating the class dam, and the reservoir class
"""

from dataclasses import dataclass

@dataclass
class Dam:
    name: str
    latitude: float
    longitude: float