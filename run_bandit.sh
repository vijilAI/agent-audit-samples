#!/bin/bash

# Directories to scan
DIRS=("mindshare-langgraph" "multi-personality-agent-langgraph")

# Output directory for reports
OUTPUT_DIR="bandit_reports"
mkdir -p "$OUTPUT_DIR"

# Run bandit for each directory
for DIR in "${DIRS[@]}"; do
    REPORT_FILE="$OUTPUT_DIR/${DIR//\//_}_bandit_report.json"
    echo "Scanning $DIR..."

    # Run bandit and allow failures without exiting the script
    if bandit -r "$DIR" -f json -o "$REPORT_FILE"; then
        echo "Report for $DIR saved to $REPORT_FILE"
    else
        echo "Bandit found issues in $DIR — report still saved to $REPORT_FILE"
    fi
done

echo "All Bandit scans complete."
