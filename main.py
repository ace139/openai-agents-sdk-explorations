import asyncio # Added
import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Agent imports
from agents import Runner # Added
from src.ai_agents.identity_verifier import identity_verification_agent # Added

app = typer.Typer()
console = Console()

# Configuration
# DEFAULT_WELCOME_MESSAGE is less relevant as agent dictates initial interaction
EXIT_COMMANDS = {"quit", "exit"}


def display_message(sender: str, message: str):
    """Display an agent's message with proper formatting, colors, and emoji."""
    if sender.lower() == "agent":
        prefix = Text("🤖 Agent: ", style="bold green")
    else: # Should not happen if we always use "Agent"
        prefix = Text(f"{sender}: ", style="bold blue")
    text = Text()
    text.append(prefix)
    text.append(str(message) if message is not None else "No response.") # Ensure message is a string
    console.print(text)


async def chat_loop(): # Changed to async
    """Main asynchronous chat loop."""
    console.print(Panel.fit("Welcome to the Health & Wellness AI assistant!", style="bold magenta"))
    
    # Start with a hardcoded message to prompt for user ID
    display_message("Agent", "Hello! Please provide your user ID to start verification.")
    # No initial agent call needed here, we directly prompt the user.
    # The agent will respond once the user provides their first input (their ID).

    while True:
        try:
            user_prompt = Text("\n👤 You: ", style="bold blue")
            console.print(user_prompt, end="")
            user_input = await asyncio.to_thread(input) # Use asyncio.to_thread for input() in async
            
            if user_input.lower() in EXIT_COMMANDS:
                console.print("\nGoodbye! 👋", style="yellow")
                return
            
            if not user_input.strip(): # Handle empty input from user
                display_message("Agent", "Please provide some input.")
                continue

            # Get agent's response
            result = await Runner.run(identity_verification_agent, user_input)
            display_message("Agent", result.final_output)
            
        except KeyboardInterrupt:
            console.print("\n\nExiting chat... Goodbye! 👋", style="yellow")
            return
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")
            console.print("[yellow]Please ensure your OPENAI_API_KEY is set correctly and you have an internet connection.[/yellow]")
            # continue # Decide if you want to continue or exit on other errors


# Async function containing the core logic previously in 'start'
async def _execute_chat_logic():
    """Core asynchronous logic for starting the chat application."""
    await chat_loop()

@app.command()
def start(): # Typer command is now synchronous
    """Start the chat application."""
    try:
        asyncio.run(_execute_chat_logic()) # Explicitly run the async logic
    except RuntimeError as e:
        if "cannot be called from a running event loop" in str(e):
            console.print("[red]Error: Could not start the application due to an existing event loop.[/red]")
            console.print("[yellow]This can happen if the CLI tool is run from an environment that already manages an asyncio loop (e.g., a Jupyter notebook or another async application).[/yellow]")
        else:
            # Re-raise other RuntimeErrors if they are not the specific event loop error
            console.print(f"[red]An unexpected runtime error occurred: {e}[/red]")
    except Exception as e:
        console.print(f"[red]An unexpected error occurred during startup: {e}[/red]")


if __name__ == "__main__":
    app()
