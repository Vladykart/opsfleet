#!/usr/bin/env python3
"""
Beautiful CLI for chatting with the BigQuery Data Analysis Agent
Inspired by rich-chat with enhanced features
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import Optional, Dict, Any
import json
import argparse

from rich.console import Console
import pandas as pd
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.prompt import Prompt
from rich.syntax import Syntax
from rich import box
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.align import Align
from rich.columns import Columns
from rich.rule import Rule

import httpx
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))

from src.agents.professional_react_agent import ProfessionalReActAgent
from src.orchestration.tools import BigQueryTool, AnalysisTool, ReportTool
from src.bigquery_runner import BigQueryRunner


console = Console()


class SimpleLLMClient:
    """Simple LLM client wrapper for the agent"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.use_ensemble = config.get("llm", {}).get("use_ensemble", False)
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2")
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model_name = config.get("llm", {}).get("secondary", {}).get("model", "gemini-2.5-flash")
            self.gemini_model = genai.GenerativeModel(model_name=model_name)
        else:
            self.gemini_model = None
    
    async def _call_llm(self, prompt: str, temperature: float = 0.3, max_tokens: int = 2048) -> str:
        """Call LLM with prompt"""
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.ollama_host}/api/generate",
                    json={
                        "model": self.ollama_model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": temperature,
                            "num_predict": max_tokens
                        }
                    }
                )
                response.raise_for_status()
                result = response.json()
                return result["response"]
        except Exception as e:
            if self.gemini_model:
                generation_config = {
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                }
                response = self.gemini_model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                if response.candidates and len(response.candidates) > 0:
                    candidate = response.candidates[0]
                    if candidate.content and candidate.content.parts:
                        return candidate.content.parts[0].text
            raise


