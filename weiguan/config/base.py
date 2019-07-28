NAME = 'weiguan'
# 运行时数据保存路径，比如日志、上传文件等
DATA_PATH = '/tmp'
# 上传文件子目录
UPLOAD_DIR = 'uploads'
# 服务监听地址和端口
HOST = '0.0.0.0'
PORT = 8000
# 是否为调试模式
DEBUG = True
# 是否热加载代码
AUTO_RELOAD = True
# 是否记录访问日志
ACCESS_LOG = True
# 工作进程数
WORKERS = 1
# 会话有效期
SESSION_EXPIRY = 30 * 24 * 3600
# 请求体大小限制
REQUEST_MAX_SIZE = 100 * 1024 * 1024
# 上传文件大小限制
UPLOAD_FILE_MAX_SIZE = 50 * 1024 * 1024
# 上传文件访问域名
UPLOAD_FILE_URL_BASE = 'http://localhost:8000/files/'

# MySQL连接信息
MYSQL_HOST = 'localhost'
MYSQL_PORT = 3306
MYSQL_DB = 'weiguan_demo'
MYSQL_USER = 'root'
MYSQL_PASSWORD = ''
MYSQL_TIMEOUT = 1
MYSQL_POOL_MIN_SIZE = 1
MYSQL_POOL_MAX_SIZE = 100

# Redis连接信息
REDIS_URI = 'redis://@localhost:6379/0'
REDIS_TIMEOUT = 1
REDIS_POOL_MIN_SIZE = 1
REDIS_POOL_MAX_SIZE = 100
