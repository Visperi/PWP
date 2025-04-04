"""
Module for populating the database
"""

import string
import random
from datetime import datetime, timezone, timedelta

from wsgi import create_app
from ranking_api.extensions import db
from ranking_api.models import (
    Player,
    Match,
    MatchPlayerRelation,
    Season
)


def _generate_string(length: int, allow_upper: bool = True) -> str:
    """
    Generate a random string.

    :param length: Length of the string.
    :param allow_upper: Allow uppercase characters in the generated string.
    :return: A random generated string.
    """

    chars = string.ascii_lowercase
    if allow_upper:
        chars += string.ascii_uppercase

    return "".join(random.choices(chars, k=length))


def generate_player() -> Player:
    """
    Generate a player with random attributes.

    :return: Random player model object.
    """
    username = _generate_string(32)
    num_of_matches = random.randint(0, 50)
    rating = random.randint(1000, 3000)

    return Player(username=username, num_of_matches=num_of_matches, rating=rating)


def generate_match() -> Match:
    """
    Generate a match with players.

    :return: A match model object.
    """
    location = _generate_string(50)
    time = datetime.now(timezone.utc)
    description = random.choice([None, _generate_string(100)])
    status = random.randint(0, 2)
    season_id = 1
    rating_shift = random.randint(1, 50)
    team1_score = random.randint(0, 16)
    team2_score = random.randint(0, 16)

    return Match(location=location,
                 time=time,
                 description=description,
                 status=status,
                 season_id=season_id,
                 rating_shift=rating_shift,
                 team1_score=team1_score,
                 team2_score=team2_score)

def generate_season() -> Season:
    """
    Generate a season.

    :return: A Season model object.
    """
    starting_date = datetime.now()
    end_date = datetime.now() + timedelta(days=365)

    return Season(starting_date=starting_date,
                  end_date=end_date)

if __name__ == "__main__":
    NUM_SEASONS = 1
    NUM_MATCHES = 8
    NUM_PLAYERS = 20
    TEAM_SIZE = 3

    if NUM_PLAYERS < TEAM_SIZE * 2:
        raise ValueError(f"There must be at least {TEAM_SIZE * 2} amount of unique players "
                         f"to generate dummy data for "
                         f"teams of size {TEAM_SIZE}")

    app = create_app()
    seasons = [generate_season() for _ in range(NUM_SEASONS)]
    matches = [generate_match() for _ in range(NUM_MATCHES)]
    all_players = [generate_player() for _ in range(NUM_PLAYERS)]
    with app.app_context():
        for season in seasons:
            db.session.add(season)
        db.session.commit()
        for match in matches:
            team1 = []
            team2 = []

            for player in random.sample(all_players, k=TEAM_SIZE*2):
                # Fill teams randomly but evenly
                if len(team1) != 3 and len(team2) != 3:
                    team = random.randint(1, 2)
                elif len(team1) == 3:
                    team = 1 # pylint: disable=invalid-name
                else:
                    team = 2 # pylint: disable=invalid-name

                if team == 1:
                    team1.append(player)
                else:
                    team2.append(player)

                player.num_of_matches += 1
                relation = MatchPlayerRelation(team=team)
                relation.player = player
                match.players.append(relation)
            db.session.add(match)

        db.session.commit()
