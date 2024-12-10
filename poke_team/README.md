Poke Model is an app that allows users to customize a pokemon.
We offer users control over a pokemon's
- Ability
- Moveset
- EVS
To get started, create a pokemon with > /api/create-pokemon-by-name/<string:name>

Route: /api/create-account
● Request Type: POST
● Purpose: Creates a new user account.
● Request Body:
  - username (str): Username for the new account.
  - password (str): Password for the new account.
● Response Format: JSON
  - Success Response Example:
    - Code: 200
    - Content: { "status": "success", "user": "user123" }
  - Error Response Example (Invalid input):
    - Code: 400
    - Content: { "error": "Invalid input, all fields are required with valid values" }
  - Error Response Example (Account creation failed):
    - Code: 500
    - Content: { "error": "Error creating account: <error_message>" }
● Example Request:
  {
    "username": "user123",
    "password": "password123"
  }
● Example Response:
  {
    "status": "success",
    "user": "user123"
  }

Route: /api/update-password
● Request Type: POST
● Purpose: Updates the password for an existing user.
● Request Body:
  - username (str): Username of the account to update the password for.
  - new (str): New password.
● Response Format: JSON
  - Success Response Example:
    - Code: 200
    - Content: { "status": "success", "user": "user123" }
  - Error Response Example (Invalid input):
    - Code: 400
    - Content: { "error": "Invalid input, all fields are required with valid values" }
  - Error Response Example (Password update failed):
    - Code: 500
    - Content: { "error": "Error updating password: <error_message>" }
● Example Request:
  {
    "username": "user123",
    "new": "newpassword123"
  }
● Example Response:
  {
    "status": "success",
    "user": "user123"
  }

Route: /api/login
● Request Type: POST
● Purpose: Logs in a user by validating their username and password.
● Request Body:
  - username (str): Username of the account to log in on.
  - password (str): Password of the account to log in on.
● Response Format: JSON
  - Success Response Example:
    - Code: 200
    - Content: { "status": "success", "message": "User login successful" }
  - Error Response Example (Invalid input):
    - Code: 400
    - Content: { "error": "Invalid input, all fields are required with valid values" }
  - Error Response Example (Invalid credentials):
    - Code: 401
    - Content: { "status": "error", "message": "Invalid username or password" }
  - Error Response Example (Login failed):
    - Code: 500
    - Content: { "error": "Error logging in: <error_message>" }
● Example Request:
  {
    "username": "user123",
    "password": "password123"
  }
● Example Response:
  {
    "status": "success",
    "message": "User login successful"
  }

Route: /api/clear-users
● Request Type: DELETE
● Purpose: Clears all users by recreating the user table.
● Response Format: JSON
  - Success Response Example:
    - Code: 200
    - Content: { "status": "success" }
  - Error Response Example:
    - Code: 500
    - Content: { "error": "Error clearing users: <error_message>" }
● Example Request: None
● Example Response:
  {
    "status": "success"
  }

Route: /api/create-pokemon-by-name/<string:name>
● Request Type: POST
● Purpose: Creates a base Pokémon using its name.
● Request Parameters:
  - name (str): Name of the Pokémon to create.
● Response Format: JSON
  - Success Response Example:
    - Code: 200
    - Content: { "status": "success", "pokemon_id": 1 }
  - Error Response Example:
    - Code: 500
    - Content: { "error": "Error creating pokemon: <error_message>" }
● Example Request:
  None
● Example Response:
  {
    "status": "success",
    "pokemon_id": 1
  }

Route: /api/get-pokemon-by-id/<int:id>
● Request Type: GET
● Purpose: Fetches a Pokémon by its ID.
● Request Parameters:
  - id (int): ID of the Pokémon to fetch.
● Response Format: JSON
  - Success Response Example:
    - Code: 200
    - Content: { "status": "success", "pokemon": { "id": 1, "name": "Pikachu", "moves": ["Thunderbolt", "Quick Attack"] } }
  - Error Response Example:
    - Code: 500
    - Content: { "error": "Error fetching pokemon: <error_message>" }
● Example Request:
  None
● Example Response:
  {
    "status": "success",
    "pokemon": {
      "id": 1,
      "name": "Pikachu",
      "moves": ["Thunderbolt", "Quick Attack"]
    }
  }

Route: /api/add-move-to-pokemon
● Request Type: POST
● Purpose: Adds a move to a Pokémon.
● Request Body:
  - id (int): ID of the Pokémon.
  - name (str): Name of the move to add.
● Response Format: JSON
  - Success Response Example:
    - Code: 200
    - Content: { "status": "success" }
  - Error Response Example:
    - Code: 500
    - Content: { "error": "Error adding move: <error_message>" }
● Example Request:
  {
    "id": 1,
    "name": "Thunderbolt"
  }
● Example Response:
  {
    "status": "success"
  }

Route: /api/remove-move-from-pokemon
● Request Type: POST
● Purpose: Removes a move from a Pokémon.
● Request Body:
  - id (int): ID of the Pokémon.
  - name (str): Name of the move to remove.
● Response Format: JSON
  - Success Response Example:
    - Code: 200
    - Content: { "status": "success" }
  - Error Response Example:
    - Code: 500
    - Content: { "error": "Error removing move: <error_message>" }
● Example Request:
  {
    "id": 1,
    "name": "Quick Attack"
  }
● Example Response:
  {
    "status": "success"
  }

Route: /api/replace-move-of-pokemon
● Request Type: POST
● Purpose: Replaces an existing move with a new move for a specified Pokémon.
● Request Body:
  - id (int): ID of the Pokémon.
  - old_name (str): Name of the move to replace.
  - new_name (str): Name of the new move.
● Response Format: JSON
  - Success Response Example:
    - Code: 200
    - Content: { "status": "success" }
● Example Request:
  {
    "id": 1,
    "old_name": "Thunderbolt",
    "new_name": "Volt Tackle"
  }
● Example Response:
  {
    "status": "success"
  }

Route: /api/distribute-effort-values
● Request Type: POST
● Purpose: Distributes effort values (EVs) to a Pokémon's stats (HP, Attack, Defense, Special Attack, Special Defense, Speed).
● Request Body:
  - id (int): ID of the Pokémon.
  - evs (List[int]): List of EVs for the stats in the order (HP, Attack, Defense, Special Attack, Special Defense, Speed).
● Response Format: JSON
  - Success Response Example:
    - Code: 200
    - Content: { "status": "success" }
● Example Request:
  {
    "id": 1,
    "evs": [4, 0, 0, 0, 0, 252]
  }
● Example Response:
  {
    "status": "success"
  }