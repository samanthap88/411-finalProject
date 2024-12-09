from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request
from app.utils.db_utils import check_database_connection, check_table_exists
# from flask_cors import CORS

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)