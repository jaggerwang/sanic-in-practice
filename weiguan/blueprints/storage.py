import os

from sanic import Blueprint
from sanic.exceptions import NotFound
import aiofiles

from ..utils import random_string
from ..models import StorageRegion, FileSchema
from ..services import StorageService
from .common import response_json, ResponseCode, authenticated

storage = Blueprint('storage', url_prefix='/storage')


@storage.post('/upload')
@authenticated()
async def upload(request):
    user_id = request['session']['user']['id']

    region = request.form.get('region') or StorageRegion.LOCAL.value
    bucket = request.form.get('bucket', '')
    path = request.form.get('path', '')

    uploaded_files = []
    for i in range(request.app.config['UPLOAD_FILE_MAX_NUMBER']):
        uploaded_file = request.files.get('file{}'.format(i+1))
        if uploaded_file is None:
            continue

        meta = {
            'name': uploaded_file.name,
            'type': uploaded_file.type,
            'size': len(uploaded_file.body),
        }
        if meta['size'] > request.app.config['UPLOAD_FILE_MAX_SIZE']:
            return response_json(
                ResponseCode.FAIL, '文件 {} 大小超过上限'.format(meta['name']))

        _, ext = os.path.splitext(meta['name'])
        filename = '{}{}'.format(random_string(16), ext)

        uploaded_files.append((meta, filename, uploaded_file.body))

    saved_files = []
    storage_service = StorageService(
        request.app.config, request.app.db, request.app.cache)
    if region == StorageRegion.LOCAL.value:
        save_dir = os.path.join(
            request.app.config['DATA_PATH'], request.app.config['UPLOAD_DIR'],
            bucket, path)
        os.makedirs(save_dir, 0o755, True)

        for (meta, filename, body) in uploaded_files:
            async with aiofiles.open(
                    os.path.join(save_dir, filename), 'wb') as f:
                await f.write(body)

            file = await storage_service.create_file(
                user_id=user_id, region=region, bucket=bucket,
                path=os.path.join(path, filename), meta=meta)

            saved_files.append(file)
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

    storage_service = StorageService(
        request.app.config, request.app.db, request.app.cache)
    file = await storage_service.file_info(id)
    if file is None:
        raise NotFound('')

    return response_json(file=FileSchema().dump(file))
