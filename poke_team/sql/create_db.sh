#!/bin/bash

# Check if the database file already exists
if [ -f "$DB_PATH" ]; then
    echo "Recreating database at $DB_PATH."
    # Drop and recreate the tables
    sqlite3 "$DB_PATH" < /app/sql/create_poke_table.sql #switch meal out for whichever database we're going to create
    sqlite3 "$DB_PATH" < /app/sql/create_user_table.sql
    echo "Database recreated successfully."
else
    echo "Creating database at $DB_PATH."
    # Create the database for the first time
    sqlite3 "$DB_PATH" < /app/sql/create_poke_table.sql #switch meal out for whichever database we're going to create
    sqlite3 "$DB_PATH" < /app/sql/create_user_table.sql
    echo "Database created successfully."
fi