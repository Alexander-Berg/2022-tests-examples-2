# pylint: disable=too-many-lines
from typing import NamedTuple
from typing import Optional

from clickhouse_driver import errors as clickhouse_errors
import pytest

import atlas_backend.internal.anomalies.change_history as _change_history
import atlas_backend.internal.anomalies.storage as _anomaly_storage


class _ReqParams(NamedTuple):
    from_ts: int
    to_ts: int
    status: Optional[str]
    level: Optional[str]
    source: Optional[str]


@pytest.mark.config(
    ATLAS_BACKEND_ANOMALY_HIERARCHY=[
        {'parent_name': 'all', 'source_name': 'yango'},
        {'parent_name': 'all', 'source_name': 'callcenter'},
    ],
)
@pytest.mark.parametrize(
    'params, expected_count',
    [
        (_ReqParams(1593129600, 1593216000, None, None, 'all'), 6),
        (
            _ReqParams(
                1593129600, 1593216000, 'confirmed,rejected', None, 'all',
            ),
            4,
        ),
        (_ReqParams(1593129600, 1593216000, None, 'minor', 'all'), 3),
        (_ReqParams(1593129600, 1593216000, None, 'minor', 'yango'), 1),
        (_ReqParams(1593129600, 1593216000, 'confirmed', None, 'all'), 3),
        (_ReqParams(1593186050, 1593216000, None, None, 'all'), 4),
    ],
)
async def test_get_anomalies_list_filters(
        web_app_client, atlas_blackbox_mock, params, expected_count,
):
    prepared_params = {
        k: v
        for k, v in {
            'from_ts': params.from_ts,
            'to_ts': params.to_ts,
            'limit': 20,
            'offset': 0,
            'status': params.status,
            'level': params.level,
            'source': params.source,
        }.items()
        if v is not None
    }

    response = await web_app_client.get(
        '/api/v1/anomalies', params=prepared_params,
    )
    assert response.status == 200
    content = await response.json()

    assert content['pagination'] == {'total_items': expected_count}
    assert len(content['anomalies']) == expected_count


async def test_get_anomalies_list_limit_offset(
        web_app_client, atlas_blackbox_mock,
):
    limit = 2
    offset = 2
    response = await web_app_client.get(
        '/api/v1/anomalies',
        params={
            'from_ts': 1593129600,
            'to_ts': 1593216000,
            'limit': limit,
            'offset': offset,
            'source': 'all',
        },
    )
    assert response.status == 200
    content = await response.json()

    assert content['pagination'] == {'total_items': 5}
    assert len(content['anomalies']) == limit
    assert content['anomalies'][0]['_id'] == '5e00b661954de74d8a6af7c7'


@pytest.mark.parametrize(
    'username, expected_status',
    [
        ('omnipotent_user', 200),
        ('anomaly_admin', 200),
        ('anomaly_viewer', 200),
        ('super_user', 200),
        ('main_user', 403),
        ('nonexisted_user', 403),
    ],
)
async def test_get_anomalies_list_permissions(
        web_app_client, atlas_blackbox_mock, username, expected_status,
):
    response = await web_app_client.get(
        '/api/v1/anomalies',
        params={
            'from_ts': 1593129600,
            'to_ts': 1593216000,
            'limit': 1,
            'offset': 0,
            'source': 'all',
        },
    )
    assert response.status == expected_status


async def test_get_anomaly(web_app_client, atlas_blackbox_mock):
    response = await web_app_client.get(
        '/api/v1/anomalies/5e00b661954de74d8a6af7c8',
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        '_id': '5e00b661954de74d8a6af7c8',
        'author': 'robot-atlas',
        'created': 1593173520,
        'description': 'Something gone very very bad',
        'duty_task': 'https://st.yandex-team.ru/ATLASBACK-1527',
        'end_ts': 1593178520,
        'level': 'major',
        'losses': {'orders': 100000},
        'notifications': {},
        'source': 'all',
        'start_ts': 1593173520,
        'status': 'confirmed',
        'updated': 1593173520,
    }


async def test_get_anomaly_invalid_id(web_app_client, atlas_blackbox_mock):
    response = await web_app_client.get('/api/v1/anomalies/invalid_id')
    assert response.status == 400


async def test_get_anomaly_non_existing(web_app_client, atlas_blackbox_mock):
    response = await web_app_client.get(
        '/api/v1/anomalies/aaaaaaaaaaaaaaaaaaaaaaaa',
    )
    assert response.status == 404


@pytest.mark.parametrize(
    'username, expected_status',
    [
        ('omnipotent_user', 200),
        ('anomaly_admin', 200),
        ('anomaly_viewer', 200),
        ('super_user', 200),
        ('main_user', 403),
        ('nonexisted_user', 403),
    ],
)
async def test_get_anomaly_permissions(
        web_app_client, atlas_blackbox_mock, username, expected_status,
):
    response = await web_app_client.get(
        '/api/v1/anomalies/5e00b661954de74d8a6af7c8',
    )
    assert response.status == expected_status


async def test_create_anomaly_with_defaults(
        web_app_client, atlas_blackbox_mock,
):
    response = await web_app_client.post(
        '/api/v1/anomalies',
        json={
            'start_ts': 1593186300,
            'end_ts': 1593186900,
            'status': 'confirmed',
        },
    )
    assert response.status == 201
    anomaly_id = await response.json()

    inserted_resp = await web_app_client.get(f'/api/v1/anomalies/{anomaly_id}')
    inserted = await inserted_resp.json()

    assert inserted['start_ts'] == 1593186300
    assert inserted['end_ts'] == 1593186900
    assert inserted['status'] == 'confirmed'
    assert inserted['level'] == 'unknown'
    assert inserted['source'] == 'all'
    assert inserted['author'] == 'omnipotent_user'

    response = await web_app_client.get(
        f'/api/v1/anomalies/{anomaly_id}/change-history',
        params={'limit': 1, 'offset': 0},
    )
    assert response.status == 200
    response_data = await response.json()
    assert response_data['pagination']['total_items'] == 1
    change_history = response_data['change_history']
    assert change_history
    inserted_change_history_item = change_history[0]
    assert inserted_change_history_item
    assert inserted_change_history_item['start_ts'] == 1593186300
    assert inserted_change_history_item['end_ts'] == 1593186900
    assert inserted_change_history_item['status'] == 'confirmed'
    assert inserted_change_history_item['level'] == 'unknown'
    assert inserted_change_history_item['source'] == 'all'
    assert inserted_change_history_item['author'] == 'omnipotent_user'


