#!/usr/bin/env python3
"""
Enhanced CLI for the Simple LangGraph Agent
Beautiful, modern, and feature-rich interface
"""
import sys
import os
from datetime import datetime
from typing import Optional
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.prompt import Prompt
from rich.syntax import Syntax
from rich import box
from rich.text import Text
from rich.rule import Rule
from rich.layout import Layout
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.columns import Columns
from rich.align import Align
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))

from agent import run_agent

console = Console()


class EnhancedCLI:
    """Enhanced CLI with beautiful UI and extended features"""
    
    def __init__(self):
        self.console = console
        self.history = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = Path("sessions")
        self.session_dir.mkdir(exist_ok=True)
        self.session_file = self.session_dir / f"session_{self.session_id}.txt"
        
    def show_welcome(self):
        """Display welcome screen"""
        welcome_text = """
# 🚀 OpsFleet Agent - Enhanced CLI

**Powered by LangGraph + Gemini 2.5 Flash**

### Features:
- 💬 Natural language queries
- 📊 BigQuery data analysis
- 🔍 Multi-stage processing
- 🔄 Error recovery
- 📝 Session history
- 🎨 Beautiful formatting

### Quick Start:
- Type your question naturally
- Use `/help` for commands
- Use `/history` to see past queries
- Use `/clear` to clear screen
- Use `/exit` or Ctrl+C to quit

### Examples:
```
How many users are in the database?
What are the top 5 products by price?
Show me sales trends by category
```
"""
        self.console.print(Panel(
            Markdown(welcome_text),
            title="[bold cyan]Welcome[/bold cyan]",
            border_style="cyan",
            box=box.DOUBLE
        ))
        self.console.print()
        
    def show_help(self):
        """Display help information"""
        help_table = Table(
            title="Available Commands",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold magenta"
        )
        help_table.add_column("Command", style="cyan", no_wrap=True)
        help_table.add_column("Description", style="white")
        
        commands = [
            ("/help", "Show this help message"),
            ("/history", "Show query history"),
            ("/clear", "Clear the screen"),
            ("/stats", "Show session statistics"),
            ("/export", "Export session history"),
            ("/exit", "Exit the application"),
        ]
        
        for cmd, desc in commands:
            help_table.add_row(cmd, desc)
            
        self.console.print(help_table)
        self.console.print()
        
    def show_history(self):
        """Display query history"""
        if not self.history:
            self.console.print("[yellow]No history yet[/yellow]\n")
            return
            
        history_table = Table(
            title="Query History",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold green"
        )
        history_table.add_column("#", style="cyan", width=4)
        history_table.add_column("Time", style="yellow", width=10)
        history_table.add_column("Query", style="white")
        history_table.add_column("Status", style="green", width=10)
        
        for idx, entry in enumerate(self.history, 1):
            history_table.add_row(
                str(idx),
                entry["time"],
                entry["query"][:60] + "..." if len(entry["query"]) > 60 else entry["query"],
                "✅" if entry.get("success") else "❌"
            )
            
        self.console.print(history_table)
        self.console.print()
        
    def show_stats(self):
        """Display session statistics"""
        total_queries = len(self.history)
        successful = sum(1 for h in self.history if h.get("success"))
        failed = total_queries - successful
        
        stats_panel = Panel(
            f"""[bold cyan]Session Statistics[/bold cyan]

📊 Total Queries: [yellow]{total_queries}[/yellow]
✅ Successful: [green]{successful}[/green]
❌ Failed: [red]{failed}[/red]
📁 Session ID: [cyan]{self.session_id}[/cyan]
💾 History File: [cyan]{self.session_file}[/cyan]
""",
            border_style="blue",
            box=box.ROUNDED
        )
        self.console.print(stats_panel)
        self.console.print()
        
    def export_history(self):
        """Export session history to file"""
        try:
            with open(self.session_file, "w") as f:
                f.write(f"OpsFleet Agent Session - {self.session_id}\n")
                f.write("=" * 60 + "\n\n")
                
                for idx, entry in enumerate(self.history, 1):
                    f.write(f"Query #{idx} - {entry['time']}\n")
                    f.write(f"Q: {entry['query']}\n")
                    f.write(f"A: {entry.get('response', 'No response')}\n")
                    f.write("-" * 60 + "\n\n")
                    
            self.console.print(f"[green]✅ History exported to {self.session_file}[/green]\n")
        except Exception as e:
            self.console.print(f"[red]❌ Export failed: {e}[/red]\n")
            
    def format_response(self, response: str) -> None:
        """Format and display agent response"""
        # Check if response contains markdown-like content
        if "```" in response or "#" in response or "*" in response:
            self.console.print(Panel(
                Markdown(response),
                title="[bold green]Response[/bold green]",
                border_style="green",
                box=box.ROUNDED
            ))
        else:
            self.console.print(Panel(
                response,
                title="[bold green]Response[/bold green]",
                border_style="green",
                box=box.ROUNDED
            ))
        self.console.print()
        
    def process_query(self, query: str) -> None:
        """Process user query with loading animation"""
        start_time = datetime.now()
        
        # Show processing animation
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task(
                "[cyan]Processing your query...",
                total=None
            )
            
            try:
                # Run the agent
                response = run_agent(query)
                success = True
                
            except Exception as e:
                response = f"❌ Error: {str(e)}"
                success = False
                
            progress.update(task, completed=True)
            
        # Calculate elapsed time
        elapsed = (datetime.now() - start_time).total_seconds()
        
        # Display response
        self.format_response(response)
        
        # Show timing
        self.console.print(f"[dim]⏱️  Completed in {elapsed:.2f}s[/dim]\n")
        
        # Save to history
        self.history.append({
            "time": start_time.strftime("%H:%M:%S"),
            "query": query,
            "response": response,
            "success": success,
            "elapsed": elapsed
        })
        
    def handle_command(self, command: str) -> bool:
        """Handle special commands. Returns True if should continue, False if should exit"""
        command = command.lower().strip()
        
        if command == "/help":
            self.show_help()
        elif command == "/history":
            self.show_history()
        elif command == "/clear":
            self.console.clear()
            self.show_welcome()
        elif command == "/stats":
            self.show_stats()
        elif command == "/export":
            self.export_history()
        elif command in ["/exit", "/quit"]:
            return False
        else:
            self.console.print(f"[red]Unknown command: {command}[/red]")
            self.console.print("[yellow]Type /help for available commands[/yellow]\n")
            
        return True
        
    def run(self):
        """Main CLI loop"""
        self.console.clear()
        self.show_welcome()
        
        try:
            while True:
                # Get user input
                self.console.print(Rule(style="dim"))
                query = Prompt.ask(
                    "[bold cyan]You[/bold cyan]",
                    console=self.console
                ).strip()
                
                if not query:
                    continue
                    
                # Handle commands
                if query.startswith("/"):
                    if not self.handle_command(query):
                        break
                    continue
                    
                # Process query
                self.console.print()
                self.process_query(query)
                
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Interrupted by user[/yellow]")
        except Exception as e:
            self.console.print(f"\n[red]Error: {e}[/red]")
        finally:
            self.show_goodbye()
            
    def show_goodbye(self):
        """Display goodbye message"""
        self.console.print()
        self.console.print(Rule(style="cyan"))
        
        goodbye_panel = Panel(
            f"""[bold cyan]Thank you for using OpsFleet Agent![/bold cyan]

📊 Session Summary:
- Queries: [yellow]{len(self.history)}[/yellow]
- Session ID: [cyan]{self.session_id}[/cyan]
- History saved to: [cyan]{self.session_file}[/cyan]

[dim]Goodbye! 👋[/dim]
""",
            border_style="cyan",
            box=box.DOUBLE
        )
        self.console.print(goodbye_panel)
        self.console.print()


def main():
    """Main entry point"""
    cli = EnhancedCLI()
    cli.run()


if __name__ == "__main__":
    main()
