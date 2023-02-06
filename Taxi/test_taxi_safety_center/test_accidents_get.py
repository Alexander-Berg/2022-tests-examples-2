import random
import unittest.mock

import pytest

from taxi_safety_center.repositories import accidents
from test_taxi_safety_center import data_generators

DEFAULT_HEADER = {
    'X-Yandex-UID': '9876',
    'Accept-Language': 'ru',
    'X-YaTaxi-UserId': '9876',
}


PATH = '/4.0/safety_center/v1/accidents'


async def _create_accident_for_order(context, order_id, status, seed=None):
    """
    Warning: test-specific generator, reuse with care
    Creates accident with accident_id = f'{order_id}_{status}' and according
    order_id and status, so we can be extra-sure which accident has which
    status in tests
    """
    random.seed(seed, version=2)
    new_accident_object = data_generators.generated_accident(
        number=random.randint(0, 1337),
    )
    accident_id = f'{order_id}_{status}'
    new_accident_object.order_alias_id = order_id
    patch = unittest.mock.patch.object(
        accidents, '_generate_accident_id', return_value=accident_id,
    )
    with patch:
        await accidents.insert_accident(
            accident=new_accident_object,
            order_id=order_id,
            context=context,
            log_extra=None,
            user_id=DEFAULT_HEADER['X-YaTaxi-UserId'],
            yandex_uid=DEFAULT_HEADER['X-Yandex-UID'],
        )

    if status is not None:
        await accidents.update_accident_status(
            accident_id=accident_id, confirmed=status, context=context,
        )


@pytest.mark.parametrize(
    'order_id,status_reports,response',
    (
        ('empty', [], []),
        (
            'all',
            [None, False, True],
            [
                {'accident_id': 'all_None', 'status': 'questionable'},
                {'accident_id': 'all_False', 'status': 'unconfirmed'},
                {'accident_id': 'all_True', 'status': 'confirmed'},
            ],
        ),
        (
            'questionable',
            [None],
            [{'accident_id': 'questionable_None', 'status': 'questionable'}],
        ),
        (
            'confirmed',
            [True],
            [{'accident_id': 'confirmed_True', 'status': 'confirmed'}],
        ),
        (
            'unconfirmed',
            [False],
            [{'accident_id': 'unconfirmed_False', 'status': 'unconfirmed'}],
        ),
    ),
)
async def test_get_accidents(
        web_app_client,
        mock_archive_response,
        web_app,
        order_id,
        status_reports,
        response,
):
    mock_archive_response({'user_id': DEFAULT_HEADER['X-YaTaxi-UserId']})
    for status in status_reports:
        await _create_accident_for_order(
            order_id=order_id,
            status=status,
            context=web_app['context'],
            seed=f'{order_id}_{status}',
        )
    get_response = await web_app_client.get(
        PATH, params={'order_id': order_id}, headers=DEFAULT_HEADER,
    )
    assert get_response.status == 200
    assert await get_response.json() == {'accidents': response}


UNAUTHORIZED_BODY = {'code': 'unauthorized_order_access'}
CORRECT_ID = None  # no id patch => correct id will be used


@pytest.mark.parametrize(
    'crossdevice_enabled,user_id,yandex_uid,resp_code,resp_body',
    [
        (False, CORRECT_ID, CORRECT_ID, 200, {}),
        (False, 'wrong_user_id', CORRECT_ID, 403, UNAUTHORIZED_BODY),
        (True, 'wrong_user_id', CORRECT_ID, 200, {}),
        (True, 'wrong_user_id', '', 403, UNAUTHORIZED_BODY),  # empty uid
        (True, 'wrong_user_id', 'wrong_yandex_uid', 403, UNAUTHORIZED_BODY),
    ],
)
async def test_unauthorized_get_accidents(
        web_app,
        web_app_client,
        mock_archive_response,
        new_accident,
        crossdevice_enabled,
        user_id,
        yandex_uid,
        resp_code,
        resp_body,
):
    web_app['context'].config.CROSSDEVICE_ENABLED = crossdevice_enabled
    mock_archive_response(
        {'user_id': new_accident.user_id, 'user_uid': new_accident.yandex_uid},
    )
    user_id = user_id or new_accident.user_id
    yandex_uid = (
        yandex_uid if yandex_uid is not None else new_accident.yandex_uid
    )
    headers = DEFAULT_HEADER.copy()
    headers['X-YaTaxi-UserId'] = user_id
    headers['X-Yandex-UID'] = yandex_uid
    response = await web_app_client.get(
        PATH, params={'order_id': new_accident.order_id}, headers=headers,
    )
    assert response.status == resp_code
    if resp_code != 200:
        assert await response.json() == resp_body
