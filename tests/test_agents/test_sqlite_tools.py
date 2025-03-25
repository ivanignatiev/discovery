import os
import pytest
from discovery.agents.sqlite import *


@pytest.fixture
def db_path():
    target_path = "."
    files = os.listdir(target_path)
    snapshot_files = [f for f in files if f.endswith(".db")]
    latest_snapshot = max(snapshot_files, key=os.path.getctime)
    return os.path.join(target_path, latest_snapshot)


def test_get_latest_snapshot_path():
    path = get_latest_snapshot_path(".")

    assert len(path) > 0


def test_list_tables_names(db_path):
    response = list_tables_names(db_path)

    assert len(response) > 0


def test_get_table_schema(db_path):
    response = get_table_schema(db_path, "az_microsoft_storage_storageaccounts")

    assert len(response) > 0


def test_execute_select_query(db_path):
    query = "SELECT * FROM az_resources LIMIT 1"
    response = execute_select_query(db_path, query)

    assert len(response) > 0
