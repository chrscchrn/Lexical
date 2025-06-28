# Lexical

Lexical is an offline dictionary server and command-line tool that provides fast word definitions using WordNet data. It can be used as a CLI tool or as a background server (suitable for integration with editors like Neovim or VS Code).

## Features
- **Offline Dictionary**: Uses local WordNet data for word lookups.
- **Command Line Tool**: Query word definitions directly from your terminal.
- **LSP/Editor Integration**: Can run as a server over stdio for editor integration (e.g., "hover" to see definitions).
- **Extensible**: Designed for future plugin and extension support (Neovim, VS Code, etc).

## Installation
### Requirements
- Python 3.13+

### Install
1. **Install Python**
   - Download and install Python 3.13 or newer from [python.org](https://www.python.org/downloads/), or use your system package manager.

2. **Clone the repository**
   ```bash
   git clone https://github.com/chrscchrn/Lexy.git
   cd Lexical
   ```

3. **Install the project with pip**
   - For development (recommended):
     ```bash
     pip install -e .
     ```
   - For regular use:
     ```bash
     pip install .
     ```

## Usage
### Command Line
Look up definitions for one or more words:
```bash
lexical word1 word2 word3
```

### As a Dictionary Server (for LSP/editor integration)
Run as a background server using stdin/stdout:
```bash
lexical --stdin
```
- This mode is designed for integration with editors or tools that can communicate over stdio (e.g., LSP clients).

## Development
- Logging is written to `log.log`.
- See `TODO.md` for roadmap, planned features, and design notes.
- To extend for Neovim or VS Code, see the "Extensions" section in `TODO.md`.

## License
This project is for educational/research use. See LICENSE for details.

---

*Lexical: Fast, offline word lookup for your terminal and editor.*
