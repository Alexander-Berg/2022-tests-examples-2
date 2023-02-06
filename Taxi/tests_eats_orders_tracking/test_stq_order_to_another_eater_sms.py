# pylint: disable=too-many-lines

import pytest

from testsuite.utils import matching


@pytest.mark.experiments3(
    is_config=True,
    name='eats_orders_tracking_order_to_another_eater_sms',
    consumers=['eats-orders-tracking/order-to-another-eater-sms'],
    default_value={
        'is_enabled': True,
        'use_url_shortener': True,
        'locale': 'ru',
        'tanker_key': 'order_to_another_eater_created_sms',
        'tanker_keyset': 'eats_eats-notifications',
        'ucommunication_intent': 'eats_on_order',
        'ucommunication_sender': 'eda',
        'shared_tracking_url_template': (
            'https://eda.yandex.ru/shared-tracking?shared_id=%(shared_id)s'
        ),
    },
)
@pytest.mark.pgsql('eats_orders_tracking', files=['fill_order_payload.sql'])
async def test_stq_order_to_another_eater_sms_green_flow(
        stq_runner, mockserver, pgsql,
):
    @mockserver.json_handler('/clck/--')
    def _mock_clck(request):
        return mockserver.make_response(status=200, json=['ya.cc/short-url'])

    @mockserver.json_handler('/ucommunications/general/sms/send')
    def _mock_ucommunications(request):
        assert (
            request.headers['X-Idempotency-Token']
            == 'eats_orders_tracking.order_to_another_sms.000000-000000'
        )
        assert request.json == {
            'sender': 'eda',
            'intent': 'eats_on_order',
            'locale': 'ru',
            'text': {
                'keyset': 'eats_eats-notifications',
                'key': 'order_to_another_eater_created_sms',
                'params': {'shared_tracking_url': 'ya.cc/short-url'},
            },
            'phone_id': 'ppid',
        }
        return mockserver.make_response(
            status=200,
            json={
                'message': 'OK',
                'code': '200',
                'message_id': 'f13bb985ce7549b181061ed3e6ad1286',
                'status': 'sent',
            },
        )

    await stq_runner.eats_orders_tracking_order_to_another_eater_sms.call(
        task_id='sample_task',
        kwargs={'order_nr': '000000-000000'},
        expect_fail=False,
    )

    assert _mock_clck.times_called == 1
    assert _mock_ucommunications.times_called == 1

    cursor = pgsql['eats_orders_tracking'].cursor()
    cursor.execute(
        f"""SELECT order_nr
            FROM eats_orders_tracking.shared_tracking_links;""",
    )
    data = cursor.fetchall()
    assert len(data) == 1
    assert data[0][0] == '000000-000000'


@pytest.mark.experiments3(
    is_config=True,
    name='eats_orders_tracking_order_to_another_eater_sms',
    consumers=['eats-orders-tracking/order-to-another-eater-sms'],
    default_value={
        'is_enabled': True,
        'use_url_shortener': False,
        'locale': 'ru',
        'tanker_key': 'order_to_another_eater_created_sms',
        'tanker_keyset': 'eats_eats-notifications',
        'ucommunication_intent': 'eats_on_order',
        'ucommunication_sender': 'eda',
        'shared_tracking_url_template': (
            'https://eda.yandex.ru/shared-tracking?shared_id=%(shared_id)s'
        ),
    },
)
@pytest.mark.pgsql('eats_orders_tracking', files=['fill_order_payload.sql'])
async def test_stq_order_to_another_eater_sms_without_shortener(
        stq_runner, mockserver, pgsql,
):
    @mockserver.json_handler('/clck/--')
    def _mock_clck(request):
        return mockserver.make_response(status=200, json=['ya.cc/short-url'])

    @mockserver.json_handler('/ucommunications/general/sms/send')
    def _mock_ucommunications(request):
        assert (
            request.headers['X-Idempotency-Token']
            == 'eats_orders_tracking.order_to_another_sms.000000-000000'
        )
        assert request.json == {
            'sender': 'eda',
            'intent': 'eats_on_order',
            'locale': 'ru',
            'text': {
                'keyset': 'eats_eats-notifications',
                'key': 'order_to_another_eater_created_sms',
                'params': {'shared_tracking_url': matching.AnyString()},
            },
            'phone_id': 'ppid',
        }
        return mockserver.make_response(
            status=200,
            json={
                'message': 'OK',
                'code': '200',
                'message_id': 'f13bb985ce7549b181061ed3e6ad1286',
                'status': 'sent',
            },
        )

    await stq_runner.eats_orders_tracking_order_to_another_eater_sms.call(
        task_id='sample_task',
        kwargs={'order_nr': '000000-000000'},
        expect_fail=False,
    )

    assert _mock_clck.times_called == 0
    assert _mock_ucommunications.times_called == 1

    cursor = pgsql['eats_orders_tracking'].cursor()
    cursor.execute(
        f"""SELECT order_nr
            FROM eats_orders_tracking.shared_tracking_links;""",
    )
    data = cursor.fetchall()
    assert len(data) == 1
    assert data[0][0] == '000000-000000'


