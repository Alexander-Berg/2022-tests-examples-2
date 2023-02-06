# pylint: disable=redefined-outer-name
import pytest

import localization.generated.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['localization.generated.pytest_plugins']

TRANSLATIONS = {
    'company': {'en': 'Yandex', 'ru': 'Яндекс'},
    'text': {
        'en': 'Lorem ipsum dolor sit amet',
        'ru': 'Lorem ipsum dolor sit amet',
    },
    'title': {'en': 'Welcome!', 'ru': 'Добро пожаловать'},
}


AZ_TRANSLATIONS = {
    'company': {'en': 'Uber', 'ru': 'Uber'},
    'title': {'ru': 'Привет'},
}

YANGO_TRANSLATIONS = {'company': {'en': 'Yango'}}


@pytest.fixture(name='mock_driver_profiles_app', autouse=True)
def mock_driver_profiles_app(mockserver):
    def _mock_driver_profiles_app_version(
            driver_app: str = 'yandex', lang: str = 'ru',
    ):
        @mockserver.json_handler(
            '/driver-profiles/v1/driver/app/profiles/retrieve',
        )
        async def _retrieve(request):
            return {
                'profiles': [
                    {
                        'park_driver_profile_id': 'park_driver',
                        'data': {
                            'locale': lang,
                            'taximeter_brand': driver_app,
                        },
                    },
                ],
            }

    return _mock_driver_profiles_app_version
