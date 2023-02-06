from typing import Any
from typing import Dict
from typing import List
from typing import Optional

# pylint: disable=redefined-outer-name
import pytest

from rida import consts
import rida.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
import rida.logic.notifications.models as notification_models

pytest_plugins = ['rida.generated.service.pytest_plugins']


@pytest.fixture(autouse=True)
def _create_required_indexes(mongodb):
    mongodb.rida_offers.create_index(
        [('start_point', '2dsphere'), ('offer_status', 1)],
    )
    mongodb.rida_drivers.create_index([('location', '2dsphere')])


def validate_sent_notifications(context, patch, monkeypatch):
    """Patch ID generation & send func to validate sent notifications"""
    calls = list()
    notification_id_counter = 0

    @patch('rida.logic.notifications.models._gen_notification_template_id')
    def _patched_gen_notification_template_id():
        nonlocal notification_id_counter
        template_id = str(notification_id_counter).rjust(32, '0')
        notification_id_counter += 1
        return template_id

    async def _patched_send_notifications(notifications):
        calls.append(notifications)
        message_statuses = [
            notification_models.NotificationSentStatus(
                message_id=f'message_id/{notification.id}',
                status=consts.NotificationStatus.SUCCESS,
            )
            for notification in notifications
        ]
        return message_statuses

    monkeypatch.setattr(
        context.firebase_client,
        'send_notifications',
        _patched_send_notifications,
    )

    def _validate_sent_notifications(
            *,
            expected_times_called: int = 1,
            expected_total_notifications: Optional[int] = None,
            expected_notifications: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        times_called = len(calls)
        assert times_called == expected_times_called
        if expected_total_notifications is not None:
            total_notifications = sum(len(call) for call in calls)
            assert total_notifications == expected_total_notifications
        if expected_notifications is not None:
            notifications = [n.serialize() for call in calls for n in call]
            assert notifications == expected_notifications

    return _validate_sent_notifications


@pytest.fixture
def validate_web_sent_notifications(  # pylint: disable=invalid-name
        web_app, patch, monkeypatch,
):
    return validate_sent_notifications(web_app['context'], patch, monkeypatch)


@pytest.fixture
def validate_stq3_sent_notifications(  # pylint: disable=invalid-name
        stq3_context, patch, monkeypatch,
):
    return validate_sent_notifications(stq3_context, patch, monkeypatch)


@pytest.fixture
def validate_cron_sent_notifications(  # pylint: disable=invalid-name
        cron_context, patch, monkeypatch,
):
    return validate_sent_notifications(cron_context, patch, monkeypatch)


@pytest.fixture
def mock_handle(patch_aiohttp_session):
    """Used to mock external handles when using aiohttp.ClientSession directly
    """

    def _wrapper_generator(url: str):
        def _wrapper(func):
            @patch_aiohttp_session(url)
            def _wrapped_func(*args, **kwargs):
                _wrapped_func.times_called += 1
                return func(*args, **kwargs)

            _wrapped_func.times_called = 0
            return _wrapped_func

        return _wrapper

    return _wrapper_generator
