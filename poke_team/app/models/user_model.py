from dataclasses import dataclass
import logging
import os
import sqlite3
import bcrypt
from typing import Any

from app.utils.db_utils import get_db_connection
from app.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)

@dataclass
class User:
    id: int
    username: str
    hashed_passwd: str
    salt: str

def create_account(username: str, password: str) -> None:
    
    """
        Creates an account and adds it to the users table
        Args:
            username (str): The username of the account to be created
            password (str): The password of the account to be created
        Raises:
            ValueError: If either the username or password is not a string
                            OR if either the username or password is empty
                                OR a user with the same username already exists

            sqlite3.Error: If any database error occurs.
        """
    
    if not isinstance(username, str) or not isinstance(password, str) or not username or not password:
        raise ValueError(f"Invalid username or passrowd: {username}, {password}. Both must be a string.")
   
    try:
        salt = bcrypt.gensalt()
        hashed_passwd = bcrypt.hashpw(password.encode('utf-8'), salt)


        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, hashed_passwd, salt)
                VALUES (?, ?, ?)
            """, (username, hashed_passwd, salt))
            conn.commit()

            logger.info("User successfully added to the database: %s", username)

    except sqlite3.IntegrityError:
        logger.error("Duplicate user name: %s", username)
        raise ValueError(f"User with name '{username}' already exists")

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e


def update_password(username:str, password: str) -> None:

    """
        Updates the password of the user with the specified name to the 
            given password (after hashing)
        Args:
            username (str): The username of the account to be updated
            password (str): The new password to be hashed and placed back into the users table
        Raises:
            ValueError: If either the username or password is not a string
                            OR if either the username or password is empty
                                OR a user with the given username does not exist
                                
            sqlite3.Error: If any database error occurs.
        """
    
    if not isinstance(username, str) or not isinstance(password, str) or not username or not password:
        raise ValueError(f"Invalid username or passrowd: {username}, {password}. Both must be a string.")
   
    try:
        with get_db_connection() as conn:
            salt = bcrypt.gensalt()
            hashed_passwd = bcrypt.hashpw(password.encode('utf-8'), salt)
            cursor = conn.cursor()
            
            cursor.execute("SELECT username FROM users WHERE username = ?", (username, ))
            row = cursor.fetchone()
            
            if row:
                
                logger.info("Password of user %s updated", username)
                
            else:
                logger.info("User %s not found", username)
                raise ValueError(f"user {username} not found")
            
            
            cursor.execute("UPDATE users SET hashed_passwd = ?, salt = ? WHERE username = ?", (hashed_passwd, salt, username, ) )
            conn.commit()

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e
    
def login(username:str, password:str)->None:

    """
        Attempts to log in by matching the given username and password with 
                the correlating username and password in the users table
        Args:
            username (str): The username of the account that's trying to be logged in
            password (str): The password of the account to be compared with the stored password
        Raises:
            ValueError: If either the username or password is not a string
                            OR if either the username or password is empty
            sqlite3.Error: If any database error occurs.
        """
    
    if not isinstance(username, str) or not isinstance(password, str) or not username or not password:
        raise ValueError(f"Invalid username or passrowd: {username}, {password}. Both must be a string.")
   
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""SELECT hashed_passwd, salt FROM users WHERE username = ?""" , (username, ))
            passwd = cursor.fetchone()

            if passwd:

                correct = bcrypt.checkpw(password.encode('utf-8'), passwd[0])
                if correct:
                    logger.info("successfully logged in :3")
                    return True
                else:
                    logger.info("wrong password :(")
                    return False
                                       

            else:
                logger.info("User %s not found", username)
                return False
           
                

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e