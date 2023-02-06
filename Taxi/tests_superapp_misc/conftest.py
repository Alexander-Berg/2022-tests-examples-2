import pytest
# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from superapp_misc_plugins import *  # noqa: F403 F401

CLIENT_MESSAGES_TRANSLATIONS = {
    'superapp.taxi.service_name': {'ru': 'Taxi'},
    'superapp.eats.service_name': {'ru': 'Eats'},
    'superapp.grocery.service_name': {'ru': 'Grocery'},
    'superapp.drive.service_name': {'ru': 'Drive'},
    'superapp.masstransit.service_name': {'ru': 'Masstransit'},
    'superapp.delivery.service_name': {'ru': 'Delivery'},
}


def pytest_collection_modifyitems(config, items):
    for item in items:
        item.add_marker(
            pytest.mark.geoareas(filename='db_geoareas.json', db_format=True),
        )
        item.add_marker(pytest.mark.tariffs(filename='tariffs.json'))
        item.add_marker(
            pytest.mark.translations(
                client_messages=CLIENT_MESSAGES_TRANSLATIONS,
            ),
        )


@pytest.fixture()
def add_experiment(experiments3):
    def _wrapper(name, value, consumers=None, predicate=None):
        if consumers is None:
            consumers = ['superapp-misc/availability']
        if predicate is None:
            predicate = {'type': 'true'}

        experiments3.add_experiment(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name=name,
            consumers=consumers,
            clauses=[
                {
                    'title': 'test_experiment',
                    'value': value,
                    'predicate': predicate,
                },
            ],
        )

    return _wrapper
