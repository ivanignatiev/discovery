"""
Notes
-----
Args section is required for the function to be discovered by the smolagents library

It is better to return from tool only information related to results, smolagents add other precisions by itself.
"""

import os
import smolagents
from typing import List


@smolagents.tool
def get_latest_snapshot_path(target_path: str) -> str:
    """
    This function lists all *.db files and returns the latest snapshot file path

    Args:
        target_path: The folder path to get the latest data snapshot from.

    Parameters
    ----------
    target_path : str
        The folder path to get the latest data snapshot from

    Returns
    -------
    str
        The latest snapshot file path
    """
    files = os.listdir(target_path)
    snapshot_files = [f for f in files if f.endswith(".db")]
    latest_snapshot = max(snapshot_files, key=os.path.getctime)
    snaphot_path = os.path.join(target_path, latest_snapshot)

    return snaphot_path


@smolagents.tool
def list_tables_names(db_path: str) -> str:
    """
    This function lists all tables in the SQLite database under db_path.

    Args:
        db_path: The path to the SQLite database. Call get_latest_snapshot_path() before to get the latest snapshot file path.

    Parameters
    ----------
    db_path : str
        The path to the SQLite database. Call get_latest_snapshot_path() before to get the latest snapshot file path.

    Returns
    -------
    List[str]
        The list of table names in the SQLite database
    """
    import sqlite3

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()

    return "\n".join([table[0] for table in tables])


@smolagents.tool
def get_table_schema(db_path: str, table_name: str) -> str:
    """
    This function returns the schema (columns and types) of the table in the SQLite database.

    Args:
        db_path: The path to the SQLite database with table.
        table_name: The name of the table. Call list_tables_names() before to get the list of table names which is needed to satisfy query. Call execute_select_query() to get the data from the table.

    Parameters
    ----------
    db_path : str
        The path to the SQLite database
    table_name : str
        The name of the table. Call list_tables_names() before to get the list of table names which is needed to satisfy query.

    Returns
    -------
    str
        Description of the schema of the table
    """
    import sqlite3

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    schema = cursor.fetchall()

    response = ""

    for col in schema:
        cursor.execute(f"SELECT DISTINCT {col[1]} FROM {table_name} LIMIT 10;")
        distinct_values = cursor.fetchall()
        response += (
            (f"{col[1]} {col[2]}, values examples: ")
            + (", ".join([str(v[0]) for v in distinct_values if v[0] is not None]))
            + "\n"
        )

    conn.close()

    return response


@smolagents.tool
def execute_select_query(db_path: str, query: str) -> str:
    """
    This function executes a SQL SELECT query on the SQLite database under db_path.

    Args:
        db_path: The path to the SQLite database
        query: The SQL SELECT query (compatible with SQLite3). Call get_table_schema() to get the schema of the table which is needed to satisfy query.

    Parameters
    ----------
    db_path : str
        The path to the SQLite database
    query : str
        The SQL SELECT query. Call get_table_schema() to get the schema of the table which is needed to satisfy query.

    Returns
    -------
    List[Dict]
        The result of the SELECT query
    """
    import sqlite3

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(query)
    columns = [description[0] for description in cursor.description]
    result = cursor.fetchall()
    conn.close()

    response = []
    response.append("\t".join(columns))
    for row in result:
        response.append("\t".join(map(str, row)))

    return "\n".join(response)


def get_sqlite_agent(model: smolagents.AzureOpenAIServerModel) -> smolagents.CodeAgent:
    return smolagents.CodeAgent(
        tools=[
            get_latest_snapshot_path,
            list_tables_names,
            get_table_schema,
            execute_select_query,
        ],
        model=model,
        additional_authorized_imports=["sqlite3"],
        planning_interval=3,
    )
