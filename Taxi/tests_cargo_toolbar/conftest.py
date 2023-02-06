import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from cargo_toolbar_plugins import *  # noqa: F403 F401


@pytest.fixture(name='default_pa_headers')
def _default_pa_headers():
    def _wrapper(phone_pd_id, app_brand='yataxi'):
        return {
            'X-Yandex-UID': 'yandex_uid',
            'X-Request-Language': 'ru',
            'X-YaTaxi-User': (
                f'personal_phone_id={phone_pd_id},'
                'personal_email_id=333,'
                'eats_user_id=444'
            ),
            'X-Request-Application': (
                f'app_name=iphone,app_ver1=10,app_ver2=2,app_brand={app_brand}'
            ),
            'User-Agent': 'some_agent',
            'X-YaTaxi-UserId': 'some_user_id',
            'Timezone': 'Europe/Moscow',
        }

    return _wrapper
