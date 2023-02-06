import copy
import dataclasses
import datetime as dt
from typing import Any
from typing import Dict
from typing import Optional

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import offer_templates
from tests_driver_mode_subscription import saga_tools
from tests_driver_mode_subscription import scenario

_UNSUBSCRIBE_REASONS = {
    'banned_by_park': {
        'current_mode_params': {},
        'actions': {
            'send_unsubscribe_notification': {'type': 'banned_by_park'},
        },
    },
    'driver_fix_expired': {
        'current_mode_params': {},
        'actions': {
            'send_unsubscribe_notification': {'type': 'driver_fix_expired'},
        },
    },
    'low_taximeter_version': {
        'current_mode_params': {},
        'actions': {
            'send_unsubscribe_notification': {
                'type': 'unsupported_taximeter_version',
            },
        },
    },
    'current_mode_unavailable': {
        'actions': {
            'send_unsubscribe_notification': {
                'transport': 'wall',
                'type': 'current_mode_unavailable',
            },
        },
        'current_mode_params': {},
    },
}

_OFFERS_LIST_DEEPLINK = 'taximeter://screen/driver_mode'


@pytest.mark.now('2019-05-01T12:00:00+0300')
@pytest.mark.parametrize(
    'dbid_uuid, notifications_enabled, config_reason_name, reason_enabled, '
    'expect_notify',
    (
        pytest.param(
            'parkid3_uuid3',
            False,
            'banned_by_park',
            True,
            False,
            id='notifications_disabled',
        ),
        pytest.param(
            'parkid3_uuid3', True, 'wrong_type', True, False, id='no_type',
        ),
        pytest.param(
            'parkid3_uuid3',
            True,
            'banned_by_park',
            False,
            False,
            id='type_disabled',
        ),
        pytest.param(
            'parkid4_uuid4',
            True,
            'banned_by_park',
            True,
            False,
            id='no accept_language',
        ),
    ),
)
@pytest.mark.pgsql('driver_mode_subscription', files=['sagas.sql'])
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [mode_rules.Patch(rule_name='driver_fix', features={})],
    ),
)
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_UNSUBSCRIBE_REASONS=_UNSUBSCRIBE_REASONS,
)
async def test_subscription_saga_notify_config(
        taxi_driver_mode_subscription,
        mode_rules_data,
        stq,
        stq_runner,
        taxi_config,
        mockserver,
        mocked_time,
        dbid_uuid: str,
        notifications_enabled: bool,
        config_reason_name: str,
        reason_enabled: bool,
        expect_notify: bool,
):
    taxi_config.set_values(
        dict(
            DRIVER_MODE_SUBSCRIPTION_NOTIFICATION_TYPES=(
                {
                    'enable_notifications': notifications_enabled,
                    'notification_settings': {
                        config_reason_name: {
                            'enabled': reason_enabled,
                            'delay_on_order': True,
                            'deeplink_url': 'taximeter://screen/driver_mode',
                            'keep_in_busy': True,
                            'localization': {
                                'keyset': 'driver_fix',
                                'push_keys': {
                                    'button_text': (
                                        'notifications.push.'
                                        'banned_by_park_button_text'
                                    ),
                                    'header': (
                                        'notifications.push.'
                                        'banned_by_park_header'
                                    ),
                                    'text': (
                                        'notifications.push.'
                                        'banned_by_park_text'
                                    ),
                                },
                                'tanker_keys_supported': False,
                            },
                        },
                    },
                }
            ),
        ),
    )

    driver_profile = driver.Profile(dbid_uuid)
    scene = scenario.Scene(
        profiles={
            driver_profile: driver.Mode(
                'driver_fix', mode_settings=common.MODE_SETTINGS,
            ),
        },
    )

    scene.setup(mockserver, mocked_time)

    @mockserver.json_handler('/client-notify/v2/push')
    def client_notify_mock(request):
        return {'notification_id': 'notification_id'}

    await saga_tools.call_stq_saga_task(stq_runner, driver_profile)

    if expect_notify:
        assert client_notify_mock.times_called == 1
    else:
        assert not client_notify_mock.has_calls


