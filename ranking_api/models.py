from ranking_api.extensions import db


class Player(db.Model):
    __tablename__ = "players"
    username = db.Column(db.String(32), primary_key=True, nullable=False, unique=True)
    num_of_matches = db.Column(db.Integer, default=0, nullable=False)
    rating = db.Column(db.Integer, default=1000, nullable=False)
    matches = db.relationship("MatchPlayerRelation", back_populates="player", lazy='select')

    @staticmethod
    def json_schema() -> dict:
        schema = {
            "type": "object"
        }
        properties = {}

        schema.update(properties=properties)
        return schema


class Match(db.Model):
    __tablename__ = "matches"
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    location = db.Column(db.String(50), nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.String(100))
    status = db.Column(db.Integer, default=0, nullable=False)
    rating_shift = db.Column(db.Integer)
    team1_score = db.Column(db.Integer, default=0)
    team2_score = db.Column(db.Integer, default=0)
    players = db.relationship('MatchPlayerRelation', back_populates='match', lazy='select')


class MatchPlayerRelation(db.Model):
    __tablename__ = "match_player_relation"
    username = db.Column(db.String(32), db.ForeignKey("players.username", ondelete='CASCADE'), nullable=False,
                         primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey("matches.id", ondelete='CASCADE'), nullable=False, primary_key=True)
    team = db.Column(db.Integer, nullable=False)

    player = db.relationship("Player", back_populates="matches")
    match = db.relationship("Match", back_populates="players")
