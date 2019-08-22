import sqlalchemy as sa
import sqlalchemy.sql as sasql
from aiomysql.sa import Engine

from ...utils import LocalDateTime
from .common import metadata, Repository


file_table = sa.Table(
    'file', metadata,
    sa.Column("id", sa.Integer, nullable=False, primary_key=True,
              comment='ID'),
    sa.Column('user_id', sa.Integer, nullable=False, comment='上传者 ID'),
    sa.Column('region', sa.VARCHAR(20), nullable=False, comment='区域'),
    sa.Column('bucket', sa.VARCHAR(20), nullable=False, comment='桶'),
    sa.Column('path', sa.VARCHAR(100), nullable=False, comment='路径'),
    sa.Column('meta', sa.JSON, nullable=False, comment='元信息'),
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
    comment='文件',
)


class FileRepo(Repository):
    def __init__(self, db: Engine):
        super().__init__(db, file_table)