_DRIVER_MODE_NOTIFICATION_TEMPLATE = {
    'intent': 'DriverModeSubscriptionMessage',
    'service': 'taximeter',
    'locale': 'ru',
    'notification': {
        'title': 'Парк отключил режим дохода',
        'text': (
            'Обратитесь в парк, чтобы узнать, в чём дело, или смените '
            'режим дохода'
        ),
        'link': _OFFERS_LIST_DEEPLINK,
    },
    'data': {
        'keep_in_busy': True,
        'delay_on_order': True,
        'id': 'driver_mode_subscription_notification_banned_by_park',
        'button_text': 'Сменить режим дохода',
        'fullscreen_notification': {
            'ui': {
                'bottom_items': [
                    {
                        'accent': True,
                        'horizontal_divider_type': 'none',
                        'payload': {
                            'type': 'deeplink',
                            'url': _OFFERS_LIST_DEEPLINK,
                        },
                        'title': 'Сменить режим дохода',
                        'type': 'button',
                    },
                ],
                'items': [
                    {
                        'gravity': 'left',
                        'horizontal_divider_type': 'none',
                        'subtitle': 'Парк отключил режим дохода',
                        'type': 'header',
                    },
                    {
                        'horizontal_divider_type': 'none',
                        'padding': 'small_bottom',
                        'text': (
                            'Обратитесь в парк, чтобы узнать в '
                            'чём дело или смените режим дохода'
                        ),
                        'type': 'text',
                    },
                ],
            },
        },
    },
    'client_id': 'parkid3-uuid3',
}


class Notification:
    def make_expected_push(self):
        raise NotImplementedError


@dataclasses.dataclass
class DriverModeNotification(Notification):
    notification_id: str
    keep_in_busy: bool
    delay_on_order: bool
    deeplink_url: str
    header: Any
    text: Any
    button_text: Any
    dbid: str
    uuid: str

    def make_expected_push(self):
        push: Dict[str, Any] = copy.deepcopy(
            _DRIVER_MODE_NOTIFICATION_TEMPLATE,
        )
        push['data']['keep_in_busy'] = self.keep_in_busy
        push['data']['id'] = self.notification_id
        push['data']['delay_on_order'] = self.delay_on_order
        push['data']['button_text'] = self.button_text
        push['client_id'] = f'{self.dbid}-{self.uuid}'
        push['notification'] = {
            'link': self.deeplink_url,
            'title': self.header,
            'text': self.text,
        }
        push_ui = push['data']['fullscreen_notification']['ui']
        push_ui['bottom_items'][0]['title'] = self.button_text
        push_ui['bottom_items'][0]['payload']['url'] = self.deeplink_url
        push_ui['items'][0]['subtitle'] = self.header
        push_ui['items'][1]['text'] = self.text
        return push


_NEW_MESSAGE_NOTIFICATION_TEMPLATE = {
    'intent': 'MessageNew',
    'client_id': 'parkid1-uuid1',
    'locale': 'ru',
    'service': 'taximeter',
    'data': {
        'flags': ['fullscreen'],
        'id': (
            'driver_mode_subscription_notification_'
            'unsupported_taximeter_version'
        ),
    },
    'notification': {
        'title': 'Парк отключил режим дохода',
        'text': (
            'Обратитесь в парк, чтобы узнать в чём дело '
            'или смените режим дохода'
        ),
    },
    'ttl': 300,
}


@dataclasses.dataclass
class NewMessageNotification(Notification):
    dbid: str
    uuid: str

    def make_expected_push(self):
        push: Dict[str, Any] = copy.deepcopy(
            _NEW_MESSAGE_NOTIFICATION_TEMPLATE,
        )
        push['client_id'] = f'{self.dbid}-{self.uuid}'
        return push


