import requests
from typing import List, Optional
from dataclasses import dataclass
import logging
import sqlite3
import os
from typing import Any

from app.utils.db_utils import get_db_connection
from app.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)

@dataclass
class Stats:
    """
    base_stat, effort_values
    Every 4 effort_values translates to 1 stat increase
    Individual effort_values are capped at 255
    Total effort_values is capped at 510

    """
    hp: List[int]
    attack: List[int]
    defense: List[int]
    special_attack: List[int]
    special_defense: List[int]
    speed: List[int]

@dataclass
class Pokemon:
    id: int
    game_id: int
    name: str
    ability: str
    learned_moves: List[str]
    stats: Stats
    total_effort: int

BASE_POKE_URL = "https://pokeapi.co/api/v2/"
global_id = 0

stat_map = {
    'hp': 'hp',
    'attack': 'attack',
    'defense': 'defense',
    'special-attack': 'special_attack',
    'special-defense': 'special_defense',
    'speed': 'speed'
}

def create_pokemon_by_name(name):
    """
    Create a pokemon by its name.
    
    Args:
        name (string): The name of the pokemon.

    Returns:
        id (int): DB ID of the pokemon

    Raises:
        ValueError: if pokemon does not exist
        sqlite3.Error: For any other database errors
    """
    response = requests.get(BASE_POKE_URL + "/pokemon/" + name)
    if response.status_code == 200:
        data = response.json()
        stats = Stats(hp=[0, 0], 
                      defense=[0, 0], 
                      attack=[0, 0], 
                      speed=[0, 0], 
                      special_defense=[0, 0], 
                      special_attack=[0, 0]
                      )

        for stat in data['stats']:
            attr_name = stat_map.get(stat['stat']['name'])
            if attr_name:
                setattr(stats, attr_name, [stat['base_stat'], 0])

        global global_id
        pokemon = Pokemon(
            id=global_id,
            game_id=data['id'],
            name=data['name'],
            ability="",
            learned_moves=[],
            stats=stats,
            total_effort=0)
        global_id += 1

        create_pokemon_by_object(pokemon)
        return pokemon.id
    else:
        logger.error("Pokemon does not exist: %s", name)
        raise ValueError("This pokemon does not exist")

def create_pokemon_by_object(pokemon):
    """
    Create a pokemon with an object.
    
    Args:
        pokemon (Pokemon): The Pokemon object.

    Raises:
        sqlite3.Error: For any other database errors
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO pokemon (id, game_id, name, ability, total_effort)
                VALUES (?, ?, ?, ?, ?)
            """, (
                pokemon.id, pokemon.game_id, pokemon.name, 
                pokemon.ability, pokemon.total_effort
            ))

            for move in pokemon.learned_moves:
                cursor.execute("INSERT INTO learned_moves (pokemon_id, move) VALUES (?, ?)", (pokemon.id, move))

            cursor.execute("""
                INSERT INTO stats (
                    pokemon_id, hp_base, hp_effort,
                    attack_base, attack_effort,
                    defense_base, defense_effort,
                    special_attack_base, special_attack_effort,
                    special_defense_base, special_defense_effort,
                    speed_base, speed_effort
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pokemon.id,
                pokemon.stats.hp[0], pokemon.stats.hp[1],
                pokemon.stats.attack[0], pokemon.stats.attack[1],
                pokemon.stats.defense[0], pokemon.stats.defense[1],
                pokemon.stats.special_attack[0], pokemon.stats.special_attack[1],
                pokemon.stats.special_defense[0], pokemon.stats.special_defense[1],
                pokemon.stats.speed[0], pokemon.stats.speed[1]
            ))
            conn.commit()

            logger.info("Pokemon successfully added to the database: %s", pokemon.name)

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e

def get_pokemon_by_id(pokemon_id):
    """
    Retrieves a Pokemon from the catalog by its pokemon_id

    Args:
        pokemon_id (int): The ID of the Pokemon to retrieve

    Returns:
        Pokemon: The Pokemon object corresponding to the pokemon_id

    Raises:
        ValueError: If the Pokemon is not found
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, game_id, name, ability, total_effort
                FROM pokemon WHERE id = ?
            """, (pokemon_id,))
            pokemon_data = cursor.fetchone()
            if not pokemon_data:
                logger.info("Pokemon with ID %s not found", pokemon_id)
                raise ValueError(f"Pokemon with ID {pokemon_id} not found")
            
            # Map to fields
            (
                id, game_id, name, 
                ability, total_effort
            ) = pokemon_data

            # Retrieve learned moves
            cursor.execute("""
                SELECT move FROM learned_moves WHERE pokemon_id = ?
            """, (pokemon_id,))
            learned_moves = [row[0] for row in cursor.fetchall()]

            # Retrieve stats
            cursor.execute("""
                SELECT 
                    hp_base, hp_effort,
                    attack_base, attack_effort,
                    defense_base, defense_effort,
                    special_attack_base, special_attack_effort,
                    special_defense_base, special_defense_effort,
                    speed_base, speed_effort
                FROM stats WHERE pokemon_id = ?
            """, (pokemon_id,))
            stats_data = cursor.fetchone()

            stats = Stats(
                hp=[stats_data[0], stats_data[1]],
                attack=[stats_data[2], stats_data[3]],
                defense=[stats_data[4], stats_data[5]],
                special_attack=[stats_data[6], stats_data[7]],
                special_defense=[stats_data[8], stats_data[9]],
                speed=[stats_data[10], stats_data[11]],
            )

            # Reconstruct the Pokemon object
            pokemon = Pokemon(
                id=id,
                game_id=game_id,
                name=name,
                ability=ability,
                learned_moves=learned_moves,
                stats=stats,
                total_effort=total_effort,
            )
            return pokemon

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e

def add_move_to_pokemon(pokemon_id, move_name):
    """
    Add a move to a Pokemon.
    
    Args:
        pokemon_id (int) : The id of the pokemon.
        move_name (string): The name of the move.

    Raises:
        ValueError: if move does not exist, or already at 4 moves, or already known
        see get_pokemon_by_id
    """
    pokemon = get_pokemon_by_id(pokemon_id)
    response = requests.get(BASE_POKE_URL + "/pokemon/" + pokemon.name)
    data = response.json()
    moves = [move['move']['name'] for move in data['moves']]
    if move_name in pokemon.learned_moves:
        raise ValueError("This pokemon already knows that move")
    if move_name in moves:
        if len(pokemon.learned_moves) < 4:
            try:
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO learned_moves (pokemon_id, move)
                        VALUES (?, ?)
                    """, (pokemon_id, move_name))
                    conn.commit()
            except sqlite3.Error as e:
                logger.error("Database error: %s", str(e))
                raise e
        else:
            raise ValueError("This pokemon already knows 4 moves")
    else:
        raise ValueError(pokemon.name + " cannot learn " + move_name)
    