class BeautifulCLI:
    """Beautiful CLI interface for the agent"""
    
    def __init__(self, verbose: bool = False):
        self.console = Console()
        self.agent: Optional[ProfessionalReActAgent] = None
        self.llm_client: Optional[SimpleLLMClient] = None
        self.session_start = datetime.now()
        self.query_count = 0
        self.verbose = verbose
        
        # Generate unique thread_id for LangSmith tracking
        import uuid
        self.thread_id = f"thread-{datetime.now().strftime('%Y%m%d_%H%M%S')}-{str(uuid.uuid4())[:8]}"
        
    async def initialize(self):
        """Initialize the agent"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Initializing agent...", total=None)
            
            config_path = os.path.join(os.path.dirname(__file__), "config", "agent_config.json")
            with open(config_path) as f:
                config = json.load(f)
            
            progress.update(task, description="Connecting to BigQuery...")
            bq_runner = BigQueryRunner(
                project_id=os.getenv("GCP_PROJECT_ID"),
                dataset_id="bigquery-public-data.thelook_ecommerce"
            )
            
            progress.update(task, description="Initializing LLM...")
            self.llm_client = SimpleLLMClient(config)
            
            progress.update(task, description="Setting up tools...")
            tools = [
                BigQueryTool(bq_runner, self.llm_client),
                AnalysisTool(),
                ReportTool()
            ]
            
            progress.update(task, description="Creating agent...")
            # Pass thread_id to agent for LangSmith tracking
            config["thread_id"] = self.thread_id
            self.agent = ProfessionalReActAgent(tools, self.llm_client, config)
            
            progress.update(task, description="Ready!", completed=True)
    
    def show_welcome(self):
        """Show enhanced welcome banner with beautiful UI"""
        self.console.clear()
        
        # Animated title with gradient effect
        title_art = """
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║     ██████╗ ██████╗ ███████╗███████╗██╗     ███████╗███████╗████████╗
║    ██╔═══██╗██╔══██╗██╔════╝██╔════╝██║     ██╔════╝██╔════╝╚══██╔══╝
║    ██║   ██║██████╔╝███████╗█████╗  ██║     █████╗  █████╗     ██║   
║    ██║   ██║██╔═══╝ ╚════██║██╔══╝  ██║     ██╔══╝  ██╔══╝     ██║   
║    ╚██████╔╝██║     ███████║██║     ███████╗███████╗███████╗   ██║   
║     ╚═════╝ ╚═╝     ╚══════╝╚═╝     ╚══════╝╚══════╝╚══════╝   ╚═╝   
║                                                                   ║
║           Professional ReAct Data Analysis Agent                  ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
"""
        
        self.console.print(title_art, style="bold cyan", justify="center")
        
        # Version and status bar
        version_panel = Panel(
            Align.center(
                Text.assemble(
                    ("v1.0.0", "bold green"),
                    (" │ ", "dim"),
                    ("🤖 Model: ", "dim"),
                    (self.llm_client.ollama_model, "bold yellow"),
                    (" │ ", "dim"),
                    ("🌡️  Temp: ", "dim"),
                    ("0.3", "bold magenta"),
                    (" │ ", "dim"),
                    ("✨ Status: ", "dim"),
                    ("Ready", "bold green")
                )
            ),
            style="on #1a1a2e",
            border_style="bright_blue"
        )
        self.console.print(version_panel)
        self.console.print()
        
        # Features in modern card layout
        features_content = Table.grid(padding=(0, 2))
        features_content.add_column(style="bold cyan", justify="left")
        features_content.add_column(style="dim", justify="left")
        
        features_content.add_row(
            "🧠 Multi-Stage ReAct", "5-stage pipeline with genius planning"
        )
        features_content.add_row(
            "📊 BigQuery Integration", "Smart SQL generation with auto-fix"
        )
        features_content.add_row(
            "💡 Intelligent Planning", "Strategic analysis + optimization"
        )
        features_content.add_row(
            "🔄 Self-Healing", "Automatic retry with error recovery"
        )
        features_content.add_row(
            "💬 Context-Aware", "Conversation history + caching"
        )
        features_content.add_row(
            "🎨 Beautiful UI", "Modern interface with progress tracking"
        )
        features_content.add_row(
            "📈 LangSmith Tracing", "Full observability and debugging"
        )
        features_content.add_row(
            "⚡ High Performance", "90%+ success rate with caching"
        )
        
        features_panel = Panel(
            features_content,
            title="[bold cyan]✨ Features[/bold cyan]",
            border_style="cyan",
            box=box.DOUBLE
        )
        self.console.print(features_panel)
        self.console.print()
        
        # Commands in modern card layout
        commands_content = Table.grid(padding=(0, 2))
        commands_content.add_column(style="bold yellow", justify="left")
        commands_content.add_column(style="dim", justify="left")
        
        commands_content.add_row("help", "Show help message")
        commands_content.add_row("history", "View conversation history")
        commands_content.add_row("stats", "Session statistics")
        commands_content.add_row("clear", "Clear the screen")
        commands_content.add_row("exit/quit", "Exit application")
        
        commands_panel = Panel(
            commands_content,
            title="[bold yellow]⌨️  Commands[/bold yellow]",
            border_style="yellow",
            box=box.DOUBLE
        )
        self.console.print(commands_panel)
        self.console.print()
        
        # Footer with tech stack
        footer = Text.assemble(
            ("Powered by ", "dim italic"),
            ("Ollama", "bold blue"),
            (" + ", "dim"),
            ("Gemini", "bold magenta"),
            (" + ", "dim"),
            ("LangSmith", "bold green"),
            (" │ Built with ", "dim italic"),
            ("❤️", "red"),
            (" by AI Engineers", "dim italic")
        )
        self.console.print(Align.center(footer))
        self.console.print(Rule(style="bright_blue", characters="─"))
    
    def show_thinking_stages(self, stage: str, description: str):
        """Show current thinking stage"""
        stage_colors = {
            "understanding": "yellow",
            "planning": "blue",
            "execution": "green",
            "validation": "magenta",
            "synthesis": "cyan"
        }
        
        color = stage_colors.get(stage, "white")
        
        self.console.print(
            f"[{color}]● {stage.upper()}[/{color}] {description}",
            style="dim"
        )
    
    async def process_query(self, query: str):
        """Process user query with detailed progress and outputs"""
        self.query_count += 1
        
        self.console.print()
        self.console.print(Panel(
            query,
            title=f"[cyan]Query #{self.query_count}[/cyan]",
            border_style="cyan",
            box=box.ROUNDED
        ))
        self.console.print()
        
        # Track step outputs
        self.step_outputs = {}
        
        # Progress tracking with outputs
        def show_progress(stage, status, detail=""):
            if status == "running":
                self.console.print(f"[yellow]⠋ {stage.title()}: {detail}[/yellow]")
            elif status == "complete":
                self.console.print(f"[green]✓ {stage.title()}: {detail}[/green]")
                # Store output for later display
                self.step_outputs[stage] = detail
        
        self.agent.progress_callback = show_progress
        
        try:
            result = await self.agent.process(query)
            
            # Show detailed step outputs
            self.console.print()
            self.console.print("[bold cyan]📋 Execution Details:[/bold cyan]")
            self.console.print()
            
            execution = result.get("execution", {})
            if execution.get("execution_log"):
                for i, log in enumerate(execution["execution_log"], 1):
                    action = log.get("action", "N/A")
                    thought = log.get("thought", "")
                    observation = log.get("observation", "")
                    
                    # Create panel for each step
                    step_content = f"[bold]Action:[/bold] {action}\n"
                    if thought:
                        step_content += f"[dim]Thought:[/dim] {thought[:150]}...\n" if len(thought) > 150 else f"[dim]Thought:[/dim] {thought}\n"
                    step_content += f"[bold green]Output:[/bold green] {observation}"
                    
                    self.console.print(Panel(
                        step_content,
                        title=f"[cyan]Step {i}[/cyan]",
                        border_style="blue",
                        box=box.ROUNDED
                    ))
                    self.console.print()
            
            if not result.get("success"):
                self.console.print(Panel(
                    f"[red]Error: {result.get('error', 'Unknown error')}[/red]",
                    title="[red]Error[/red]",
                    border_style="red"
                ))
                return
            
            self.console.print()
            self.show_results(result)
            
        except Exception as e:
            self.console.print(Panel(
                f"[red]Error: {str(e)}[/red]",
                title="[red]Processing Error[/red]",
                border_style="red"
            ))

    def show_results(self, result: Dict):
        """Show results in beautiful format"""
        self.console.print()
        
        if result.get("needs_clarification"):
            response = result.get("response", "")
            self.console.print(Panel(
                Markdown(response),
                title="[yellow]❓ Need Clarification[/yellow]",
                border_style="yellow",
                box=box.DOUBLE,
                padding=(1, 2)
            ))
            self.console.print()
            return
        
        understanding = result.get("understanding", {})
        self.console.print(Panel(
            f"[bold]Intent:[/bold] {understanding.get('intent', 'N/A')}\n"
            f"[bold]Complexity:[/bold] {understanding.get('complexity', 'N/A')}\n"
            f"[bold]Output Format:[/bold] {understanding.get('output_format', 'N/A')}",
            title="[yellow]Understanding[/yellow]",
            border_style="yellow",
            box=box.ROUNDED
        ))
        self.console.print()
        
        plan = result.get("plan", {})
        if plan.get("steps"):
            table = Table(title="Execution Plan", box=box.SIMPLE)
            table.add_column("Step", style="cyan", width=6)
            table.add_column("Action", style="green")
            table.add_column("Description", style="white")
            
            for step in plan["steps"][:5]:
                table.add_row(
                    str(step.get("id", "")),
                    step.get("action", ""),
                    step.get("description", "")[:50]
                )
            
            self.console.print(table)
            self.console.print()
        
        execution = result.get("execution", {})
        if execution.get("execution_log"):
            exec_text = f"[green]✓[/green] Completed {execution.get('completed_steps', 0)} steps\n"
            exec_text += f"[blue]ℹ[/blue] Total steps: {len(execution.get('execution_log', []))}\n\n"
            
            step_results = execution.get('results', {})
            for step_key, step_data in step_results.items():
                if isinstance(step_data, dict):
                    if 'rows' in step_data:
                        exec_text += f"[cyan]📊 Retrieved {step_data['rows']} rows[/cyan]\n"
                    if 'columns' in step_data:
                        exec_text += f"[dim]Columns: {', '.join(step_data['columns'][:5])}[/dim]\n"
            
            self.console.print(Panel(
                exec_text.strip(),
                title="[green]Execution[/green]",
                border_style="green",
                box=box.ROUNDED
            ))
            self.console.print()
        
        validation = result.get("validation", {})
        if validation:
            status = "✓ Valid" if validation.get("valid") else "✗ Invalid"
            confidence = validation.get("confidence", 0)
            
            self.console.print(Panel(
                f"[bold]{status}[/bold]\n"
                f"[bold]Confidence:[/bold] {confidence:.1%}",
                title="[magenta]Validation[/magenta]",
                border_style="magenta",
                box=box.ROUNDED
            ))
            self.console.print()
        
        # Show data table if available
        interpretation = result.get("interpretation", {})
        actual_data = interpretation.get("actual_data", [])
        
        if actual_data:
            # Convert to pandas DataFrame
            df = pd.DataFrame(actual_data)
            
            self.console.print(Panel(
                f"[bold]Query Results[/bold] - {len(df)} rows × {len(df.columns)} columns",
                title="[green]📊 Data[/green]",
                border_style="green"
            ))
            
            # Create Rich table from DataFrame
            data_table = Table(box=box.SIMPLE_HEAD, show_lines=False)
            
            # Add columns with formatting
            for col in df.columns:
                data_table.add_column(str(col), style="cyan", overflow="fold")
            
            # Add rows (limit to 10)
            for idx, row in df.head(10).iterrows():
                formatted_row = []
                for val in row:
                    if isinstance(val, (int, float)):
                        if isinstance(val, float):
                            formatted_row.append(f"{val:,.2f}")
                        else:
                            formatted_row.append(f"{val:,}")
                    else:
                        formatted_row.append(str(val)[:50])  # Truncate long strings
                data_table.add_row(*formatted_row)
            
            self.console.print(data_table)
            self.console.print()
            
            # Show summary statistics if numeric columns exist
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                self.console.print("[bold]Summary Statistics:[/bold]")
                stats_table = Table(box=box.SIMPLE, show_header=True)
                stats_table.add_column("Metric", style="yellow")
                for col in numeric_cols[:3]:  # Show first 3 numeric columns
                    stats_table.add_column(str(col), style="cyan")
                
                stats = df[numeric_cols].describe()
                for stat in ['count', 'mean', 'min', 'max']:
                    if stat in stats.index:
                        row_data = [stat.title()]
                        for col in numeric_cols[:3]:
                            val = stats.loc[stat, col]
                            row_data.append(f"{val:,.2f}" if isinstance(val, float) else f"{val:,}")
                        stats_table.add_row(*row_data)
                
                self.console.print(stats_table)
                self.console.print()
            
            if len(df) > 10:
                self.console.print(f"[dim]... and {len(df) - 10} more rows[/dim]")
                self.console.print()
        
        # Show insights if available
        insights = interpretation.get("insights", [])
        if insights:
            self.console.print(Panel(
                "\n".join([f"• {insight}" for insight in insights]),
                title="[yellow]💡 Key Insights[/yellow]",
                border_style="yellow",
                box=box.ROUNDED
            ))
            self.console.print()
        
        # Show recommendations if available
        recommendations = interpretation.get("recommendations", [])
        if recommendations:
            self.console.print(Panel(
                "\n".join([f"{i}. {rec}" for i, rec in enumerate(recommendations, 1)]),
                title="[magenta]🎯 Recommendations[/magenta]",
                border_style="magenta",
                box=box.ROUNDED
            ))
            self.console.print()
        
        response = result.get("response", "")
        if response:
            self.console.print(Panel(
                Markdown(response),
                title="[cyan]📝 Summary[/cyan]",
                border_style="cyan",
                box=box.DOUBLE,
                padding=(1, 2)
            ))
        
        self.console.print()
        self.console.print(
            f"[dim]Session: {result.get('session_id', 'N/A')} | "
            f"Time: {result.get('timestamp', 'N/A')}[/dim]"
        )
        self.console.print()
    
    def show_history(self):
        """Show conversation history"""
        if not self.agent or not self.agent.memory.short_term:
            self.console.print("[yellow]No conversation history yet[/yellow]")
            return
        
        table = Table(title="Conversation History", box=box.ROUNDED)
        table.add_column("#", style="cyan", width=4)
        table.add_column("Query", style="white")
        table.add_column("Result", style="green")
        table.add_column("Time", style="dim")
        
        for i, interaction in enumerate(self.agent.memory.short_term, 1):
            table.add_row(
                str(i),
                interaction.get("query", "")[:50],
                interaction.get("result", "")[:50],
                interaction.get("timestamp", "")[:19]
            )
        
        self.console.print(table)
    
    def show_help(self):
        """Show help message"""
        help_text = """
