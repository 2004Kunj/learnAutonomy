#!/bin/sh
# Anatomy Lab.app launcher: starts the local server (if it isn't already running) and opens the app in your browser.
R="$(cd "$(dirname "$0")/../Resources" && pwd)"
for PORT in 8259 8260 8261 8262 8263 8264 8265; do
  URL="http://localhost:$PORT/"
  if curl -s --max-time 2 "$URL" 2>/dev/null | grep -q "Anatomy Lab"; then open "$URL"; exit 0; fi       # already running
  if ! curl -s -o /dev/null --max-time 1 "$URL" 2>/dev/null; then                                       # port is free
    nohup /usr/bin/perl "$R/server.pl" "$R/app" "$PORT" >/dev/null 2>&1 &
    i=0; while [ $i -lt 50 ]; do curl -s -o /dev/null --max-time 1 "$URL" 2>/dev/null && break; sleep 0.2; i=$((i+1)); done
    open "$URL"; exit 0
  fi
done
osascript -e 'display alert "Anatomy Lab" message "Couldn’t find a free port between 8259 and 8265."' >/dev/null 2>&1
