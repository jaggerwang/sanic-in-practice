from enum import Enum

import sqlalchemy as sa
import sqlalchemy.sql as sasql
from marshmallow import Schema, fields

from ..utils import LocalDateTime
from .common import metadata

UserStatModel = sa.Table(
    'user_stat', metadata,
    sa.Column("id", sa.Integer, nullable=False, primary_key=True,
              comment='ID'),
    sa.Column('user_id', sa.Integer, nullable=False, comment='用户 ID'),
    sa.Column('post_count', sa.Integer, nullable=False,
              server_default=sasql.text('0'), comment='发布动态数'),
    sa.Column('like_count', sa.Integer, nullable=False,
              server_default=sasql.text('0'), comment='喜欢动态数'),
    sa.Column('following_count', sa.Integer, nullable=False,
              server_default=sasql.text('0'), comment='关注人数'),
    sa.Column('follower_count', sa.Integer, nullable=False,
              server_default=sasql.text('0'), comment='粉丝人数'),
    sa.Column("created_at", LocalDateTime, nullable=False,
              server_default=sasql.text('CURRENT_TIMESTAMP'),
              comment='创建时间'),
    sa.Column("updated_at", LocalDateTime, nullable=False,
              server_default=sasql.text(
                  'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
              comment='更新时间'),
    sa.Index('idx_user_id', 'user_id', unique=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE',
                            onupdate='CASCADE'),
    comment='用户统计',
)


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


PostStatModel = sa.Table(
    'post_stat', metadata,
    sa.Column("id", sa.Integer, nullable=False, primary_key=True,
              comment='ID'),
    sa.Column('post_id', sa.Integer, nullable=False, comment='动态 ID'),
    sa.Column('like_count', sa.Integer, nullable=False,
              server_default=sasql.text('0'), comment='被喜欢次数'),
    sa.Column("created_at", LocalDateTime, nullable=False,
              server_default=sasql.text('CURRENT_TIMESTAMP'),
              comment='创建时间'),
    sa.Column("updated_at", LocalDateTime, nullable=False,
              server_default=sasql.text(
                  'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
              comment='更新时间'),
    sa.Index('idx_post_id', 'post_id', unique=True),
    sa.ForeignKeyConstraint(['post_id'], ['post.id'], ondelete='CASCADE',
                            onupdate='CASCADE'),
    comment='动态统计',
)


class PostStatSchema(Schema):
    id = fields.Integer()
    postId = fields.Integer(attribute='post_id')
    likeCount = fields.Integer(attribute='like_count')
    createdAt = fields.DateTime(attribute='created_at')
    updatedAt = fields.DateTime(attribute='updated_at')

    post = fields.Nested('PostSchema')
