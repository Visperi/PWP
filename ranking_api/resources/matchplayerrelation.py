"""
API representation of MatchPlayerRelation
"""
from flask import (
    request,
    Response
)
from flask_restful import Resource

from ranking_api.extensions import db
from ranking_api.models import MatchPlayerRelation, Match

class MatchPlayerRelationItem(Resource):
    """
    Represents a single MatchPlayerRelation resource and its HTTP methods in the api.
    """
    @staticmethod
    def post(match: Match):
        """
        POST Method handler for adding a player to the match.

        :param match: a Match object
        """
        player_name = request.json["player_name"]
        relation = MatchPlayerRelation(
            username=player_name,
            match=match,
            team=0
        )
        db.session.add(relation)
        db.session.commit()
        return Response(status=201)
