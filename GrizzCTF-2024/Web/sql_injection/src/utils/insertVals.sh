#!/bin/bash

# Database file
DB_FILE="../database.db"

# Function to insert into users table
insert_user() {
    sqlite3 $DB_FILE "INSERT INTO users (username, password) VALUES ('$1', '$2');"
    echo "Inserted user: $1"
}

# Function to insert into flag table
insert_flag() {
    sqlite3 $DB_FILE "INSERT INTO flag (id, text) VALUES (1, '$1');"
    echo "Inserted flag: $1"
}

# Check if the correct flags are provided
if [[ $# -eq 0 ]]; then
    echo "No arguments provided. Use -u for username, -p for password, -f for flag."
    exit 1
fi

# Parse flags
while getopts ":u:p:f:" opt; do
  case $opt in
    u) USERNAME=$OPTARG ;;
    p) PASSWORD=$OPTARG ;;
    f) FLAG=$OPTARG ;;
    \?) echo "Invalid option -$OPTARG" >&2 ;;
  esac
done

# Insert data based on flags provided
[ ! -z "$USERNAME" ] && [ ! -z "$PASSWORD" ] && insert_user "$USERNAME" "$PASSWORD"
[ ! -z "$FLAG" ] && insert_flag "$FLAG"

# Check if data was inserted
if [ -z "$USERNAME" ] && [ -z "$FLAG" ]; then
    echo "No data inserted. Use -u and -p to insert a user or -f to insert a flag."
fi
