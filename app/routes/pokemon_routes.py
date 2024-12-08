from flask import Blueprint, jsonify, request
from app.services.pokeapi_service import fetch_pokemon

bp = Blueprint("pokemon", __name__)

@bp.route("/<int:pokemon_id>", methods=["GET"])
def get_pokemon(pokemon_id):
    data = fetch_pokemon(pokemon_id)
    if not data:
        return jsonify({"error": "Pokémon not found"}), 404
    return jsonify(data)
