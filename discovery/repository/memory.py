from typing import List, Any, Dict
from .repository import Repository
from .targets.target import Target
from .config import SYSTEM_UNIQUE_ID_KEY

class MemoryRepository(Repository):
    """
    Keep all resources in memory
    """

    resources_count: Dict[str, int] = {}
    resources: Dict[str, List[Dict]] = {}

    def __init__(self) -> None:
        self.resources = {}

    def add(self, type: str, resource: dict, unique_id_key = SYSTEM_UNIQUE_ID_KEY) -> None:
        """
        Add a resource to the repository

        Parameters
        ----------
        type : str
            The type of the resource lowercased with underscores
        resource : dict
            The resource to add to the repository flattened to a dictionary
        unique_id_key : str
            The key of the unique identifier in the resource, default is "id" <- .config.SYSTEM_UNIQUE_ID_KEY
        """

        if type not in self.resources:
            self.resources[type] = []
            self.resources_count[type] = 0

        resource[SYSTEM_UNIQUE_ID_KEY] = resource[unique_id_key]
        self.resources[type].append(resource)
        self.resources_count[type] += 1

    def get_all(self) -> Dict[str, List[Dict]]:
        return self.resources

    def get_all_by_type(self, type: str) -> List[Dict]:
        return self.resources.get(type, [])

    def get_count_by_type(self, type: str) -> int:
        return self.resources_count.get(type, 0)

    def save_to(self, target: Target) -> None:
        target.save(self.resources)
