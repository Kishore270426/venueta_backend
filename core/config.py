import os
import secrets

SECRET_KEY = secrets.token_hex(32)

ALGORITHM = os.getenv("ALGORITHM", "HS256")
