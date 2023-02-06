import json
import typing

import jsondiff

from . import db  # noqa
from . import files  # noqa
from . import filters  # noqa
from . import experiment  # noqa

DEFAULT_NAMESPACE = None
DEFAULT_DEPARTMENT = 'market'


def _clean_body(body, with_removed=True):
    body.pop('created', None)
    body.pop('last_manual_update', None)
    body.pop('biz_revision', None)
    body.pop('last_modified_at', None)
    body.pop('name', None)
    body.pop('owners', None)
    body.pop('watchers', None)
    for clause in body['clauses']:
        clause.pop('alias', None)
    if with_removed:
        body.pop('removed', None)


def assert_with_diff(first, second, message):
    diff = jsondiff.diff(first, second)
    assert first == second, message + ':\n{}'.format(diff)


async def experiment_check_tests(
        taxi_exp_client, experiment_name, expected_data,
):
    response = await taxi_exp_client.get(
        'v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': experiment_name},
    )
    assert response.status == 200, await response.text()
    body = await response.json()
    revision = body['last_modified_at']
    _clean_body(body)
    assert_with_diff(body, expected_data, 'Get by name')

    response = await taxi_exp_client.get(
        'v1/experiments/updates/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'limit': 1, 'newer_than': revision - 1},
    )
    assert response.status == 200, await response.text()
    body = (await response.json())['experiments'][0]
    _clean_body(body)
    assert_with_diff(body, expected_data, 'Get by updates')

    response = await taxi_exp_client.get(
        'v1/history/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'revision': revision},
    )
    assert response.status == 200, await response.text()
    body = (await response.json())['body']
    _clean_body(body)
    assert_with_diff(body, expected_data, 'Get by history:')


async def get_experiment(
        taxi_exp_client, name, namespace=DEFAULT_NAMESPACE, raw_answer=False,
):
    return await _get_obj(
        taxi_exp_client,
        name,
        is_config=False,
        namespace=namespace,
        raw_answer=raw_answer,
    )


async def get_config(
        taxi_exp_client, name, namespace=DEFAULT_NAMESPACE, raw_answer=False,
):
    return await _get_obj(
        taxi_exp_client,
        name,
        is_config=True,
        namespace=namespace,
        raw_answer=raw_answer,
    )


async def _get_obj(
        taxi_exp_client,
        name,
        is_config,
        namespace=DEFAULT_NAMESPACE,
        raw_answer=False,
):
    source = 'configs' if is_config else 'experiments'
    params = {'name': name}
    if namespace is not None:
        params['tplatform_namespace'] = namespace
    response = await taxi_exp_client.get(
        f'/v1/{source}/', headers={'YaTaxi-Api-Key': 'secret'}, params=params,
    )
    if raw_answer:
        return response
    assert response.status == 200, await response.text()
    return await response.json()


async def remove_exp(
        taxi_exp_client, name, last_modified_at, namespace=DEFAULT_NAMESPACE,
):
    return await _remove_obj(
        taxi_exp_client,
        name,
        last_modified_at,
        namespace=namespace,
        source='experiments',
    )


async def remove_config(
        taxi_exp_client, name, last_modified_at, namespace=DEFAULT_NAMESPACE,
):
    return await _remove_obj(
        taxi_exp_client,
        name,
        last_modified_at,
        namespace=namespace,
        source='configs',
    )


async def _remove_obj(
        taxi_exp_client,
        name,
        last_modified_at,
        namespace=DEFAULT_NAMESPACE,
        source='experiments',
):
    params = {'name': name, 'last_modified_at': last_modified_at}
    if namespace is not None:
        params['tplatform_namespace'] = namespace
    response = await taxi_exp_client.delete(
        f'/v1/{source}/', headers={'YaTaxi-Api-Key': 'secret'}, params=params,
    )
    assert response.status == 200, await response.text()


async def create_default_exp(
        taxi_exp_client, name, namespace=DEFAULT_NAMESPACE, **kwargs,
):
    kwargs['name'] = name
    params = {'name': name}
    if namespace is not None:
        params['tplatform_namespace'] = namespace
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params=params,
        json=experiment.generate_default(**kwargs),
    )
    assert response.status == 200, await response.text()