@pytest.mark.experiments3(
    is_config=True,
    name='eats_orders_tracking_order_to_another_eater_sms',
    consumers=['eats-orders-tracking/order-to-another-eater-sms'],
    default_value={
        'is_enabled': False,
        'use_url_shortener': True,
        'locale': 'ru',
        'tanker_key': 'order_to_another_eater_created_sms',
        'tanker_keyset': 'eats_eats-notifications',
        'ucommunication_intent': 'eats_on_order',
        'ucommunication_sender': 'eda',
        'shared_tracking_url_template': (
            'https://eda.yandex.ru/shared-tracking?shared_id=%(shared_id)s'
        ),
    },
)
@pytest.mark.pgsql('eats_orders_tracking', files=['fill_order_payload.sql'])
async def test_stq_order_to_another_eater_sms_disabled(
        stq_runner, mockserver, pgsql,
):
    @mockserver.json_handler('/clck/--')
    def _mock_clck(request):
        return mockserver.make_response(status=200, json=['ya.cc/short-url'])

    @mockserver.json_handler('/ucommunications/general/sms/send')
    def _mock_ucommunications(request):
        return mockserver.make_response(
            status=200,
            json={
                'message': 'OK',
                'code': '200',
                'message_id': 'f13bb985ce7549b181061ed3e6ad1286',
                'status': 'sent',
            },
        )

    await stq_runner.eats_orders_tracking_order_to_another_eater_sms.call(
        task_id='sample_task',
        kwargs={'order_nr': '000000-000000'},
        expect_fail=False,
    )

    assert _mock_clck.times_called == 0
    assert _mock_ucommunications.times_called == 0

    cursor = pgsql['eats_orders_tracking'].cursor()
    cursor.execute(
        f"""SELECT order_nr
            FROM eats_orders_tracking.shared_tracking_links;""",
    )
    data = cursor.fetchall()
    assert not data


@pytest.mark.experiments3(
    is_config=True,
    name='eats_orders_tracking_order_to_another_eater_sms',
    consumers=['eats-orders-tracking/order-to-another-eater-sms'],
    default_value={
        'is_enabled': True,
        'use_url_shortener': True,
        'locale': 'ru',
        'tanker_key': 'order_to_another_eater_created_sms',
        'tanker_keyset': 'eats_eats-notifications',
        'ucommunication_intent': 'eats_on_order',
        'ucommunication_sender': 'eda',
        'shared_tracking_url_template': (
            'https://eda.yandex.ru/shared-tracking?shared_id=%(shared_id)s'
        ),
    },
)
@pytest.mark.pgsql('eats_orders_tracking', files=['fill_order_payload.sql'])
@pytest.mark.pgsql(
    'eats_orders_tracking',
    queries=[
        'insert into eats_orders_tracking.idempotency_keys (idempotency_key)'
        'values (\'eats_orders_tracking.order_to_another_sms.000000-000000\')',
    ],
)
async def test_stq_order_to_another_eater_idempotency_key_duplicated(
        stq_runner, mockserver, pgsql,
):
    @mockserver.json_handler('/clck/--')
    def _mock_clck(request):
        return mockserver.make_response(status=200, json=['ya.cc/short-url'])

    @mockserver.json_handler('/ucommunications/general/sms/send')
    def _mock_ucommunications(request):
        return mockserver.make_response(
            status=200,
            json={
                'message': 'OK',
                'code': '200',
                'message_id': 'f13bb985ce7549b181061ed3e6ad1286',
                'status': 'sent',
            },
        )

    await stq_runner.eats_orders_tracking_order_to_another_eater_sms.call(
        task_id='sample_task',
        kwargs={'order_nr': '000000-000000'},
        expect_fail=False,
    )

    assert _mock_clck.times_called == 0
    assert _mock_ucommunications.times_called == 0

    cursor = pgsql['eats_orders_tracking'].cursor()
    cursor.execute(
        f"""SELECT order_nr
            FROM eats_orders_tracking.shared_tracking_links;""",
    )
    data = cursor.fetchall()
    assert not data