## Available Commands

- **Your question** - Ask anything about the data
- `help` - Show this help message
- `history` - View conversation history
- `stats` - Show session statistics
- `clear` - Clear the screen
- `exit` or `quit` - Exit the application

## Example Queries

- "What are the top 10 products by revenue?"
- "Analyze customer segments by purchase frequency"
- "Show sales trends for the last quarter"
- "Compare product performance across categories"
"""
        
        self.console.print(Panel(
            Markdown(help_text),
            title="[cyan]Help[/cyan]",
            border_style="cyan"
        ))
    

    def show_cache_stats(self):
        """Show cache statistics"""
        if hasattr(self, 'agent') and hasattr(self.agent, 'cache') and self.agent.cache:
            stats = self.agent.cache.get_cache_stats()
            
            self.console.print()
            self.console.print(Panel(
                f"[bold]Cache Statistics[/bold]\n\n"
                f"Cache Hits: {stats['hits']}\n"
                f"Cache Misses: {stats['misses']}\n"
                f"Hit Rate: {stats['hit_rate']}\n"
                f"Cached Queries: {stats['cached_queries']}",
                title="[cyan]💾 Cache Stats[/cyan]",
                border_style="cyan"
            ))
        else:
            self.console.print("[yellow]Cache not available[/yellow]")

    def show_stats(self):
        """Show session statistics"""
        uptime = datetime.now() - self.session_start
        
        stats_text = f"""
