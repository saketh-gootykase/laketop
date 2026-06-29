from typing import Dict, Any, List, Optional
from textual import work, on
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, DataTable, TabbedContent, TabPane
from textual.containers import Container, Horizontal, Vertical
from laketop.engine import LakeTopEngine

class ConfigPanel(Static):
    """Displays table configuration details."""
    def __init__(self, engine: LakeTopEngine, **kwargs):
        super().__init__(**kwargs)
        self.engine = engine
        self.current_text = ""

    def on_mount(self) -> None:
        self.update_content()

    def update_content(self) -> None:
        try:
            config = self.engine.get_config()
            path = config["table_path"]
            partitions = ", ".join(config["partition_columns"]) or "None"
            
            # Format size nicely (KB/MB/GB)
            size_bytes = config["total_size_bytes"]
            if size_bytes >= 1024 * 1024 * 1024:
                size_str = f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
            elif size_bytes >= 1024 * 1024:
                size_str = f"{size_bytes / (1024 * 1024):.2f} MB"
            elif size_bytes >= 1024:
                size_str = f"{size_bytes / 1024:.2f} KB"
            else:
                size_str = f"{size_bytes} Bytes"
                
            files = config["total_files"]
            
            text = (
                f"[bold #00adb5]Delta Table Config[/]\n\n"
                f"[bold]Path:[/] {path}\n"
                f"[bold]Partition Columns:[/] {partitions}\n"
                f"[bold]Total Size:[/] {size_str}\n"
                f"[bold]Active Files:[/] {files}\n"
            )
        except Exception as e:
            text = f"[bold red]Error loading config:[/] {str(e)}"
            
        self.current_text = text
        self.update(text)


class HealthPanel(Static):
    """Displays file size buckets as a simulated bar chart."""
    def __init__(self, engine: LakeTopEngine, **kwargs):
        super().__init__(**kwargs)
        self.engine = engine
        self.current_text = ""

    def on_mount(self) -> None:
        self.update_content()

    def update_content(self) -> None:
        try:
            stats = self.engine.get_health_stats()
            max_val = max(stats.values()) if stats else 0
            
            # Color mapping for buckets (simulated bar chart)
            colors = {
                "Under 16MB": "#ff8a5c",      # Coral / Alert (small files problem)
                "16MB to 64MB": "#ffd95a",    # Yellow / Warning
                "64MB to 256MB": "#4e9f3d",   # Green / Healthy target range
                "Over 256MB": "#3f72af"       # Blue / Large files
            }
            
            text = f"[bold #00adb5]Storage Health (File Size Distribution)[/]\n\n"
            
            for bucket, count in stats.items():
                color = colors.get(bucket, "#eeeeee")
                if max_val > 0:
                    bar_len = int((count / max_val) * 20)
                else:
                    bar_len = 0
                
                # Minimum 1 block if count > 0 but rounded to 0
                if count > 0 and bar_len == 0:
                    bar_len = 1
                    
                bar = "█" * bar_len
                text += f"[bold]{bucket:<14}[/] | [{color}]{bar:<20}[/] ({count} files)\n"
                
            # Quick fragmentation diagnosis
            under_16_count = stats.get("Under 16MB", 0)
            total_files = sum(stats.values())
            if total_files > 0:
                frag_pct = (under_16_count / total_files) * 100
                if frag_pct > 50:
                    text += f"\n[bold #ff8a5c]⚠️ WARNING:[/] High fragmentation! {frag_pct:.1f}% of files are under 16MB."
                elif frag_pct > 20:
                    text += f"\n[bold #ffd95a]ℹ️ INFO:[/] Moderate fragmentation detected ({frag_pct:.1f}% under 16MB)."
                else:
                    text += f"\n[bold #4e9f3d]✅ HEALTHY:[/] File size distribution looks good!"
            else:
                text += "\n[bold #eeeeee]Table is empty or has no active data files.[/]"
        except Exception as e:
            text = f"[bold red]Error loading health stats:[/] {str(e)}"
            
        self.current_text = text
        self.update(text)


class HistoryPanel(DataTable):
    """Displays commit history in a DataTable."""
    def __init__(self, engine: LakeTopEngine, **kwargs):
        super().__init__(**kwargs)
        self.engine = engine

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.add_columns("Version", "Timestamp", "Operation", "Metrics")
        self.update_content()

    def update_content(self) -> None:
        self.clear()
        try:
            history = self.engine.get_history()
            for row in history:
                self.add_row(
                    str(row["version"]),
                    row["timestamp"],
                    row["operation"],
                    row["metrics"]
                )
        except Exception as e:
            self.add_row("Error", "N/A", "N/A", str(e))


