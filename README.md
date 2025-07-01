# Lexical

Lexical is an offline dictionary server that provides fast word definitions using WordNet data.

## Features
- **Offline Dictionary**: Uses local WordNet data for word lookups.
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
### As a Dictionary Server (for LSP/editor integration)
Run as a background server using stdin/stdout:
```bash
lexical --stdin
```
Request:
```
run
```
Response:
```
(noun)
1. A score in baseball made by a runner touching all four bases safely
  - "the Yankees scored 3 runs in the bottom of the 9th"
2. The act of testing something
  - "in the experimental trials the amount of carbon was measured separately"
(verb)
3. Move fast by using one's feet, with one foot off the ground at any given time
  - "Don't run--you'll be out of breath"
4. Flee
  - take to one's heels
```
