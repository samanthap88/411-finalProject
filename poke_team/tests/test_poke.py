from contextlib import contextmanager
import re
import sqlite3

import pytest

from app.models.poke_model import *
from unittest.mock import Mock

pokemon = Pokemon(
    id=0,
    game_id=132,
    name="ditto",
    ability="limber",
    learned_moves=["transform"],
    stats= Stats(
        hp=[48, 0],
        attack=[48, 0],
        defense=[48, 0],
        special_attack=[48, 0],
        special_defense=[48, 0],
        speed=[48, 0]
    ),
    total_effort=0
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
    mock_cursor.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("app.models.poke_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test


@pytest.fixture
def mock_requests(mocker):
    """Mock the requests.get call."""
    return mocker.patch('requests.get')

@pytest.fixture
def mock_get_pokemon_by_id(mocker):
    """Mock the get_pokemon_by_id function."""
    return mocker.patch('app.models.poke_model.get_pokemon_by_id')

######################################################
#
#    Tests
#
######################################################

def test_create_pokemon_by_object(mock_cursor):
    """Test creating a new Pokémon in the database."""

    # Call the function to create the Pokémon
    create_pokemon_by_object(pokemon)

    # Assert the `pokemon` table insert query
    expected_pokemon_query = normalize_whitespace("""
        INSERT INTO pokemon (id, game_id, name, ability, total_effort)
        VALUES (?, ?, ?, ?, ?)
    """)
    actual_pokemon_query = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    assert actual_pokemon_query == expected_pokemon_query, "The `pokemon` SQL query did not match the expected structure."

    expected_pokemon_arguments = (0, 132, "ditto", "limber", 0)
    actual_pokemon_arguments = mock_cursor.execute.call_args_list[0][0][1]
    assert actual_pokemon_arguments == expected_pokemon_arguments, (
        f"The `pokemon` SQL query arguments did not match. Expected {expected_pokemon_arguments}, got {actual_pokemon_arguments}."
    )

    # Assert the `learned_moves` table insert query
    expected_moves_query = normalize_whitespace("""
        INSERT INTO learned_moves (pokemon_id, move) VALUES (?, ?)
    """)
    actual_moves_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])
    assert actual_moves_query == expected_moves_query, "The `learned_moves` SQL query did not match the expected structure."

    expected_moves_arguments = (0, "transform")
    actual_moves_arguments = mock_cursor.execute.call_args_list[1][0][1]
    assert actual_moves_arguments == expected_moves_arguments, (
        f"The `learned_moves` SQL query arguments did not match. Expected {expected_moves_arguments}, got {actual_moves_arguments}."
    )

    # Assert the `stats` table insert query
    expected_stats_query = normalize_whitespace("""
        INSERT INTO stats (
            pokemon_id, hp_base, hp_effort,
            attack_base, attack_effort,
            defense_base, defense_effort,
            special_attack_base, special_attack_effort,
            special_defense_base, special_defense_effort,
            speed_base, speed_effort
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """)
    actual_stats_query = normalize_whitespace(mock_cursor.execute.call_args_list[2][0][0])
    assert actual_stats_query == expected_stats_query, "The `stats` SQL query did not match the expected structure."

    expected_stats_arguments = (
        0,
        48, 0,
        48, 0,
        48, 0,
        48, 0,
        48, 0,
        48, 0
    )
    actual_stats_arguments = mock_cursor.execute.call_args_list[2][0][1]
    assert actual_stats_arguments == expected_stats_arguments, (
        f"The `stats` SQL query arguments did not match. Expected {expected_stats_arguments}, got {actual_stats_arguments}."
    )

