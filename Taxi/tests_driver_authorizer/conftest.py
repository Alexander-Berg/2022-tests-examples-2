# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import json

from driver_authorizer_plugins import *  # noqa: F403 F401
import pytest


@pytest.fixture
async def put_session(taxi_driver_authorizer):
    async def _put_session(
            client_id,
            park_id,
            uuid,
            driver_app_profile_id,
            ttl,
            yandex_uid=None,
            eats_courier_id=None,
            headers=None,
    ):
        params = {'client_id': client_id, 'uuid': uuid}
        if park_id is not None:
            params.update({'park_id': park_id})
        if driver_app_profile_id is not None:
            params.update({'driver_app_profile_id': driver_app_profile_id})
        if eats_courier_id is not None:
            params.update({'eats_courier_id': eats_courier_id})

        data = {'ttl': ttl}
        if yandex_uid is not None:
            data.update({'yandex_uid': yandex_uid})

        return await taxi_driver_authorizer.put(
            'driver/sessions',
            params=params,
            data=json.dumps(data),
            headers=headers or {},
        )

    return _put_session