class SchemaPanel(DataTable):
    """Displays table schema details in a DataTable."""
    def __init__(self, engine: LakeTopEngine, **kwargs):
        super().__init__(**kwargs)
        self.engine = engine

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.add_columns("Field Name", "Type", "Nullable", "Partition Key")
        self.update_content()

    def update_content(self) -> None:
        self.clear()
        try:
            columns = self.engine.get_schema()
            for col in columns:
                nullable_str = "[#4e9f3d]Yes[/]" if col["nullable"] else "[#ff8a5c]No[/]"
                partition_str = "[#00adb5]Yes[/]" if col["partition"] else "[#eeeeee]No[/]"
                
                self.add_row(
                    col["name"],
                    str(col["type"]),
                    nullable_str,
                    partition_str
                )
        except Exception as e:
            self.add_row("Error", str(e), "N/A", "N/A")


class LakeTopApp(App):
    """Terminal User Interface dashboard for LakeTop."""
    CSS_PATH = "styles.css"
    BINDINGS = [
        ("q", "exit", "Quit"),
        ("r", "refresh_dashboard", "Refresh"),
        ("o", "optimize_table", "Optimize/Compact")
    ]

    def __init__(self, table_path: str, storage_options: Optional[Dict[str, str]] = None, **kwargs):
        super().__init__(**kwargs)
        self.table_path = table_path
        self.storage_options = storage_options
        self.engine = LakeTopEngine(table_path, storage_options=storage_options)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        with TabbedContent(initial="dashboard-tab"):
            with TabPane("Dashboard", id="dashboard-tab"):
                with Container(id="main-container"):
                    with Horizontal(id="top-row"):
                        yield ConfigPanel(self.engine, id="config-panel")
                        yield HealthPanel(self.engine, id="health-panel")
                    
                    with Vertical(id="bottom-row"):
                        yield Static("[bold #00adb5]Time Travel Ledger (Delta History)[/]", id="ledger-title")
                        yield HistoryPanel(self.engine, id="history-table")
                        
            with TabPane("Schema", id="schema-tab"):
                with Container(id="schema-panel"):
                    yield Static("[bold #00adb5]Table Schema Details[/]", id="schema-title")
                    yield SchemaPanel(self.engine, id="schema-table")
                
        yield Footer()

    def action_refresh_dashboard(self) -> None:
        """Reloads metadata and updates all visual panels."""
        try:
            self.engine = LakeTopEngine(self.table_path, storage_options=self.storage_options)
            
            config_panel = self.query_one("#config-panel", ConfigPanel)
            health_panel = self.query_one("#health-panel", HealthPanel)
            history_table = self.query_one("#history-table", HistoryPanel)
            schema_table = self.query_one("#schema-table", SchemaPanel)
            
            config_panel.engine = self.engine
            health_panel.engine = self.engine
            history_table.engine = self.engine
            schema_table.engine = self.engine
            
            config_panel.update_content()
            health_panel.update_content()
            history_table.update_content()
            schema_table.update_content()
            self.notify("Dashboard Refreshed")
        except Exception as e:
            self.notify(f"Refresh failed: {str(e)}", severity="error")

    @work(thread=True)
    def action_optimize_table(self) -> None:
        """Runs table file compaction in a background thread."""
        self.notify("Compacting files in background...", title="Optimize Started")
        
        metrics = self.engine.optimize_compact()
        
        if "error" in metrics:
            self.notify(f"Compaction failed: {metrics['error']}", severity="error", title="Optimize Error")
        else:
            added = metrics.get("numFilesAdded", 0)
            removed = metrics.get("numFilesRemoved", 0)
            parts = metrics.get("partitionsOptimized", 0)
            
            msg = f"Compacted! Added {added} files, removed {removed} files across {parts} partitions."
            self.notify(msg, title="Optimize Complete")
            
            # Safely refresh UI from the worker thread
            self.call_from_thread(self.action_refresh_dashboard)

    @on(TabbedContent.TabActivated)
    def handle_tab_activated(self, event: TabbedContent.TabActivated) -> None:
        """Triggered when the user switches tabs, forcing a layout update."""
        active_pane_id = event.tabbed_content.active
        if active_pane_id == "schema-tab":
            schema_table = self.query_one("#schema-table", SchemaPanel)
            schema_table.update_content()
        elif active_pane_id == "dashboard-tab":
            history_table = self.query_one("#history-table", HistoryPanel)
            history_table.update_content()
