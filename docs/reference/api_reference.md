# API and CLI Reference

This reference document provides technical details on the LakeTop command-line interface and package API.

Author: Saketh Kase

---

## Command Line Interface (CLI)

The CLI is built using `typer`.

### `laketop scan`

Profiles a local Delta table and launches the terminal user interface dashboard.

**Usage:**
```bash
laketop scan [OPTIONS] TABLE_PATH
```

#### Arguments
- **`TABLE_PATH`** (Required, Text): Local directory path to the Delta table. Must exist and contain the `_delta_log` directory.

#### Options
- **`--help`**: Shows command details and exits.

---

## Python Developer API

For developers extending LakeTop or integrating the metadata parser, the core parsing logic is isolated in the `LakeTopEngine` class.

### `LakeTopEngine` Class

Located in `laketop.engine`. Handles reading the Delta transaction logs without any UI coupling.

#### `__init__(self, table_path: str)`
Initializes the engine for a given directory path.
- **Parameters**: `table_path` (str) - Absolute or relative path to the Delta table root directory.
- **Raises**: `deltalake.exceptions.TableNotFoundError` if the directory does not contain a valid Delta table log structure.

#### `get_config(self) -> Dict[str, Any]`
Retrieves basic table configuration properties.
- **Returns**: A dictionary containing:
  - `table_path` (str): Full path to the directory.
  - `partition_columns` (List[str]): List of partition column names.
  - `total_size_bytes` (int): Total size in bytes of active data files.
  - `total_files` (int): Total number of active data files.

#### `get_health_stats(self) -> Dict[str, int]`
Categorizes active files into size ranges.
- **Returns**: A dictionary mapping size range names to the count of matching active files:
  - `"Under 16MB"`
  - `"16MB to 64MB"`
  - `"64MB to 256MB"`
  - `"Over 256MB"`

#### `get_history(self) -> List[Dict[str, Any]]`
Fetches transaction log operation records.
- **Returns**: A list of up to 10 dictionaries, sorted reverse-chronologically (latest first), containing:
  - `version` (int): Commit version number.
  - `timestamp` (str): Human-readable formatted local time of the commit.
  - `operation` (str): Operation type.
  - `metrics` (str): Raw or formatted operation metrics.
