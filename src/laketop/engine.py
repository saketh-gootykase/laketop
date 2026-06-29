from typing import Dict, Any, List
from deltalake import DeltaTable
from datetime import datetime

class LakeTopEngine:
    """Core logic to interact with local Delta Lake tables using delta-rs."""
    def __init__(self, table_path: str):
        self.table_path = table_path
        self.dt = DeltaTable(table_path)

    def get_config(self) -> Dict[str, Any]:
        """
        Retrieves table configuration details.
        
        Returns:
            Dict[str, Any] with table_path, partition_columns, total_size_bytes, and total_files.
        """
        metadata = self.dt.metadata()
        partition_cols = metadata.partition_columns
        
        try:
            import pyarrow as pa
            arrow_table = pa.table(self.dt.get_add_actions(flatten=True))
            add_actions = arrow_table.to_pydict()
            sizes = add_actions.get("size_bytes", [])
            total_size = sum(sizes)
            total_files = len(sizes)
        except Exception:
            # Fallback if get_add_actions fails (e.g. empty table with no log files yet)
            total_size = 0
            total_files = 0
            
        return {
            "table_path": self.table_path,
            "partition_columns": partition_cols,
            "total_size_bytes": total_size,
            "total_files": total_files,
        }

    def get_health_stats(self) -> Dict[str, int]:
        """
        Analyzes active files in the table and buckets them by size to detect fragmentation.
        
        Returns:
            Dict[str, int] representing counts in different file size ranges.
        """
        buckets = {
            "Under 16MB": 0,
            "16MB to 64MB": 0,
            "64MB to 256MB": 0,
            "Over 256MB": 0
        }
        
        try:
            import pyarrow as pa
            arrow_table = pa.table(self.dt.get_add_actions(flatten=True))
            add_actions = arrow_table.to_pydict()
            sizes = add_actions.get("size_bytes", [])
        except Exception:
            sizes = []
            
        mb = 1024 * 1024
        for size in sizes:
            if size < 16 * mb:
                buckets["Under 16MB"] += 1
            elif size < 64 * mb:
                buckets["16MB to 64MB"] += 1
            elif size < 256 * mb:
                buckets["64MB to 256MB"] += 1
            else:
                buckets["Over 256MB"] += 1
                
        return buckets

    def get_history(self) -> List[Dict[str, Any]]:
        """
        Retrieves the last 10 operations from the Delta transaction log.
        
        Returns:
            List[Dict[str, Any]] containing version, timestamp, operation, and metrics.
        """
        try:
            history_list = self.dt.history(limit=10)
        except Exception:
            return []
            
        result = []
        for commit in history_list:
            # Format timestamp
            ts_epoch = commit.get("timestamp")
            ts_str = "N/A"
            if ts_epoch is not None:
                try:
                    # Epoch timestamp is in milliseconds
                    ts_str = datetime.fromtimestamp(ts_epoch / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    pass
            
            # Format metrics
            metrics = commit.get("operationMetrics")
            metrics_str = ""
            if metrics:
                # Format metrics as a compact string, e.g. "numOutputRows: 50, numAddedFiles: 1"
                metrics_str = ", ".join(f"{k}: {v}" for k, v in metrics.items())
            else:
                metrics_str = "N/A"
                
            result.append({
                "version": commit.get("version", -1),
                "timestamp": ts_str,
                "operation": commit.get("operation", "N/A"),
                "metrics": metrics_str
            })
            
        return result