async def test_create_anomaly(web_app_client, atlas_blackbox_mock):
    response = await web_app_client.post(
        '/api/v1/anomalies',
        json={
            'start_ts': 1593186300,
            'end_ts': 1593186900,
            'status': 'rejected',
            'level': 'minor',
            'source': 'lavka',
            'description': 'ratatat',
            'duty_task': 'https://st.yandex-team.ru/ATLASBACK-1527',
            'losses': {'orders': -200},
        },
    )
    assert response.status == 201
    anomaly_id = await response.json()

    inserted_resp = await web_app_client.get(f'/api/v1/anomalies/{anomaly_id}')
    inserted = await inserted_resp.json()

    assert inserted['start_ts'] == 1593186300
    assert inserted['end_ts'] == 1593186900
    assert inserted['status'] == 'rejected'
    assert inserted['level'] == 'minor'
    assert inserted['source'] == 'lavka'
    assert inserted['author'] == 'omnipotent_user'
    assert inserted['losses'] == {'orders': -200}
    assert inserted['description'] == 'ratatat'
    assert inserted['duty_task'] == 'https://st.yandex-team.ru/ATLASBACK-1527'

    response = await web_app_client.get(
        f'/api/v1/anomalies/{anomaly_id}/change-history',
        params={'limit': 1, 'offset': 0},
    )
    assert response.status == 200
    response_data = await response.json()
    assert response_data['pagination']['total_items'] == 1
    change_history = response_data['change_history']
    assert change_history
    inserted_change_history_item = change_history[0]
    assert inserted_change_history_item
    assert inserted_change_history_item['start_ts'] == 1593186300
    assert inserted_change_history_item['end_ts'] == 1593186900
    assert inserted_change_history_item['status'] == 'rejected'
    assert inserted_change_history_item['level'] == 'minor'
    assert inserted_change_history_item['source'] == 'lavka'
    assert inserted_change_history_item['author'] == 'omnipotent_user'
    assert inserted_change_history_item['description'] == 'ratatat'
    assert (
        inserted_change_history_item['duty_task']
        == 'https://st.yandex-team.ru/ATLASBACK-1527'
    )


async def test_create_vezet_anomaly(web_app_client, atlas_blackbox_mock):
    response = await web_app_client.post(
        '/api/v1/anomalies',
        json={
            'start_ts': 1593186300,
            'end_ts': 1593186900,
            'status': 'rejected',
            'level': 'minor',
            'source': 'vezet',
            'description': 'ratatat',
            'duty_task': 'https://st.yandex-team.ru/ATLASBACK-1527',
            'losses': {'orders': -200},
        },
    )
    assert response.status == 400, await response.text()
    result = await response.json()
    assert result == {
        'message': '"vezet" source is deprecated. Use "callcenter" instead',
        'code': 'BadRequest',
    }


@pytest.mark.parametrize(
    'username, expected_status',
    [
        ('omnipotent_user', 201),
        ('anomaly_admin', 201),
        ('anomaly_viewer', 403),
        ('super_user', 201),
        ('main_user', 403),
        ('nonexisted_user', 403),
    ],
)
async def test_create_anomaly_permissions(
        web_app_client, atlas_blackbox_mock, username, expected_status,
):
    response = await web_app_client.post(
        '/api/v1/anomalies',
        json={
            'start_ts': 1593186300,
            'end_ts': 1593186900,
            'status': 'confirmed',
        },
    )
    assert response.status == expected_status


@pytest.mark.config(
    ATLAS_BACKEND_ANOMALY_HIERARCHY=[
        {'parent_name': 'all', 'source_name': 'uber'},
    ],
)
async def test_create_anomaly_hierarchical(
        web_app_client, atlas_blackbox_mock, web_context,
):
    response = await web_app_client.post(
        '/api/v1/anomalies',
        json={
            'start_ts': 1593186300,
            'end_ts': 1593186900,
            'status': 'confirmed',
            'level': 'minor',
            'source': 'all',
            'description': 'ratatat',
            'duty_task': 'https://st.yandex-team.ru/ATLASBACK-1527',
            'losses': {'orders': -200},
        },
    )
    assert response.status == 201
    anomaly_id = await response.json()

    storage = _anomaly_storage.AnomalyStorage.from_context(web_context)
    inserted = await storage.get(anomaly_id)

    assert inserted is not None
    assert inserted.start_ts == 1593186300
    assert inserted.end_ts == 1593186900
    assert inserted.status.value == 'confirmed'
    assert inserted.severity_level.value == 'minor'
    assert inserted.order_source.value == 'all'
    assert inserted.author == 'omnipotent_user'
    assert inserted.losses == {'orders': -200}
    assert inserted.description == 'ratatat'
    assert inserted.duty_task == 'https://st.yandex-team.ru/ATLASBACK-1527'
    assert inserted.parent_anomaly_id is None
    assert len(inserted.child_anomaly_ids) == 1

    response = await web_app_client.get(
        f'/api/v1/anomalies/{anomaly_id}/change-history',
        params={'limit': 1, 'offset': 0},
    )
    assert response.status == 200
    response_data = await response.json()
    assert response_data['pagination']['total_items'] == 1
    change_history = response_data['change_history']
    assert change_history
    inserted_change_history_item = change_history[0]
    assert inserted_change_history_item
    assert inserted_change_history_item['start_ts'] == 1593186300
    assert inserted_change_history_item['end_ts'] == 1593186900
    assert inserted_change_history_item['status'] == 'confirmed'
    assert inserted_change_history_item['level'] == 'minor'
    assert inserted_change_history_item['source'] == 'all'
    assert inserted_change_history_item['author'] == 'omnipotent_user'
    assert inserted_change_history_item['description'] == 'ratatat'
    assert (
        inserted_change_history_item['duty_task']
        == 'https://st.yandex-team.ru/ATLASBACK-1527'
    )

    child_id = inserted.child_anomaly_ids[0]

    child = await storage.get(child_id)

    assert child is not None
    assert child.start_ts == 1593186300
    assert child.end_ts == 1593186900
    assert child.status.value == 'confirmed'
    assert child.severity_level.value == 'minor'
    assert child.order_source.value == 'uber'
    assert child.author == 'omnipotent_user'
    assert child.losses == {'orders': None}
    assert child.description == 'ratatat'
    assert child.duty_task == 'https://st.yandex-team.ru/ATLASBACK-1527'
    assert child.parent_anomaly_id == anomaly_id
    assert not child.child_anomaly_ids

    response = await web_app_client.get(
        f'/api/v1/anomalies/{child_id}/change-history',
        params={'limit': 1, 'offset': 0},
    )
    assert response.status == 200
    response_data = await response.json()
    assert response_data['pagination']['total_items'] == 1
    change_history = response_data['change_history']
    assert change_history
    inserted_change_history_item = change_history[0]
    assert inserted_change_history_item
    assert inserted_change_history_item['start_ts'] == 1593186300
    assert inserted_change_history_item['end_ts'] == 1593186900
    assert inserted_change_history_item['status'] == 'confirmed'
    assert inserted_change_history_item['level'] == 'minor'
    assert inserted_change_history_item['source'] == 'uber'
    assert inserted_change_history_item['author'] == 'omnipotent_user'
    assert inserted_change_history_item['description'] == 'ratatat'
    assert (
        inserted_change_history_item['duty_task']
        == 'https://st.yandex-team.ru/ATLASBACK-1527'
    )


