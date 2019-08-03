NAME = 'weiguan'
# Directory of runtime data, like logs and uploaded files etc
DATA_PATH = '/tmp'
# Subdirectory of uploaded files
UPLOAD_DIR = 'uploads'
# Listen host and port of server
HOST = '0.0.0.0'
PORT = 8000
# Whether in debug mode
DEBUG = True
# Whether to auto load modified code
AUTO_RELOAD = True
# Whether log access record
ACCESS_LOG = True
# Number of working processes
WORKERS = 1
# Valid seconds of session
SESSION_EXPIRY = 30 * 24 * 3600
# Max size of request in bytes
REQUEST_MAX_SIZE = 100 * 1024 * 1024
# Max allowed size of uploaded file in bytes
UPLOAD_FILE_MAX_SIZE = 50 * 1024 * 1024
# Endpoint of uploaded files
UPLOAD_FILE_URL_BASE = 'http://localhost:8000/files/'

# MySQL connection parameters
MYSQL_HOST = 'localhost'
MYSQL_PORT = 3306
MYSQL_DB = 'weiguan_demo'
MYSQL_USER = 'root'
MYSQL_PASSWORD = ''
MYSQL_TIMEOUT = 1
MYSQL_POOL_MIN_SIZE = 1
MYSQL_POOL_MAX_SIZE = 100

# Redis connection parameters
REDIS_URI = 'redis://@localhost:6379/0'
REDIS_TIMEOUT = 1
REDIS_POOL_MIN_SIZE = 1
REDIS_POOL_MAX_SIZE = 100
