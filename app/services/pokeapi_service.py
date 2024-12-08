import requests

POKEAPI_BASE_URL = "https://pokeapi.co/api/v2/pokemon"

def fetch_pokemon(pokemon_id):
    response = requests.get(f"{POKEAPI_BASE_URL}/{pokemon_id}")
    if response.status_code != 200:
        return None
    return response.json()