@pytest.mark.config(
    ATLAS_BACKEND_ANOMALY_HIERARCHY=[
        {'parent_name': 'all', 'source_name': 'uber'},
    ],
)
async def test_create_anomaly_hierarchical_not_confirmed(
        web_app_client, atlas_blackbox_mock, web_context,
):
    response = await web_app_client.post(
        '/api/v1/anomalies',
        json={
            'start_ts': 1593186300,
            'end_ts': 1593186900,
            'status': 'rejected',
            'level': 'minor',
            'source': 'all',
            'description': 'ratatat',
            'duty_task': 'https://st.yandex-team.ru/ATLASBACK-1527',
            'losses': {'orders': -200},
        },
    )
    assert response.status == 201
    anomaly_id = await response.json()

    storage = _anomaly_storage.AnomalyStorage.from_context(web_context)
    inserted = await storage.get(anomaly_id)

    assert inserted is not None
    assert inserted.start_ts == 1593186300
    assert inserted.end_ts == 1593186900
    assert inserted.status.value == 'rejected'
    assert inserted.severity_level.value == 'minor'
    assert inserted.order_source.value == 'all'
    assert inserted.author == 'omnipotent_user'
    assert inserted.losses == {'orders': -200}
    assert inserted.description == 'ratatat'
    assert inserted.duty_task == 'https://st.yandex-team.ru/ATLASBACK-1527'
    assert inserted.parent_anomaly_id is None
    assert not inserted.child_anomaly_ids

    response = await web_app_client.get(
        f'/api/v1/anomalies/{anomaly_id}/change-history',
        params={'limit': 1, 'offset': 0},
    )
    assert response.status == 200
    response_data = await response.json()
    assert response_data['pagination']['total_items'] == 1
    change_history = response_data['change_history']
    assert change_history
    inserted_change_history_item = change_history[0]
    assert inserted_change_history_item
    assert inserted_change_history_item['start_ts'] == 1593186300
    assert inserted_change_history_item['end_ts'] == 1593186900
    assert inserted_change_history_item['status'] == 'rejected'
    assert inserted_change_history_item['level'] == 'minor'
    assert inserted_change_history_item['source'] == 'all'
    assert inserted_change_history_item['author'] == 'omnipotent_user'
    assert inserted_change_history_item['description'] == 'ratatat'
    assert (
        inserted_change_history_item['duty_task']
        == 'https://st.yandex-team.ru/ATLASBACK-1527'
    )


@pytest.mark.config(
    ATLAS_BACKEND_ANOMALY_HIERARCHY=[
        {'parent_name': 'all', 'source_name': 'uber'},
    ],
)
async def test_create_anomaly_atomicity(
        monkeypatch, mock, web_app_client, atlas_blackbox_mock, web_context,
):
    @mock
    async def mock_create(*args, **kwargs):
        raise _change_history.AnomalyChangeHistoryStorageError(
            'Write operation was interrupted due to timeout',
        )

    monkeypatch.setattr(
        _change_history.AnomalyChangeHistoryStorage, 'create', mock_create,
    )

    response = await web_app_client.post(
        '/api/v1/anomalies',
        json={
            'start_ts': 1593186300,
            'end_ts': 1593186900,
            'status': 'rejected',
            'level': 'minor',
            'source': 'all',
            'description': 'ratatat',
            'duty_task': 'https://st.yandex-team.ru/ATLASBACK-1527',
            'losses': {'orders': -200},
        },
    )
    response_data = await response.json()
    assert response.status == 400
    assert (
        response_data['message']
        == 'Write operation was interrupted due to timeout'
    )


@pytest.mark.usefixtures('freeze')
@pytest.mark.parametrize(
    'update, expected_result',
    [
        (
            {
                'start_ts': 1593181520,
                'end_ts': 1593186537,
                'status': 'rejected',
                'level': 'major',
                'source': 'all',
                'description': 'new description',
                'duty_task': 'https://st.yandex-team.ru/ATLASBACK-1527',
            },
            {
                '_id': '5e00b661954de74d8a6af7c7',
                'author': 'omnipotent_user',
                'created': 1593173520,
                'description': 'new description',
                'duty_task': 'https://st.yandex-team.ru/ATLASBACK-1527',
                'end_ts': 1593186537,
                'level': 'major',
                'losses': {'orders': -38},
                'notifications': {},
                'source': 'all',
                'start_ts': 1593181520,
                'status': 'rejected',
            },
        ),
        (
            {
                'start_ts': 1593181520,
                'end_ts': 1593186837,
                'status': 'confirmed',
                'level': 'minor',
                'source': 'callcenter',
                'description': 'new description',
                'duty_task': 'https://st.yandex-team.ru/ATLASBACK-1527',
            },
            {
                '_id': '5e00b661954de74d8a6af7c7',
                'author': 'omnipotent_user',
                'created': 1593173520,
                'description': 'new description',
                'duty_task': 'https://st.yandex-team.ru/ATLASBACK-1527',
                'end_ts': 1593186837,
                'level': 'minor',
                'losses': {},  # losses are nullified
                'notifications': {},
                'source': 'callcenter',
                'start_ts': 1593181520,
                'status': 'confirmed',
            },
        ),
    ],
)
async def test_update_anomaly_simple(
        freeze, web_app_client, atlas_blackbox_mock, update, expected_result,
):
    anomaly_id = '5e00b661954de74d8a6af7c7'
    response = await web_app_client.post(
        f'/api/v1/anomalies/{anomaly_id}', json=update,
    )
    assert response.status == 204

    changed_response = await web_app_client.get(
        f'/api/v1/anomalies/{anomaly_id}',
    )
    assert changed_response.status == 200
    changed_doc = await changed_response.json()

    del changed_doc['updated']
    assert changed_doc == expected_result

    response = await web_app_client.get(
        f'/api/v1/anomalies/{anomaly_id}/change-history',
        params={'limit': 1, 'offset': 0},
    )
    assert response.status == 200
    response_data = await response.json()
    assert response_data['pagination']['total_items'] == 1
    change_history = response_data['change_history']
    assert change_history
    inserted_change_history_item = change_history[0]
    assert inserted_change_history_item
    assert inserted_change_history_item['start_ts'] == update['start_ts']
    assert inserted_change_history_item['end_ts'] == update['end_ts']
    assert inserted_change_history_item['status'] == update['status']
    assert inserted_change_history_item['level'] == update['level']
    assert inserted_change_history_item['source'] == update['source']
    assert inserted_change_history_item['author'] == 'omnipotent_user'
    assert inserted_change_history_item['description'] == update['description']
    assert inserted_change_history_item['duty_task'] == update['duty_task']


