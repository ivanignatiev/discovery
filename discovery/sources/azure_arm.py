from azure.mgmt.resourcegraph import ResourceGraphClient
from discovery.repository import Repository
from discovery.helpers.flatten_json import flatten_json
from discovery.helpers.logging import get_logger

logger = get_logger(__name__)


class AzureARM:
    """
    Extracts all resources from Azure Resource Graph and stores them in the repository
    """

    azure_credential: "TokenCredential" = None
    azure_resource_graph_client: ResourceGraphClient = None
    repository: Repository = None

    def __init__(self, credential: "TokenCredential", repository: Repository) -> None:
        self.azure_credential = credential
        self.repository = repository
        self.azure_resource_graph_client = ResourceGraphClient(
            credential=self.azure_credential
        )

    def _normalize_resource_type(self, resource_type: str) -> str:
        """
        Normalize resource type to be used as a key in the repository

        Parameters
        ----------
        resource_type : str
            Azure Resource Graph resource type
            Example: "Microsoft.Compute/virtualMachines"

        Returns
        -------
        str
            Normalized resource type
            Example: "microsoft_compute_virtualmachines"
        """
        return resource_type.lower().replace("/", "_").replace(".", "_")

    def _get_generic_resource(self, resource: dict) -> dict:
        """
        Get a generic resource with properties from Azure Resource Graph

        Parameters
        ----------
        resource : dict
            Azure Resource Graph resource

        Returns
        -------
        dict
            Generic resource with common to all Azure resources properties
        """
        return {
            "id": resource["id"],
            "name": resource["name"],
            "type": resource["type"],
            "location": resource.get("location", ""),
            "tags": resource.get("tags", {})
        }

    def _add_resources_to_repository(self, resources: list) -> None:
        """
        Add resources to the repository
        """
        logger.info("Adding resources to repository")
        logger.debug(f"Resources Count: {len(resources)}")

        for resource in resources:
            normalized_resource_type = self._normalize_resource_type(resource["type"])
            generic_resource = self._get_generic_resource(resource)
            flattened_generic_resource = flatten_json(generic_resource)
            flattened_resource = flatten_json(resource)

            self.repository.add("az_resources", flattened_generic_resource)
            self.repository.add(f"az_{normalized_resource_type}", flattened_resource)

    def _add_all_resource_containers(self) -> None:
        """
        Add all resource containers with their properties from Azure Resource Graph to repository
        """
        logger.info(
            "Getting from Az Resource Graph API all resource containers (management groups, subscriptions, resource group) to repository"
        )

        query = {"query": "ResourceContainers"}

        resource_containers_response = self.azure_resource_graph_client.resources(
            query=query
        )

        self._add_resources_to_repository(resource_containers_response.data)

        while resource_containers_response.skip_token:
            resource_containers_response = self.azure_resource_graph_client.resources(
                query={**query, "$skipToken": resource_containers_response.skip_token}
            )

            self._add_resources_to_repository(resource_containers_response.data)

    def _add_all_resources(self) -> None:
        """
        Get all resources with their properties from Azure Resource Graph
        """
        logger.info("Getting from Az Resource Graph API all resources to repository")

        query = {"query": "Resources"}

        resources_response = self.azure_resource_graph_client.resources(query=query)

        self._add_resources_to_repository(resources_response.data)

        while resources_response.skip_token:
            resources_response = self.azure_resource_graph_client.resources(
                query={**query, "$skipToken": resources_response.skip_token}
            )

            self._add_resources_to_repository(resources_response.data)

    def extract_all_resources(self) -> None:
        """
        Extract all resources from Azure Resource Graph and store them in the repository
        """

        logger.info("Extracting all resources from Azure Resource Graph")

        self._add_all_resource_containers()
        self._add_all_resources()