async def create_default_conf(
        taxi_exp_client, name, namespace=DEFAULT_NAMESPACE, **kwargs,
):
    kwargs['name'] = name
    params = {'name': name}
    if namespace is not None:
        params['tplatform_namespace'] = namespace
    response = await taxi_exp_client.post(
        '/v1/configs/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params=params,
        json=experiment.generate_config(**kwargs),
    )
    assert response.status == 200, await response.text()


async def on_off_experiment(
        taxi_exp_client,
        name,
        last_modified_at,
        namespace=DEFAULT_NAMESPACE,
        enable=False,
        raw_answer=False,
):
    return await _on_off_obj(
        taxi_exp_client,
        name,
        namespace,
        last_modified_at,
        enable=enable,
        is_config=False,
        raw_answer=raw_answer,
    )


async def on_off_config(
        taxi_exp_client,
        name,
        last_modified_at,
        namespace=DEFAULT_NAMESPACE,
        enable=False,
        raw_answer=False,
):
    return await _on_off_obj(
        taxi_exp_client,
        name,
        namespace,
        last_modified_at,
        enable=enable,
        is_config=True,
        raw_answer=raw_answer,
    )


async def _on_off_obj(
        taxi_exp_client,
        name,
        namespace,
        last_modified_at,
        enable=False,
        is_config=False,
        raw_answer=False,
):
    source = 'configs' if is_config else 'experiments'
    action = 'enable' if enable else 'disable'
    params = {'name': name, 'last_modified_at': last_modified_at}
    if namespace is not None:
        params['tplatform_namespace'] = namespace
    response = await taxi_exp_client.post(
        f'/v1/{source}/{action}/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params=params,
    )
    if raw_answer:
        return response
    assert response.status == 200, await response.text()
    return await response.json()


async def uplift_to_config(
        taxi_exp_client, name, disable=False, namespace=DEFAULT_NAMESPACE,
):
    exp_body = await get_experiment(taxi_exp_client, name, namespace=namespace)

    modification = 'close' if not disable else 'close_and_disable'
    req_json = {
        'experiment_name': name,
        'last_updated_at': exp_body['last_modified_at'],
        'modification': modification,
    }
    params = {}
    if namespace is not None:
        params['tplatform_namespace'] = namespace
    response = await taxi_exp_client.post(
        '/v1/experiments/uplift-to-config/',
        headers={'YaTaxi-Api-Key': 'secret'},
        json=req_json,
        params=params,
    )
    assert response.status == 200, await response.text()


async def experiment_smoke_tests(taxi_exp_client, experiment_name: str):
    response = await taxi_exp_client.get(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': experiment_name},
    )
    assert response.status == 200, await response.text()
    revision = (await response.json())['last_modified_at']

    response = await taxi_exp_client.get(
        '/v1/experiments/updates/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'limit': 1, 'newer_than': revision - 1},
    )
    assert response.status == 200, await response.text()

    response = await taxi_exp_client.get(
        '/v1/history/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'revision': revision},
    )
    assert response.status == 200, await response.text()


async def get_updates(taxi_exp_client, newer_than=None, limit=None):
    return await _get_updates(taxi_exp_client, newer_than, limit)


async def get_configs_updates(taxi_exp_client, newer_than=None, limit=None):
    return await _get_updates(
        taxi_exp_client, newer_than, limit, path='configs',
    )


async def get_last_modified_at(
        taxi_exp_client, experiment_name, namespace=DEFAULT_NAMESPACE,
):
    params = {'name': experiment_name}
    if namespace is not None:
        params['tplatform_namespace'] = namespace
    response = await taxi_exp_client.get(
        '/v1/experiments/',
        params=params,
        headers={'YaTaxi-Api-Key': 'secret'},
    )
    assert response.status == 200
    result = await response.json()
    return result['last_modified_at']


async def _get_updates(
        taxi_exp_client, newer_than=None, limit=None, path='experiments',
):
    params = {}
    if newer_than is not None:
        params['newer_than'] = newer_than
    if limit is not None:
        params['limit'] = limit
    response = await taxi_exp_client.get(
        f'/v1/{path}/updates/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params=params,
    )
    return await response.json()


