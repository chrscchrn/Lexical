# Lexical

## Current Status
- "ran" is not showing any defs

## Problem Statement
As a user I should be able to get the definition of a word by command line or lsp by 'hovering' over its name.

Command Line:
```
lexical word1 word2 word3
```
> Use command line arguements to get the definition of a word.

LSP (Running proram for speed):
```
function delegate()
        [definition of delegate here]
```
by running:
```
lexical --stdin
```
as a server using stdio.
> This uses the stdin of the command to read the input word(s) and stdout to output the definitions.

### Extensions
- Create a neovim plugin that installs and runs lexical via lua without LSP
- Create a VS Code extension that installs and runs lexical via lua without LSP

## Future Plans
- command line
    - open file -> binary search or map -> get synsets -> binary search or map -> get definitions
- restructure the wordnet data to embedded DB
    - SQLite, DuckDB, RocksDB
- Networking
    - TCP
    - websocket (async)
- sattelite adjective support
- synonyms, anyonyms, word proximity
    - request should have method string -> convert to function

## wordnet response protocol
response to one word = {
    "word": "word",
    "method": "method"
    "synset_count": 1, # number of words
    "body": {
        "n": [
            {
                "base":? base_word,
                "base_type":? "n",
                "content": [
                    {
                        "definition": "a meaning of a word",
                        "examples": ["example1", ...]
                    }
                ]
            },
        ],
        "v": [...]
    },
}

synonyms:
n: ["word1", "word2", ...],
v: ["word1", "word2", ...],
r: ["word1", "word2", ...],
a: ["word1", "word2", ...],
