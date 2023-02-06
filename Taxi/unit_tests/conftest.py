from taxidwh_settings import build_settings, DictSettingsSource
from context import settings


def unittest_settings():
    return build_settings(
        DictSettingsSource({
            'GP': {'DATABASE': {'UNITTEST': {'CONTOUR': 'test', 'MAX_TABLE_NAME_LENGTH': 99}}},
            'SQS': {
                'ACCESS_KEY': 'mock',
                'SECRET_KEY': 'mock',
                'SESSION_TOKEN': 'mock',
                'ENDPOINT': 'mock'
            },
            'APP': {'CELERY': {'BROKER': 'SQS'}}
        })
    )


def pytest_sessionstart(session):
    settings.settings = unittest_settings()
