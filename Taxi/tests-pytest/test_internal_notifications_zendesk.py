import pytest

from taxi import config

from taxi.internal import dbh
from taxi.internal.notifications import zendesk


@pytest.mark.config(USER_CHAT_PLATFORM_BY_APPLICATION={
    'android': 'yandex',
    'iphone': 'yandex',
    'taximeter': 'taximeter',
    'uber_android': 'uber',
    'uber_az_android': 'uber',
    'uber_az_iphone': 'uber',
    'uber_by_android': 'uber',
    'uber_by_iphone': 'uber',
    'uber_iphone': 'uber',
    'uber_kz_android': 'uber',
    'uber_kz_iphone': 'uber',
    'yango_android': 'yango',
    'yango_iphone': 'yango',
})
@pytest.mark.parametrize(
    'user_id, result_deeplink',
    [
        ('user_iphone', 'yandextaxi://chat'),
        ('user_yango_android', 'yandexyango://chat'),
        ('user_uber_iphone', 'ubermlbv://chat'),
        ('user_uber_android', 'ubermlbv://chat'),
    ]
)
@pytest.inline_callbacks
def test_deeplink_by_user(user_id, result_deeplink):
    user = yield dbh.users.Doc.find_one_by_id(user_id)
    push_config = yield config.USER_CHAT_PUSH_BY_TYPES.get()
    deeplink = yield zendesk._get_deeplink_by_user(
        user, push_config['client_support']['deeplink']
    )
    assert deeplink == result_deeplink