async def test_update_anomaly_to_vezet(
        freeze, web_app_client, atlas_blackbox_mock,
):
    update = {
        'start_ts': 1593181520,
        'end_ts': 1593186537,
        'status': 'rejected',
        'level': 'major',
        'source': 'vezet',
        'description': 'new description',
        'duty_task': 'https://st.yandex-team.ru/ATLASBACK-1527',
    }
    anomaly_id = '5e00b661954de74d8a6af7c7'
    response = await web_app_client.post(
        f'/api/v1/anomalies/{anomaly_id}', json=update,
    )
    assert response.status == 400, await response.text()
    result = await response.json()
    assert result == {
        'message': (
            '"vezet" source is deprecated. Could not change source to it.'
        ),
        'code': 'BadRequest',
    }


@pytest.mark.usefixtures('freeze')
@pytest.mark.config(
    ATLAS_BACKEND_ANOMALY_HIERARCHY=[
        {'parent_name': 'all', 'source_name': 'uber'},
    ],
)
@pytest.mark.parametrize(
    'anomaly_id, update, expected_result',
    [
        (
            '5e00b661954de74d8a6af7c7',
            {
                'start_ts': 1593181520,
                'end_ts': 1593186837,
                'status': 'confirmed',
                'level': 'minor',
                'source': 'all',
                'description': 'new description',
                'duty_task': 'https://st.yandex-team.ru/ATLASBACK-1527',
            },
            {
                'author': 'omnipotent_user',
                'created': 1593173520,
                'description': 'new description',
                'duty_task': 'https://st.yandex-team.ru/ATLASBACK-1527',
                'end_ts': 1593186837,
                'level': 'minor',
                'losses': {'orders': None},  # losses are nullified
                'notifications': {},
                'start_ts': 1593181520,
                'status': 'confirmed',
            },
        ),
        (
            '5e00b661954de74d8a6af7ce',
            {
                'start_ts': 1593181580,
                'end_ts': 1593186597,
                'status': 'confirmed',
                'level': 'minor',
                'source': 'all',
                'description': 'new description',
                'duty_task': None,
            },
            {
                'author': 'omnipotent_user',
                'created': 1593173520,
                'description': 'new description',
                'duty_task': None,
                'end_ts': 1593186597,
                'level': 'minor',
                'losses': {'orders': 122},
                'notifications': {},
                'start_ts': 1593181580,
                'status': 'confirmed',
            },
        ),
    ],
)
async def test_update_anomaly_hierarchical_with_create(
        freeze,
        web_app_client,
        atlas_blackbox_mock,
        anomaly_id,
        update,
        expected_result,
        web_context,
):
    response = await web_app_client.post(
        f'/api/v1/anomalies/{anomaly_id}', json=update,
    )
    assert response.status == 204

    storage = _anomaly_storage.AnomalyStorage.from_context(web_context)
    skip_fields = [
        '_id',
        'source',
        'child_anomaly_ids',
        'parent_anomaly_id',
        'updated',
    ]
    changed = await storage.get(anomaly_id)
    assert changed is not None
    assert changed.to_dict(skip_fields) == expected_result
    assert len(changed.child_anomaly_ids) == 1
    assert changed.order_source.value == 'all'

    expected_result['losses']['orders'] = None
    child_id = changed.child_anomaly_ids[0]
    child_anomaly = await storage.get(child_id)
    assert child_anomaly is not None
    assert child_anomaly.to_dict(skip_fields) == expected_result
    assert child_anomaly.order_source.value == 'uber'
    assert child_anomaly.parent_anomaly_id == anomaly_id

    response = await web_app_client.get(
        f'/api/v1/anomalies/{child_id}/change-history',
        params={'limit': 1, 'offset': 0},
    )
    assert response.status == 200
    response_data = await response.json()
    assert response_data['pagination']['total_items'] == 1
    change_history = response_data['change_history']
    assert change_history
    inserted_change_history_item = change_history[0]
    assert inserted_change_history_item
    assert inserted_change_history_item['start_ts'] == update['start_ts']
    assert inserted_change_history_item['end_ts'] == update['end_ts']
    assert inserted_change_history_item['status'] == update['status']
    assert inserted_change_history_item['level'] == update['level']
    assert inserted_change_history_item['source'] == 'uber'
    assert inserted_change_history_item['author'] == 'omnipotent_user'
    assert inserted_change_history_item['description'] == update['description']


@pytest.mark.usefixtures('freeze')
@pytest.mark.config(
    ATLAS_BACKEND_ANOMALY_HIERARCHY=[
        {'parent_name': 'all', 'source_name': 'callcenter'},
        {'parent_name': 'all', 'source_name': 'uber'},
    ],
)
@pytest.mark.parametrize(
    'update, expected_result',
    [
        (
            {
                'start_ts': 1593173520,
                'end_ts': 1593178520,
                'status': 'rejected',
                'level': 'minor',
                'description': 'new description',
                'duty_task': 'https://st.yandex-team.ru/ATLASBACK-1527',
                'source': 'all',
            },
            {
                'author': 'omnipotent_user',
                'created': 1593173520,
                'description': 'new description',
                'duty_task': 'https://st.yandex-team.ru/ATLASBACK-1527',
                'end_ts': 1593178520,
                'level': 'minor',
                'losses': {'orders': 100000},
                'notifications': {},
                'start_ts': 1593173520,
                'status': 'rejected',
                'source': 'all',
            },
        ),
    ],
)
async def test_update_anomaly_hierarchical(
        freeze,
        web_app_client,
        atlas_blackbox_mock,
        update,
        expected_result,
        web_context,
):
    anomaly_id = '5e00b661954de74d8a6af7c8'
    child_id = '5e00b661954de74d8a6af7cd'
    response = await web_app_client.post(
        f'/api/v1/anomalies/{anomaly_id}', json=update,
    )
    assert response.status == 204

    storage = _anomaly_storage.AnomalyStorage.from_context(web_context)
    skip_fields = ['_id', 'child_anomaly_ids', 'parent_anomaly_id', 'updated']
    changed = await storage.get(anomaly_id)
    assert changed is not None
    assert changed.to_dict(skip_fields) == expected_result

    # Хотя в конфиге прописана 2 дочерних источника для all
    # мы не создаем новых детей, если уже были старые
    assert changed.child_anomaly_ids == [child_id]

    child_expected_result = expected_result
    child_expected_result['losses'] = {'orders': 1000}
    child_expected_result['source'] = 'callcenter'

    child_anomaly = await storage.get(child_id)
    assert child_anomaly is not None
    assert child_anomaly.to_dict(skip_fields) == expected_result
    assert child_anomaly.parent_anomaly_id == anomaly_id

    response = await web_app_client.get(
        f'/api/v1/anomalies/{child_id}/change-history',
        params={'limit': 1, 'offset': 0},
    )
    assert response.status == 200
    response_data = await response.json()
    assert response_data['pagination']['total_items'] == 1
    change_history = response_data['change_history']
    assert change_history
    inserted_change_history_item = change_history[0]
    assert inserted_change_history_item
    assert inserted_change_history_item['start_ts'] == update['start_ts']
    assert inserted_change_history_item['end_ts'] == update['end_ts']
    assert inserted_change_history_item['status'] == update['status']
    assert inserted_change_history_item['level'] == update['level']
    assert inserted_change_history_item['source'] == 'callcenter'
    assert inserted_change_history_item['author'] == 'omnipotent_user'
    assert inserted_change_history_item['description'] == update['description']
    assert inserted_change_history_item['duty_task'] == update['duty_task']


