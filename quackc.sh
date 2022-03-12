#!/bin/zsh

python3 new_translator.py $1 > ./tests/src/Main.asm
python3 assemble.py ./tests/src/Main.asm ./tests/OBJ/Main.json
