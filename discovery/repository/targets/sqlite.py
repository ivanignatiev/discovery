import os
import sqlite3
from pathlib import Path
from typing import List, Any, Dict
from .target import Target
from ..config import SYSTEM_UNIQUE_ID_KEY
from discovery.helpers.logging import get_logger

logger = get_logger(__name__)


class Columns:
    columns_with_types_list: List[str] = []
    columns_names_list: List[tuple] = []

    def __init__(
        self, columns_with_types_list: List[str], columns_names_list: List[tuple]
    ):
        self.columns_with_types_list = columns_with_types_list
        self.columns_names_list = columns_names_list


class SQLiteTarget(Target):
    """
    Save the data snapshot to a SQLite database
    """

    path: Path = None
    conn: sqlite3.Connection = None
    cursor: sqlite3.Cursor = None

    def __init__(self, path: Path) -> None:
        if path.exists():
            logger.debug(f"SQLite database {path} exists")
            raise ValueError(
                f"SQLite database {path} exists, use a different path to avoid side effects"
            )

        self.path = path
        self.conn = sqlite3.connect(self.path)
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def _create_table(self, table_name: str, columns: List[str]) -> None:
        logger.info("Create table")

        logger.debug(f"Table name: {table_name}")

        self.cursor.execute(
            f"CREATE TABLE IF NOT EXISTS {table_name} (\n{',\n'.join(columns)}\n)"
        )

    def _normalize_column_name(self, column_name: str) -> str:
        """
        Replace any non-alphanumeric characters with underscores
        """
        column_name = column_name.lower()

        return "".join(char if char.isalnum() else "_" for char in column_name)

    def _define_columns_with_types(
        self, columns_with_types_dict: Dict, resource: Dict
    ) -> Dict:
        for key, value in resource.items():
            column_name_type = self._normalize_column_name(key)

            column = columns_with_types_dict.get(column_name_type, {})

            column["key"] = key
            column["name"] = column_name_type

            if column.get("type") is None and isinstance(value, int):
                column["type"] = "INTEGER"
            elif column.get("type") is None and isinstance(value, float):
                column["type"] = " REAL"
            elif column.get("type") is None:
                column["type"] = "TEXT"
            elif (
                column["type"] != "TEXT"
                and not isinstance(value, int)
                and not isinstance(value, float)
            ):
                column["type"] = "TEXT"

            if key == SYSTEM_UNIQUE_ID_KEY:
                column["type"] += " NOT NULL PRIMARY KEY"

            columns_with_types_dict[column_name_type] = column

        return columns_with_types_dict

    def _discover_columns_over_list(self, resources: List[Dict]) -> Columns:
        logger.info("Define columns over list of resources")

        columns_with_types_dict = {}
        columns_names_set = set()

        for resource in resources:
            columns_with_types_dict = self._define_columns_with_types(
                columns_with_types_dict, resource
            )

            columns_names_set.update(
                [tuple([self._normalize_column_name(k), k]) for k in resource.keys()]
            )

        return Columns(
            columns_with_types_list=[
                f"{v['name']} {v['type']}" for v in columns_with_types_dict.values()
            ],
            columns_names_list=list(columns_names_set),
        )

    def save(self, data: Dict[str, List[Dict]]) -> None:
        """
        Save the data to the SQLite database

        Parameters
        ----------
        data : Dict[str, List[Dict]]
            The data to save to the SQLite database
            key is the type of the resource which is transformed to a table name
            value is a list of resources which are transformed to rows
            resource is represented as a flattened dictionary where keys are columns
        """
        logger.info("Saving data to SQLite database")

        tables = data.keys()

        for table_name in tables:
            resources = data[table_name]
            if not resources:
                continue

            columns = self._discover_columns_over_list(resources)
            self._create_table(table_name, columns.columns_with_types_list)

            columns_for_insert = ", ".join(col[0] for col in columns.columns_names_list)
            placeholders = ", ".join("?" * len(columns.columns_names_list))
            values = [
                tuple(resource.get(col[1]) for col in columns.columns_names_list)
                for resource in resources
            ]

            self.cursor.executemany(
                f"INSERT INTO {table_name} ({columns_for_insert}) VALUES ({placeholders})",
                values,
            )
            self.cursor.connection.commit()

            logger.debug(f"Inserted {len(resources)} resources into {table_name}")
