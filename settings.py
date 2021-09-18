import os

SCRIPTS_DIR = os.getenv('SC_SCRIPTS_DIR') or os.path.join(os.path.dirname(__file__), 'scripts')

CONFIG_FILENAME = '.sc.conf'
CONFIG_FILE_PATH = os.path.join(SCRIPTS_DIR, CONFIG_FILENAME)

IGNORE_FILENAME = '.scignore'
IGNORE_FILE_PATH = os.path.join(SCRIPTS_DIR, IGNORE_FILENAME)

ADMINISTRATOR = 'admin'
