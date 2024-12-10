from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request
from app.utils.db_utils import check_database_connection, check_table_exists
# from flask_cors import CORS

from app.models import user_model
from app.models import poke_model

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
# This bypasses standard security stuff we'll talk about later
# If you get errors that use words like cross origin or flight,
# uncomment this
# CORS(app)


####################################################
#
# Healthchecks
#
####################################################


@app.route('/api/health', methods=['GET'])
def healthcheck() -> Response:
    """
    Health check route to verify the service is running.

    Returns:
        JSON response indicating the health status of the service.
    """
    app.logger.info('Health check')
    return make_response(jsonify({'status': 'healthy'}), 200)

@app.route('/api/db-check', methods=['GET'])
def db_check() -> Response:
    """
    Route to check if the database connection and meals table are functional.

    Returns:
        JSON response indicating the database health status.
    Raises:
        404 error if there is an issue with the database.
    """
    try:
        app.logger.info("Checking database connection...")
        check_database_connection()
        app.logger.info("Database connection is OK.")
        app.logger.info("Checking if user table exists...")
        check_table_exists("users")
        app.logger.info("users table exists.")
        app.logger.info("Checking if pokemon table exists...")
        check_table_exists("pokemon")
        app.logger.info("pokemon table exists.")
        return make_response(jsonify({'database_status': 'healthy'}), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 404)

@app.route('/api/create-account', methods=['POST'])
def create_account() -> Response:
    """
    Route create account.

    Expected JSON Input:
        - username (str): username of account to be created
        - password (str): password of the account to be created

    Returns:
        JSON response indicating the success of account creation.
    Raises:
        400 error ifinput validation fails.
        500 error if account creation fails.
    """
    app.logger.info("Creating account...")
    try:
        data = request.get_json()

        username = data.get('username')
        password = data.get('password')
        if not username or not password:
            app.logger.info("Invalid input: Username or password ")
            return make_response(jsonify({'error': 'Invalid input, all fields are required with valid values'}), 400)

        # Add the user
        app.logger.info('Adding user: %s,', username )
        user_model.create_account(username=username, password=password)
        app.logger.info("User created: %s ", username)
        return make_response(jsonify({'status': 'success', 'user': username}), 200)
    except Exception as e:
        app.logger.error("Failed to add user: %s", str(e))
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/update-password', methods=['POST'])
def update_password() -> Response:
    """
    Route to update password

    Expected JSON Input:
        - username (str): username of account of which the password is to be updated
        - new (str): new password

    Returns:
        JSON response indicating the success of password updating.
    Raises:
        400 error ifinput validation fails.
        500 error if password fails to update.
    """
    app.logger.info("Updating password...")
    try:
        data = request.get_json()

        username = data.get('username')
        new = data.get('new')

        if not username or not new:
            app.logger.info("Invalid input: must have Username and password ")
            return make_response(jsonify({'error': 'Invalid input, all fields are required with valid values'}), 400)

        # Add the user
        app.logger.info('Updating password for user %s,', username )
        user_model.update_password(username=username, password=new)
        return make_response(jsonify({'status': 'success', 'user': username}), 200)
    except Exception as e:
        app.logger.error("Failed to update password: %s", str(e))
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/login', methods=['POST'])
def login() -> Response:
    """
    Route to log in a user

    Expected JSON Input:
        - username (str): username of account to be logged in on
        - password (str): password of the account to log in on

    Returns:
        JSON response indicating the success of password updating.
    Raises:
        400 error ifinput validation fails.
        401 error if username or password is invalid
        500 error if login fails.
    """
    app.logger.info("Updating password...")
    try:
        data = request.get_json()

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            app.logger.info("Invalid input: must have Username and password ")
            return make_response(jsonify({'error': 'Invalid input, all fields are required with valid values'}), 400)

        if user_model.login(username, password):
            return make_response(jsonify({'status': 'success', 'message': "User login successful"}), 200)
        else:
            return make_response(jsonify({'status': 'error', 'message': "Invalid username or password"}), 401)
        

    except Exception as e:
        app.logger.error("Failed to login user: %s", str(e))
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/clear-users', methods=['DELETE'])
def clear_users() -> Response:
    """
    Route to clear all users (recreates the table).

    Returns:
        JSON response indicating success of the operation or error message.
    """
    try:
        app.logger.info("Clearing the Pokemon")
        user_model.clear_user()
        return make_response(jsonify({'status': 'success'}), 200)
    except Exception as e:
        app.logger.error(f"Error clearing catalog: {e}")
        return make_response(jsonify({'error': str(e)}), 500)
    