@pytest.mark.usefixtures('freeze')
@pytest.mark.config(
    ATLAS_BACKEND_ANOMALY_HIERARCHY=[
        {'parent_name': 'all', 'source_name': 'callcenter'},
        {'parent_name': 'all', 'source_name': 'uber'},
    ],
)
@pytest.mark.parametrize(
    'update, expected_result',
    [
        (
            {
                'start_ts': 1593173520,
                'end_ts': 1593178520,
                'status': 'rejected',
                'level': 'minor',
                'description': 'new description',
                'duty_task': 'https://st.yandex-team.ru/ATLASBACK-1527',
                'source': 'callcenter',
            },
            {
                'author': 'omnipotent_user',
                'created': 1593173520,
                'description': 'new description',
                'duty_task': 'https://st.yandex-team.ru/ATLASBACK-1527',
                'end_ts': 1593178520,
                'level': 'minor',
                'losses': {'orders': 100000},
                'notifications': {},
                'start_ts': 1593173520,
                'status': 'rejected',
                'source': 'callcenter',
                'child_anomaly_ids': [],
            },
        ),
    ],
)
async def test_update_anomaly_change_source_to_child(
        freeze,
        web_app_client,
        atlas_blackbox_mock,
        update,
        expected_result,
        web_context,
):
    anomaly_id = '5e00b661954de74d8a6af7c8'
    child_id = '5e00b661954de74d8a6af7cd'
    response = await web_app_client.post(
        f'/api/v1/anomalies/{anomaly_id}', json=update,
    )
    assert response.status == 204

    storage = _anomaly_storage.AnomalyStorage.from_context(web_context)
    skip_fields = ['_id', 'parent_anomaly_id', 'updated']
    changed = await storage.get(anomaly_id)
    assert changed is not None
    assert changed.to_dict(skip_fields) == expected_result

    child_anomaly = await storage.get(child_id)
    assert child_anomaly is None  # deleted


@pytest.mark.usefixtures('freeze')
@pytest.mark.config(
    ATLAS_BACKEND_ANOMALY_HIERARCHY=[
        {'parent_name': 'all', 'source_name': 'callcenter'},
        {'parent_name': 'all', 'source_name': 'yango'},
    ],
)
@pytest.mark.parametrize(
    'update, expected_result',
    [
        (
            {
                'start_ts': 1593173520,
                'end_ts': 1593178520,
                'status': 'rejected',
                'level': 'minor',
                'description': 'new description',
                'duty_task': '',
                'source': 'all',
            },
            {
                'author': 'omnipotent_user',
                'created': 1593173520,
                'description': 'new description',
                'duty_task': '',
                'end_ts': 1593178520,
                'level': 'minor',
                'losses': {'orders': None},
                'notifications': {},
                'start_ts': 1593173520,
                'status': 'rejected',
                'source': 'all',
            },
        ),
    ],
)
async def test_update_anomaly_change_source_to_parent(
        freeze,
        web_app_client,
        atlas_blackbox_mock,
        update,
        expected_result,
        web_context,
):
    anomaly_id = '5e00b661954de74d8a6af7cb'
    response = await web_app_client.post(
        f'/api/v1/anomalies/{anomaly_id}', json=update,
    )
    assert response.status == 204

    storage = _anomaly_storage.AnomalyStorage.from_context(web_context)
    skip_fields = ['_id', 'parent_anomaly_id', 'updated', 'child_anomaly_ids']
    changed = await storage.get(anomaly_id)
    assert changed is not None
    assert changed.to_dict(skip_fields) == expected_result
    assert len(changed.child_anomaly_ids) == 2

    for child_anomaly_id, source in zip(
            changed.child_anomaly_ids, ['callcenter', 'yango'],
    ):
        response = await web_app_client.get(
            f'/api/v1/anomalies/{child_anomaly_id}/change-history',
            params={'limit': 1, 'offset': 0},
        )
        assert response.status == 200
        response_data = await response.json()
        assert response_data['pagination']['total_items'] == 1
        change_history = response_data['change_history']
        assert change_history
        inserted_change_history_item = change_history[0]
        assert inserted_change_history_item
        assert inserted_change_history_item['start_ts'] == update['start_ts']
        assert inserted_change_history_item['end_ts'] == update['end_ts']
        assert inserted_change_history_item['status'] == update['status']
        assert inserted_change_history_item['level'] == update['level']
        assert inserted_change_history_item['source'] == source
        assert inserted_change_history_item['author'] == 'omnipotent_user'
        assert (
            inserted_change_history_item['description']
            == update['description']
        )
        assert inserted_change_history_item['duty_task'] == update['duty_task']


@pytest.mark.usefixtures('freeze')
@pytest.mark.config(
    ATLAS_BACKEND_ANOMALY_HIERARCHY=[
        {'parent_name': 'all', 'source_name': 'callcenter'},
        {'parent_name': 'all', 'source_name': 'uber'},
    ],
)
async def test_update_anomaly_hierarchical_with_parent(
        freeze, web_app_client, atlas_blackbox_mock,
):
    update = {
        'start_ts': 1593173520,
        'end_ts': 1593178520,
        'status': 'rejected',
        'level': 'minor',
        'description': 'new description',
        'duty_task': 'https://st.yandex-team.ru/ATLASBACK-1527',
        'source': 'callcenter',
    }
    child_id = '5e00b661954de74d8a6af7cd'
    response = await web_app_client.post(
        f'/api/v1/anomalies/{child_id}', json=update,
    )
    assert response.status == 400


