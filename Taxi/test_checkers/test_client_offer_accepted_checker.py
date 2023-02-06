import pytest

from taxi_corp_integration_api import consts
from taxi_corp_integration_api.api.common.payment_methods import (
    client_checkers,
)
from test_taxi_corp_integration_api import utils
from test_taxi_corp_integration_api.test_checkers import (
    utils as checkers_utils,
)


@pytest.mark.parametrize(
    ['input_data', 'expected_result'],
    [
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client={'_id': 'client_id_2'},
                    client_contracts=[
                        {
                            'service_ids': [650],
                            'is_active': True,
                            'is_offer': True,
                            'offer_accepted': False,
                        },
                    ],
                ),
                'service': consts.ServiceName.TAXI,
            },
            (True, ''),
            id='client in skip config',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client_contracts=[
                        {
                            'service_ids': [650],
                            'is_active': True,
                            'is_offer': True,
                            'offer_accepted': True,
                        },
                    ],
                ),
                'service': consts.ServiceName.TAXI,
            },
            (True, ''),
            id='is_offer and offer_accepted',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client_contracts=[
                        {
                            'service_ids': [650],
                            'is_active': True,
                            'is_offer': True,
                            'offer_accepted': True,
                            'edo_accepted': False,
                        },
                    ],
                ),
                'service': consts.ServiceName.TAXI,
            },
            (True, ''),
            id='is_offer and offer_accepted and not edo_accepted',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client_contracts=[
                        {
                            'service_ids': [650],
                            'is_active': True,
                            'is_offer': True,
                            'offer_accepted': False,
                        },
                    ],
                ),
                'service': consts.ServiceName.TAXI,
            },
            (False, 'Оферта не принята'),
            id='is_offer and not offer_accepted',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client_contracts=[
                        {
                            'service_ids': [650],
                            'is_active': True,
                            'is_offer': True,
                            'offer_accepted': False,
                            'edo_accepted': None,
                        },
                    ],
                ),
                'service': consts.ServiceName.TAXI,
            },
            (False, 'Оферта не принята'),
            id='is_offer and not offer_accepted and edo_accepted is None',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client_contracts=[
                        {
                            'service_ids': [650],
                            'is_active': True,
                            'is_offer': True,
                            'offer_accepted': False,
                            'edo_accepted': True,
                        },
                    ],
                ),
                'service': consts.ServiceName.TAXI,
            },
            (True, ''),
            id='is_offer and not offer_accepted and edo_accepted',
        ),
    ],
)
@pytest.mark.translations(**utils.TRANSLATIONS)
@pytest.mark.config(CORP_CLIENTS_WITH_UNCHECKED_OFFER_ACCEPTED=['client_id_2'])
async def test_client_offer_accepted_checker(
        web_context, input_data, expected_result,
):
    checker = checkers_utils.get_checker_instance(
        client_checkers.ClientOfferAcceptedChecker, web_context, **input_data,
    )

    assert await checker.check() == expected_result
