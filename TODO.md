# TODO:
    
## Problem Statement
As a user I should be able to get the definition of a word by command line or lsp by 'hovering' over its name.

Command Line:
```
define word1 word2 word3
```
> This uses the arguements of the command to get the definitions.

LSP (Running proram for speed):
```
function delegate()
        [definition of delegate here]
```
by running:
```
define --stdin
```
as a LSP server.
> This uses the stdin of the command to read the input word(s) and stdout to output the definitions.

## System Design
- how should I load data and store it in memory? Should I store it completely in memory?
    - index.sense
    - data.pos
    - index.pos


