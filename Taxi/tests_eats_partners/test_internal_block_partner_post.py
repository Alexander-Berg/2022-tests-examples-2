# flake8: noqa
# pylint: disable=too-many-lines

import pytest


def get_update_in_vendor_experiment(disabled: bool):
    return pytest.mark.experiments3(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        is_config=True,
        name='eats_partners_update_in_vendor',
        consumers=['eats_partners/internal_create'],
        clauses=[],
        default_value={'disabled': disabled},
    )


@pytest.mark.pgsql('eats_partners', files=['insert_partner_data.sql'])
@pytest.mark.parametrize(
    'response_code, partner_id, vendor_response_code, vendor_response, vendor_expected_calls',
    [
        pytest.param(
            200,
            1,
            200,
            {'isSuccess': True},
            True,
            marks=(get_update_in_vendor_experiment(False)),
            id='normal block',
        ),
        pytest.param(
            200,
            2,
            200,
            {'isSuccess': True},
            True,
            marks=(get_update_in_vendor_experiment(False)),
            id='already blocked',
        ),
        pytest.param(
            200,
            3,
            200,
            {'isSuccess': True},
            False,
            marks=(get_update_in_vendor_experiment(False)),
            id='partner not found',
        ),
        pytest.param(
            200,
            1,
            None,
            None,
            False,
            marks=(get_update_in_vendor_experiment(True)),
            id='disable vendor update exp',
        ),
        pytest.param(
            400,
            1,
            400,
            {'isSuccess': False, 'errors': []},
            True,
            marks=(get_update_in_vendor_experiment(False)),
            id='error during delete in vendor',
        ),
        pytest.param(
            500,
            1,
            500,
            {'isSuccess': False},
            True,
            marks=(get_update_in_vendor_experiment(False)),
            id='internal error in vendor',
        ),
    ],
)
async def test_internal_block_partner(
        taxi_eats_partners,
        response_code,
        partner_id,
        vendor_response_code,
        vendor_response,
        vendor_expected_calls,
        pgsql,
        mockserver,
        mock_personal_retrieve,
):
    if vendor_expected_calls:

        @mockserver.json_handler(
            '/eats-vendor/api/v1/server/users/{}'.format(partner_id),
        )
        def _handler(_):
            return mockserver.make_response(
                status=vendor_response_code, json=vendor_response,
            )

    response = await taxi_eats_partners.post(
        '/internal/partners/v1/block?partner_id={}'.format(partner_id),
    )

    assert response.status_code == response_code
