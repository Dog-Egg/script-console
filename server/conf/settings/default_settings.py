import os
import secrets

from .typing import readonly

DEBUG: bool = False

SCRIPTS_DIR = os.path.join(os.getcwd(), 'scripts')

DATA_DIR = os.path.join(os.getcwd(), 'data')

COOKIE_SECRET = secrets.token_hex()

ADMINISTRATOR: readonly = 'admin'
