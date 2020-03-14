from enum import Enum
from uuid import uuid1

from ..util import local_now


class MessageType(Enum):
    NORMAL = 'NORMAL'
    NOTIFY = 'NOTIFY'


class MessageLevel(Enum):
    INFO = 'INFO'
    SUCCESS = 'SUCCESS'
    ERROR = 'ERROR'


class Message:
    def __init__(self, type, level):
        self.id = uuid1()
        self.type = type
        self.level = level
        self.created_at = local_now()


class NormalMessage(Message):
    def __init__(self, content, level=MessageLevel.INFO.value):
        super().__init__(MessageType.NORMAL.value, level)

        self.content = content


class NotifyMessage(Message):
    def __init__(self, title, content, level=MessageLevel.INFO.value):
        super().__init__(MessageType.NOTIFY.value, level)

        self.title = title
        self.content = content
