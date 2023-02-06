# pylint: disable=invalid-name

import pytest

CIBUS_APPLICATION_ID = 'some-applicatin-id'
CIBUS_FINISH_URL = 'finish-url'
FINISH_FORM = '<html>123</html>'


class Context:
    def __init__(self, experiments3, taxi_config):
        self.experiments3 = experiments3
        self.taxi_config = taxi_config

        self.taxi_config.set(GROCERY_CIBUS_FINISH_URL=CIBUS_FINISH_URL)
        self.taxi_config.set(GROCERY_CIBUS_FINISH_FORM=FINISH_FORM)

    def set_payment_timeout(self, value):
        self.taxi_config.set(GROCERY_CIBUS_PAYMENT_TIMEOUT=value)

    def set_cibus_application_id(self, application_id):
        self.experiments3.add_config(
            name='grocery_cibus_application_id',
            consumers=['grocery-cibus'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=[
                {
                    'title': 'Always enabled',
                    'predicate': {'type': 'true'},
                    'value': {'application_id': application_id},
                },
            ],
        )

    def set_cibus_error_descriptions(self, value):
        self.taxi_config.set(GROCERY_CIBUS_ERROR_DESCRIPTIONS=value)


@pytest.fixture(name='grocery_cibus_configs', autouse=True)
def grocery_cibus_configs(experiments3, taxi_config):
    return Context(experiments3, taxi_config)


GROCERY_CURRENCY = pytest.mark.config(
    CURRENCY_ROUNDING_RULES={'RUB': {'__default__': 1, 'grocery': 0.0001}},
    CURRENCY_FORMATTING_RULES={
        'RUB': {
            '__default__': 2,
            'grocery': 2,  # проверяем что возьмется именно grocery
        },
    },
    CURRENCY_KEEP_TRAILING_ZEROS={
        'RUB': {
            '__default__': False,
            'grocery': True,  # проверяем что возьмется именно grocery
        },
    },
)
