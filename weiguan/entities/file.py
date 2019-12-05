from enum import Enum
import os

from marshmallow import Schema, fields, post_dump

from ..config import config


class FileRegion(Enum):
    LOCAL = 'LOCAL'


class FileThumbType(Enum):
    SMALL = 'SMALL'
    MIDDLE = 'MIDDLE'
    LARGE = 'LARGE'
    HUGE = 'HUGE'


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
            FileThumbType.SMALL: '',
            FileThumbType.MIDDLE: '',
            FileThumbType.LARGE: '',
            FileThumbType.HUGE: '',
        }
        if data['region'] == FileRegion.LOCAL.value:
            url = '{}{}'.format(config['UPLOAD_FILE_URL_BASE'],
                                os.path.join(data['bucket'], data['path']))
            if data['meta']['type'].startswith('image/'):
                thumbs = {
                    FileThumbType.SMALL: '{}?process={}'.format(url, 'thumb-small'),
                    FileThumbType.MIDDLE: '{}?process={}'.format(url, 'thumb-middle'),
                    FileThumbType.LARGE: '{}?process={}'.format(url, 'thumb-large'),
                    FileThumbType.HUGE: '{}?process={}'.format(url, 'thumb-huge'),
                }

        return dict(data, url=url, thumbs=thumbs)
