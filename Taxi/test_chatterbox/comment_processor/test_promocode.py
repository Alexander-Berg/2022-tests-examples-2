import pytest

from taxi.clients import driver_promocodes

from chatterbox import constants
from test_chatterbox import helpers
from test_chatterbox import plugins as conftest


@pytest.fixture(scope='function')
def _mock_internal_v1_promocodes(monkeypatch) -> helpers.BaseAsyncPatcher:
    client_patcher = helpers.BaseAsyncPatcher(
        target=driver_promocodes.DriverPromocodesClient,
        method='internal_v1_promocodes',
        response_body={'id': '_promo_code_'},
    )
    client_patcher.patch(monkeypatch)
    return client_patcher


@pytest.mark.parametrize(
    'comment, platform, expected_comment, gen_promo_called',
    [
        (
            'hello vasya {{nominal}}{{currency}}',
            'yandex',
            'hello vasya {{nominal}}{{currency}}',
            None,
        ),
        (
            'base promo from yandex!{{promo:500}} {{nominal}}{{currency}}',
            'yandex',
            'base promo from yandex!_promo_code_ 500₽',
            {
                'args': ('yandex', 'forgive', '+79001211221', '1'),
                'kwargs': {
                    'cookies': {'c': 'v'},
                    'enable_csrf': True,
                    'token': '99',
                    'real_ip': 'some_ip',
                    'x_forwarded_for': 'test',
                    'log_extra': None,
                },
            },
        ),
        (
            'base promo from uber!{{promo:500}} {{nominal}}{{currency}}',
            'uber',
            'base promo from uber!_promo_code_ 500₽',
            {
                'args': ('yandex', 'merc', '+79001211221', '1'),
                'kwargs': {
                    'cookies': {'c': 'v'},
                    'enable_csrf': True,
                    'token': '99',
                    'real_ip': 'some_ip',
                    'x_forwarded_for': 'test',
                    'log_extra': None,
                },
            },
        ),
        (
            'yandex promo!{{promo:500:premium}} {{nominal}}{{currency}}',
            'yandex',
            'yandex promo!_promo_code_ 500₽',
            {
                'args': ('yandex', 'warmwishes', '+79001211221', '1'),
                'kwargs': {
                    'cookies': {'c': 'v'},
                    'enable_csrf': True,
                    'token': '99',
                    'real_ip': 'some_ip',
                    'x_forwarded_for': 'test',
                    'log_extra': None,
                },
            },
        ),
        (
            'na uber promo!{{promo:500:premium}} {{nominal}}{{currency}}',
            'uber',
            'na uber promo!_promo_code_ 500₽',
            {
                'args': ('yandex', 'greetings', '+79001211221', '1'),
                'kwargs': {
                    'cookies': {'c': 'v'},
                    'enable_csrf': True,
                    'token': '99',
                    'real_ip': 'some_ip',
                    'x_forwarded_for': 'test',
                    'log_extra': None,
                },
            },
        ),
    ],
)
async def test_insert_promo(
        cbox: conftest.CboxWrap,
        mock_admin_generate_promocode,
        comment,
        platform,
        expected_comment,
        gen_promo_called,
):

    comment_processor = cbox.app.comment_processor
    task_data = {
        'task_id': '1',
        'user_phone': '+79001211221',
        'platform': platform,
        'country': 'rus',
        'phone_type': 'yandex',
    }
    auth_data = {
        'cookies': {'c': 'v'},
        'token': '99',
        'real_ip': 'some_ip',
        'x_forwarded_for': 'test',
    }

    new_comment, processing_info = await comment_processor.process(
        comment, task_data, auth_data, constants.DEFAULT_STARTRACK_PROFILE,
    )
    assert new_comment == expected_comment
    assert mock_admin_generate_promocode.call == gen_promo_called

    if gen_promo_called:
        assert processing_info.error is False
        assert processing_info.operations_log == ['Client promocode generated']
        assert processing_info.promocodes == ['_promo_code_']
        assert processing_info.succeed_operations == set()
    else:
        assert processing_info.error is True
        assert processing_info.operations_log == [
            'Cant apply macro: unknown templates',
        ]
        assert processing_info.promocodes == []
        assert processing_info.succeed_operations == set()


@pytest.mark.parametrize(
    'comment, platform, expected_comment, gen_promo_called, request_id',
    [
        (
            '{{driver_promo:168:P}}',
            'yandex',
            '_promo_code_ 168₽',
            {
                'args': ('yandex', 'greetings', '+79001211221', '1'),
                'kwargs': {
                    'cookies': {'c': 'v'},
                    'enable_csrf': True,
                    'token': '99',
                    'real_ip': 'some_ip',
                    'x_forwarded_for': 'test',
                    'log_extra': None,
                },
            },
            'some_request_id',
        ),
    ],
)
@pytest.mark.config(DRIVER_SUPPORT_USE_LEGACY_PROMOCODES=False)
async def test_insert_driver_promo(
        cbox: conftest.CboxWrap,
        mock_admin_generate_promocode,
        _mock_internal_v1_promocodes,
        comment,
        platform,
        expected_comment,
        gen_promo_called,
        request_id,
):
    comment_processor = cbox.app.comment_processor
    task_data = {
        'task_id': '1',
        'user_phone': '+79001211221',
        'platform': platform,
        'country': 'rus',
        'phone_type': 'yandex',
        'clid': 'some_clid',
        'driver_uuid': 'a35d1e1d-e35c-4fa7-a185-34cfbba465d7',
        'park_driver_profile_id': 'some_pdpid',
    }
    auth_data = {
        'cookies': {'c': 'v'},
        'token': '99',
        'real_ip': 'some_ip',
        'x_forwarded_for': 'test',
        'login': 'Vasya',
    }

    _, processing_info = await comment_processor.process(
        comment,
        task_data,
        auth_data,
        constants.DEFAULT_STARTRACK_PROFILE,
        request_id=request_id,
    )

    assert (
        _mock_internal_v1_promocodes.call.get('kwargs').get(
            'idempotency_token',
        )
        == request_id
    )

    assert processing_info.error is False
    assert processing_info.operations_log == ['Driver promocode generated']
    assert processing_info.promocodes == ['_promo_code_']
    assert processing_info.succeed_operations == {'promocode'}
