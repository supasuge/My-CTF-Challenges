#!/bin/bash

# Default Database file
DB_FILE="database.db"

# Parse flags
while getopts ":o:" opt; do
  case $opt in
    o) DB_FILE=$OPTARG ;;
    \?) echo "Invalid option -$OPTARG" >&2; exit 1 ;;
  esac
done

# Initialize SQLite Database
sqlite3 $DB_FILE <<EOF
CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT);
CREATE TABLE IF NOT EXISTS flag (id INTEGER PRIMARY KEY, text TEXT);
EOF

echo "Database initialized with tables: users, flag at $DB_FILE"