import re
import sys
import unicodedata
import subprocess
import duckdb
import polars as pl

from pathlib import Path

con = duckdb.connect(database='gold.duckdb')

def _s3_sync(source, destination):
    """
    Runs the 'aws s3 sync' command using the subprocess module.

    Args:
        source (str): The source path (local directory or s3://bucket/prefix).
        destination (str): The destination path (local directory or s3://bucket/prefix).
    """
    command = [
        'aws', 's3', 'sync',
        source,
        destination
    ]

    try:
        # Run the command and capture output
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print("Sync successful:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Sync failed with error code {e.returncode}:")
        print(e.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: 'aws' command not found. Ensure AWS CLI is installed and in your PATH.")
        sys.exit(1)

def _list_subfolders(folder_path: Path):
    """
    Lists all immediate subfolders in the given folder path.

    Args:
        folder_path (Path): The path to the folder.
    """
    return [f for f in folder_path.iterdir() if f.is_dir()]

def _create_or_replace_table_from_parquet(table_name: str, parquet_path: Path):
    """
    Creates or replaces a DuckDB table from Parquet files located in the given path.

    Args:
        table_name (str): The name of the DuckDB table to create or replace.
        parquet_path (Path): The path to the Parquet files.
    """
    con.execute(f"""
        CREATE OR REPLACE TABLE {table_name} AS
        SELECT * FROM read_parquet('{parquet_path}/*.parquet')
    """)
    print(f"Table '{table_name}' created or replaced from Parquet files at '{parquet_path}'.")


def update_duck_db():
    """
    Syncs data from an S3 bucket to local Parquet files and updates DuckDB tables accordingly.

    This function performs the following steps:
        1. Syncs Parquet files from the specified S3 bucket to a local directory.
        2. Lists all subfolders in the local directory, each representing a table.
        3. For each subfolder, creates or replaces a DuckDB table using the Parquet files found within.
    
    Args:
        None

    Returns:
        None
    
    """

    s3_bucket = "s3://precos-pmc-app-db/gold_parquet/"

    local_data_path = Path('.') / 'cache' / 'gold_parquet'
    local_data_path.mkdir(parents=True, exist_ok=True)

    _s3_sync(s3_bucket, str(local_data_path))

    tables = _list_subfolders(local_data_path)
    for table_path in tables:
        table_name = table_path.name
        _create_or_replace_table_from_parquet(table_name, table_path)

    print("Data sync from S3 completed.")

def mount_query(table: str, dump: dict = None, page: int = 1, results_per_page: int = 100, columns: list[str] = None) -> list[str]:

    if table not in ['f_precos', 'd_empresas', 'd_produtos']:
        raise ValueError("Invalid table")

    sql = f"SELECT {', '.join(columns) if columns else '*'} FROM {table}"
    params = []

    if dump:
        sql += " WHERE 1=1"

        for col_name, col_value in dump.items():
            
            if col_value is None:
                continue

            if not any(col_name.startswith(p) for p in ["vl_", "cd_", "dt_", "nm_"]):
                raise ValueError("Invalid column")

            if col_name.startswith(("vl_", "cd_")):
                sql += f" AND {col_name} = ?"
                params.append(col_value)

            elif col_name.startswith("dt_"):

                if col_name.endswith("_ge"):
                    real_col_name = col_name[:-3]
                    sql += f" AND {real_col_name} >= ?"
                    params.append(col_value)

                elif col_name.endswith("_le"):
                    real_col_name = col_name[:-3]
                    sql += f" AND {real_col_name} <= ?"
                    params.append(col_value)
                
                else:
                    sql += f" AND {col_name} = ?"
                    params.append(col_value)

            elif col_name.startswith("nm_"):
                txt = unicodedata.normalize('NFKD', str(col_value))
                txt = re.sub(r'[\u0300-\u036f]', '', txt).upper().strip()

                txts = txt.split(' ')
                for t in txts:
                    sql += f" AND {col_name} LIKE ?"
                    params.append(f"%{t}%")

    sql = f"""
        WITH base_query AS ({sql})
        SELECT DISTINCT * FROM base_query LIMIT {results_per_page} OFFSET {(page - 1) * results_per_page}
    """

    return sql, params

            
def query_duck_db(query: str, params: list) -> pl.DataFrame:
    """
    Executes a SQL query against the DuckDB database and returns the results.

    Args:
        query (str): The SQL query to execute.
    Returns:
        pl.DataFrame: The results of the query as a Polars DataFrame.
    """

    #print(query, params)
    result = con.execute(query, params).fetchdf()
    return result