def test_get_pokemon_by_id(mock_cursor):
    """Test retrieving a Pokémon by its ID."""

    # Setup mock data returned by the cursor
    mock_cursor.fetchone.side_effect = [
        # First call (pokemon table)
        (1, 132, "ditto", "limber", 0),
        # Third call (stats table)
        (48, 0, 48, 0, 48, 0, 48, 0, 48, 0, 48, 0),
    ]
    mock_cursor.fetchall.side_effect = [
        # Second call (learned_moves table)
        [("transform",)],
    ]

    # Call the function to retrieve the Pokémon
    pokemon = get_pokemon_by_id(1)

    # Expected Pokémon object
    expected_pokemon = Pokemon(
        id=1,
        game_id=132,
        name="ditto",
        ability="limber",
        learned_moves=["transform"],
        stats=Stats(
            hp=[48, 0],
            attack=[48, 0],
            defense=[48, 0],
            special_attack=[48, 0],
            special_defense=[48, 0],
            speed=[48, 0],
        ),
        total_effort=0,
    )

    # Assert that the returned Pokémon matches the expected object
    assert pokemon == expected_pokemon, f"Expected {expected_pokemon}, but got {pokemon}."

    # Verify the SQL queries were executed in the correct sequence
    expected_queries = [
        normalize_whitespace("""
            SELECT id, game_id, name, ability, total_effort
            FROM pokemon WHERE id = ?
        """),
        normalize_whitespace("""
            SELECT move FROM learned_moves WHERE pokemon_id = ?
        """),
        normalize_whitespace("""
            SELECT 
                hp_base, hp_effort,
                attack_base, attack_effort,
                defense_base, defense_effort,
                special_attack_base, special_attack_effort,
                special_defense_base, special_defense_effort,
                speed_base, speed_effort
            FROM stats WHERE pokemon_id = ?
        """)
    ]

    actual_queries = [normalize_whitespace(call[0][0]) for call in mock_cursor.execute.call_args_list]
    assert actual_queries == expected_queries, (
        f"Expected SQL queries {expected_queries}, but got {actual_queries}."
    )

    # Verify arguments for the queries
    expected_arguments = [
        (1,),  # Argument for the Pokémon retrieval
        (1,),  # Argument for the learned_moves retrieval
        (1,),  # Argument for the stats retrieval
    ]

    actual_arguments = [call[0][1] for call in mock_cursor.execute.call_args_list]
    assert actual_arguments == expected_arguments, (
        f"Expected SQL query arguments {expected_arguments}, but got {actual_arguments}."
    )

