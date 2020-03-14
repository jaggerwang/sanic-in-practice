import sqlalchemy as sa
import sqlalchemy.sql as sasql
from aiomysql.sa import Engine

from ...util import LocalDateTime
from .common import metadata, Repository

user_stat_table = sa.Table(
    'user_stat', metadata,
    sa.Column('id', sa.Integer, nullable=False, primary_key=True,
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
    sa.Column('created_at', LocalDateTime, nullable=False,
              server_default=sasql.text('CURRENT_TIMESTAMP'),
              comment='创建时间'),
    sa.Column('updated_at', LocalDateTime, nullable=True,
              server_default=sasql.text(
                  'DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP'),
              comment='更新时间'),
    sa.Index('idx_user_id', 'user_id', unique=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE',
                            onupdate='CASCADE'),
    comment='用户统计',
)


class UserStatRepo(Repository):
    def __init__(self, db: Engine):
        super().__init__(db, user_stat_table)


post_stat_table = sa.Table(
    'post_stat', metadata,
    sa.Column('id', sa.Integer, nullable=False, primary_key=True,
              comment='ID'),
    sa.Column('post_id', sa.Integer, nullable=False, comment='动态 ID'),
    sa.Column('like_count', sa.Integer, nullable=False,
              server_default=sasql.text('0'), comment='被喜欢次数'),
    sa.Column('created_at', LocalDateTime, nullable=False,
              server_default=sasql.text('CURRENT_TIMESTAMP'),
              comment='创建时间'),
    sa.Column('updated_at', LocalDateTime, nullable=True,
              server_default=sasql.text(
                  'DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP'),
              comment='更新时间'),
    sa.Index('idx_post_id', 'post_id', unique=True),
    sa.ForeignKeyConstraint(['post_id'], ['post.id'], ondelete='CASCADE',
                            onupdate='CASCADE'),
    comment='动态统计',
)


class PostStatRepo(Repository):
    def __init__(self, db: Engine):
        super().__init__(db, post_stat_table)