@pytest.mark.usefixtures('freeze')
@pytest.mark.parametrize(
    'update, expected_result',
    [
        (
            {
                'start_ts': 1593173540,
                'end_ts': 1593178570,
                'status': 'created',
                'level': 'major',
                'source': 'yango',
            },
            {
                'author': 'some-user',
                'created': 1593173520,
                'description': '',
                'duty_task': '',
                'end_ts': 1593186597,
                'level': 'minor',
                'losses': {'orders': None},
                'notifications': {},
                'start_ts': 1593181580,
                'status': 'created',
                'source': 'all',
            },
        ),
        (
            {
                'start_ts': 1593173520,
                'end_ts': 1593178520,
                'status': 'rejected',
                'level': 'unknown',
                'description': 'new description',
                'duty_task': 'https://st.yandex-team.ru/ATLASBACK-1527',
                'source': 'all',
            },
            {
                'author': 'some-user',
                'created': 1593173520,
                'description': '',
                'duty_task': '',
                'end_ts': 1593186597,
                'level': 'minor',
                'losses': {'orders': None},
                'notifications': {},
                'start_ts': 1593181580,
                'status': 'created',
                'source': 'all',
            },
        ),
    ],
)
async def test_update_anomaly_simple_atomicity(
        freeze,
        monkeypatch,
        mock,
        web_app_client,
        atlas_blackbox_mock,
        web_context,
        update,
        expected_result,
):
    @mock
    async def mock_create(*args, **kwargs):
        raise _change_history.AnomalyChangeHistoryStorageError(
            'Write operation was interrupted due to timeout',
        )

    monkeypatch.setattr(
        _change_history.AnomalyChangeHistoryStorage, 'create', mock_create,
    )

    anomaly_id = '5e00b661954de74d8a6af7ce'
    response = await web_app_client.post(
        f'/api/v1/anomalies/{anomaly_id}', json=update,
    )
    assert response.status == 400
    response_data = await response.json()
    assert (
        response_data['message']
        == 'Write operation was interrupted due to timeout'
    )

    storage = _anomaly_storage.AnomalyStorage.from_context(web_context)
    skip_fields = ['_id', 'parent_anomaly_id', 'updated', 'child_anomaly_ids']
    anomaly = await storage.get(anomaly_id)
    assert anomaly is not None
    assert anomaly.to_dict(skip_fields) == expected_result


@pytest.mark.usefixtures('freeze')
@pytest.mark.config(
    ATLAS_BACKEND_ANOMALY_HIERARCHY=[
        {'parent_name': 'all', 'source_name': 'callcenter'},
    ],
)
@pytest.mark.parametrize(
    'anomaly_id, update, expected_result, has_child_anomaly_ids',
    [
        (
            '5e00b661954de74d8a6af7c7',
            {
                'start_ts': 1593181520,
                'end_ts': 1593186837,
                'status': 'confirmed',
                'level': 'minor',
                'source': 'callcenter',
                'description': 'new description',
                'duty_task': 'https://st.yandex-team.ru/ATLASBACK-1527',
            },
            {
                'author': 'some-user',
                'created': 1593173520,
                'description': '',
                'duty_task': 'https://st.yandex-team.ru/ATLASBACK-1527',
                'end_ts': 1593186537,
                'level': 'minor',
                'source': 'all',
                'losses': {'orders': None},
                'notifications': {},
                'start_ts': 1593181520,
                'status': 'confirmed',
            },
            True,
        ),
        (
            '5e00b661954de74d8a6af7ce',
            {
                'start_ts': 1593181580,
                'end_ts': 1593186597,
                'status': 'confirmed',
                'level': 'minor',
                'source': 'all',
                'description': 'new description',
                'duty_task': None,
            },
            {
                'author': 'some-user',
                'created': 1593173520,
                'description': '',
                'duty_task': '',
                'end_ts': 1593186597,
                'level': 'minor',
                'source': 'all',
                'losses': {'orders': 122},
                'notifications': {},
                'start_ts': 1593181580,
                'status': 'created',
            },
            True,
        ),
        (
            '5e00b661954de74d8a6af7c9',
            {
                'start_ts': 1593181580,
                'end_ts': 1593186597,
                'status': 'confirmed',
                'level': 'minor',
                'source': 'all',
                'description': 'new description',
                'duty_task': None,
            },
            {
                'author': 'robot-atlas',
                'created': 1593173520,
                'description': 'Something gone very very bad',
                'duty_task': 'https://st.yandex-team.ru/ATLASBACK-1527',
                'end_ts': 1593177520,
                'level': 'major',
                'source': 'lavka',
                'losses': {'orders': None},
                'notifications': {},
                'start_ts': 1593174520,
                'status': 'confirmed',
            },
            False,
        ),
    ],
)
async def test_update_anomaly_hierarchical_with_create_atomicity(
        freeze,
        monkeypatch,
        mock,
        web_app_client,
        atlas_blackbox_mock,
        web_context,
        anomaly_id,
        update,
        expected_result,
        has_child_anomaly_ids,
):
    @mock
    async def mock_create(*args, **kwargs):
        raise _change_history.AnomalyChangeHistoryStorageError(
            'Write operation was interrupted due to timeout',
        )

    monkeypatch.setattr(
        _change_history.AnomalyChangeHistoryStorage, 'create', mock_create,
    )

    response = await web_app_client.post(
        f'/api/v1/anomalies/{anomaly_id}', json=update,
    )
    assert response.status == 400
    response_data = await response.json()
    assert (
        response_data['message']
        == 'Write operation was interrupted due to timeout'
    )

    storage = _anomaly_storage.AnomalyStorage.from_context(web_context)
    skip_fields = ['_id', 'parent_anomaly_id', 'updated', 'child_anomaly_ids']
    anomaly = await storage.get(anomaly_id)
    assert anomaly is not None
    assert anomaly.to_dict(skip_fields) == expected_result
    assert bool(anomaly.child_anomaly_ids) is has_child_anomaly_ids