async def add_exp(taxi_exp_client, body):
    return await _add_obj(taxi_exp_client, body, '/v1/experiments/')


async def add_checked_exp(taxi_exp_client, body):
    return await _add_obj(
        taxi_exp_client, body, '/v1/experiments/', need_check=True,
    )


async def add_config(taxi_exp_client, body):
    return await _add_obj(taxi_exp_client, body, '/v1/configs/')


async def add_checked_config(taxi_exp_client, body):
    return await _add_obj(
        taxi_exp_client, body, '/v1/configs/', need_check=True,
    )


async def _add_obj(taxi_exp_client, body, url, need_check=False):
    name = body['name']
    response = await taxi_exp_client.post(
        url,
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': name},
        json=body,
    )
    if need_check:
        assert response.status == 200, await response.text()
    return await response.json()


async def init_exp(
        taxi_exp_client,
        body,
        name=None,
        namespace=DEFAULT_NAMESPACE,
        raw_answer=False,
        allow_empty_schema=None,
):
    return await _init(
        taxi_exp_client,
        body,
        name,
        namespace,
        is_config=False,
        raw_answer=raw_answer,
        allow_empty_schema=allow_empty_schema,
    )


async def init_config(
        taxi_exp_client,
        body,
        name=None,
        namespace=DEFAULT_NAMESPACE,
        raw_answer=False,
        allow_empty_schema=None,
):
    return await _init(
        taxi_exp_client,
        body,
        name,
        namespace,
        is_config=True,
        raw_answer=raw_answer,
        allow_empty_schema=allow_empty_schema,
    )


async def _init(
        taxi_exp_client,
        body,
        name=None,
        namespace=DEFAULT_NAMESPACE,
        is_config=False,
        raw_answer=False,
        allow_empty_schema=None,
):
    source = 'configs' if is_config else 'experiments'
    if name is None:
        name = body['name']

    params = {'name': name}
    if namespace is not None:
        params['tplatform_namespace'] = namespace
    if allow_empty_schema is not None:
        body['allow_empty_schema'] = allow_empty_schema
    response = await taxi_exp_client.post(
        f'/v1/{source}/',
        headers={'X-Ya-Service-Ticket': '123'},
        params=params,
        json=body,
    )
    if raw_answer:
        return response
    assert response.status == 200, await response.text()

    response = await taxi_exp_client.get(
        f'/v1/{source}/',
        headers={'X-Ya-Service-Ticket': '123'},
        params=params,
    )
    assert response.status == 200, await response.text()
    return await response.json()


async def verbose_init_exp_by_draft(
        taxi_exp_client,
        body,
        namespace=DEFAULT_NAMESPACE,
        allow_empty_schema=None,
):
    return await _init_by_draft(
        taxi_exp_client,
        body,
        '/v1/experiments/',
        namespace=namespace,
        allow_empty_schema=allow_empty_schema,
    )


async def success_init_exp_by_draft(
        taxi_exp_client,
        body,
        namespace=DEFAULT_NAMESPACE,
        allow_empty_schema=None,
):
    return await _init_by_draft(
        taxi_exp_client,
        body,
        '/v1/experiments/',
        need_check=True,
        namespace=namespace,
        allow_empty_schema=allow_empty_schema,
    )


async def verbose_init_config_by_draft(
        taxi_exp_client,
        body,
        namespace=DEFAULT_NAMESPACE,
        allow_empty_schema=None,
):
    return await _init_by_draft(
        taxi_exp_client,
        body,
        '/v1/configs/',
        namespace=namespace,
        allow_empty_schema=allow_empty_schema,
    )


async def success_init_config_by_draft(
        taxi_exp_client,
        body,
        namespace=DEFAULT_NAMESPACE,
        allow_empty_schema=None,
):
    return await _init_by_draft(
        taxi_exp_client,
        body,
        '/v1/configs/',
        need_check=True,
        namespace=namespace,
        allow_empty_schema=allow_empty_schema,
    )


