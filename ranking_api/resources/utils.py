from werkzeug.exceptions import BadRequest


def str_to_bool(value: str):
    casefold = value.casefold()

    if casefold == "true":
        return True
    elif casefold == "false":
        return False
    else:
        raise BadRequest(description="Bad query parameter")
