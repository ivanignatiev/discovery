import pytest
import sqlite3
from datetime import datetime
from pathlib import Path


def test_sqlite_repository_target(tmp_path):
    from discovery.repository.targets.sqlite import SQLiteTarget
    from discovery.repository import MemoryRepository

    db_path = Path(tmp_path / f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
    repository = MemoryRepository()
    target = SQLiteTarget(db_path)

    test_row = {"id": 1, "key1": "value1", "key2": "value2", "key@3": "value3", "key-4": "value4", "key.5": "value5"}
    repository.add("resource_type_1", test_row)

    repository.save_to(target)

    with sqlite3.connect(db_path) as target:
        cursor = target.cursor()
        cursor.execute("SELECT * FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        assert len(tables) == 1

        cursor.execute("SELECT * FROM resource_type_1")
        columns = cursor.description
        assert len(columns) == 6
        test_row_values = cursor.fetchone()
        assert len(test_row_values) == 6
        assert cursor.fetchone() == None
