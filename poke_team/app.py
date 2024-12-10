from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request
from app.utils.db_utils import check_database_connection, check_table_exists
# from flask_cors import CORS

from app.models import user_model
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



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)