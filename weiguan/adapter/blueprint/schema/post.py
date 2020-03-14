from enum import Enum

from marshmallow import Schema, fields


class PostSchema(Schema):
    id = fields.Integer()
    userId = fields.Integer(attribute='user_id')
    type = fields.String()
    text = fields.String()
    imageIds = fields.List(fields.Integer, attribute='image_ids')
    videoId = fields.Integer(attribute='video_id')
    createdAt = fields.DateTime(attribute='created_at')
    updatedAt = fields.DateTime(attribute='updated_at')

    user = fields.Nested('UserSchema')
    images = fields.Nested('FileSchema', many=True)
    video = fields.Nested('FileSchema')
