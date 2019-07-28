from enum import Enum

import sqlalchemy as sa
import sqlalchemy.sql as sasql
from marshmallow import Schema, fields

from .common import metadata, LocalDateTime


class PostType(Enum):
    TEXT = 'text'
    IMAGE = 'image'
    VIDEO = 'video'


PostModel = sa.Table(
    'post', metadata,
    sa.Column("id", sa.Integer, nullable=False, primary_key=True,
              comment='ID'),
    sa.Column('user_id', sa.Integer, nullable=False, comment='发布者 ID'),
    sa.Column('type', sa.VARCHAR(20), nullable=False, comment='类型'),
    sa.Column('text', sa.VARCHAR(100), nullable=False, server_default='',
              comment='文本内容'),
    sa.Column('image_ids', sa.JSON, nullable=True, comment='图片文件 ID 列表'),
    sa.Column('video_id', sa.Integer, nullable=True, comment='视频文件 ID'),
    sa.Column("created_at", LocalDateTime, nullable=False,
              server_default=sasql.text('CURRENT_TIMESTAMP'),
              comment='创建时间'),
    sa.Column("updated_at", LocalDateTime, nullable=False,
              server_default=sasql.text(
                  'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
              comment='更新时间'),
    sa.Index('idx_user_id', 'user_id'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE',
                            onupdate='CASCADE'),
    sa.ForeignKeyConstraint(['video_id'], ['file.id'], ondelete='CASCADE',
                            onupdate='CASCADE'),
    comment='动态',
)


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


PostLikeModel = sa.Table(
    'post_like', metadata,
    sa.Column("id", sa.Integer, nullable=False, primary_key=True,
              comment='ID'),
    sa.Column('post_id', sa.Integer, nullable=False, comment='动态 ID'),
    sa.Column('user_id', sa.Integer, nullable=False, comment='点赞用户 ID'),
    sa.Column("created_at", LocalDateTime, nullable=False,
              server_default=sasql.text('CURRENT_TIMESTAMP'),
              comment='创建时间'),
    sa.Column("updated_at", LocalDateTime, nullable=False,
              server_default=sasql.text(
                  'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
              comment='更新时间'),
    sa.Index('idx_user_id_post_id', 'user_id', 'post_id', unique=True),
    sa.Index('idx_post_id_created_at', 'post_id', 'created_at'),
    sa.Index('idx_user_id_created_at', 'user_id', 'created_at'),
    sa.ForeignKeyConstraint(['post_id'], ['post.id'], ondelete='CASCADE',
                            onupdate='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE',
                            onupdate='CASCADE'),
    comment='动态点赞',
)
