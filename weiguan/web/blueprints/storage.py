import os

from sanic import Blueprint
from sanic.exceptions import NotFound
import aiofiles

from ...utils import random_string
from ...container import Container
from ...entities import StorageRegion, FileSchema
from .common import response_json, ResponseCode, authenticated

storage = Blueprint('storage', url_prefix='/storage')


@storage.post('/upload')
@authenticated()
async def upload(request):
    user_id = request['session']['user']['id']
    config = Container().config

    region = request.form.get('region') or StorageRegion.LOCAL.value
    bucket = request.form.get('bucket', '')
    path = request.form.get('path', '')
    files = request.files.getlist('files', [])

    if len(files) > config['UPLOAD_FILE_MAX_NUMBER']:
        return response_json(
            ResponseCode.FAIL,
            '文件数不能超过 {} 个'.format(config['UPLOAD_FILE_MAX_NUMBER']))

    saved_files = []
    storage_service = Container().storage_service
    for file in files:
        meta = {
            'name': file.name,
            'type': file.type,
            'size': len(file.body),
        }
        if meta['size'] > config['UPLOAD_FILE_MAX_SIZE']:
            return response_json(
                ResponseCode.FAIL, '文件 {} 大小超过上限'.format(meta['name']))

        _, ext = os.path.splitext(meta['name'])
        filename = '{}{}'.format(random_string(16), ext)

        if region == StorageRegion.LOCAL.value:
            save_dir = os.path.join(
                config['DATA_PATH'], config['UPLOAD_DIR'], bucket, path)
            os.makedirs(save_dir, 0o755, True)

            async with aiofiles.open(
                    os.path.join(save_dir, filename), 'wb') as f:
                await f.write(file.body)

            saved_file = await storage_service.create_file(
                user_id=user_id, region=region, bucket=bucket,
                path=os.path.join(path, filename), meta=meta)

            saved_files.append(saved_file)
        else:
            return response_json(ResponseCode.FAIL, '暂不支持该区域')

    return response_json(
        files=[FileSchema().dump(v) for v in saved_files])


@storage.get('/file/info')
@authenticated()
async def file_info(request):
    id = request.args.get('id')
    if id is not None:
        id = int(id)

    storage_service = Container().storage_service
    file = await storage_service.file_info(id)
    if file is None:
        raise NotFound('')

    return response_json(file=FileSchema().dump(file))