@pytest.mark.usefixtures('freeze')
@pytest.mark.config(
    ATLAS_BACKEND_ANOMALY_HIERARCHY=[
        {'parent_name': 'all', 'source_name': 'callcenter'},
        {'parent_name': 'all', 'source_name': 'uber'},
    ],
)
@pytest.mark.parametrize(
    'update, expected_result',
    [
        (
            {
                'start_ts': 1593173520,
                'end_ts': 1593178520,
                'status': 'rejected',
                'level': 'minor',
                'description': 'new description',
                'duty_task': 'https://st.yandex-team.ru/ATLASBACK-1527',
                'source': 'all',
            },
            {
                'author': 'robot-atlas',
                'created': 1593173520,
                'description': 'Something gone very very bad',
                'duty_task': 'https://st.yandex-team.ru/ATLASBACK-1527',
                'end_ts': 1593178520,
                'level': 'major',
                'losses': {'orders': 100000},
                'notifications': {},
                'start_ts': 1593173520,
                'status': 'confirmed',
                'source': 'all',
            },
        ),
    ],
)
async def test_update_anomaly_hierarchical_atomicity(
        freeze,
        monkeypatch,
        mock,
        web_app_client,
        atlas_blackbox_mock,
        update,
        expected_result,
        web_context,
):
    @mock
    async def mock_create(*args, **kwargs):
        raise _change_history.AnomalyChangeHistoryStorageError(
            'Write operation was interrupted due to timeout',
        )

    monkeypatch.setattr(
        _change_history.AnomalyChangeHistoryStorage, 'create', mock_create,
    )

    anomaly_id = '5e00b661954de74d8a6af7c8'
    child_id = '5e00b661954de74d8a6af7cd'
    response = await web_app_client.post(
        f'/api/v1/anomalies/{anomaly_id}', json=update,
    )
    assert response.status == 400
    response_data = await response.json()
    assert (
        response_data['message']
        == 'Write operation was interrupted due to timeout'
    )

    storage = _anomaly_storage.AnomalyStorage.from_context(web_context)
    skip_fields = ['_id', 'parent_anomaly_id', 'updated', 'child_anomaly_ids']
    anomaly = await storage.get(anomaly_id)
    assert anomaly is not None
    assert anomaly.to_dict(skip_fields) == expected_result
    assert anomaly.child_anomaly_ids == [child_id]


@pytest.mark.usefixtures('freeze')
@pytest.mark.config(
    ATLAS_BACKEND_ANOMALY_HIERARCHY=[
        {'parent_name': 'lavka', 'source_name': 'callcenter'},
        {'parent_name': 'lavka', 'source_name': 'uber'},
    ],
)
@pytest.mark.parametrize(
    'update_with_parent, update_without_parent',
    [
        (
            {
                'start_ts': 1593173520,
                'end_ts': 1593178520,
                'status': 'confirmed',
                'level': 'minor',
                'description': 'new description',
                'duty_task': 'https://st.yandex-team.ru/ATLASBACK-1527',
                'source': 'lavka',
            },
            {
                'start_ts': 1593173520,
                'end_ts': 1593178520,
                'status': 'rejected',
                'level': 'minor',
                'description': 'new description',
                'duty_task': 'https://st.yandex-team.ru/ATLASBACK-1527',
                'source': 'callcenter',
            },
        ),
    ],
)
async def test_update_anomaly_change_history_durability(
        freeze,
        web_app_client,
        atlas_blackbox_mock,
        update_with_parent,
        update_without_parent,
        web_context,
):
    anomaly_id = '5e00b661954de74d8a6af7c8'
    response = await web_app_client.post(
        f'/api/v1/anomalies/{anomaly_id}', json=update_with_parent,
    )
    assert response.status == 204

    storage = _anomaly_storage.AnomalyStorage.from_context(web_context)
    changed = await storage.get(anomaly_id)
    assert changed is not None
    assert len(changed.child_anomaly_ids) == 2
    child_anomaly_ids = changed.child_anomaly_ids

    response = await web_app_client.post(
        f'/api/v1/anomalies/{anomaly_id}', json=update_without_parent,
    )
    assert response.status == 204

    storage = _anomaly_storage.AnomalyStorage.from_context(web_context)
    changed = await storage.get(anomaly_id)
    assert changed is not None
    assert not changed.child_anomaly_ids

    change_history_storage = (
        _change_history.AnomalyChangeHistoryStorage.from_context(web_context)
    )

    for child_anomaly_id, source in zip(
            child_anomaly_ids, ['callcenter', 'uber'],
    ):
        child_anomaly = await storage.get(child_anomaly_id)
        assert child_anomaly is None
        items = await change_history_storage.get_items_by_anomaly_id(
            child_anomaly_id, limit=1, offset=0,
        )
        assert items
        inserted_change_history_item = items[0]
        assert inserted_change_history_item.start_ts == 1593173520
        assert inserted_change_history_item.end_ts == 1593178520
        assert inserted_change_history_item.status == 'confirmed'
        assert inserted_change_history_item.level == 'minor'
        assert inserted_change_history_item.description == 'new description'
        assert (
            inserted_change_history_item.duty_task
            == 'https://st.yandex-team.ru/ATLASBACK-1527'
        )
        assert inserted_change_history_item.source == source


@pytest.mark.config(
    ATLAS_GRANULARITY_MAPPING={'plot': {'7': None}},
    ATLAS_BACKEND_ANOMALY_LOSS_METRICS={'all': 'anomaly_trips_taxi_all'},
)
async def test_downtime_info(
        clickhouse_client_mock, web_app_client, atlas_blackbox_mock, patch,
):
    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        async def _result():
            data = [
                (('atlas_ts', 'UInt64'), ('value', 'UInt64')),
                (1593172980, 900000),
            ]
            for item in data:
                yield item

        return _result()

    response = await web_app_client.post(
        '/api/v1/anomalies/downtime-info',
        json={'start_ts': 1593173000, 'end_ts': 1593178999, 'source': 'all'},
    )
    assert response.status == 200

    content = await response.json()
    assert content == {
        'confirmed_problem_time': 83,
        'total_time': 101,
        'uptime': 17.475,
        'orders_lost': 100000,
        'orders_successful': 900000,
        'orders_uptime': 90.0,
    }


@pytest.mark.config(
    ATLAS_GRANULARITY_MAPPING={'plot': {'7': None}},
    ATLAS_BACKEND_ANOMALY_LOSS_METRICS={'all': 'anomaly_trips_taxi_all'},
)
async def test_downtime_info_with_exceeded_timeout(
        clickhouse_client_mock, web_app_client, atlas_blackbox_mock, patch,
):
    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        raise clickhouse_errors.ServerException(
            message='', code=clickhouse_errors.ErrorCodes.TIMEOUT_EXCEEDED,
        )

    response = await web_app_client.post(
        '/api/v1/anomalies/downtime-info',
        json={'start_ts': 1593173000, 'end_ts': 1593178999, 'source': 'all'},
    )
    assert response.status == 400
    content = await response.json()
    assert content == {
        'code': 'BadRequest::TooLongTimeSpan',
        'message': 'Too long time span',
    }


