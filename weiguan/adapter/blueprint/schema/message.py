from enum import Enum
from uuid import uuid1

from marshmallow import Schema, fields, post_load

from ....entity import Message, NormalMessage, NotifyMessage
from ....util import local_now


class MessageSchema(Schema):
    id = fields.UUID()
    type = fields.String()
    level = fields.String()
    createdAt = fields.DateTime(attribute='created_at')

    @post_load
    def make_object(self, data):
        return Message(**data)


class NormalMessageSchema(MessageSchema):
    content = fields.String()

    @post_load
    def make_object(self, data):
        return NormalMessage(**data)


class NotifyMessageSchema(MessageSchema):
    title = fields.String()
    content = fields.String()

    @post_load
    def make_object(self, data):
        return NotifyMessage(**data)
