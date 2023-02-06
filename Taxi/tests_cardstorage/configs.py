import pytest

AVS_POST_CODE = 'avs post code'
AVS_STREET_ADDRESS = 'avs street address'

AVS_POST_CODE_PASSED = 'avs post code passed'
AVS_STREET_ADDRESS_PASSED = 'avs street address passed'

PROCESSING_NAME = 'sberbank'

RETURN_PATH = 'https://trust.ru/finish_3ds'

CHANGED_HOST = 'sos.com'

CARD_ID = 'card-x2809'

CARDSTORAGE_AVS_DATA = pytest.mark.experiments3(
    name='cardstorage_avs_data',
    consumers=['cardstorage/payment_verifications'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'avs_post_code': AVS_POST_CODE,
                'avs_street_address': AVS_STREET_ADDRESS,
            },
        },
    ],
    is_config=True,
)


BINDING_RETURN_PATH_URL = pytest.mark.experiments3(
    name='binding_return_path_url',
    consumers=['cardstorage/payment_verifications'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'return_path': RETURN_PATH},
        },
    ],
    is_config=True,
)


BILLING_SERVICE_NAME = pytest.mark.experiments3(
    name='payment_billing_service_name',
    consumers=['cardstorage/payment_verifications'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'uber',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': 'yauber',
                    'arg_name': 'application.brand',
                    'arg_type': 'string',
                },
            },
            'value': {'service_name': 'uber'},
        },
    ],
    default_value={'service_name': 'card'},
    is_config=True,
)

BILLING_FORM_HOST = pytest.mark.experiments3(
    name='binding_form_host',
    consumers=['cardstorage/payment_verifications'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'host': CHANGED_HOST},
        },
    ],
    default_value={'service_name': 'card'},
    is_config=True,
)

BINDING_PROCESSING_NAME = pytest.mark.experiments3(
    name='binding_processing_name',
    consumers=['cardstorage/payment_verifications'],
    default_value={'processing_name': PROCESSING_NAME},
    is_config=True,
)