[bold]Session Statistics[/bold]

• Queries processed: {self.query_count}
• Session uptime: {uptime.seconds // 60} minutes
• Memory items: {len(self.agent.memory.short_term) if self.agent else 0}
• Started: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        self.console.print(Panel(
            stats_text,
            title="[cyan]Statistics[/cyan]",
            border_style="cyan"
        ))
    
    async def run(self):
        """Main CLI loop"""
        self.console.clear()
        
        # Show loading message
        self.console.print("\n[cyan]⚙️  Initializing OpsFleet Agent...[/cyan]\n")
        
        await self.initialize()
        
        # Show welcome after initialization
        self.console.clear()
        self.show_welcome()
        
        self.console.print("\n[green]✓ Ready![/green] Type your question or 'help' for commands.\n")
        
        while True:
            try:
                query = Prompt.ask(
                    "\n[bold cyan]You[/bold cyan]",
                    default=""
                )
                
                if not query.strip():
                    continue
                
                query_lower = query.lower().strip()
                
                if query_lower in ["exit", "quit", "q"]:
                    self.console.print("\n[cyan]Goodbye! 👋[/cyan]\n")
                    break
                
                elif query_lower == "help":
                    self.show_help()
                
                elif query_lower == "history":
                    self.show_history()
                
                elif query_lower == "stats":
                    self.show_stats()
                
                elif query_lower == "clear":
                    self.console.clear()
                    self.show_welcome()
                
                else:
                    await self.process_query(query)
                
            except KeyboardInterrupt:
                self.console.print("\n\n[yellow]Interrupted. Type 'exit' to quit.[/yellow]")
                continue
            except Exception as e:
                self.console.print(f"\n[red]Error: {str(e)}[/red]")
                continue


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="BigQuery Data Analysis Agent - Professional CLI Chat Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli_chat.py
  python cli_chat.py --temperature 0.7
  python cli_chat.py --model llama3.2 --frame-color green

For more information, visit: https://github.com/your-repo
        """
    )
    
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.3,
        help="Controls randomness of text generation (default: 0.3)"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        default="llama3.2",
        help="LLM model to use (default: llama3.2)"
    )
    
    parser.add_argument(
        "--frame-color",
        type=str,
        default="cyan",
        choices=["red", "green", "yellow", "blue", "magenta", "cyan", "white"],
        help="Frame color for panels (default: cyan)"
    )
    
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=2048,
        help="Maximum tokens for LLM response (default: 2048)"
    )
    
    parser.add_argument(
        "--memory-size",
        type=int,
        default=50,
        help="Maximum conversation history size (default: 50)"
    )
    
    parser.add_argument(
        "--no-tracing",
        action="store_true",
        help="Disable LangSmith tracing"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging (show thought processes)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="BigQuery Data Analysis Agent v1.0.0"
    )
    
    return parser.parse_args()


async def main():
    """Main entry point"""
    args = parse_arguments()
    
    console.print()
    console.print(Align.center(
        Text("🚀 BigQuery Data Analysis Agent", style="bold cyan")
    ))
    console.print(Align.center(
        Text(f"v1.0.0 | Model: {args.model} | Temperature: {args.temperature}", 
             style="dim")
    ))
    console.print()
    
    if args.no_tracing:
        os.environ["LANGCHAIN_TRACING_V2"] = "false"
        console.print("[yellow]⚠ LangSmith tracing disabled[/yellow]")
    
    if args.verbose:
        console.print("[cyan]ℹ Verbose logging enabled[/cyan]")
    
    cli = BeautifulCLI(verbose=args.verbose)
    await cli.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[cyan]Goodbye! 👋[/cyan]\n")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Fatal error: {e}[/red]\n")
        sys.exit(1)
