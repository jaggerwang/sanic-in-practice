from enum import Enum
import os

import sqlalchemy as sa
import sqlalchemy.sql as sasql
from marshmallow import Schema, fields, post_dump

from ..config import config
from .common import metadata, LocalDateTime


class StorageRegion(Enum):
    LOCAL = 'local'


FileModel = sa.Table(
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


class FileSchema(Schema):
    id = fields.Integer()
    userId = fields.Integer(attribute='user_id')
    region = fields.String()
    bucket = fields.String()
    path = fields.String()
    meta = fields.Dict()
    createdAt = fields.DateTime(attribute='created_at')
    updatedAt = fields.DateTime(attribute='updated_at')

    user = fields.Nested('UserSchema')

    @post_dump
    def add_url(self, data, many):
        url = ''
        thumbs = {
            'small': '',
            'middle': '',
            'large': '',
        }
        if data['region'] == StorageRegion.LOCAL.value:
            url = '{}{}'.format(config['UPLOAD_FILE_URL_BASE'],
                                os.path.join(data['bucket'], data['path']))
            if data['meta']['type'].startswith('image/'):
                thumbs = {
                    'small': '{}?process={}'.format(url, 'thumb-small'),
                    'middle': '{}?process={}'.format(url, 'thumb-middle'),
                    'large': '{}?process={}'.format(url, 'thumb-large'),
                }

        return dict(data, url=url, thumbs=thumbs)
