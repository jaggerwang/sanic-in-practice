import os

from sanic import Blueprint
import aiofiles

from ...utils import random_string
from ...container import Container
from ...entities import FileRegion, FileSchema
from ...services import UsecaseException
from .common import response_json, authenticated

file = Blueprint('file', url_prefix='/file')


@file.post('/upload')
@authenticated()
async def upload(request):
    logged_user_id = request['session']['user']['id']
    config = Container().config

    region = request.form.get('region') or FileRegion.LOCAL.value
    bucket = request.form.get('bucket', '')
    path = request.form.get('path', '')
    files = request.files.getlist('file', [])

    if len(files) > config['UPLOAD_FILE_MAX_NUMBER']:
        raise UsecaseException('文件数不能超过 {} 个'.format(
            config['UPLOAD_FILE_MAX_NUMBER']))

    saved_files = []
    file_service = Container().file_service
    for file in files:
        meta = {
            'name': file.name,
            'type': file.type,
            'size': len(file.body),
        }
        if meta['size'] > config['UPLOAD_FILE_MAX_SIZE']:
            raise UsecaseException('文件 {} 大小超过上限'.format(meta['name']))

        _, ext = os.path.splitext(meta['name'])
        filename = '{}{}'.format(random_string(16), ext)

        if region == FileRegion.LOCAL.value:
            save_dir = os.path.join(
                config['DATA_PATH'], config['UPLOAD_DIR'], bucket, path)
            os.makedirs(save_dir, 0o755, True)

            async with aiofiles.open(
                    os.path.join(save_dir, filename), 'wb') as f:
                await f.write(file.body)

            saved_file = await file_service.create(
                user_id=logged_user_id, region=region, bucket=bucket,
                path=os.path.join(path, filename), meta=meta)

            saved_files.append(saved_file)
        else:
            raise UsecaseException('未知区域')

    return response_json(
        files=[FileSchema().dump(v) for v in saved_files])


@file.get('/info')
@authenticated()
async def info(request):
    id = request.args.get('id')
    if id is not None:
        id = int(id)

    file_service = Container().file_service
    file = await file_service.info(id)

    return response_json(file=FileSchema().dump(file))
