import pytest

from order_notify.repositories import configs as configs_repo


@pytest.mark.config(
    APPLICATION_MAP_BRAND={'__default__': 'yataxi', 'vezet_ios': 'vezet'},
    COMMUNICATIONS_SMS_SENDER_BY_BRAND={'yataxi': 'go'},
)
@pytest.mark.parametrize(
    'application, expected_sender',
    [
        pytest.param('yataxi', 'go', id='simple'),
        pytest.param('vezet_ios', None, id='vezet'),
        pytest.param('unknown', 'go', id='unknown'),
    ],
)
async def test_sms_sender(stq3_context, application, expected_sender):
    sender = configs_repo.get_sms_sender(stq3_context, application)
    assert sender == expected_sender


@pytest.mark.config(
    APPLICATION_MAP_BRAND={'__default__': 'yataxi', 'vezet_ios': 'vezet'},
    DEEPLINK_PREFIX={'yataxi': 'yandextaxi', 'vezet': 'vezet'},
)
@pytest.mark.parametrize(
    'application, expected_deeplink',
    [
        pytest.param(
            'yataxi', 'yandextaxi://linkedorder?key=key_1', id='simple',
        ),
        pytest.param('vezet_ios', 'vezet://linkedorder?key=key_1', id='vezet'),
        pytest.param(
            'unknown', 'yandextaxi://linkedorder?key=key_1', id='unknown',
        ),
    ],
)
async def test_deeplink_linkedorder(
        stq3_context, application, expected_deeplink,
):
    deeplink = configs_repo.get_deeplink_linkedorder(
        stq3_context, application, 'key_1',
    )
    assert deeplink == expected_deeplink


@pytest.mark.config(
    NOTIFICATION_SUFFIX_BY_TARIFF={
        'econom': {'notifications': ['driving'], 'suffix': 'econom_suffix'},
    },
)
@pytest.mark.parametrize(
    'tariff_class, notification_name, expected_suffix',
    [
        pytest.param('econom', 'driving', 'econom_suffix', id='simple'),
        pytest.param('econom', 'unknown', None, id='disabled notification'),
        pytest.param('vip', '', None, id='disabled tariff'),
    ],
)
async def test_tk_suffix_by_tariff(
        stq3_context, tariff_class, notification_name, expected_suffix,
):
    suffix = configs_repo.get_tk_suffix_by_tariff(
        stq3_context, tariff_class, notification_name,
    )
    assert suffix == expected_suffix
