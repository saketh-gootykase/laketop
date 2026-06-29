# LakeTop

LakeTop is a lightweight, responsive command-line interface (CLI) utility for profiling local Delta Lake tables natively from the terminal. It bypasses the PySpark JVM by utilizing the Rust-powered `deltalake` (delta-rs) library to read `_delta_log` transaction metadata directly, offering a fast and dependency-free visual profiling experience.

Author: Saketh Kase

---

## Key Features

- **JVM-free Delta Reading**: Direct parsing of Delta Lake transaction logs without installing PySpark or Java.
- **Storage Health & Fragmentation Analysis**: Visual detection of the "small-file problem" by bucketing active parquet file sizes.
- **Time Travel Ledger**: Tabular display of the last 10 operations, timestamps, operations, and associated metrics.
- **Interactive Terminal UI**: A high-density dashboard built using Textual.

---

## Quick Start

### Installation

Install the package in editable mode from the repository root:

```bash
pip install -e .
```

### Usage

To scan a local Delta table directory:

```bash
laketop scan /path/to/delta/table
```

Or run via Python:

```bash
python -m laketop scan /path/to/delta/table
```

---

## Documentation

Our documentation is structured using the **Diátaxis** framework:

*   **[Tutorials](docs/tutorials/getting_started.md)**: A step-by-step guide to get LakeTop running locally and profiling your first table.
*   **[How-To Guides](docs/how-to/profile_local_tables.md)**: Task-focused guides for diagnosing fragmentation and refreshing the TUI.
*   **[Explanation](docs/explanation/architecture.md)**: High-level architectural discussion on why LakeTop runs without Spark and how its layouts are constructed.
*   **[Reference](docs/reference/api_reference.md)**: Command-line arguments, options, and developer API references for the parsing engine.
