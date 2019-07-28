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

    region = request.form.get('region', StorageRegion.LOCAL.value)
    bucket = request.form.get('bucket', '')
    path = request.form.get('path', '')

    saved_files = []
    storage_service = StorageService(
        request.app.config, request.app.db, request.app.cache)
    if region == StorageRegion.LOCAL.value:
        save_dir = os.path.join(
            request.app.config['DATA_PATH'], request.app.config['UPLOAD_DIR'],
            bucket, path)
        if not os.path.exists(save_dir):
            old_mask = os.umask(0o022)
            os.makedirs(save_dir)
            os.umask(old_mask)

        for i in range(10):
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
            save_path = os.path.join(save_dir, filename)
            async with aiofiles.open(save_path, 'wb') as f:
                await f.write(uploaded_file.body)

            bucket_path = os.path.join(path, filename)
            file = await storage_service.create_file(
                user_id=user_id, region=region, bucket=bucket, path=bucket_path,
                meta=meta)

            saved_files.append(file)
    else:
        return response_json(ResponseCode.FAIL, '暂不支持该区域')

    return response_json(
        files=[FileSchema().dump(v) for v in saved_files])


@storage.get('/file/info')
@authenticated()
async def file_info(request):
    id = int(request.args.get('id'))

    storage_service = StorageService(
        request.app.config, request.app.db, request.app.cache)
    file = await storage_service.file_info(id)
    if file is None:
        raise NotFound

    return response_json(file=FileSchema().dump(file))
