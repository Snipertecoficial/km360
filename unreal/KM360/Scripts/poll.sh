#!/bin/zsh
# espera o render do MRQ terminar (consulta o editor a cada N s). uso: poll.sh [intervalo] [max_iter]
cd "/Users/douglasnogueira/Desktop/KM 360/unreal/KM360/Scripts"
for i in $(seq 1 ${2:-60}); do
  sleep ${1:-10}
  S=$(python3 -I mcp.py py 'print(K.render_status())' 2>&1 | grep -v '^$' | tail -1)
  case "$S" in *state=done*|done*) echo "$S"; exit 0;; esac
done
echo "timeout: $S"
