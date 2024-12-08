from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    favorites = db.relationship("Favorite", backref="user", lazy=True)
    teams = db.relationship("Team", backref="user", lazy=True)