def test_get_pokemon_by_invalid_id(mock_cursor):
    """Test retrieving a Pokémon with an invalid ID."""

    # Setup mock to simulate no Pokémon found
    mock_cursor.fetchone.return_value = None  # No data returned for the Pokémon query

    # Call the function and verify it raises a ValueError
    invalid_id = 999  # Example of an invalid Pokémon ID
    with pytest.raises(ValueError, match=f"Pokemon with ID {invalid_id} not found"):
        get_pokemon_by_id(invalid_id)

    # Verify the query executed
    expected_query = normalize_whitespace("""
        SELECT id, game_id, name, ability, total_effort
        FROM pokemon WHERE id = ?
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    assert actual_query == expected_query, "The SQL query for Pokémon retrieval did not match the expected structure."

    # Verify the argument passed to the query
    actual_argument = mock_cursor.execute.call_args[0][1]
    assert actual_argument == (invalid_id,), f"Expected argument {(invalid_id,)}, but got {actual_argument}."

def test_add_move_to_pokemon_successful(mock_cursor, mock_requests, mock_get_pokemon_by_id):
    # Set up the mock responses for the requests and get_pokemon_by_id
    mock_pokemon = Mock()
    mock_pokemon.id = 1
    mock_pokemon.name = 'ditto'
    mock_pokemon.learned_moves = ['transform']
    
    # Set up mock response for requests.get
    mock_response = Mock()
    mock_response.json.return_value = {'moves': [{'move': {'name': 'transform'}}, {'move': {'name': 'growl'}}]}
    mock_requests.return_value = mock_response
    
    # Mock get_pokemon_by_id to return a mock pokemon object
    mock_get_pokemon_by_id.return_value = mock_pokemon

    # Call the function to add a move to the pokemon
    add_move_to_pokemon(pokemon_id=1, move_name='growl')

    # Assert the correct database insertions or any other side effects.
    expected_query = "INSERT INTO learned_moves (pokemon_id, move) VALUES (?, ?)"
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    assert actual_query == expected_query
    expected_args = (1, 'growl')
    actual_args = mock_cursor.execute.call_args[0][1]
    assert actual_args == expected_args
    """Test successfully adding a move to a Pokémon."""
    
    pokemon_id = 2
    move_name = "thunderbolt"
    mock_pokemon = Pokemon(
        id=2,
        game_id=132,
        name="pikachu",
        ability="static",
        learned_moves=["quick-attack", "tail-whip"],
        stats=Stats([35, 0], [55, 0], [40, 0], [50, 0], [50, 0], [90, 0]),
        total_effort=0
    )

    mock_get_pokemon_by_id.return_value = mock_pokemon
    mock_response.json.return_value = {
        "moves": [{"move": {"name": "quick-attack"}}, {"move": {"name": "tail-whip"}}, {"move": {"name": "thunderbolt"}}]
    }
    mock_requests.return_value = mock_response

    add_move_to_pokemon(pokemon_id, move_name)

    # Check that the correct query was executed
    expected_query = normalize_whitespace("""
        INSERT INTO learned_moves (pokemon_id, move)
        VALUES (?, ?)
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Check that the correct arguments were passed
    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = (pokemon_id, move_name)
    assert actual_arguments == expected_arguments, f"Expected arguments {expected_arguments}, got {actual_arguments}."

def test_add_move_to_pokemon_invalid_move(mock_cursor, mock_requests, mock_get_pokemon_by_id):
    """Test adding an invalid move to a Pokémon."""
    
    pokemon_id = 1
    move_name = "fire-blast"
    mock_pokemon = Pokemon(
        id=1,
        game_id=132,
        name="pikachu",
        ability="static",
        learned_moves=["quick-attack", "tail-whip"],
        stats=Stats([35, 0], [55, 0], [40, 0], [50, 0], [50, 0], [90, 0]),
        total_effort=0
    )

    mock_get_pokemon_by_id.return_value = mock_pokemon
    mock_requests.get.return_value.json.return_value = {
        "moves": [{"move": {"name": "quick-attack"}}, {"move": {"name": "tail-whip"}}]
    }

    with pytest.raises(ValueError, match=mock_pokemon.name + " cannot learn " + move_name):
        add_move_to_pokemon(pokemon_id, move_name)

def test_add_move_to_pokemon_four_moves(mock_cursor, mock_requests, mock_get_pokemon_by_id):
    """Test adding a move to a Pokémon that already knows four moves."""
    
    pokemon_id = 1
    move_name = "thunderbolt"
    mock_pokemon = Pokemon(
        id=1,
        game_id=132,
        name="pikachu",
        ability="static",
        learned_moves=["quick-attack", "tail-whip", "iron-tail", "electro-ball"],
        stats=Stats([35, 0], [55, 0], [40, 0], [50, 0], [50, 0], [90, 0]),
        total_effort=0
    )

    mock_response = Mock()
    mock_get_pokemon_by_id.return_value = mock_pokemon
    mock_response.json.return_value = {
        "moves": [{"move": {"name": "quick-attack"}}, {"move": {"name": "tail-whip"}}, {"move": {"name": "thunderbolt"}}]
    }
    mock_requests.return_value = mock_response

    with pytest.raises(ValueError, match="This pokemon already knows 4 moves"):
        add_move_to_pokemon(pokemon_id, move_name)

def test_remove_move_from_pokemon_successful(mock_cursor, mock_get_pokemon_by_id):
    """Test successfully removing a move from a Pokémon."""
    
    pokemon_id = 1
    move_name = "quick-attack"
    mock_pokemon = Pokemon(
        id=1,
        game_id=132,
        name="pikachu",
        ability="static",
        learned_moves=["quick-attack", "tail-whip"],
        stats=Stats([35, 0], [55, 0], [40, 0], [50, 0], [50, 0], [90, 0]),
        total_effort=0
    )

    mock_get_pokemon_by_id.return_value = mock_pokemon

    remove_move_from_pokemon(pokemon_id, move_name)

    # Check that the correct SQL query was executed
    expected_query = normalize_whitespace("""
        DELETE FROM learned_moves
        WHERE pokemon_id = ? AND move = ?
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Check that the correct arguments were passed
    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = (pokemon_id, move_name)
    assert actual_arguments == expected_arguments, f"Expected arguments {expected_arguments}, got {actual_arguments}."

def test_remove_move_from_pokemon_move_not_known(mock_get_pokemon_by_id):
    """Test removing a move from a Pokémon that doesn't know it."""
    
    pokemon_id = 1
    move_name = "thunderbolt"
    mock_pokemon = Pokemon(
        id=1,
        game_id=132,
        name="pikachu",
        ability="static",
        learned_moves=["quick-attack", "tail-whip"],
        stats=Stats([35, 0], [55, 0], [40, 0], [50, 0], [50, 0], [90, 0]),
        total_effort=0
    )

    mock_get_pokemon_by_id.return_value = mock_pokemon

    with pytest.raises(ValueError, match="This pokemon does not know this move"):
        remove_move_from_pokemon(pokemon_id, move_name)

def test_distribute_effort_values_successful(mock_cursor, mock_get_pokemon_by_id):
    """Test successfully redistributing effort values for a Pokémon."""

    pokemon_id = 1
    evs = [100, 200, 50, 60, 70, 30]  # Input EVs for redistribution
    mock_pokemon = Pokemon(
        id=1,
        game_id=132,
        name="pikachu",
        ability="static",
        learned_moves=["quick-attack", "tail-whip"],
        stats=Stats([35, 0], [55, 0], [40, 0], [50, 0], [50, 0], [90, 0]),
        total_effort=0
    )

    mock_get_pokemon_by_id.return_value = mock_pokemon

    distribute_effort_values(pokemon_id, evs)

    # Verify the SQL query
    expected_query = normalize_whitespace("""
        UPDATE stats
        SET 
            hp_effort = ?, 
            attack_effort = ?, 
            defense_effort = ?, 
            special_attack_effort = ?, 
            special_defense_effort = ?, 
            speed_effort = ?
        WHERE pokemon_id = ?
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Verify the SQL arguments
    expected_effort_values = [100, 200, 50, 60, 70, 30]  # These values should remain unchanged
    expected_arguments = (*expected_effort_values, pokemon_id)
    actual_arguments = mock_cursor.execute.call_args[0][1]
    assert actual_arguments == expected_arguments, (
        f"Expected arguments {expected_arguments}, got {actual_arguments}."
    )

def test_distribute_effort_values_with_caps(mock_cursor, mock_get_pokemon_by_id):
    """Test redistributing effort values exceeding caps for a Pokémon."""

    pokemon_id = 1
    evs = [300, 300, 300, 300, 300, 300]  # Exceeding both individual and total caps
    mock_pokemon = Pokemon(
        id=1,
        game_id=132,
        name="charizard",
        ability="blaze",
        learned_moves=["flamethrower", "fly"],
        stats=Stats([78, 0], [84, 0], [78, 0], [109, 0], [85, 0], [100, 0]),
        total_effort=0
    )

    mock_get_pokemon_by_id.return_value = mock_pokemon

    distribute_effort_values(pokemon_id, evs)

    # Verify the SQL query
    expected_query = normalize_whitespace("""
        UPDATE stats
        SET 
            hp_effort = ?, 
            attack_effort = ?, 
            defense_effort = ?, 
            special_attack_effort = ?, 
            special_defense_effort = ?, 
            speed_effort = ?
        WHERE pokemon_id = ?
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Verify the SQL arguments
    expected_effort_values = [255, 255, 0, 0, 0, 0]  # Caps applied: max 255 for two stats, total 510
    expected_arguments = (*expected_effort_values, pokemon_id)
    actual_arguments = mock_cursor.execute.call_args[0][1]
    assert actual_arguments == expected_arguments, (
        f"Expected arguments {expected_arguments}, got {actual_arguments}."
    )
