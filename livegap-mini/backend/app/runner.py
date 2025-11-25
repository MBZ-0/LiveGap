import os
import yaml
from dataclasses import dataclass
from typing import List, Dict
from .models import Goal

@dataclass
class Site:
    id: str
    name: str
    url: str  # start_url

_sites_cache: List[Site] | None = None
_success_cache: Dict[str, Dict[Goal, List[str]]] | None = None

def _config_path() -> str:
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "sites.yaml")

def _load_yaml() -> Dict:
    path = _config_path()
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def load_sites() -> List[Site]:
    global _sites_cache, _success_cache
    if _sites_cache is not None:
        return _sites_cache
    raw = _load_yaml()
    sites: List[Site] = []
    success_map: Dict[str, Dict[Goal, List[str]]] = {}
    for entry in raw.get("sites", []):
        sid = entry.get("id")
        if not sid:
            continue
        site = Site(id=sid, name=entry.get("name", sid), url=entry.get("start_url", ""))
        sites.append(site)
        success_map[sid] = {}
        success_cfg = entry.get("success", {})
        for key, urls in success_cfg.items():
            # map lowercase key to Goal enum name lowercased
            lk = key.lower()
            for g in Goal:
                if g.name.lower() == lk:
                    success_map[sid][g] = urls or []
    _sites_cache = sites
    _success_cache = success_map
    return sites

def success_urls_for(site_id: str, goal: Goal) -> List[str]:
    if _success_cache is None:
        load_sites()
    return (_success_cache.get(site_id, {}) or {}).get(goal, [])

__all__ = ["Site", "load_sites", "success_urls_for"]