async def _init_by_draft(
        taxi_exp_client,
        body,
        url,
        need_check=False,
        namespace=DEFAULT_NAMESPACE,
        allow_empty_schema=None,
):
    name = body['name']
    params = {'name': name}
    if namespace is not None:
        params['tplatform_namespace'] = namespace
    if allow_empty_schema is not None:
        body['allow_empty_schema'] = allow_empty_schema
    response = await taxi_exp_client.post(
        url + 'drafts/check/',
        headers={'X-Ya-Service-Ticket': '123'},
        params=params,
        json=body,
    )
    if response.status != 200:
        if not need_check:
            return await response.json()
        assert False, await response.text()

    body = await response.json()
    response = await taxi_exp_client.post(
        url + 'drafts/apply/',
        headers={'X-Ya-Service-Ticket': '123'},
        params=params,
        json=body['data'],
    )
    if response.status != 200:
        if not need_check:
            return await response.json()
        assert False, await response.text()

    response = await taxi_exp_client.get(
        url, headers={'X-Ya-Service-Ticket': '123'}, params=params,
    )
    if response.status != 200 and need_check:
        assert False, await response.text()
    return await response.json()


async def check_exp_by_draft(taxi_exp_client, body):
    name = body['name']
    response = await taxi_exp_client.post(
        '/v1/experiments/drafts/check/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': name},
        json=body,
    )
    return await response.json()


async def update_exp(
        taxi_exp_client, body, raw_answer=False, namespace=DEFAULT_NAMESPACE,
):
    return await _update(
        taxi_exp_client, body, raw_answer, namespace, is_config=False,
    )


async def update_config(
        taxi_exp_client, body, raw_answer=False, namespace=DEFAULT_NAMESPACE,
):
    return await _update(
        taxi_exp_client, body, raw_answer, namespace, is_config=True,
    )


async def _update(
        taxi_exp_client,
        body,
        raw_answer=False,
        namespace=DEFAULT_NAMESPACE,
        is_config=False,
):
    source = 'configs' if is_config else 'experiments'
    name = body['name']
    last_modified_at = body['last_modified_at']
    params = {'name': name, 'last_modified_at': last_modified_at}
    if namespace is not None:
        params['tplatform_namespace'] = namespace
    response = await taxi_exp_client.put(
        f'/v1/{source}/',
        headers={'X-Ya-Service-Ticket': '123'},
        params=params,
        json=body,
    )
    if raw_answer:
        return response
    assert response.status == 200, await response.text()
    params.pop('last_modified_at')
    if (
            namespace is None
            and 'namespace' in body
            and body['namespace'] is not None
    ):
        params['tplatform_namespace'] = body['namespace']
    response = await taxi_exp_client.get(
        f'/v1/{source}/',
        headers={'X-Ya-Service-Ticket': '123'},
        params=params,
    )
    assert response.status == 200, await response.text()
    return await response.json()


async def update_exp_by_draft(
        taxi_exp_client, body, raw_answer=False, namespace=DEFAULT_NAMESPACE,
):
    return await _update_by_draft(
        taxi_exp_client, body, raw_answer, namespace, is_config=False,
    )


async def update_config_by_draft(
        taxi_exp_client, body, raw_answer=False, namespace=DEFAULT_NAMESPACE,
):
    return await _update_by_draft(
        taxi_exp_client, body, raw_answer, namespace, is_config=True,
    )


async def draft_disable_financial(
        taxi_exp_client,
        name,
        is_config,
        department=DEFAULT_DEPARTMENT,
        namespace=DEFAULT_NAMESPACE,
):
    source = 'configs' if is_config else 'experiments'
    params = {'name': name, 'department': department}
    if namespace is not None:
        params['tplatform_namespace'] = namespace
    response = await taxi_exp_client.put(
        f'/v1/{source}/drafts-disable-financial/check/',
        headers={'X-Ya-Service-Ticket': '123'},
        params=params,
        json={},
    )
    assert response.status == 200, await response.text()
    body = await response.json()
    response = await taxi_exp_client.put(
        f'/v1/{source}/drafts-disable-financial/apply/',
        headers={'X-Ya-Service-Ticket': '123'},
        params=params,
        json=body['data'],
    )
    assert response.status == 200, await response.text()
    if namespace is not None:
        params['tplatform_namespace'] = namespace
    response = await taxi_exp_client.get(
        f'/v1/{source}/',
        headers={'X-Ya-Service-Ticket': '123'},
        params=params,
    )
    assert response.status == 200, await response.text()
    return await response.json()


