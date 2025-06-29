# Lexical (in progress)

Lexical is an offline dictionary server and command-line tool that provides fast word definitions using WordNet data. It can be used as a CLI tool or as a background server.

## Features
- **Offline Dictionary**: Uses local WordNet data for word lookups.
- **Command Line Tool**: Query word definitions directly from your terminal.
- **LSP/Editor Integration**: Can run as a server over stdio for editor integration

## Installation
### Requirements
- Python 3.13+

### Install

**Install the project with pip**
   - For development:
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

