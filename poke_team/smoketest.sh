#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5000/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done


###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}


###############################################
#
# User Checks
#
###############################################

create_account() {
  username=$1
  password=$2

  echo "Creating account ($username, $password)..."
  curl -s -X POST "$BASE_URL/create-account" -H "Content-Type: application/json" \
    -d "{\"username\":\"$username\", \"password\":\"$password\"}" | grep -q '"status": "success"'

  if [ $? -eq 0 ]; then
    echo "Account added successfully."
  else
    echo "Failed to add account."
    exit 1
  fi
}


update_password(){
  username=$1
  new=$2

  echo "Updating password for user $username..."
  response=$(curl -s -X POST "$BASE_URL/update-password" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$username\", \"new\":\"$new\"}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Password of user ($username) updated successfully."
  else
    echo "Failed to update password for user ($username)"
    exit 1
  fi
  }

  login() {
  username=$1
  password=$2

  echo "Logging in user $username"

  response=$(curl -s -X POST "$BASE_URL/login" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$username\", \"password\":\"$password\"}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "User $username logged in successfully"
    if [ "$ECHO_JSON" = true ]; then
      echo "Login JSON:"
      echo "$response" | jq .
    fi
  else
    echo "User $username failed to log in"
    exit 1
  fi
}

# Health checks
check_health
check_db
create_user "user" "pass"
update_password "user" "new"
login "user" "new"