async def _update_by_draft(
        taxi_exp_client,
        body,
        raw_answer=False,
        namespace=DEFAULT_NAMESPACE,
        is_config=False,
):
    source = 'configs' if is_config else 'experiments'
    name = body['name']
    last_modified_at = body['last_modified_at']
    if 'namespace' in body and body['namespace'] is not None:
        new_namespace = body['namespace']
    else:
        new_namespace = namespace
    params = {'name': name, 'last_modified_at': last_modified_at}
    if namespace is not None:
        params['tplatform_namespace'] = namespace
    response = await taxi_exp_client.put(
        f'/v1/{source}/drafts/check/',
        headers={'X-Ya-Service-Ticket': '123'},
        params=params,
        json=body,
    )
    if raw_answer:
        return response
    assert response.status == 200, await response.text()
    body = await response.json()
    response = await taxi_exp_client.put(
        f'/v1/{source}/drafts/apply/',
        headers={'X-Ya-Service-Ticket': '123'},
        params=params,
        json=body['data'],
    )
    assert response.status == 200, await response.text()
    params.pop('last_modified_at')
    if namespace is None and new_namespace is not None:
        params['tplatform_namespace'] = new_namespace
    response = await taxi_exp_client.get(
        f'/v1/{source}/',
        headers={'X-Ya-Service-Ticket': '123'},
        params=params,
    )
    assert response.status == 200, await response.text()
    return await response.json()


async def delete_exp_by_draft(
        taxi_exp_client,
        name,
        last_modified_at,
        raw_answer=False,
        namespace=DEFAULT_NAMESPACE,
):
    return await _delete_by_draft(
        taxi_exp_client,
        name,
        last_modified_at,
        raw_answer,
        namespace,
        is_config=False,
    )


async def delete_config_by_draft(
        taxi_exp_client,
        name,
        last_modified_at,
        raw_answer=False,
        namespace=DEFAULT_NAMESPACE,
):
    return await _delete_by_draft(
        taxi_exp_client,
        name,
        last_modified_at,
        raw_answer,
        namespace,
        is_config=True,
    )


async def _delete_by_draft(
        taxi_exp_client,
        name,
        last_modified_at,
        raw_answer=False,
        namespace=DEFAULT_NAMESPACE,
        is_config=False,
):
    source = 'configs' if is_config else 'experiments'
    params = {'name': name, 'last_modified_at': last_modified_at}
    if namespace is not None:
        params['tplatform_namespace'] = namespace
    response = await taxi_exp_client.delete(
        f'/v1/{source}/drafts/check/',
        headers={'X-Ya-Service-Ticket': '123'},
        params=params,
    )
    if raw_answer:
        return response
    assert response.status == 200, await response.text()
    response = await taxi_exp_client.delete(
        f'/v1/{source}/drafts/apply/',
        headers={'X-Ya-Service-Ticket': '123'},
        params=params,
    )
    assert response.status == 200, await response.text()
    return response


async def get_experiments_list(taxi_exp_client, **kwargs):
    return await _get_list(taxi_exp_client, source='experiments', **kwargs)


async def get_configs_list(taxi_exp_client, **kwargs):
    return await _get_list(taxi_exp_client, source='configs', **kwargs)


async def _get_list(
        taxi_exp_client,
        name=None,
        namespace=DEFAULT_NAMESPACE,
        limit=None,
        offset=None,
        show_closed='false',
        source='experiments',
        merge_value_tag=None,
        service_id=None,
):
    params = {}
    if name is not None:
        params['name'] = name
    if namespace is not None:
        params['tplatform_namespace'] = namespace
    if limit is not None:
        params['limit'] = limit
    if offset is not None:
        params['offset'] = offset
    if show_closed is not None:
        params['show_closed'] = show_closed
    if merge_value_tag is not None:
        params['merge_value_tag'] = merge_value_tag
    if service_id is not None:
        params['service_id'] = service_id
    return await taxi_exp_client.get(
        f'/v1/{source}/list/',
        headers={'X-Ya-Service-Ticket': '123'},
        params=params,
    )


