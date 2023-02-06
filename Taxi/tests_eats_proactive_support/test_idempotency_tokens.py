# flake8: noqa
# pylint: disable=import-error,wildcard-import,too-many-lines
import datetime
import pytest


TEST_ORDER_NR = '111111-111111'
TEST_ACTION_ID_NOTIFICATION = 100
TEST_ACTION_ID_ROBOCALL = 101


def build_idempotency_token(order_nr, action_id):
    return 'order_nr:' + order_nr + '_action_id:' + str(action_id)


def build_stq_task_id(order_nr, action_id):
    return 'order_nr:' + order_nr + '_action_id:' + str(action_id)


def load_idempotency_tokens(pgsql):
    with pgsql['eats_proactive_support'].cursor() as cursor:
        cursor.execute(
            'SELECT destination, token_sensitive, token_uuid '
            + 'FROM eats_proactive_support.idempotency_tokens '
            + 'ORDER BY destination, token_sensitive ASC',
        )
        return list(list(row) for row in cursor)


@pytest.fixture(name='mock_eats_core_order_support')
def _mock_eats_core_order_support(mockserver):
    @mockserver.json_handler(
        '/eats-core-order-support/internal-api/v1/order-support/meta',
    )
    def mock(request):
        return mockserver.make_response(status=200, json={})

    return mock


@pytest.mark.pgsql('eats_proactive_support', files=['init_test_actions.sql'])
async def test_action_notification(
        pgsql, stq_runner, mockserver, mock_eats_core_order_support,
):
    token_uuid = ''
    token_sensitive = build_idempotency_token(
        TEST_ORDER_NR, TEST_ACTION_ID_NOTIFICATION,
    )

    @mockserver.json_handler(
        '/eats-core-communication/internal-api/v1/communication/notification',
    )
    def mock_eats_core_communication(request):
        nonlocal token_uuid
        token_uuid = request.headers['X-Idempotency-Key']
        assert token_uuid != ''
        assert token_uuid != token_sensitive
        return mockserver.make_response(
            status=200, json={'notification_id': '123'},
        )

    await stq_runner.eats_proactive_support_actions.call(
        task_id=build_stq_task_id(TEST_ORDER_NR, TEST_ACTION_ID_NOTIFICATION),
        kwargs={
            'order_nr': TEST_ORDER_NR,
            'action_id': TEST_ACTION_ID_NOTIFICATION,
            'action_type': 'eater_notification',
        },
    )

    assert mock_eats_core_communication.times_called == 1
    assert load_idempotency_tokens(pgsql) == [
        ['eats_core_notification', token_sensitive, token_uuid],
    ]


@pytest.mark.pgsql('eats_proactive_support', files=['init_test_actions.sql'])
async def test_action_robocall(
        pgsql, stq_runner, mockserver, mock_eats_core_order_support,
):
    token_uuid = ''
    token_sensitive = build_idempotency_token(
        TEST_ORDER_NR, TEST_ACTION_ID_ROBOCALL,
    )

    @mockserver.json_handler(
        '/eats-robocall/internal/eats-robocall/v1/create-call',
    )
    def mock_eats_robocall(request):
        nonlocal token_uuid
        token_uuid = request.headers['X-Idempotency-Token']
        assert token_uuid != ''
        assert token_uuid != token_sensitive
        return mockserver.make_response(status=200, json={'call_id': '123'})

    await stq_runner.eats_proactive_support_actions.call(
        task_id=build_stq_task_id(TEST_ORDER_NR, TEST_ACTION_ID_ROBOCALL),
        kwargs={
            'order_nr': TEST_ORDER_NR,
            'action_id': TEST_ACTION_ID_ROBOCALL,
            'action_type': 'eater_robocall',
        },
    )

    assert mock_eats_robocall.times_called == 1
    assert load_idempotency_tokens(pgsql) == [
        ['eats_robocall', token_sensitive, token_uuid],
    ]


