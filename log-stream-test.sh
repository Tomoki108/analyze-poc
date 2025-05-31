#!/bin/bash

# Log stream test script for log-ingest and log-consumer

API_URL="http://localhost:8080/api/log"
INTERVAL=1  # seconds between requests

echo "Starting log stream test to $API_URL"
echo "Press Ctrl+C to stop"

while true; do
  # Generate random user_id (u1 to u100)
  user_id="u$((1 + RANDOM % 100))"
  
  # Randomly choose menu type (50% washoku, 50% yoshoku)
  if [ $((RANDOM % 2)) -eq 0 ]; then
    menu_type="washoku"
  else
    menu_type="yoshoku"
  fi

  # Get current timestamp in ISO format
  timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

  # Create JSON payload
  json_payload=$(jq -n \
    --arg user_id "$user_id" \
    --arg timestamp "$timestamp" \
    --arg menu_type "$menu_type" \
    '{user_id: $user_id, timestamp: $timestamp, menu_type: $menu_type}')

  # Send POST request
  echo "Sending: $json_payload"
  curl -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d "$json_payload"

  # Wait for interval
  sleep $INTERVAL
done
