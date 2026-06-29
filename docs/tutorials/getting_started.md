# Getting Started with LakeTop

This tutorial guides you step-by-step through setting up LakeTop, generating a sample Delta table, and profiling it from your terminal.

Author: Saketh Kase

---

## Prerequisites

Before starting, ensure you have:
- Python 3.9 or higher installed.
- Pip (Python package installer) configured.

---

## Step 1: Install LakeTop

1. Clone or download the repository to your local machine.
2. Open a terminal in the project directory.
3. Run the following command to install the package and its dependencies in editable mode:
   ```bash
   pip install -e .
   ```

This will automatically fetch and install:
- `deltalake` (to parse Delta transaction logs)
- `textual` (to render the Terminal UI)
- `typer` (to handle CLI arguments and routing)
- `pyarrow` (to process Arrow tables)

---

## Step 2: Generate a Test Delta Table

If you don't have an active Delta table locally, you can create one using the provided test generator script:

```bash
# Create a test table inside a 'test_table' folder
python -c "
import pyarrow as pa
from deltalake.writer import write_deltalake
data = pa.table({'id': [1, 2, 3], 'name': ['Alice', 'Bob', 'Charlie'], 'category': ['A', 'B', 'A']})
write_deltalake('test_table', data, partition_by=['category'])
"
```

This commands writes a new Delta table partitioned by the `category` column to the `test_table` directory.

---

## Step 3: Run the CLI Scanner

Start profiling the table using the `scan` command:

```bash
laketop scan ./test_table
```

You will see the visual terminal dashboard launch:
- **Top-Left Panel**: Table configuration details, containing the path, partition columns, total size, and file counts.
- **Top-Right Panel**: Storage health size distribution chart.
- **Bottom Panel**: Time Travel Ledger showing the history and metrics for your table write.

---

## Step 4: Interact with the TUI

Inside the dashboard:
- Press **`r`** to refresh data on-demand if new writes have happened.
- Press **`q`** to safely close the terminal UI and return to your shell prompt.
