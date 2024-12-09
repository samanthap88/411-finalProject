import requests
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class Ability:
    is_hidden: bool
    slot: int
    ability_name: str  # Only storing the name of the ability

@dataclass
class Form:
    name: str

@dataclass
class Move:
    move_name: str  # Only storing the name of the move

@dataclass
class Species:
    name: str

@dataclass
class Pokemon:
    id: int
    name: str
    base_experience: int
    height: int
    order: int
    weight: int
    abilities: List[Ability]
    forms: List[Form]
    moves: List[Move]
    species: Species

BASE_POKE_URL = "https://pokeapi.co/api/v2/"

def get_pokemon_by_name(name):
    """
    Route to get a pokemon by its name.
    
    Path Parameter:
        - name (string): The name of the pokemon.

    Returns:
        JSON response with the pokemon details or error message.
    """
    response = requests.get(BASE_POKE_URL + "/pokemon/" + name)
    if response.status_code == 200:
        data = response.json()  # Parse the JSON response
        abilities = [Ability(is_hidden=ability['is_hidden'], slot=ability['slot'], ability_name=ability['ability']['name']) for ability in data['abilities']]
        forms = [Form(name=form['name']) for form in data['forms']]
        moves = [Move(move_name=move['move']['name']) for move in data['moves']]

        pokemon = Pokemon(
            id=data['id'],
            name=data['name'],
            base_experience=data['base_experience'],
            height=data['height'],
            order=data['order'],
            weight=data['weight'],
            abilities=abilities,
            forms=forms,
            moves=moves,
            species=data['species']['name'])
        
        return pokemon
    else:
        return 0
        

print(get_pokemon_by_name("ditto"))