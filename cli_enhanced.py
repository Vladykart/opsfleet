#!/usr/bin/env python3
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich import box
from rich.text import Text
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich.align import Align
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))

from agent import run_agent
from schema_analyzer import get_schema_info, get_relationships

console = Console()

COMMANDS = {
    "/help": "Show available commands",
    "/history": "View query history",
    "/schema": "Show database schema",
    "/stats": "Session statistics",
    "/export": "Export session history",
    "/clear": "Clear screen",
    "/exit": "Exit application"
}

class RichChatCLI:
    def __init__(self):
        self.console = console
        self.history = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = Path("sessions")
        self.session_dir.mkdir(exist_ok=True)
        self.session_file = self.session_dir / f"session_{self.session_id}.txt"
        self.history_file = Path(".opsfleet_history")
        self.session = PromptSession(history=FileHistory(str(self.history_file)))
        self.bindings = self._create_key_bindings()
        
    def _create_key_bindings(self):
        kb = KeyBindings()
        
        @kb.add('c-c')
        def _(event):
            event.app.exit()
            
        @kb.add('c-d')
        def _(event):
            event.app.exit()
            
        return kb
    
    def show_banner(self):
        banner = Text()
        banner.append("╔═══════════════════════════════════════════════════════════╗\n", style="bold cyan")
        banner.append("║                                                           ║\n", style="bold cyan")
        banner.append("║              ", style="bold cyan")
        banner.append("🚀 OpsFleet Agent", style="bold white")
        banner.append(" - BigQuery AI                ║\n", style="bold cyan")
        banner.append("║                                                           ║\n", style="bold cyan")
        banner.append("║              ", style="bold cyan")
        banner.append("Powered by LangGraph + Gemini 2.5", style="dim white")
        banner.append("              ║\n", style="bold cyan")
        banner.append("║                                                           ║\n", style="bold cyan")
        banner.append("╚═══════════════════════════════════════════════════════════╝", style="bold cyan")
        
        self.console.print(Align.center(banner))
        self.console.print()
        
        help_text = Table.grid(padding=(0, 2))
        help_text.add_column(style="cyan", justify="right")
        help_text.add_column(style="white")
        
        help_text.add_row("💬", "Type your question naturally")
        help_text.add_row("⌨️", "Use /help to see all commands")
        help_text.add_row("⏎", "Press Enter to send (Shift+Enter for multiline)")
        help_text.add_row("⌃C", "Press Ctrl+C to exit")
        
        self.console.print(Panel(
            Align.center(help_text),
            border_style="dim cyan",
            box=box.ROUNDED
        ))
        self.console.print()
    
    def show_commands_menu(self):
        table = Table(
            title="📋 Available Commands",
            box=box.ROUNDED,
            border_style="cyan",
            show_header=True,
            header_style="bold magenta"
        )
        table.add_column("Command", style="cyan bold", no_wrap=True)
        table.add_column("Description", style="white")
        
        for cmd, desc in COMMANDS.items():
            table.add_row(cmd, desc)
        
        self.console.print(table)
        self.console.print()
    
    def show_history_panel(self):
        if not self.history:
            self.console.print(Panel(
                "[yellow]No queries yet. Start asking questions![/yellow]",
                title="📜 History",
                border_style="yellow"
            ))
            return
        
        table = Table(
            title="📜 Query History",
            box=box.ROUNDED,
            border_style="green",
            show_header=True,
            header_style="bold green"
        )
        table.add_column("#", style="cyan", width=4, justify="right")
        table.add_column("Time", style="yellow", width=10)
        table.add_column("Query", style="white", no_wrap=False)
        table.add_column("Status", style="green", width=8, justify="center")
        
        for idx, entry in enumerate(self.history[-10:], 1):
            status = "✅" if entry.get("success") else "❌"
            query_preview = entry["query"][:60] + "..." if len(entry["query"]) > 60 else entry["query"]
            table.add_row(
                str(idx),
                entry["time"],
                query_preview,
                status
            )
        
        self.console.print(table)
        self.console.print()
    
    def show_stats_panel(self):
        total = len(self.history)
        successful = sum(1 for h in self.history if h.get("success"))
        failed = total - successful
        avg_time = sum(h.get("elapsed", 0) for h in self.history) / total if total > 0 else 0
        
        stats_grid = Table.grid(padding=(0, 2))
        stats_grid.add_column(style="cyan bold", justify="right")
        stats_grid.add_column(style="white")
        
        stats_grid.add_row("📊 Total Queries:", f"[yellow]{total}[/yellow]")
        stats_grid.add_row("✅ Successful:", f"[green]{successful}[/green]")
        stats_grid.add_row("❌ Failed:", f"[red]{failed}[/red]")
        stats_grid.add_row("⏱️  Avg Time:", f"[cyan]{avg_time:.2f}s[/cyan]")
        stats_grid.add_row("📁 Session ID:", f"[dim]{self.session_id}[/dim]")
        
        self.console.print(Panel(
            Align.center(stats_grid),
            title="📈 Session Statistics",
            border_style="blue",
            box=box.DOUBLE
        ))
        self.console.print()
    
    def show_schema_panel(self, table_name: Optional[str] = None):
        try:
            with Progress(
                SpinnerColumn(style="cyan"),
                TextColumn("[cyan]Fetching schema..."),
                console=self.console
            ) as progress:
                progress.add_task("", total=None)
                
                if table_name:
                    analysis = get_schema_info(table_name)
                    
                    col_table = Table(
                        title=f"📋 Table: {analysis['table_name']}",
                        box=box.ROUNDED,
                        border_style="green",
                        show_header=True,
                        header_style="bold green"
                    )
                    col_table.add_column("Column", style="cyan bold")
                    col_table.add_column("Type", style="yellow")
                    col_table.add_column("Description", style="white")
                    
                    for col in analysis['columns']:
                        col_table.add_row(
                            col['name'],
                            col['type'],
                            col['description'] or "—"
                        )
                    
                    stats_text = f"""[cyan]📊 Statistics:[/cyan]
  • Rows: [yellow]{analysis['row_count']:,}[/yellow]
  • Size: [yellow]{analysis['size_mb']} MB[/yellow]
  • Columns: [yellow]{analysis['column_count']}[/yellow]"""
                    
                    self.console.print(Panel(stats_text, border_style="blue", box=box.ROUNDED))
                    self.console.print(col_table)
                    
                    relationships = get_relationships()
                    if table_name in relationships:
                        rel_text = "\n".join([f"  → {rel}" for rel in relationships[table_name]])
                        self.console.print(Panel(
                            rel_text,
                            title="🔗 Relationships",
                            border_style="magenta",
                            box=box.ROUNDED
                        ))
                else:
                    summary = get_schema_info()
                    
                    summary_table = Table(
                        title=f"🗄️  Database: {summary['dataset']}",
                        box=box.ROUNDED,
                        border_style="cyan",
                        show_header=True,
                        header_style="bold cyan"
                    )
                    summary_table.add_column("Table", style="cyan bold")
                    summary_table.add_column("Rows", style="yellow", justify="right")
                    summary_table.add_column("Columns", style="green", justify="right")
                    summary_table.add_column("Size (MB)", style="magenta", justify="right")
                    
                    for table, info in summary['tables'].items():
                        summary_table.add_row(
                            table,
                            f"{info['rows']:,}",
                            str(info['columns']),
                            str(info['size_mb'])
                        )
                    
                    stats_text = f"""[cyan]📊 Total Statistics:[/cyan]
  • Tables: [yellow]{summary['table_count']}[/yellow]
  • Total Rows: [yellow]{summary['total_rows']:,}[/yellow]
  • Total Size: [yellow]{summary['total_size_mb']} MB[/yellow]"""
                    
                    self.console.print(Panel(stats_text, border_style="blue", box=box.ROUNDED))
                    self.console.print(summary_table)
                    self.console.print("\n[dim cyan]💡 Tip: Use /schema <table_name> for details[/dim cyan]")
                
                self.console.print()
                
        except Exception as e:
            self.console.print(f"[red]❌ Error: {e}[/red]\n")
    
    def export_history(self):
        try:
            with open(self.session_file, "w") as f:
                f.write(f"OpsFleet Agent Session - {self.session_id}\n")
                f.write("=" * 70 + "\n\n")
                
                for idx, entry in enumerate(self.history, 1):
                    f.write(f"Query #{idx} - {entry['time']}\n")
                    f.write(f"Q: {entry['query']}\n")
                    f.write(f"A: {entry.get('response', 'No response')}\n")
                    f.write(f"Time: {entry.get('elapsed', 0):.2f}s\n")
                    f.write("-" * 70 + "\n\n")
            
            self.console.print(Panel(
                f"[green]✅ History exported to:[/green]\n[cyan]{self.session_file}[/cyan]",
                border_style="green"
            ))
            self.console.print()
        except Exception as e:
            self.console.print(f"[red]❌ Export failed: {e}[/red]\n")
    
    def format_response(self, response: str):
        self.console.print()
        self.console.print(Panel(
            Markdown(response),
            title="[bold green]🤖 Assistant[/bold green]",
            border_style="green",
            box=box.ROUNDED,
            padding=(1, 2)
        ))
        self.console.print()
    
    def process_query(self, query: str):
        start_time = datetime.now()
        
        self.console.print()
        with Progress(
            SpinnerColumn(style="cyan"),
            TextColumn("[cyan]Processing your query..."),
            console=self.console
        ) as progress:
            task = progress.add_task("", total=None)
            
            try:
                response = run_agent(query)
                success = True
            except Exception as e:
                response = f"❌ Error: {str(e)}"
                success = False
            
            progress.update(task, completed=True)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        self.format_response(response)
        
        self.console.print(f"[dim]⏱️  Completed in {elapsed:.2f}s[/dim]\n")
        
        self.history.append({
            "time": start_time.strftime("%H:%M:%S"),
            "query": query,
            "response": response,
            "success": success,
            "elapsed": elapsed
        })
    
    def handle_command(self, command: str) -> bool:
        cmd_lower = command.lower().strip()
        
        if cmd_lower == "/help":
            self.show_commands_menu()
        elif cmd_lower == "/history":
            self.show_history_panel()
        elif cmd_lower.startswith("/schema"):
            parts = command.strip().split(maxsplit=1)
            table_name = parts[1] if len(parts) > 1 else None
            self.show_schema_panel(table_name)
        elif cmd_lower == "/clear":
            self.console.clear()
            self.show_banner()
        elif cmd_lower == "/stats":
            self.show_stats_panel()
        elif cmd_lower == "/export":
            self.export_history()
        elif cmd_lower in ["/exit", "/quit"]:
            return False
        else:
            self.console.print(f"[red]❌ Unknown command: {command}[/red]")
            self.console.print("[yellow]Type /help for available commands[/yellow]\n")
        
        return True
    
    def run(self):
        self.console.clear()
        self.show_banner()
        
        try:
            while True:
                try:
                    self.console.print("─" * 70, style="dim")
                    query = self.session.prompt(
                        [
                            ("class:prompt", "💬 "),
                            ("class:text", "You"),
                            ("class:prompt", " › "),
                        ],
                        multiline=False,
                        key_bindings=self.bindings
                    ).strip()
                    
                    if not query:
                        continue
                    
                    if query.startswith("/"):
                        if not self.handle_command(query):
                            break
                        continue
                    
                    self.process_query(query)
                    
                except KeyboardInterrupt:
                    continue
                except EOFError:
                    break
                    
        except Exception as e:
            self.console.print(f"\n[red]Error: {e}[/red]")
        finally:
            self.show_goodbye()
    
    def show_goodbye(self):
        self.console.print()
        self.console.print("─" * 70, style="cyan")
        
        goodbye_text = f"""[bold cyan]Thank you for using OpsFleet Agent! 👋[/bold cyan]

[cyan]📊 Session Summary:[/cyan]
  • Queries: [yellow]{len(self.history)}[/yellow]
  • Session ID: [dim]{self.session_id}[/dim]
  • History: [dim]{self.session_file}[/dim]

[dim]Goodbye! Come back soon! ✨[/dim]
"""
        
        self.console.print(Panel(
            goodbye_text,
            border_style="cyan",
            box=box.DOUBLE
        ))
        self.console.print()

def main():
    cli = RichChatCLI()
    cli.run()

if __name__ == "__main__":
    main()
