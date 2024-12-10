from contextlib import contextmanager
import re
import sqlite3
import bcrypt

import pytest

from app.models.user_model import (
    create_account,
    update_password,
    login
)


######################################################
#
#    Fixtures
#
######################################################

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

# Mocking the database connection for tests
@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_conn.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("app.models.user_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test

######################################################
#
#    Create account
#
######################################################

def test_create_account(mock_cursor):
    """Test creating a new user."""

    # Call the function to create an account
    create_account(username="bucket", password="hehehe")

    expected_query = normalize_whitespace("""
        INSERT INTO users (username, hashed_passwd, salt)
        VALUES (?, ?, ?)
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call (second element of call_args)
    actual_arguments = mock_cursor.execute.call_args[0][1]

    assert actual_arguments[0] == "bucket", "username did not match expected user"
    assert actual_arguments[1], "password should not be empty"
    assert actual_arguments[2], "salt should not be emoty"

def test_create_account_bad_user(mock_cursor):
    """Test creating a new user with a username that is not a string."""

    with pytest.raises(ValueError, match="Invalid username or passrowd: 2, hehehe. Both must be a string."):
        create_account(username=2, password="hehehe")

def test_create_account_bad_password():
    """Test creating a new user with a username that is not a string."""

    with pytest.raises(ValueError, match="Invalid username or passrowd: user, 3. Both must be a string."):
        create_account(username="user", password=3)

def test_create_account_duplicate_user(mock_cursor):
    """Test creating a new user with a duplicate username"""

    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: users.username")

    with pytest.raises(ValueError, match="User with name 'user' already exists"):
        create_account(username="user", password="hehehe")
   

######################################################
#
#    Update password
#
######################################################

def test_update_password(mock_cursor):
    """Test updating the password of an existing user"""

    mock_cursor.fetchone.return_value = (1, "bucket", "old", "ejh")

    update_password(username="bucket", password="hehehe")

    expected_query = normalize_whitespace("""
    UPDATE users SET hashed_passwd = ?, salt = ? WHERE username = ?
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert expected_query==actual_query, "The SQL query did not match the expected structure."        

def test_update_password_bad_user():
    """Test updating password with a username that is not a string."""

    with pytest.raises(ValueError, match="Invalid username or passrowd: 2, pass. Both must be a string."):
        update_password(username=2, password="pass")

def test_update_password_bad_password():
    """Test updating password with a username that is not a string."""

    with pytest.raises(ValueError, match="Invalid username or passrowd: user, 3. Both must be a string."):
        update_password(username="user", password=3)

def test_update_password_nonexistent_user(mock_cursor):
    """Test updating password of a user that doesn't exist"""
    
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="user user not found"):
        update_password(username="user", password="pass")




######################################################
#
#    Login
#
######################################################

def test_login(mock_cursor):
    """Test login of existing user"""
    password = "test"
    salt = bcrypt.gensalt()
    hashed_pass = bcrypt.hashpw(password.encode('utf-8'), salt)

    mock_cursor.fetchone.return_value = (hashed_pass, salt)

    
    actual_result = login(username = "user", password ="test")

    assert actual_result == True, f"Expected True but got {actual_result}"

def test_login_bad_user():
    """Test login username not a string"""
    
    with pytest.raises(ValueError, match="Invalid username or passrowd: 2, hehehe. Both must be a string."):
        login(username=2, password="hehehe")

def test_login_bad_password():
    """Test login password not a string"""
    
    with pytest.raises(ValueError, match="Invalid username or passrowd: user, 3. Both must be a string."):
        login(username="user", password=3)


def test_login_nonexistent_user(mock_cursor):
    """Test logging into a nonexistent account"""
    
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="user user not found"):
        update_password(username="user", password="pass")

def test_login_wrong_password(mock_cursor):
    """Test logging into existing account with a wrong password"""
    mock_cursor.fetchone.return_value = False

    assert False == login(username="user", password="wrong"), "Expected False, but got true"