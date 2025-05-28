import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

app = typer.Typer()
console = Console()

# Configuration
DEFAULT_WELCOME_MESSAGE = "Hello! I'm your AI assistant. How can I help you today?"
EXIT_COMMANDS = {"quit", "exit"}


def display_message(sender: str, message: str):
    """Display an agent's message with proper formatting, colors, and emoji."""
    prefix = Text("🤖 Agent: ", style="bold green")
    text = Text()
    text.append(prefix)
    text.append(message)
    console.print(text)


def chat_loop(welcome_message: str = DEFAULT_WELCOME_MESSAGE):
    """Main chat loop."""
    console.print(Panel.fit("Welcome to the Chat CLI!", style="bold magenta"))
    display_message("Agent", welcome_message)
    
    while True:
        try:
            # Get user input with emoji and blue color
            user_prompt = Text("\n👤 You: ", style="bold blue")
            console.print(user_prompt, end="")
            user_input = input()
            
            # Check for exit commands
            if user_input.lower() in EXIT_COMMANDS:
                console.print("\nGoodbye! 👋", style="yellow")
                return
                
            # Show the user's message and get agent's response
            display_message("Agent", f"You said: {user_input}")
            
        except KeyboardInterrupt:
            console.print("\n\nExiting chat... Goodbye! 👋", style="yellow")
            return
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")
            continue


@app.command()
def start():
    """Start the chat application."""
    chat_loop(DEFAULT_WELCOME_MESSAGE)


if __name__ == "__main__":
    app()
