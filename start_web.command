#!/bin/bash
cd "$(dirname "$0")" || exit 1
python3 -m http.server 8000 --bind 127.0.0.1 &
server_pid=$!
sleep 1
open http://localhost:8000/web/
wait "$server_pid"