@pytest.mark.pgsql(
    'eats_proactive_support',
    files=['init_test_actions.sql', 'add_idempotency_token.sql'],
)
async def test_existing_token(
        pgsql, stq_runner, mockserver, mock_eats_core_order_support,
):
    token_uuid = 'test_token_uuid_1'
    token_sensitive = build_idempotency_token(
        TEST_ORDER_NR, TEST_ACTION_ID_NOTIFICATION,
    )

    @mockserver.json_handler(
        '/eats-core-communication/internal-api/v1/communication/notification',
    )
    def mock_eats_core_communication(request):
        assert request.headers['X-Idempotency-Key'] == token_uuid
        return mockserver.make_response(
            status=200, json={'notification_id': '123'},
        )

    await stq_runner.eats_proactive_support_actions.call(
        task_id=build_stq_task_id(TEST_ORDER_NR, TEST_ACTION_ID_NOTIFICATION),
        kwargs={
            'order_nr': TEST_ORDER_NR,
            'action_id': TEST_ACTION_ID_NOTIFICATION,
            'action_type': 'eater_notification',
        },
    )

    assert mock_eats_core_communication.times_called == 1
    assert load_idempotency_tokens(pgsql) == [
        ['eats_core_notification', token_sensitive, token_uuid],
    ]


@pytest.mark.pgsql('eats_proactive_support', files=['init_test_actions.sql'])
async def test_existing_uuid(
        pgsql, stq_runner, mockserver, mock_eats_core_order_support, testpoint,
):
    token_uuid_1 = ''
    token_uuid_2 = ''
    token_sensitive = build_idempotency_token(
        TEST_ORDER_NR, TEST_ACTION_ID_NOTIFICATION,
    )

    @testpoint('eats-proactive-support-generated-uuid')
    def _testpoint(json):
        # При первой итерации сохраняем в базе uuid, чтобы произошла коллизия.
        nonlocal token_uuid_1
        if token_uuid_1 == '':
            token_uuid_1 = json['generated_uuid']
            sql_script = f"""
                INSERT INTO eats_proactive_support.idempotency_tokens
                    (destination, token_sensitive, token_uuid)
                VALUES
                    ('another_destination', 'another_token_sensitive',
                    '{token_uuid_1}');"""

            cursor = pgsql['eats_proactive_support'].cursor()
            cursor.execute(sql_script)

    @mockserver.json_handler(
        '/eats-core-communication/internal-api/v1/communication/notification',
    )
    def mock_eats_core_communication(request):
        nonlocal token_uuid_2
        token_uuid_2 = request.headers['X-Idempotency-Key']
        assert token_uuid_2 != ''
        assert token_uuid_2 != token_uuid_1
        assert token_uuid_2 != token_sensitive
        return mockserver.make_response(
            status=200, json={'notification_id': '123'},
        )

    await stq_runner.eats_proactive_support_actions.call(
        task_id=build_stq_task_id(TEST_ORDER_NR, TEST_ACTION_ID_NOTIFICATION),
        kwargs={
            'order_nr': TEST_ORDER_NR,
            'action_id': TEST_ACTION_ID_NOTIFICATION,
            'action_type': 'eater_notification',
        },
    )

    assert mock_eats_core_communication.times_called == 1
    assert load_idempotency_tokens(pgsql) == [
        ['another_destination', 'another_token_sensitive', token_uuid_1],
        ['eats_core_notification', token_sensitive, token_uuid_2],
    ]


@pytest.mark.pgsql('eats_proactive_support', files=['init_test_actions.sql'])
async def test_token_prefix(
        pgsql, stq_runner, mockserver, mock_eats_core_order_support,
):
    prefix = 'eats-proactive-support_'
    prefix_length = len(prefix)

    @mockserver.json_handler(
        '/eats-core-communication/internal-api/v1/communication/notification',
    )
    def mock_eats_core_communication(request):
        token = request.headers['X-Idempotency-Key']
        substring = token[0:prefix_length]
        assert substring == prefix
        return mockserver.make_response(
            status=200, json={'notification_id': '123'},
        )

    await stq_runner.eats_proactive_support_actions.call(
        task_id=build_stq_task_id(TEST_ORDER_NR, TEST_ACTION_ID_NOTIFICATION),
        kwargs={
            'order_nr': TEST_ORDER_NR,
            'action_id': TEST_ACTION_ID_NOTIFICATION,
            'action_type': 'eater_notification',
        },
    )

    assert mock_eats_core_communication.times_called == 1
