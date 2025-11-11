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
import pandas as pd
import json
import re

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
    "/save": "Save conversation (txt, csv, json, excel, md)",
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
        self.last_query_data = None
        self.last_suggestions = []
        
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
        
        # Show environment info
        env_info = Table.grid(padding=(0, 2))
        env_info.add_column(style="dim cyan", justify="right")
        env_info.add_column(style="dim white")
        
        env_info.add_row("📦 Version:", "v0.1.0")
        env_info.add_row("🔧 Python:", f"{sys.version.split()[0]}")
        env_info.add_row("📁 Session:", self.session_id)
        
        if os.getenv("LANGSMITH_TRACING_V2") == "true":
            env_info.add_row("✅ LangSmith:", "Enabled")
        
        gcp_project = os.getenv("GCP_PROJECT_ID")
        if gcp_project:
            env_info.add_row("☁️  GCP Project:", gcp_project)
        
        self.console.print(Panel(
            Align.center(env_info),
            title="[dim cyan]Environment Info[/dim cyan]",
            border_style="dim cyan",
            box=box.ROUNDED,
            padding=(0, 1)
        ))
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
    
    def save_conversation(self, format_type: str = "csv"):
        try:
            if not self.history:
                self.console.print("[yellow]⚠️  No conversation to save yet[/yellow]\n")
                return
            
            df = pd.DataFrame(self.history)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if format_type == "csv":
                filename = self.session_dir / f"conversation_{timestamp}.csv"
                df.to_csv(filename, index=False)
            elif format_type == "json":
                filename = self.session_dir / f"conversation_{timestamp}.json"
                df.to_json(filename, orient="records", indent=2)
            elif format_type == "excel" or format_type == "xlsx":
                filename = self.session_dir / f"conversation_{timestamp}.xlsx"
                df.to_excel(filename, index=False, engine="openpyxl")
            elif format_type == "md" or format_type == "markdown":
                filename = self.session_dir / f"conversation_{timestamp}.md"
                with open(filename, "w") as f:
                    f.write(f"# OpsFleet Conversation - {timestamp}\n\n")
                    for idx, entry in enumerate(self.history, 1):
                        f.write(f"## Query {idx} ({entry['time']})\n\n")
                        f.write(f"**User:** {entry['query']}\n\n")
                        f.write(f"**Assistant:**\n\n{entry.get('response', 'No response')}\n\n")
                        f.write(f"*Time: {entry.get('elapsed', 0):.2f}s | Status: {'✅' if entry.get('success') else '❌'}*\n\n")
                        f.write("---\n\n")
            elif format_type == "txt":
                filename = self.session_dir / f"conversation_{timestamp}.txt"
                with open(filename, "w") as f:
                    f.write(f"OpsFleet Conversation - {timestamp}\n")
                    f.write("=" * 70 + "\n\n")
                    for idx, entry in enumerate(self.history, 1):
                        f.write(f"[{entry['time']}] Query #{idx}\n")
                        f.write(f"User: {entry['query']}\n\n")
                        f.write(f"Assistant: {entry.get('response', 'No response')}\n\n")
                        f.write(f"Time: {entry.get('elapsed', 0):.2f}s\n")
                        f.write("-" * 70 + "\n\n")
            else:
                self.console.print(f"[red]❌ Unknown format: {format_type}[/red]")
                self.console.print("[yellow]Available: txt, csv, json, excel, md[/yellow]\n")
                return
            
            stats_text = f"""[green]✅ Conversation saved successfully![/green]

[cyan]📁 File:[/cyan] {filename}
[cyan]📊 Format:[/cyan] {format_type.upper()}
[cyan]💬 Queries:[/cyan] {len(self.history)}
[cyan]📏 Size:[/cyan] {filename.stat().st_size / 1024:.2f} KB"""
            
            self.console.print(Panel(
                stats_text,
                title="💾 Save Complete",
                border_style="green",
                box=box.ROUNDED
            ))
            self.console.print()
            
        except Exception as e:
            self.console.print(f"[red]❌ Save failed: {e}[/red]\n")
            self.console.print("[yellow]💡 Tip: For Excel format, install: pip install openpyxl[/yellow]\n")
    
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
    
    def suggest_next_steps(self, query: str, response: str):
        suggestions = self._generate_suggestions(query, response)
        
        if not suggestions:
            return
        
        self.last_suggestions = suggestions
        
        suggestions_table = Table(
            title="💡 What would you like to do next?",
            box=box.ROUNDED,
            border_style="cyan",
            show_header=False,
            padding=(0, 1)
        )
        suggestions_table.add_column("Option", style="cyan bold", width=8)
        suggestions_table.add_column("Suggestion", style="white")
        
        for idx, suggestion in enumerate(suggestions, 1):
            suggestions_table.add_row(f"[{idx}]", suggestion)
        
        self.console.print(suggestions_table)
        self.console.print("[dim]💬 Type 1, 2, or 3 to select, or ask a new question[/dim]\n")
    
    def _generate_suggestions(self, query: str, response: str) -> List[str]:
        query_lower = query.lower()
        
        if "how many" in query_lower or "count" in query_lower:
            return [
                "Show me the top 10 by a specific metric",
                "Break down the data by category or region",
                "Compare with historical data or trends"
            ]
        elif "top" in query_lower or "best" in query_lower or "highest" in query_lower:
            return [
                "Show me the bottom/worst performers",
                "Analyze the trend over time",
                "Get detailed information about the top item"
            ]
        elif "recent" in query_lower or "latest" in query_lower:
            return [
                "Compare with older data",
                "Show trends over a longer period",
                "Filter by specific criteria"
            ]
        elif "average" in query_lower or "mean" in query_lower:
            return [
                "Show the distribution or breakdown",
                "Compare with median or other metrics",
                "Identify outliers or anomalies"
            ]
        elif "schema" in query_lower or "table" in query_lower:
            return [
                "Query data from this table",
                "See relationships with other tables",
                "Get sample data from the table"
            ]
        else:
            return [
                "Dive deeper into specific details",
                "Compare with other metrics or categories",
                "Save this conversation (just say 'save this as csv')"
            ]
    
    def process_query(self, query: str):
        start_time = datetime.now()
        
        self.console.print()
        
        # Show processing steps
        log_panel = Panel(
            "[dim]📋 Processing Steps:[/dim]\n"
            "[dim]  1. Loading system prompt...[/dim]\n"
            "[dim]  2. Analyzing query intent...[/dim]\n"
            "[dim]  3. Generating SQL if needed...[/dim]\n"
            "[dim]  4. Executing query...[/dim]\n"
            "[dim]  5. Formatting response...[/dim]",
            title="[cyan]🔍 Agent Workflow[/cyan]",
            border_style="dim cyan",
            padding=(0, 1)
        )
        self.console.print(log_panel)
        self.console.print()
        
        with Progress(
            SpinnerColumn(style="cyan"),
            TextColumn("[cyan]Processing your query..."),
            console=self.console
        ) as progress:
            task = progress.add_task("", total=None)
            
            try:
                # Log: Starting agent
                self.console.print("[dim]→ Invoking LangGraph agent...[/dim]")
                response = run_agent(query)
                success = True
                self.console.print("[dim]✓ Agent completed successfully[/dim]")
            except Exception as e:
                response = f"❌ Error: {str(e)}"
                success = False
                self.console.print(f"[dim red]✗ Agent error: {str(e)}[/dim red]")
            
            progress.update(task, completed=True)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        # Check if agent wants to save conversation
        cleaned_response, save_format = self.extract_save_command(response)
        
        # Log: Formatting response
        self.console.print("[dim]→ Formatting response...[/dim]\n")
        self.format_response(cleaned_response)
        
        # Show timing and token info
        info_text = f"[dim]⏱️  Completed in {elapsed:.2f}s"
        if os.getenv("LANGSMITH_TRACING_V2") == "true":
            info_text += " | 📊 Trace: LangSmith"
        info_text += "[/dim]\n"
        self.console.print(info_text)
        
        # If agent requested save, do it
        if save_format:
            self.console.print(f"\n[cyan]💾 Saving conversation as {save_format}...[/cyan]")
            self.save_conversation(save_format)
        
        if success:
            self.suggest_next_steps(query, cleaned_response)
        
        self.history.append({
            "time": start_time.strftime("%H:%M:%S"),
            "query": query,
            "response": cleaned_response,
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
        elif cmd_lower.startswith("/save"):
            parts = command.strip().split(maxsplit=1)
            format_type = parts[1] if len(parts) > 1 else "csv"
            self.save_conversation(format_type)
        elif cmd_lower == "/export":
            self.export_history()
        elif cmd_lower in ["/exit", "/quit"]:
            return False
        else:
            self.console.print(f"[red]❌ Unknown command: {command}[/red]")
            self.console.print("[yellow]Type /help for available commands[/yellow]\n")
        
        return True
    
    def extract_save_command(self, response: str) -> tuple[str, str | None]:
        """Extract save command from agent response if present.
        
        Args:
            response: Agent's response text
            
        Returns:
            Tuple of (cleaned_response, format_type or None)
        """
        if "__SAVE_CONVERSATION__" in response:
            # Extract format from marker
            parts = response.split("__SAVE_CONVERSATION__")
            if len(parts) >= 2:
                format_part = parts[1].split("__")[0]
                # Remove the marker from response
                cleaned_response = parts[0].strip()
                return cleaned_response, format_part
        
        return response, None
    
    def show_welcome_message(self):
        """Display welcome message from the agent."""
        welcome_text = """I am an expert BigQuery SQL engineer and data analyst specializing in e-commerce analytics. I can help you by:

• Analyzing the schema of the bigquery-public-data.thelook_ecommerce dataset.
• Writing and executing optimized SQL queries to extract insights from tables like users, products, orders, and order_items.
• Answering questions related to user behavior, product performance, order trends, and sales data within the e-commerce domain.

What specific e-commerce analytics question do you have in mind?"""
        
        self.console.print(Panel(
            welcome_text,
            title="[cyan]🤖 Assistant[/cyan]",
            border_style="cyan",
            padding=(1, 2)
        ))
        self.console.print()
    
    def run(self):
        self.console.clear()
        self.show_banner()
        self.show_welcome_message()
        
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
                    )
                    
                    if query is None:
                        continue
                    
                    query = query.strip()
                    
                    if not query:
                        continue
                    
                    if query in ["1", "2", "3"] and self.last_suggestions:
                        idx = int(query) - 1
                        if 0 <= idx < len(self.last_suggestions):
                            selected = self.last_suggestions[idx]
                            self.console.print(f"[cyan]Selected:[/cyan] {selected}\n")
                            if "save this" in selected.lower():
                                self.save_conversation("csv")
                            else:
                                self.console.print("[yellow]💡 Tip: Describe what you'd like to know based on this suggestion[/yellow]\n")
                            continue
                    
                    if query.startswith("/"):
                        if not self.handle_command(query):
                            break
                        continue
                    
                    save_format = self.detect_save_request(query)
                    if save_format:
                        self.save_conversation(save_format)
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
