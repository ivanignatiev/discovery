from typing import List, Any, Dict
from .targets.target import Target


class Repository:
    def add(self, type: str, resource: dict) -> None:
        raise NotImplementedError("add() Method not implemented")

    def get_all(self) -> Dict[str, List[Dict]]:
        raise NotImplementedError("get_all() Method not implemented")

    def get_all_by_type(self, type: str) -> List[Dict]:
        raise NotImplementedError("get_all_by_type() Method not implemented")

    def save_to(self, target: Target) -> None:
        raise NotImplementedError("save_to() Method not implemented")
