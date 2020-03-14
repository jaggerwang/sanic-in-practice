from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.Integer()
    username = fields.String()
    mobile = fields.String()
    email = fields.String()
    avatarId = fields.Integer(attribute='avatar_id')
    intro = fields.String()
    createdAt = fields.DateTime(attribute='created_at')
    updatedAt = fields.DateTime(attribute='updated_at')

    avatar = fields.Nested('FileSchema')