@app.route('/api/create-pokemon-by-name/<string:name>', methods=['POST'])
def create_pokemon_by_name(name: str) -> Response:
    """
    Route create a base pokemon with its name

    Args:
        name (str): Name of the pokemon
    
    Returns:
        pokemon_id (int) : Database ID of the pokemon, for use in other methods
    
    Raises:
        500 error if fail.
    """
    app.logger.info(f"Creating " + name)
    try:
        id = poke_model.create_pokemon_by_name(name)
        return make_response(jsonify({'status': 'success', 'pokemon_id': id}), 200)
    except Exception as e:
        app.logger.error(f"Error creating pokemon: {e}")
        return make_response(jsonify({'error': str(e)}), 500)    

@app.route('/api/get-pokemon-by-id/<int:id>', methods=['GET'])
def get_pokemond_by_id(id: int) -> Response:
    """
    Route get a pokemon by its id

    Args:
        id (int): ID of the pokemon
    
    Returns:
        pokemon (Pokemon) : Pokemon object corresponding to the ID
    
    Raises:
        500 error if fail.
    """
    app.logger.info(f"Fetching " + str(id))
    try:
        pokemon = poke_model.get_pokemon_by_id(id)
        return make_response(jsonify({'status': 'success', 'pokemon': pokemon}), 200)
    except Exception as e:
        app.logger.error(f"Error creating pokemon: {e}")
        return make_response(jsonify({'error': str(e)}), 500)    

@app.route('/api/add-move-to-pokemon', methods=['POST'])
def add_move_to_pokemon() -> Response:
    """
    Route add a move to a pokemon

    Expected JSON Input:
        - id (int): ID of the pokemon
        - name (str): name of the move
    
    Raises:
        500 error if fail.
    """
    try:
        data = request.json
        id = data.get('id')
        name = data.get('name')

        app.logger.info("Adding " + name + " to " + str(id))

        poke_model.add_move_to_pokemon(id, name)
        return make_response(jsonify({'status': 'success'}), 200)
    except Exception as e:
        app.logger.error(f"Error creating pokemon: {e}")
        return make_response(jsonify({'error': str(e)}), 500) 

@app.route('/api/remove-move-from-pokemon', methods=['POST'])
def remove_move_from_pokemon() -> Response:
    """
    Route remove a move from a pokemon

    Expected JSON Input:
        - id (int): ID of the pokemon
        - name (str): name of the move
    
    Raises:
        500 error if fail.
    """
    try:
        data = request.json
        id = data.get('id')
        name = data.get('name')

        app.logger.info("Removing " + name + " from " + str(id))

        poke_model.remove_move_from_pokemon(id, name)
        return make_response(jsonify({'status': 'success'}), 200)
    except Exception as e:
        app.logger.error(f"Error creating pokemon: {e}")
        return make_response(jsonify({'error': str(e)}), 500) 

@app.route('/api/replace-move-of-pokemon', methods=['POST'])
def replace_move_of_pokemon() -> Response:
    """
    Route replace a move for a pokemon

    Expected JSON Input:
        - id (int): ID of the pokemon
        - old_name (str): name of the move to replace
        - new_name (str) name of the new move
    
    Raises:
        500 error if fail.
    """
    try:
        data = request.json
        id = data.get('id')
        old = data.get('old_name')
        new = data.get('new_name')

        app.logger.info("Replacing " + old + " with " + new + " for " + str(id))

        poke_model.replace_move_of_pokemon(id, old, new)
        return make_response(jsonify({'status': 'success'}), 200)
    except Exception as e:
        app.logger.error(f"Error creating pokemon: {e}")
        return make_response(jsonify({'error': str(e)}), 500) 

@app.route('/api/distribute-effort-values', methods=['POST'])
def distribute_effort_values() -> Response:
    """
    Route distribute evs for a pokemon

    Expected JSON Input:
        - id (int): ID of the pokemon
        - evs (List[int]): list of evs (hp, atk, def, sp atk, sp def, spd)
    
    Raises:
        500 error if fail.
    """
    try:
        data = request.json
        id = data.get('id')
        evs = data.get('evs')

        app.logger.info("Distributing evs for " + str(id))

        poke_model.distribute_effort_values(id, evs)
        return make_response(jsonify({'status': 'success'}), 200)
    except Exception as e:
        app.logger.error(f"Error creating pokemon: {e}")
        return make_response(jsonify({'error': str(e)}), 500) 

@app.route('/api/clear-poke', methods=['DELETE'])
def clear_poke() -> Response:
    """
    Route to clear all Pokemon (recreates the table).

    Returns:
        JSON response indicating success of the operation or error message.
    """
    try:
        app.logger.info("Clearing the Pokemon")
        poke_model.clear_poke()
        return make_response(jsonify({'status': 'success'}), 200)
    except Exception as e:
        app.logger.error(f"Error clearing catalog: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)