@pytest.mark.config(
    ATLAS_GRANULARITY_MAPPING={'plot': {'10': 60}},
    ATLAS_BACKEND_ANOMALY_PLOT={
        'all': {'metric_ids': ['anomaly_trips_taxi_all']},
    },
)
async def test_get_anomaly_plot(
        clickhouse_client_mock, web_app_client, patch, atlas_blackbox_mock,
):
    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        async def _result():
            data = [
                (('atlas_ts', 'UInt64'), ('value', 'UInt64')),
                (1608012180, 4),
                (1608012120, 138),
                (1608012000, 140),
                (1608012060, 158),
            ]
            for item in data:
                yield item

        return _result()

    result = await web_app_client.post(
        '/api/v1/anomalies/plot',
        json={
            'car_class': 'any',
            'city': [],
            'date_from': 1608012000,
            'date_to': 1608012180,
            'granularity': '10',
            'metric': 'anomaly_trips_taxi_all',
            'offset_time': False,
            'quadkeys': None,
            'utcoffset': 3,
            'wow': '0',
            'polygons': None,
        },
    )
    assert result.status == 200
    data = await result.json()
    expected = [
        [
            [1608012000, 140.0],
            [1608012060, 158.0],
            [1608012120, 138.0],
            [1608012180, 4.0],
        ],
    ]
    assert data == expected


@pytest.mark.config(ATLAS_GRANULARITY_MAPPING={'plot': {'10': 60}})
async def test_get_anomaly_plot_not_in_whitelist(
        clickhouse_client_mock, web_app_client, patch, atlas_blackbox_mock,
):
    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        async def _result():
            data = [
                (('atlas_ts', 'UInt64'), ('value', 'UInt64')),
                (1608012180, 4),
            ]
            for item in data:
                yield item

        return _result()

    result = await web_app_client.post(
        '/api/v1/anomalies/plot',
        json={
            'car_class': 'any',
            'city': [],
            'date_from': 1608012000,
            'date_to': 1608012180,
            'granularity': '10',
            'metric': 'requests_share_found',
            'offset_time': False,
            'quadkeys': None,
            'utcoffset': 3,
            'wow': '0',
            'polygons': None,
        },
    )
    assert result.status == 400


@pytest.mark.config(ATLAS_GRANULARITY_MAPPING={'plot': {'10': 60}})
async def test_get_anomaly_plot_city_specification(
        clickhouse_client_mock, web_app_client, patch, atlas_blackbox_mock,
):
    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        async def _result():
            data = [
                (('atlas_ts', 'UInt64'), ('value', 'UInt64')),
                (1608012180, 4),
            ]
            for item in data:
                yield item

        return _result()

    result = await web_app_client.post(
        '/api/v1/anomalies/plot',
        json={
            'car_class': 'any',
            'city': 'Казань',
            'date_from': 1608012000,
            'date_to': 1608012180,
            'granularity': '10',
            'metric': 'anomaly_trips_taxi_all',
            'offset_time': False,
            'quadkeys': None,
            'utcoffset': 3,
            'wow': '0',
            'polygons': None,
        },
    )
    assert result.status == 400


@pytest.mark.config(
    ATLAS_GRANULARITY_MAPPING={'plot': {'10': 60}},
    ATLAS_BACKEND_ANOMALY_PLOT={
        'all': {'metric_ids': ['anomaly_trips_taxi_all']},
    },
)
async def test_get_anomaly_plot_with_exceeded_timeout(
        clickhouse_client_mock, web_app_client, patch, atlas_blackbox_mock,
):
    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        raise clickhouse_errors.ServerException(
            message='', code=clickhouse_errors.ErrorCodes.TIMEOUT_EXCEEDED,
        )

    response = await web_app_client.post(
        '/api/v1/anomalies/plot',
        json={
            'car_class': 'any',
            'city': [],
            'date_from': 1608012000,
            'date_to': 1608012180,
            'granularity': '10',
            'metric': 'anomaly_trips_taxi_all',
            'offset_time': False,
            'quadkeys': None,
            'utcoffset': 3,
            'wow': '0',
            'polygons': None,
        },
    )
    assert response.status == 400
    content = await response.json()
    assert content == {
        'code': 'BadRequest::TooLongTimeSpan',
        'message': 'Too long time span',
    }


@pytest.mark.config(
    ATLAS_BACKEND_ANOMALY_PLOT={
        'all': {
            'metric_ids': [
                'anomaly_trips_taxi_all',
                'anomaly_driver_cancel_taxi_all',
                'anomaly_user_cancel_taxi_all',
            ],
        },
        'yataxi': {'metric_ids': []},
    },
)
async def test_get_anomaly_plot_config(web_app_client):
    result = await web_app_client.get('/api/v1/anomalies/plot-config')
    assert result.status == 200
    contents = await result.json()
    assert contents['all']['metrics'] == [
        'anomaly_trips_taxi_all',
        'anomaly_driver_cancel_taxi_all',
        'anomaly_user_cancel_taxi_all',
    ]
    assert contents['yataxi']['metrics'] == []
    assert contents['callcenter']['metrics'] == []  # default value


@pytest.mark.config(
    ATLAS_BACKEND_ANOMALY_HIERARCHY=[
        {'parent_name': 'all', 'source_name': 'yango'},
        {'parent_name': 'all', 'source_name': 'callcenter'},
    ],
)
async def test_check_intersection(web_app_client, atlas_blackbox_mock):
    response = await web_app_client.post(
        '/api/v1/anomalies/check-intersection',
        json={'start_ts': 1593129600, 'end_ts': 1593180300, 'source': 'all'},
    )
    assert response.status == 200
    content = await response.json()

    assert len(content['anomalies']) == 2


@pytest.mark.config(
    ATLAS_BACKEND_ANOMALY_HIERARCHY=[
        {'parent_name': 'all', 'source_name': 'yango'},
        {'parent_name': 'all', 'source_name': 'callcenter'},
    ],
)
async def test_check_intersection_with_id(web_app_client, atlas_blackbox_mock):
    response = await web_app_client.post(
        '/api/v1/anomalies/check-intersection',
        json={
            'start_ts': 1593129600,
            'end_ts': 1593178400,
            'source': 'all',
            'anomaly_id': '5e00b661954de74d8a6af7c8',
        },
    )
    assert response.status == 200
    content = await response.json()

    assert not content['anomalies']


@pytest.mark.config(
    ATLAS_BACKEND_ANOMALY_HIERARCHY=[
        {'parent_name': 'all', 'source_name': 'yango'},
        {'parent_name': 'all', 'source_name': 'callcenter'},
    ],
)
async def test_check_intersection_sublevel(
        web_app_client, atlas_blackbox_mock,
):
    response = await web_app_client.post(
        '/api/v1/anomalies/check-intersection',
        json={
            'start_ts': 1593129600,
            'end_ts': 1593178400,
            'source': 'callcenter',
        },
    )
    assert response.status == 200
    content = await response.json()

    assert len(content['anomalies']) == 1
    anomaly = content['anomalies'][0]
    assert anomaly['_id'] == '5e00b661954de74d8a6af7cd'
    assert anomaly['source'] == 'callcenter'
