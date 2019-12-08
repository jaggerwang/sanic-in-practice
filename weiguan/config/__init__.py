from sanic.config import Config

from . import base as base_config
from .log import get_log_config

config = Config(load_env=False)
config.from_object(base_config)
config.load_environment_vars('SIP_')

log_config = get_log_config(config)
