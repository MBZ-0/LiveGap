from .models import Goal
from .runner import success_urls_for

def get_success_urls(site_id: str, goal: Goal) -> list[str]:
    return success_urls_for(site_id, goal)

__all__ = ["get_success_urls"]