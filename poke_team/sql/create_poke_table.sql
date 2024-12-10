DROP TABLE IF EXISTS pokemon;
DROP TABLE IF EXISTS learned_moves;
DROP TABLE IF EXISTS stats;

CREATE TABLE pokemon (
    id INTEGER PRIMARY KEY,
    game_id INTEGER,
    name TEXT,
    base_experience INTEGER,
    height INTEGER,
    order INTEGER,
    weight INTEGER,
    ability TEXT,
    species TEXT,
    total_effort INTEGER
);

CREATE TABLE learned_moves (
    pokemon_id INTEGER,
    move TEXT,
    FOREIGN KEY (pokemon_id) REFERENCES pokemon(id)
);

CREATE TABLE stats (
    pokemon_id INTEGER,
    hp_base INTEGER, hp_effort INTEGER,
    attack_base INTEGER, attack_effort INTEGER,
    defense_base INTEGER, defense_effort INTEGER,
    special_attack_base INTEGER, special_attack_effort INTEGER,
    special_defense_base INTEGER, special_defense_effort INTEGER,
    speed_base INTEGER, speed_effort INTEGER,
    FOREIGN KEY (pokemon_id) REFERENCES pokemon(id)
);
