import json
from pathlib import Path
from dataclasses import dataclass
from typing import List

@dataclass
class Site:
    id: str
    name: str
    url: str


def load_sites() -> List[Site]:
    """Load static site list; heuristic agent removed."""
    sites_path = Path(__file__).with_name("sites.json")
    data = json.loads(sites_path.read_text())
    return [Site(**item) for item in data]

__all__ = ["Site", "load_sites"]
