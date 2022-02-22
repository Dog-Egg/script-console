import os

SCRIPTS_DIR = os.getenv('SC_SCRIPTS_DIR') or os.path.join(os.path.dirname(__file__), 'scripts')

CONFIG_FILENAME = '.sc-conf.yaml'

ADMINISTRATOR = 'admin'
