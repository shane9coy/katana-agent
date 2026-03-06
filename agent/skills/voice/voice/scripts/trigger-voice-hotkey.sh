#!/bin/bash
# MAGI3 Voice Hotkey Trigger
# Sends POST to Audio Service to activate listening window

curl -s -X POST http://127.0.0.1:9001/trigger \
  -H "Content-Type: application/json" \
  -d '{"window_seconds": 12}' \
  > /dev/null 2>&1 &
