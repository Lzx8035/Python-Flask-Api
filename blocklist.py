from flask_jwt_extended import get_jwt

BLOCKLIST = set()

def add_to_blocklist():
    jti = get_jwt()["jti"]
    BLOCKLIST.add(jti)

def is_in_blocklist(jti):
    return jti in BLOCKLIST