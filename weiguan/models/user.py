import sqlalchemy as sa
import sqlalchemy.sql as sasql
from marshmallow import Schema, fields

from ..utils import LocalDateTime
from .common import metadata

UserModel = sa.Table(
    'user', metadata,
    sa.Column('id', sa.Integer, nullable=False, primary_key=True,
              comment='ID'),
    sa.Column('username', sa.VARCHAR(20), nullable=False, comment='用户名'),
    sa.Column('password', sa.CHAR(64), nullable=False, comment='已加密的密码'),
    sa.Column('salt', sa.CHAR(64), nullable=False, comment='密钥'),
    sa.Column('mobile', sa.CHAR(11), nullable=True, comment='手机号'),
    sa.Column('email', sa.VARCHAR(50), nullable=True, comment='邮箱'),
    sa.Column('avatar_id', sa.Integer, nullable=True, comment='头像文件 ID'),
    sa.Column('intro', sa.VARCHAR(100), nullable=False, server_default='',
              comment='自我介绍'),
    sa.Column('created_at', LocalDateTime, nullable=False,
              server_default=sasql.text('CURRENT_TIMESTAMP'),
              comment='创建时间'),
    sa.Column('updated_at', LocalDateTime, nullable=False,
              server_default=sasql.text(
                  'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
              comment='更新时间'),
    sa.Index('idx_username', 'username', unique=True),
    sa.Index('idx_mobile', 'mobile', unique=True),
    sa.ForeignKeyConstraint(['avatar_id'], ['file.id'], ondelete='SET NULL',
                            onupdate='CASCADE'),
    comment='用户',
)


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
    stat = fields.Nested('UserStatSchema')


UserFollowModel = sa.Table(
    'user_follow', metadata,
    sa.Column("id", sa.Integer, nullable=False, primary_key=True,
              comment='ID'),
    sa.Column('following_id', sa.Integer, nullable=False, comment='被关注用户 ID'),
    sa.Column('follower_id', sa.Integer, nullable=False, comment='粉丝用户 ID'),
    sa.Column("created_at", LocalDateTime, nullable=False,
              server_default=sasql.text('CURRENT_TIMESTAMP'),
              comment='创建时间'),
    sa.Column("updated_at", LocalDateTime, nullable=False,
              server_default=sasql.text(
                  'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
              comment='更新时间'),
    sa.Index('idx_follower_id_following_id', 'follower_id', 'following_id',
             unique=True),
    sa.Index('idx_follower_id_created_at', 'follower_id', 'created_at'),
    sa.Index('idx_following_id_created_at', 'following_id', 'created_at'),
    sa.ForeignKeyConstraint(['following_id'], ['user.id'], ondelete='CASCADE',
                            onupdate='CASCADE'),
    sa.ForeignKeyConstraint(['follower_id'], ['user.id'], ondelete='CASCADE',
                            onupdate='CASCADE'),
    comment='用户关注',
)
