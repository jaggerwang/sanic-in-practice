from marshmallow import Schema, fields


class UserStatSchema(Schema):
    id = fields.Integer()
    userId = fields.Integer(attribute='user_id')
    postCount = fields.Integer(attribute='post_count')
    likeCount = fields.Integer(attribute='like_count')
    followingCount = fields.Integer(attribute='following_count')
    followerCount = fields.Integer(attribute='follower_count')
    createdAt = fields.DateTime(attribute='created_at')
    updatedAt = fields.DateTime(attribute='updated_at')

    user = fields.Nested('UserSchema')


class PostStatSchema(Schema):
    id = fields.Integer()
    postId = fields.Integer(attribute='post_id')
    likeCount = fields.Integer(attribute='like_count')
    createdAt = fields.DateTime(attribute='created_at')
    updatedAt = fields.DateTime(attribute='updated_at')

    post = fields.Nested('PostSchema')
