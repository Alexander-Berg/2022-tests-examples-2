import hashlib
import os
from typing import Mapping

from taxi.util import itertools_ext

from taxi_exp.stuff.update_tags import common

DEFAULT_NAMESPACE = None


async def _search(taxi_exp_client, url, **kwargs):
    data = {}
    if 'limit' in kwargs:
        data['limit'] = kwargs.pop('limit')
    if 'offset' in kwargs:
        data['offset'] = kwargs.pop('offset')
    params = {}
    if 'namespace' in kwargs:
        if kwargs.get('namespace') is not None:
            params['tplatform_namespace'] = kwargs.get('namespace')
        kwargs.pop('namespace')
    else:
        if DEFAULT_NAMESPACE is not None:
            params['tplatform_namespace'] = DEFAULT_NAMESPACE

    data['query'] = kwargs

    return await taxi_exp_client.post(
        url, headers={'YaTaxi-Api-Key': 'secret'}, json=data, params=params,
    )


async def search_file(taxi_exp_client, **kwargs):
    return await _search(taxi_exp_client, '/v1/files/search/', **kwargs)


async def get_files_by_experiment(
        taxi_exp_client, name, namespace=DEFAULT_NAMESPACE,
):
    return await _get_files_by_obj(
        taxi_exp_client,
        name=name,
        source='by_experiment',
        namespace=namespace,
    )


async def get_files_by_config(
        taxi_exp_client, name, namespace=DEFAULT_NAMESPACE,
):
    return await _get_files_by_obj(
        taxi_exp_client, name=name, source='by_config', namespace=namespace,
    )


async def _get_files_by_obj(
        taxi_exp_client,
        name,
        source='by_experiment',
        namespace=DEFAULT_NAMESPACE,
):
    params = {'name': name}
    if namespace is not None:
        params['tplatform_namespace'] = namespace
    return await taxi_exp_client.get(
        f'/v1/files/{source}/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params=params,
    )


async def get_original_file_by_mds_id(taxi_exp_client, mds_id):
    return await taxi_exp_client.get(
        f'/v1/files/{mds_id}/input/', headers={'YaTaxi-Api-Key': 'secret'},
    )


async def get_history_by_experiment(taxi_exp_client, experiment_name):
    return await taxi_exp_client.get(
        f'/v1/files/history/by_experiment/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': experiment_name},
    )


async def history_search(taxi_exp_client, **kwargs):
    return await _search(taxi_exp_client, '/v1/files/history/', **kwargs)


async def post_file(
        taxi_exp_client,
        filename,
        content,
        namespace=DEFAULT_NAMESPACE,
        file_type=None,
        enable_transform=False,
        check=None,
):
    headers = {'YaTaxi-Api-Key': 'secret', 'X-File-Name': filename}
    if file_type:
        headers['X-Arg-Type'] = file_type
        if check is not None:
            headers['X-Arg-Type'] = '{};{}'.format(
                headers['X-Arg-Type'], check,
            )
    if enable_transform:
        headers['X-Arg-Transform'] = 'replace_phone_to_personal_phone_id'
    params = {}
    if namespace is not None:
        params['tplatform_namespace'] = namespace
    params['experiment'] = ''

    return await taxi_exp_client.post(
        '/v1/files/', headers=headers, data=content, params=params,
    )


async def post_trusted_file(
        taxi_exp_client, tag: str, raw_content: bytes,
) -> Mapping:

    headers = {
        'YaTaxi-Api-Key': 'secret',
        'X-File-Tag': tag,
        'X-Is-Trusted': 'true',
        'Content-Length': str(len(raw_content)),
    }

    return await taxi_exp_client.post(
        '/v1/files/', headers=headers, data=raw_content,
    )


async def get_trusted_file_metadata(taxi_exp_client, tag):
    return await taxi_exp_client.get(
        '/v1/trusted-files/metadata/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': tag},
    )


def get_content_metadata(raw_content):
    content = raw_content.split('\n')
    count_lines = len(content)

    sha = hashlib.sha256()
    content_length = 0
    for phone_ids_chunk in itertools_ext.chunks(content, common.SAVE_LIMIT):
        body = '\n'.join([item for item in phone_ids_chunk if item]) + '\n'
        content_length += len(body)
        sha.update(body.encode('utf-8'))
    return sha.hexdigest(), count_lines, content_length


async def delete_file(taxi_exp_client, file_id, version):
    params = {'id': file_id, 'version': version}
    return await taxi_exp_client.delete(
        '/v1/files/', headers={'YaTaxi-Api-Key': 'secret'}, params=params,
    )


async def get_file_redirect(taxi_exp_client, file_id, allow_s3=False):
    params = {'id': file_id}
    if allow_s3:
        params['s3_redirect_support'] = 'true'
    return await taxi_exp_client.get(
        '/v1/files/', headers={'YaTaxi-Api-Key': 'secret'}, params=params,
    )


async def get_file_body(taxi_exp_client, file_id):
    params = {'id': file_id}
    response = await taxi_exp_client.get(
        '/v1/files/', headers={'YaTaxi-Api-Key': 'secret'}, params=params,
    )
    assert response.status == 200

    uri = response.headers['X-Accel-Redirect']
    base_path = taxi_exp_client.app.files_snapshot_path
    file_name = uri.split('/')[-1]
    body = None
    with open(os.path.join(base_path, file_name), mode='rb') as file:
        body = file.read()
    return body
