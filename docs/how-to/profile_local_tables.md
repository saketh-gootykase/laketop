# How-To: Profile and Analyze Local Delta Tables

This guide covers specific tasks and workflows you can accomplish when profiling local storage layers with LakeTop.

Author: Saketh Kase

---

## How to Diagnose File Fragmentation (The Small File Problem)

Delta tables can accumulate large amounts of tiny parquet files due to frequent low-volume streaming appends. This degrades read performance.

1. Run LakeTop on your table directory:
   ```bash
   laketop scan /path/to/table
   ```
2. Inspect the **Storage Health** panel on the top-right.
3. Observe the file size buckets:
   - **Under 16MB**: Represents highly fragmented files.
   - **16MB to 64MB**: Represents moderate/small files.
   - **64MB to 256MB**: Standard targets for optimized query performance.
   - **Over 256MB**: Large files.
4. Read the diagnostic summary at the bottom of the Health panel.
   - If a warning is displayed (`⚠️ WARNING: High fragmentation!`), you should run an `OPTIMIZE` command via your data processing pipeline to compact these files.

---

## How to Check Table Transaction History (Time Travel Ledger)

To inspect historical operations and check the metrics of commits:

1. Launch LakeTop on the target table.
2. Focus on the bottom panel: **Time Travel Ledger**.
3. Use the arrow keys or mouse scroll wheel to navigate the table rows.
4. The ledger displays:
   - **Version**: Commit version number (e.g. `0`, `1`, `2`).
   - **Timestamp**: Human-readable date and time of the commit.
   - **Operation**: The action type (e.g., `WRITE`, `DELETE`, `UPDATE`, `OPTIMIZE`).
   - **Metrics**: Key statistics of the operation (e.g., `num_added_files`, `num_removed_files`, `num_added_rows`).

---

## How to Refresh the Dashboard on Live Tables

If your data pipeline is actively writing to the Delta table while you are profiling it:

1. Press **`r`** inside the LakeTop terminal screen.
2. The engine will re-scan the transaction log, retrieve the latest version, and update all three panels automatically.
3. A success notification will appear at the bottom-right of your screen confirming the refresh.
