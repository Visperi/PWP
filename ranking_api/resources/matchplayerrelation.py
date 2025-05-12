"""
API representation of MatchPlayerRelation
"""
from flask import (
    request,
    Response
)
from werkzeug.exceptions import BadRequest, NotFound

from flask_restful import Resource

from ranking_api.extensions import db
from ranking_api.models import MatchPlayerRelation, Match, Player

class MatchPlayerRelationJoin(Resource):
    """
    Represents the game join resource and its HTTP methods in the api.
    """
    @staticmethod
    def post(match: Match):
        """
        POST Method handler for adding a player to the match.

        :param match: a Match object
        """
        player_name = request.json["player_name"]
        if not player_name:
            raise BadRequest
        relation = MatchPlayerRelation(
            username=player_name,
            match=match,
            team=0
        )
        db.session.add(relation)
        db.session.commit()
        return Response(status=201)

class MatchPlayerRelationItem(Resource):
    """
    Represents a single MatchPlayerRelationItem in the api.
    """
    @staticmethod
    def put(match: Match, player: Player):
        """
        PUT method handler to updating a relation object (change team)
        """
        new_team = int(request.json["team"])
        if not new_team or new_team not in range(3):
            raise BadRequest
        relation = db.session.get(
            MatchPlayerRelation,
            {"match_id": match.id, "username": player.username}
            )
        if not relation:
            raise NotFound
        relation.team = new_team
        db.session.commit()
        return Response(status=200)
