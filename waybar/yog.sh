#!/bin/bash
# yog: what is next, from https://yog.felipeafonso.com.
# The server computes the text, tooltip and class; this only fetches them.
# Token: ~/.config/yog/token (one line, YOG_WAYBAR_TOKEN). Not in this repo.
url="${YOG_URL:-https://yog.felipeafonso.com}/api/waybar"
token_file="${XDG_CONFIG_HOME:-$HOME/.config}/yog/token"
cache="${XDG_RUNTIME_DIR:-/tmp}/yog-waybar.json"

if [ ! -r "$token_file" ]; then
  echo '{"text":"yog: sem token","tooltip":"Crie ~/.config/yog/token com o YOG_WAYBAR_TOKEN.","class":["offline"]}'
  exit 0
fi

if out=$(curl -fsS --max-time 8 -H "Authorization: Bearer $(tr -d '[:space:]' < "$token_file")" "$url") &&
  [ "${out:0:1}" = "{" ]; then
  printf '%s' "$out" > "$cache"
  printf '%s\n' "$out"
elif [ -r "$cache" ]; then
  # Network or server down: keep showing the last answer, marked offline.
  sed -e 's/"class":\[/"class":["offline",/' -e 's/"text":"/"text":"⌁ /' "$cache"
  echo
else
  echo '{"text":"yog: sem conexão","tooltip":"Não consegui falar com o yog.","class":["offline"]}'
fi
