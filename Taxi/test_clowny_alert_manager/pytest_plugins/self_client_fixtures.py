from typing import Optional

import pytest
import typing_extensions


DRAFT_API_TYPE = typing_extensions.Literal['check', 'apply']


@pytest.fixture
def get_service(taxi_clowny_alert_manager_web):
    async def _do_it(service_id, status=200):
        response = await taxi_clowny_alert_manager_web.get(
            '/v1/services/get/', params={'id': service_id},
        )
        assert response.status == status, await response.text()
        return await response.json()

    return _do_it


@pytest.fixture
def upsert_service(taxi_clowny_alert_manager_web):
    async def _do_it(
            data, status=200, draft_api_type: Optional[DRAFT_API_TYPE] = None,
    ):
        url = '/v1/services/upsert/'
        if draft_api_type:
            url = f'{url}{draft_api_type}/'
        response = await taxi_clowny_alert_manager_web.post(url, json=data)
        assert response.status == status, await response.text()
        return await response.json()

    return _do_it


@pytest.fixture
def delete_service(taxi_clowny_alert_manager_web):
    async def _do_it(service_id, status=200):
        response = await taxi_clowny_alert_manager_web.post(
            '/v1/services/delete/', params={'id': service_id},
        )
        assert response.status == status, await response.text()
        return await response.json()

    return _do_it


@pytest.fixture
def get_template(taxi_clowny_alert_manager_web):
    async def _do_it(tmpl_id, status=200):
        response = await taxi_clowny_alert_manager_web.get(
            '/v1/templates/get/', params={'id': tmpl_id},
        )
        assert response.status == status, await response.text()
        return await response.json()

    return _do_it


@pytest.fixture
def upsert_template(taxi_clowny_alert_manager_web):
    async def _do_it(data, status=200):
        response = await taxi_clowny_alert_manager_web.post(
            '/v1/templates/upsert/', json=data,
        )
        assert response.status == status, await response.text()
        return await response.json()

    return _do_it


@pytest.fixture
def delete_template(taxi_clowny_alert_manager_web):
    async def _do_it(tmpl_id, status=200):
        response = await taxi_clowny_alert_manager_web.post(
            '/v1/templates/delete/', params={'id': tmpl_id},
        )
        assert response.status == status, await response.text()
        return await response.json()

    return _do_it


@pytest.fixture
def upsert_event(taxi_clowny_alert_manager_web):
    async def _do_it(data, status=200):
        response = await taxi_clowny_alert_manager_web.post(
            '/v1/events/upsert/', json=data,
        )
        assert response.status == status, await response.text()
        return await response.json()

    return _do_it


@pytest.fixture
def delete_event(taxi_clowny_alert_manager_web):
    async def _do_it(event_id, status=200):
        response = await taxi_clowny_alert_manager_web.post(
            '/v1/events/delete/', params={'id': event_id},
        )
        assert response.status == status, await response.text()
        return await response.json()

    return _do_it


@pytest.fixture
def get_notification_option(taxi_clowny_alert_manager_web):
    async def _do_it(no_id, status=200):
        response = await taxi_clowny_alert_manager_web.get(
            '/v1/notification-options/get/', params={'id': no_id},
        )
        assert response.status == status, await response.text()
        return await response.json()

    return _do_it


@pytest.fixture
def get_notification_options_list(taxi_clowny_alert_manager_web):
    async def _do_it(filters: dict, status=200):
        response = await taxi_clowny_alert_manager_web.post(
            '/v1/notification-options/list/', json=filters,
        )
        assert response.status == status, await response.text()
        return await response.json()

    return _do_it


@pytest.fixture
def delete_notification_option(taxi_clowny_alert_manager_web):
    async def _do_it(no_id, status=200):
        response = await taxi_clowny_alert_manager_web.post(
            '/v1/notification-options/delete/', params={'id': no_id},
        )
        assert response.status == status, await response.text()
        return await response.json()

    return _do_it


@pytest.fixture
def upsert_notification_option(taxi_clowny_alert_manager_web):
    async def _do_it(data, status=200):
        response = await taxi_clowny_alert_manager_web.post(
            '/v1/notification-options/upsert/', json=data,
        )
        assert response.status == status, await response.text()
        return await response.json()

    return _do_it


@pytest.fixture
def get_configs_queue_list(taxi_clowny_alert_manager_web):
    async def _do_it(service_id: int, status=200):
        response = await taxi_clowny_alert_manager_web.get(
            '/v1/configs/queue/list/', params={'service_id': service_id},
        )
        assert response.status == status, await response.text()
        return await response.json()

    return _do_it


@pytest.fixture
def get_recipients_suggest(taxi_clowny_alert_manager_web):
    async def _do_it(params, status=200):
        response = await taxi_clowny_alert_manager_web.get(
            '/v1/recipients/suggest/', params=params,
        )
        assert response.status == status, await response.text()
        return await response.json()

    return _do_it


@pytest.fixture
def get_services_duty_group(taxi_clowny_alert_manager_web):
    async def _do_it(params, status=200):
        response = await taxi_clowny_alert_manager_web.get(
            '/v1/services/duty-group/', params=params,
        )
        assert response.status == status, await response.text()
        return await response.json()

    return _do_it


@pytest.fixture
def unified_recipients_upsert_apply(taxi_clowny_alert_manager_web):
    async def _do_it(data, status=200):
        response = await taxi_clowny_alert_manager_web.post(
            '/v1/recipients/unified/upsert/apply/', json=data,
        )
        assert response.status == status, await response.text()
        return await response.json()

    return _do_it


@pytest.fixture
def unified_recipients_upsert_check(taxi_clowny_alert_manager_web):
    async def _do_it(data, status=200):
        response = await taxi_clowny_alert_manager_web.post(
            '/v1/recipients/unified/upsert/check/', json=data,
        )
        assert response.status == status, await response.text()
        return await response.json()

    return _do_it


@pytest.fixture
def unified_recipients(taxi_clowny_alert_manager_web):
    async def _do_it(params, status=200):
        response = await taxi_clowny_alert_manager_web.get(
            '/v1/recipients/unified/', params=params,
        )
        assert response.status == status, await response.text()
        return await response.json()

    return _do_it


@pytest.fixture
def unified_recipients_set_default(taxi_clowny_alert_manager_web):
    async def _do_it(data, status=200):
        response = await taxi_clowny_alert_manager_web.post(
            '/v1/recipients/unified/set-default/', json=data,
        )
        assert response.status == status, await response.text()
        return await response.json()

    return _do_it