def remove_move_from_pokemon(pokemon_id, move_name):
    """
    Removes a move from a pokemon
    
    Args:
        pokemon_id (int) : The id of the pokemon.
        move_name (string): The name of the move.

    Raises:
        ValueError: if move does not exist
        see get_pokemon_by_id
    """
    pokemon = get_pokemon_by_id(pokemon_id)

    if move_name in pokemon.learned_moves:
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM learned_moves
                    WHERE pokemon_id = ? AND move = ?
                """, (pokemon_id, move_name))
                conn.commit()
        except sqlite3.Error as e:
            logger.error("Database error: %s", str(e))
            raise e
    else:
        raise ValueError("This pokemon does not know this move")
    
def replace_move_of_pokemon(pokemon, old_move, new_move):
    """
    Replaces a move for a Pokemon object.
    
    Args:
        pokemon (Pokemon) : The pokemon object.
        old_move (string) : The name of the move to replace.
        new_move (string) : The name of the new move.

    Raises:
        ValueError: see remove_move_from_pokemon and add_move_to_pokemon
    """
    remove_move_from_pokemon(pokemon, old_move)
    add_move_to_pokemon(pokemon, new_move)

def distribute_effort_values(pokemon_id, evs):
    """
    Redistributes the effort values of a Pokemon
    Stops if limits are reached

    Args:
        pokemon_id (int) : The pokemon_id.
        evs (List[int]) : values to redistribute
    """
    pokemon = get_pokemon_by_id(pokemon_id)

    effort_values = [0, 0, 0, 0, 0, 0]
    while len(evs) < 6:
        evs.append(0)
    total_effort = 0
    i = 0
    for stat in pokemon.stats.__dict__.items():
        effort_values[i] = stat[1]
        increase = min(evs[i], 255)
        if increase + total_effort > 510:
            effort_values[i] = 510 - total_effort
            total_effort = 510
            break
        else:
            effort_values[i] = increase
            total_effort += increase
        i+=1
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE stats
                SET 
                    hp_effort = ?, 
                    attack_effort = ?, 
                    defense_effort = ?, 
                    special_attack_effort = ?, 
                    special_defense_effort = ?, 
                    speed_effort = ?
                WHERE pokemon_id = ?
            """, (*effort_values, pokemon_id))

            conn.commit()
    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e

def clear_poke() -> None:
    """
    Recreates the pokemon table, effectively deleting all pokemon.

    Raises:
        sqlite3.Error: If any database error occurs.
    """
    try:
        with open(os.getenv("SQL_CREATE_POKE_TABLE_PATH", "/sql/create_poke_table.sql"), "r") as fh:
            create_table_script = fh.read()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.executescript(create_table_script)
            conn.commit()

            global global_id
            global_id = 0
            logger.info("Pokemon cleared successfully.")

    except sqlite3.Error as e:
        logger.error("Database error while clearing meals: %s", str(e))
        raise e