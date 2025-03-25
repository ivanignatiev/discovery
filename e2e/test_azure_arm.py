from pathlib import Path

def test_azure_arm_get_all_resources(tmp_path):
    """
    Login to Azure with any available credential and extract all resources to memory repository

    To test on non-empty Azure subscription
    """

    from azure.identity import DefaultAzureCredential
    from discovery.sources.azure_arm import AzureARM
    from discovery.repository import MemoryRepository

    credential = DefaultAzureCredential()
    repository = MemoryRepository()
    azure_arm = AzureARM(credential, repository)
    azure_arm.extract_all_resources()

    assert repository.get_count_by_type("az_resources") > 0

    from discovery.repository.targets import SQLiteTarget

    db_path = Path(tmp_path / "test.db")
    target = SQLiteTarget(db_path)
    repository.save_to(target)

    assert db_path.exists()