async def restore_experiment(
        taxi_exp_client,
        name,
        last_modified_at,
        revision=None,
        namespace=DEFAULT_NAMESPACE,
        restore_to_previous=None,
):
    return await _restore_obj(
        taxi_exp_client,
        name=name,
        last_modified_at=last_modified_at,
        revision=revision,
        namespace=namespace,
        source='experiments',
        restore_to_previous=restore_to_previous,
    )


async def restore_config(
        taxi_exp_client,
        name,
        last_modified_at,
        revision=None,
        namespace=DEFAULT_NAMESPACE,
        restore_to_previous=None,
):
    return await _restore_obj(
        taxi_exp_client,
        name=name,
        last_modified_at=last_modified_at,
        revision=revision,
        namespace=namespace,
        source='configs',
        restore_to_previous=restore_to_previous,
    )


async def _restore_obj(
        taxi_exp_client,
        name,
        last_modified_at,
        revision,
        namespace=DEFAULT_NAMESPACE,
        source='experiments',
        restore_to_previous=None,
):
    params = {'name': name, 'last_modified_at': last_modified_at}
    if namespace is not None:
        params['tplatform_namespace'] = namespace
    if revision is not None:
        params['revision'] = revision
    if restore_to_previous:
        params['restore_to_previous'] = 'true'
    return await taxi_exp_client.post(
        f'/v1/{source}/restore/',
        headers={'X-Ya-Service-Ticket': '123'},
        params=params,
    )


async def add_schema_draft(
        taxi_exp_client,
        name,
        schema_body,
        default_value=None,
        namespace=None,
        is_config=False,
        skip_validating_values=None,
):
    params = (
        {'experiment_name': name} if not is_config else {'config_name': name}
    )
    if namespace:
        params['tplatform_namespace'] = namespace
    body = {'schema_body': schema_body}
    if skip_validating_values is not None:
        body['skip_validating_values'] = skip_validating_values
    if default_value is not None:
        body['default_value'] = json.dumps(default_value)
    return await taxi_exp_client.post(
        '/v1/schemas/draft',
        headers={'X-Ya-Service-Ticket': '123'},
        params=params,
        json=body,
    )


async def get_schema_draft(
        taxi_exp_client,
        draft_id=None,
        name=None,
        namespace=None,
        is_config=False,
        copy_name=False,
):
    if draft_id is not None:
        params = {'draft_id': draft_id}
    else:
        if not copy_name:
            params = (
                {'experiment_name': name}
                if not is_config
                else {'config_name': name}
            )
        else:
            params = {'experiment_name': name, 'config_name': name}
    if namespace:
        params['tplatform_namespace'] = namespace
    return await taxi_exp_client.get(
        '/v1/schemas/draft',
        headers={'X-Ya-Service-Ticket': '123'},
        params=params,
    )


async def delete_schema_draft(
        taxi_exp_client,
        draft_id=None,
        name=None,
        namespace=None,
        is_config=False,
        copy_name=False,
):
    if draft_id is not None:
        params = {'draft_id': draft_id}
    else:
        if not copy_name:
            params = (
                {'experiment_name': name}
                if not is_config
                else {'config_name': name}
            )
        else:
            params = {'experiment_name': name, 'config_name': name}
    if namespace:
        params['tplatform_namespace'] = namespace
    return await taxi_exp_client.delete(
        '/v1/schemas/draft',
        headers={'X-Ya-Service-Ticket': '123'},
        params=params,
    )


async def publish_schema(taxi_exp_client, draft_id, namespace=None):
    params = {'draft_id': draft_id}
    if namespace:
        params['tplatform_namespace'] = namespace
    return await taxi_exp_client.post(
        '/v1/schemas/publish',
        headers={'X-Ya-Service-Ticket': '123'},
        params=params,
    )


def idfn(val):
    return str(val)


def get_args(typename: typing.Any) -> str:
    return ','.join(typename.__annotations__.keys())