@pytest.mark.now('2019-05-01T12:00:00+0300')
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [mode_rules.Patch(rule_name='driver_fix', features={})],
    ),
)
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_UNSUBSCRIBE_REASONS=_UNSUBSCRIBE_REASONS,
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
@pytest.mark.parametrize(
    'expected_push, park_driver_id',
    [
        pytest.param(
            DriverModeNotification(
                notification_id='driver_mode_subscription_notification_'
                'banned_by_park',
                keep_in_busy=True,
                delay_on_order=True,
                deeplink_url=_OFFERS_LIST_DEEPLINK,
                header='Парк отключил режим дохода',
                text='Обратитесь в парк, чтобы узнать в чём дело или смените '
                'режим дохода',
                button_text='Сменить режим дохода',
                dbid='parkid3',
                uuid='uuid3',
            ),
            'parkid3_uuid3',
            marks=pytest.mark.config(
                DRIVER_MODE_SUBSCRIPTION_NOTIFICATION_TYPES=(
                    {
                        'enable_notifications': True,
                        'notification_settings': {
                            'banned_by_park': {
                                'delay_on_order': True,
                                'deeplink_url': _OFFERS_LIST_DEEPLINK,
                                'keep_in_busy': True,
                                'localization': {
                                    'push_keys': {
                                        'button_text': (
                                            'notifications.push.'
                                            'banned_by_park_button_text'
                                        ),
                                        'header': (
                                            'notifications.push.'
                                            'banned_by_park_header'
                                        ),
                                        'text': (
                                            'notifications.push.'
                                            'banned_by_park_text'
                                        ),
                                    },
                                },
                            },
                        },
                    }
                ),
            ),
            id='manual_localization',
        ),
        pytest.param(
            DriverModeNotification(
                notification_id='driver_mode_subscription_notification_'
                'driver_fix_expired',
                keep_in_busy=True,
                delay_on_order=True,
                deeplink_url=_OFFERS_LIST_DEEPLINK,
                header={
                    'key': 'notifications.push.driver_fix_expired_header',
                    'keyset': 'taximeter_messages',
                },
                text={
                    'key': 'notifications.push.driver_fix_expired_text',
                    'keyset': 'taximeter_messages',
                },
                button_text={
                    'key': 'notifications.push.driver_fix_expired_button_text',
                    'keyset': 'taximeter_messages',
                },
                dbid='parkid2',
                uuid='uuid2',
            ),
            'parkid2_uuid2',
            marks=pytest.mark.config(
                DRIVER_MODE_SUBSCRIPTION_NOTIFICATION_TYPES=(
                    {
                        'enable_notifications': True,
                        'notification_settings': {
                            'driver_fix_expired': {
                                'delay_on_order': True,
                                'deeplink_url': _OFFERS_LIST_DEEPLINK,
                                'keep_in_busy': True,
                                'localization': {
                                    'push_keys': {
                                        'button_text': (
                                            'notifications.push.'
                                            'driver_fix_expired_button_text'
                                        ),
                                        'header': (
                                            'notifications.push.'
                                            'driver_fix_expired_header'
                                        ),
                                        'text': (
                                            'notifications.push.'
                                            'driver_fix_expired_text'
                                        ),
                                    },
                                },
                            },
                        },
                    }
                ),
            ),
            id='auto_localization',
        ),
        pytest.param(
            DriverModeNotification(
                notification_id='driver_mode_subscription_notification_'
                'driver_fix_expired',
                keep_in_busy=False,
                delay_on_order=False,
                deeplink_url='taximeter://screen/main',
                header={
                    'key': 'notifications.push.driver_fix_expired_header',
                    'keyset': 'taximeter_messages',
                },
                text={
                    'key': 'notifications.push.driver_fix_expired_text',
                    'keyset': 'taximeter_messages',
                },
                button_text={
                    'key': 'notifications.push.driver_fix_expired_button_text',
                    'keyset': 'taximeter_messages',
                },
                dbid='parkid2',
                uuid='uuid2',
            ),
            'parkid2_uuid2',
            marks=pytest.mark.config(
                DRIVER_MODE_SUBSCRIPTION_NOTIFICATION_TYPES=(
                    {
                        'enable_notifications': True,
                        'notification_settings': {
                            'driver_fix_expired': {
                                'delay_on_order': False,
                                'deeplink_url': 'taximeter://screen/main',
                                'keep_in_busy': False,
                                'localization': {
                                    'push_keys': {
                                        'button_text': (
                                            'notifications.push.'
                                            'driver_fix_expired_button_text'
                                        ),
                                        'header': (
                                            'notifications.push.'
                                            'driver_fix_expired_header'
                                        ),
                                        'text': (
                                            'notifications.push.'
                                            'driver_fix_expired_text'
                                        ),
                                    },
                                },
                            },
                        },
                    }
                ),
            ),
            id='change_other_settings',
        ),
        pytest.param(
            NewMessageNotification(dbid='parkid1', uuid='uuid1'),
            'parkid1_uuid1',
            marks=pytest.mark.config(
                DRIVER_MODE_SUBSCRIPTION_NOTIFICATION_TYPES=(
                    {
                        'enable_notifications': True,
                        'notification_settings': {
                            'unsupported_taximeter_version': {
                                'delay_on_order': True,
                                'deeplink_url': _OFFERS_LIST_DEEPLINK,
                                'keep_in_busy': True,
                                'localization': {
                                    'keyset': 'driver_fix',
                                    'push_keys': {
                                        'button_text': 'NOT_USED',
                                        'header': (
                                            'notifications.push.'
                                            'banned_by_park_header'
                                        ),
                                        'text': (
                                            'notifications.push.'
                                            'banned_by_park_text'
                                        ),
                                    },
                                    'tanker_keys_supported': False,
                                },
                            },
                        },
                    }
                ),
            ),
            id='unsupported_taximeter_version_overrides',
        ),
    ],
)
@pytest.mark.pgsql('driver_mode_subscription', files=['sagas.sql'])
async def test_subscription_saga_notify_config_keep_in_busy(
        taxi_driver_mode_subscription,
        mode_rules_data,
        stq,
        stq_runner,
        mockserver,
        mocked_time,
        expected_push: Notification,
        park_driver_id: str,
):
    driver_profile = driver.Profile(park_driver_id)
    scene = scenario.Scene(
        profiles={driver_profile: driver.Mode('driver_fix')},
    )
    scene.setup(mockserver, mocked_time)

    await taxi_driver_mode_subscription.invalidate_caches()

    @mockserver.json_handler('/client-notify/v2/push')
    def client_notify_mock(request):
        return {'notification_id': 'notification_id'}

    await saga_tools.call_stq_saga_task(stq_runner, driver_profile)

    assert stq.subscription_sync.times_called == 0

    assert client_notify_mock.times_called == 1
    client_notify_request = client_notify_mock.next_call()['request'].json
    assert client_notify_request == expected_push.make_expected_push()


