import requests
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class Ability:
    is_hidden: bool
    slot: int
    ability_name: str

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
    name: str
    base_experience: int
    height: int
    order: int
    weight: int
    abilities: List[Ability]
    forms: List[str]
    learned_moves: List[str]
    species: str
    stats: Stats
    total_effort: int

BASE_POKE_URL = "https://pokeapi.co/api/v2/"

stat_map = {
    'hp': 'hp',
    'attack': 'attack',
    'defense': 'defense',
    'special-attack': 'special_attack',
    'special-defense': 'special_defense',
    'speed': 'speed'
}

global_id = 0

def get_pokemon_by_name(name):
    """
    Get a pokemon by its name.
    
    Args:
        name (string): The name of the pokemon.

    Returns:
        New Pokemon object, with no learned moves

    Raises:
        ValueError: if pokemon does not exist
    """
    response = requests.get(BASE_POKE_URL + "/pokemon/" + name)
    if response.status_code == 200:
        data = response.json()  # Parse the JSON response
        # print(data)
        abilities = [Ability(is_hidden=ability['is_hidden'], 
                             slot=ability['slot'], 
                             ability_name=ability['ability']['name']) 
                             for ability in data['abilities']]
        forms = [form['name'] for form in data['forms']]
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

        pokemon = Pokemon(
            id=data['id'],
            name=data['name'],
            base_experience=data['base_experience'],
            height=data['height'],
            order=data['order'],
            weight=data['weight'],
            abilities=abilities,
            forms=forms,
            learned_moves=[],
            species=data['species']['name'],
            stats=stats,
            total_effort=0)
        return pokemon
    else:
        raise ValueError("This pokemone does not exist")
    
def add_move_to_pokemon(pokemon, move_name):
    """
    Add a move to a Pokemon object.
    
    Args:
        pokemon (Pokemon) : The pokemon object.
        move_name (string): The name of the move.

    Raises:
        ValueError: if move does not exist, or already at 4 moves
    """
    response = requests.get(BASE_POKE_URL + "/pokemon/" + pokemon.name)
    data = response.json()  # Parse the JSON response
    moves = [move['move']['name'] for move in data['moves']]
    if move_name in moves:
        if len(pokemon.learned_moves) < 4:
            pokemon.learned_moves.append(move_name)
        else:
            raise ValueError("This pokemon already knows 4 moves")
    else:
        raise ValueError("This pokemon cannot learn this move")
    
def remove_move_from_pokemon(pokemon, move_name):
    """
    Removes a move from a Pokemon object.
    
    Args:
        pokemon (Pokemon) : The pokemon object.
        move_name (string): The name of the move.

    Raises:
        ValueError: if move does not exist
    """
    if move_name in pokemon.learned_moves:
        pokemon.learned_moves.remove(move_name)
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

def distribute_effort_values(pokemon, evs):
    """
    Redistributes the effort values of a Pokemon object
    Stops if limits are reached

    Args:
        pokemon (Pokemon) : The pokemon object.
        evs (List[int]) : values to redistribute
    """
    while len(evs) < 6:
        evs.append(0)
    pokemon.total_effort = 0
    i = 0
    for stat in pokemon.stats.__dict__.items():
        stat = stat[1]
        increase = min(evs[i], 255)
        if increase + pokemon.total_effort > 510:
            stat[1] = 510 - pokemon.total_effort
            pokemon.total_effort = 510
            return
        else:
            stat[1] = increase
            pokemon.total_effort += increase
        i+=1


p = get_pokemon_by_name("blaziken")
# print(p)
add_move_to_pokemon(p, "fire-punch")
print(p)
remove_move_from_pokemon(p, "fire-punch")
print(p)
distribute_effort_values(p, [4])
distribute_effort_values(p, [4, 4, 4, 4, 4, 4])
distribute_effort_values(p, [1000, 1000])
print(p)