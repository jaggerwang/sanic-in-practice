from enum import Enum
from uuid import uuid1

from marshmallow import Schema, fields, post_load

from ..utils import local_now


class MessageType(Enum):
    NORMAL = 'normal'
    NOTIFY = 'notify'


class MessageLevel(Enum):
    INFO = 'info'
    SUCCESS = 'success'
    ERROR = 'error'


class Message:
    def __init__(self, type, level):
        self.id = uuid1()
        self.type = type
        self.level = level
        self.created_at = local_now()


class MessageSchema(Schema):
    id = fields.UUID()
    type = fields.String()
    level = fields.String()
    createdAt = fields.DateTime(attribute='created_at')

    @post_load
    def make_object(self, data):
        return Message(**data)


class NormalMessage(Message):
    def __init__(self, content, level=MessageLevel.INFO.value):
        super().__init__(MessageType.NORMAL.value, level)

        self.content = content


class NormalMessageSchema(MessageSchema):
    content = fields.String()

    @post_load
    def make_object(self, data):
        return NormalMessage(**data)


class NotifyMessage(Message):
    def __init__(self, title, content, level=MessageLevel.INFO.value):
        super().__init__(MessageType.NOTIFY.value, level)

        self.title = title
        self.content = content


class NotifyMessageSchema(MessageSchema):
    title = fields.String()
    content = fields.String()

    @post_load
    def make_object(self, data):
        return NotifyMessage(**data)