_TEMPLATE_WITH_BUTTON_FULLSCREEN = {
    'title': 'Режим "За время" стал недоступен',
    'text': 'Вы были переключены на подходящий режим: За заказы.',
    'type': 'newsletter',
    'format': 'Raw',
    'url': _OFFERS_LIST_DEEPLINK,
    'teaser': 'Сменить режим',
    'important': False,
    'alert': True,
}

_TEMPLATE_WITHOUT_BUTTON_NORMAL = {
    'title': 'Режим "За время" стал недоступен',
    'text': 'Вы были переключены на подходящий режим: За заказы.',
    'type': 'newsletter',
    'format': 'Raw',
    'important': False,
    'alert': False,
}


@dataclasses.dataclass
class DriverWallRequestBody:
    id_: str
    template: Dict[str, Any]
    filters: Dict[str, Any]
    expire: dt.datetime

    @staticmethod
    def from_dict(api_dict: Dict[str, Any]):
        return DriverWallRequestBody(
            id_=api_dict['id'],
            template=api_dict['template'],
            filters=api_dict['filters'],
            expire=dt.datetime.fromisoformat(api_dict['expire']),
        )


@pytest.mark.now('2019-05-01T12:00:00+0300')
@pytest.mark.parametrize(
    'expected_notification_template, expected_expires_at, expect_saga_fail',
    (
        pytest.param(
            _TEMPLATE_WITH_BUTTON_FULLSCREEN,
            '2019-05-02T12:00:00+03:00',
            False,
            id='full_message',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_WALL_NOTIFICATION_TYPES={
                        'enable_notifications': True,
                        'notification_settings': {
                            'current_mode_unavailable': {
                                'enabled': True,
                                'payload': {
                                    'button': {
                                        'caption': (
                                            'driver_wall.'
                                            'current_mode_unavailable.'
                                            'button_title'
                                        ),
                                        'url': _OFFERS_LIST_DEEPLINK,
                                    },
                                    'text': (
                                        'driver_wall.'
                                        'current_mode_unavailable.text'
                                    ),
                                    'title': (
                                        'driver_wall.'
                                        'current_mode_unavailable.title'
                                    ),
                                    'is_fullscreen': True,
                                },
                                'ttl_days': 1,
                            },
                        },
                    },
                ),
            ],
        ),
        pytest.param(
            _TEMPLATE_WITHOUT_BUTTON_NORMAL,
            '2019-05-11T12:00:00+03:00',
            False,
            id='no_button',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_WALL_NOTIFICATION_TYPES={
                        'enable_notifications': True,
                        'notification_settings': {
                            'current_mode_unavailable': {
                                'enabled': True,
                                'payload': {
                                    'text': (
                                        'driver_wall.'
                                        'current_mode_unavailable.text'
                                    ),
                                    'title': (
                                        'driver_wall.'
                                        'current_mode_unavailable.title'
                                    ),
                                    'is_fullscreen': False,
                                },
                                'ttl_days': 10,
                            },
                        },
                    },
                ),
            ],
        ),
        pytest.param(
            _TEMPLATE_WITHOUT_BUTTON_NORMAL,
            '2019-05-11T12:00:00+03:00',
            True,
            id='failed_localization',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_WALL_NOTIFICATION_TYPES={
                        'enable_notifications': True,
                        'notification_settings': {
                            'current_mode_unavailable': {
                                'enabled': True,
                                'payload': {
                                    'text': 'incorrect_key',
                                    'title': (
                                        'driver_wall.'
                                        'current_mode_unavailable.title'
                                    ),
                                    'is_fullscreen': False,
                                },
                                'ttl_days': 1,
                            },
                        },
                    },
                ),
            ],
        ),
        pytest.param(
            None,
            None,
            False,
            id='disabled_type',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_WALL_NOTIFICATION_TYPES={
                        'enable_notifications': True,
                        'notification_settings': {
                            'current_mode_unavailable': {
                                'enabled': False,
                                'payload': {
                                    'text': (
                                        'driver_wall.'
                                        'current_mode_unavailable.text'
                                    ),
                                    'title': (
                                        'driver_wall.'
                                        'current_mode_unavailable.title'
                                    ),
                                    'is_fullscreen': False,
                                },
                                'ttl_days': 1,
                            },
                        },
                    },
                ),
            ],
        ),
        pytest.param(
            None,
            None,
            False,
            id='missing_type',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_WALL_NOTIFICATION_TYPES={
                        'enable_notifications': True,
                        'notification_settings': {
                            'wrong_type': {
                                'enabled': True,
                                'payload': {
                                    'text': (
                                        'driver_wall.'
                                        'current_mode_unavailable.text'
                                    ),
                                    'title': (
                                        'driver_wall.'
                                        'current_mode_unavailable.title'
                                    ),
                                    'is_fullscreen': False,
                                },
                                'ttl_days': 1,
                            },
                        },
                    },
                ),
            ],
        ),
        pytest.param(
            None,
            None,
            False,
            id='config_disabled',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_WALL_NOTIFICATION_TYPES={
                        'enable_notifications': False,
                        'notification_settings': {
                            'current_mode_unavailable': {
                                'enabled': True,
                                'payload': {
                                    'text': (
                                        'driver_wall.'
                                        'current_mode_unavailable.text'
                                    ),
                                    'title': (
                                        'driver_wall.'
                                        'current_mode_unavailable.title'
                                    ),
                                    'is_fullscreen': False,
                                },
                                'ttl_days': 1,
                            },
                        },
                    },
                ),
            ],
        ),
    ),
)
@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        saga_tools.make_insert_saga_query(
            park_id='dbid1',
            driver_id='uuid1',
            next_mode='orders',
            next_mode_settings=None,
            next_mode_timepoint='2019-05-01T12:00:00+0300',
            prev_mode='driver_fix',
            prev_mode_settings=None,
            prev_mode_timepoint='2019-05-01T10:00:00+0300',
            source=saga_tools.SOURCE_SUBSCRIPTION_SYNC,
            change_reason=saga_tools.REASON_CURRENT_MODE_UNAVAILABLE,
        ),
    ],
)
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [mode_rules.Patch(rule_name='driver_fix', features={})],
    ),
)
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_UNSUBSCRIBE_REASONS=_UNSUBSCRIBE_REASONS,
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
async def test_subscription_saga_wall_notification(
        taxi_driver_mode_subscription,
        mode_rules_data,
        stq,
        stq_runner,
        mockserver,
        mocked_time,
        pgsql,
        expected_notification_template: Optional[Dict[str, Any]],
        expected_expires_at: Optional[str],
        expect_saga_fail: bool,
):
    driver_profile = driver.Profile('dbid1_uuid1')
    scene = scenario.Scene(
        profiles={
            driver_profile: driver.Mode(
                'driver_fix', mode_settings=common.MODE_SETTINGS,
            ),
        },
    )

    scene.setup(mockserver, mocked_time)

    saga_id = saga_tools.get_saga_db_data(driver_profile, pgsql)[0]
    expected_idempotency_key = saga_tools.make_idempotency_key(
        saga_id, 'notifications_step', False,
    )

    @mockserver.json_handler('/driver-wall/internal/driver-wall/v1/add')
    def driver_wall_mock(request):
        return {'id': request.json['id']}

    await saga_tools.call_stq_saga_task(
        stq_runner, driver_profile, expect_saga_fail,
    )

    if expect_saga_fail:
        return

    if expected_notification_template:
        assert expected_expires_at

        assert driver_wall_mock.times_called == 1
        driver_wall_request = driver_wall_mock.next_call()['request']

        assert (
            driver_wall_request.headers['X-Idempotency-Token']
            == expected_idempotency_key
        )

        assert (
            DriverWallRequestBody.from_dict(driver_wall_request.json)
            == DriverWallRequestBody(
                id_=expected_idempotency_key,
                template=expected_notification_template,
                filters={'drivers': ['dbid1_uuid1']},
                expire=dt.datetime.fromisoformat(expected_expires_at),
            )
        )
    else:
        assert not driver_wall_mock.has_calls
