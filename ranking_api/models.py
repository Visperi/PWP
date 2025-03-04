"""
Model definitions for the api database
"""
from .extensions import db
from .resources.utils import ts_to_datetime


class Player(db.Model):
    """
    Player database model class
    """
    __tablename__ = "players"
    username = db.Column(db.String(32), primary_key=True, nullable=False, unique=True)
    num_of_matches = db.Column(db.Integer, default=0, nullable=False)
    rating = db.Column(db.Integer, default=1000, nullable=False)
    matches = db.relationship("MatchPlayerRelation", back_populates="player", lazy='select')

    @staticmethod
    def json_schema() -> dict:
        """
        JSON schema for player model
        """
        schema = {
            "type": "object",
            "required": ["username"]
        }
        properties = {
            "username": {
                "description": "The users' name",
                "type": "string",
                "minLength": 1,
                "maxLength": 32
            },
            "num_of_matches": {
                "description": "Number of played matches",
                "type": "integer",
                "minimum": 0
            },
            "rating": {
                "description": "Current rating of the player",
                "type": "integer",
                "minimum": 0
            }}

        schema.update(properties=properties)
        return schema

    def deserialize(self, data: dict):
        """
        Deserialization method for user data
        """
        self.username = data["username"]
        self.num_of_matches = data.get("num_of_matches", 0)
        self.rating = data.get("rating", 1000)

    def serialize(self, include_matches: bool = True) -> dict:
        """
        Serialization method for user data

        :return: User data serialized
        """
        ret = {"username": self.username,
               "num_of_matches": self.num_of_matches,
               "rating": self.rating}

        if include_matches:
            ret.update(matches=[match.serialize_match() for match in self.matches])

        return ret


class Match(db.Model):
    """
    Match database model class
    """
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

    @staticmethod
    def json_schema() -> dict:
        """
        JSON schema for match model
        """
        schema = {
            "type": "object",
            "required": ["location", "time"]
        }
        properties = {
            "location": {
                "description": "Physical location of the game",
                "type": "string",
                "minLength": 1,
                "maxLength": 50
            },
            "time": {
                "description": "UTC timestamp for the game starting time",
                "type": "string",
                "format": "date-time"
            },
            "description": {
                "description": "Optional description, e.g. hashtag for the game",
                "type": "string",
                "maxLength": 100
            },
            "status": {
                "description": "On-going status of the game",
                "type": "integer",
                "minimum": 0,
                "maximum": 2
            },
            "rating_shift": {
                "description": "Rating shift for the teams after finishing the game. \
                                Negative for losing team.",
                "anyOf": [
                    {"type": "null"},
                    {"type": "integer", "minimum": 0}
                ]
            },
            "team1_score": {
                "description": "Team 1 score in the game",
                "type": "integer",
                "minimum": 0
            },
            "team2_score": {
                "description": "Team 2 score in the game",
                "type": "integer",
                "minimum": 0
            }
        }

        schema.update(properties=properties)
        return schema

    def deserialize(self, data):
        """
        Deserialization method for match data
        """
        self.location = data.get('location')
        self.time = ts_to_datetime(data.get('time'))  # Convert to datetime or raise BadRequest
        self.description = data.get('description')
        self.status = data.get('status')
        self.rating_shift = data.get('rating_shift')
        self.team1_score = data.get('team1_score')
        self.team2_score = data.get('team2_score')

    def serialize(self, include_players: bool = True) -> dict:
        """
        Serialization method for match data

        :return: Match data serialized
        """
        ret = {"id": self.id,
               "location": self.location,
               "timestamp": str(self.time),
               "description": self.description,
               "status": self.status,
               "rating_shift": self.rating_shift,
               "team1_score": self.team1_score,
               "team2_score": self.team2_score}

        if include_players:
            ret.update(players=[player.serialize_player() for player in self.players])

        return ret


class MatchPlayerRelation(db.Model):
    """
    Relation object model for junction table meant to
    handle the player/match many-to-many relationship
    """
    __tablename__ = "match_player_relation"
    username = db.Column(db.String(32),
                         db.ForeignKey("players.username", ondelete='CASCADE'),
                         nullable=False,
                         primary_key=True)
    match_id = db.Column(db.Integer,
                         db.ForeignKey("matches.id", ondelete='CASCADE'),
                         nullable=False,
                         primary_key=True)
    team = db.Column(db.Integer, nullable=False)

    player = db.relationship("Player", back_populates="matches")
    match = db.relationship("Match", back_populates="players")

    def serialize_match(self) -> dict:
        """
        Serialize relation data from players perspective and combine it with team satellite data.

        :return: Match data serialized and combined with team data.
        """

        match_data = self.match.serialize(include_players=False)
        match_data.update(team=self.team)
        return match_data

    def serialize_player(self) -> dict:
        """
        Serialize relation data from matches perspective and combine it with team satellite data.

        :return: Player data serialized and combined with team data.
        """

        player_data = self.player.serialize(include_matches=False)
        player_data.update(team=self.team)
        return player_data
