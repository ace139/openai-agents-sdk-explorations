# CLI Chat Application

A simple and interactive command-line chat application built with Python, Typer, and Rich. This application demonstrates a basic chat interface with color-coded messages and emoji support.

## Features

- 🎨 Color-coded messages for better readability
- 🤖 Agent responses in bold green
- 👤 User input prompts in bold blue
- 🚪 Graceful exit with "quit" or "exit" commands
- 🛡️ Error handling for unexpected inputs
- 🎭 Beautiful terminal formatting with Rich

## Prerequisites

- Python 3.7 or higher
- [uv](https://github.com/astral-sh/uv) (Python package installer and resolver)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd openai-agents-sdk-explorations
   ```

2. Install the required dependencies using UV:
   ```bash
   uv pip install -r requirements.txt
   ```

   Or if you prefer to use UV's native dependency resolution:
   ```bash
   uv pip sync
   ```

## Usage

Start the chat application by running:

```bash
python main.py start
```

### Commands

- Type your message and press Enter to chat with the agent
- Type `quit` or `exit` to end the chat session
- Use `Ctrl+C` to exit at any time

## Project Structure

```
.
├── .gitignore          # Git ignore file
├── README.md           # This file
├── main.py             # Main application code
└── requirements.txt    # Project dependencies
```

## Dependencies

- [Typer](https://typer.tiangolo.com/): For building the CLI interface
- [Rich](https://github.com/Textualize/rich): For rich text and beautiful formatting in the terminal

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).

---

Happy chatting! 👋
