from enum import Enum
import os

from marshmallow import Schema, fields, post_dump

from ..config import config


class StorageRegion(Enum):
    LOCAL = 'local'


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
            'huge': '',
        }
        if data['region'] == StorageRegion.LOCAL.value:
            url = '{}{}'.format(config['UPLOAD_FILE_URL_BASE'],
                                os.path.join(data['bucket'], data['path']))
            if data['meta']['type'].startswith('image/'):
                thumbs = {
                    'small': '{}?process={}'.format(url, 'thumb-small'),
                    'middle': '{}?process={}'.format(url, 'thumb-middle'),
                    'large': '{}?process={}'.format(url, 'thumb-large'),
                    'huge': '{}?process={}'.format(url, 'thumb-huge'),
                }

        return dict(data, url=url, thumbs=thumbs)
