#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5001/api"

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

#
# Health checks
#
check_health
check_db
create_account "user" "pass"
update_password "user" "new"
login "user" "new"

###############################################
#
# Poke Checks
#
###############################################


clear_poke() {
  echo "Clearing the poke table..."
  curl -s -X DELETE "$BASE_URL/clear-poke" | grep -q '"status": "success"'
}

create_pokemon_by_name() {
  name=$1

  echo "Creating Pokemon ($name)..."
  curl -s -X POST "$BASE_URL/create-pokemon-by-name/$name" -H "Content-Type: application/json" \
    | grep -q '"status": "success"'

  if [ $? -eq 0 ]; then
    echo "Pokemon created successfully."
  else
    echo "Failed to create Pokemon."
    exit 1
  fi
}

get_pokemon_by_id() {
  id=$1

  echo "Fetching Pokemon with ID ($id)..."
  response=$(curl -s -X GET "$BASE_URL/get-pokemon-by-id/$id" -H "Content-Type: application/json")
  echo "$response" | grep -q '"status": "success"'

  if [ $? -eq 0 ]; then
    echo "Pokemon fetched successfully: $response"
  else
    echo "Failed to fetch Pokemon."
    exit 1
  fi
}

add_move_to_pokemon() {
  id=$1
  name=$2

  echo "Adding move ($name) to Pokemon with ID ($id)..."
  curl -s -X POST "$BASE_URL/add-move-to-pokemon" -H "Content-Type: application/json" \
    -d "{\"id\": $id, \"name\": \"$name\"}" | grep -q '"status": "success"'

  if [ $? -eq 0 ]; then
    echo "Move added successfully."
  else
    echo "Failed to add move."
    exit 1
  fi
}

remove_move_from_pokemon() {
  id=$1
  name=$2

  echo "Removing move ($name) from Pokemon with ID ($id)..."
  curl -s -X POST "$BASE_URL/remove-move-from-pokemon" -H "Content-Type: application/json" \
    -d "{\"id\": $id, \"name\": \"$name\"}" | grep -q '"status": "success"'

  if [ $? -eq 0 ]; then
    echo "Move removed successfully."
  else
    echo "Failed to remove move."
    exit 1
  fi
}

replace_move_of_pokemon() {
  id=$1
  old_name=$2
  new_name=$3

  echo "Replacing move ($old_name) with ($new_name) for Pokemon with ID ($id)..."
  curl -s -X POST "$BASE_URL/replace-move-of-pokemon" -H "Content-Type: application/json" \
    -d "{\"id\": $id, \"old_name\": \"$old_name\", \"new_name\": \"$new_name\"}" | grep -q '"status": "success"'

  if [ $? -eq 0 ]; then
    echo "Move replaced successfully."
  else
    echo "Failed to replace move."
    exit 1
  fi
}

distribute_effort_values() {
  id=$1
  evs=$2

  echo "Distributing EVs ($evs) to Pokemon with ID ($id)..."
  curl -s -X POST "$BASE_URL/distribute-effort-values" -H "Content-Type: application/json" \
    -d "{\"id\": $id, \"evs\": $evs}" | grep -q '"status": "success"'

  if [ $? -eq 0 ]; then
    echo "EVs distributed successfully."
  else
    echo "Failed to distribute EVs."
    exit 1
  fi
}

clear_poke

create_pokemon_by_name "ditto"
create_pokemon_by_name "blaziken"
get_pokemon_by_id 1
add_move_to_pokemon 1 "blaze_kick"
remove_move_from_pokemon 1 "peck"
replace_move_of_pokemon 1 "peck "flamethrower"
distribute_effort_values 1 [4, 4, 4, 4, 4, 4]
