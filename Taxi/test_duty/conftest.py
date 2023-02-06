# pylint: disable=redefined-outer-name
import pytest

import duty.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = [
    'duty.generated.service.gap.pytest_plugin',
    'duty.generated.service.pytest_plugins',
]


@pytest.fixture
def simple_secdist(simple_secdist):
    simple_secdist.update(
        {
            'GAP_OAUTH': 'valid_oauth',
            'CALENDAR_UID': '1234567890',
            'CALENDAR_OAUTH': 'valid_cal_oauth',
            'TMP_AUTH_TOKEN': 'auth_token',
        },
    )
    return simple_secdist


@pytest.fixture
def add_duty_group(taxi_duty_web):
    async def _wrapper(
            name='test group',
            calendar_layer=123,
            abc_service='abc_serv',
            extra_fields=None,
    ):
        if extra_fields is None:
            extra_fields = {}

        data = {
            'name': name,
            'calendar_layer': calendar_layer,
            'abc_service': abc_service,
        }
        data.update(extra_fields)

        response = await taxi_duty_web.post('/v1/duty_groups/', json=data)
        assert response.status == 200

        result = await response.json()
        return result['id']

    return _wrapper


@pytest.fixture
def add_event(taxi_duty_web):
    async def _wrapper(
            duty_group_id,
            start_time='2020-04-06 12:00:00',
            end_time='2020-04-13 12:00:00',
            login='username',
            extra_fields=None,
    ):
        if extra_fields is None:
            extra_fields = {}

        data = {
            'duty_group_id': duty_group_id,
            'start_time': start_time,
            'end_time': end_time,
            'login': login,
        }
        data.update(extra_fields)

        response = await taxi_duty_web.post(
            '/v1/events/', headers={'X-Real-Ip': '1.2.3.4'}, json=data,
        )
        assert response.status == 200

        result = await response.json()
        return result['id']

    return _wrapper
