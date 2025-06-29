# Lexical
    
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
- restructure the wordnet data to embedded DB
    - SQLite, DuckDB, RocksDB
- floating window for multiple definitions
    - telescope.nvim
- Networking
    - TCP
    - websocket
- Verbosity (too many definitions and examples)

## words
### working
- nouns are working
- adverbs are working

### not working
- verbs are not working
- adjectives are not working
