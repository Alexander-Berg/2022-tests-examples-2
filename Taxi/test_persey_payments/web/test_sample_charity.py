import pytest


@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
@pytest.mark.parametrize(
    'post_kwargs', [{}, {'json': {}}, {'json': {'fund_id': 'some_fund'}}],
)
@pytest.mark.parametrize(
    'response_additional',
    [
        pytest.param(
            {'stock_link': 'http://stock.com'},
            marks=pytest.mark.config(
                PERSEY_PAYMENTS_FUNDS={
                    'operator_uid': '123',
                    'funds': [
                        {
                            'fund_id': 'some_fund',
                            'name': 'name',
                            'balance_client_id': 'id',
                            'offer_link': 'offer_link',
                            'stock_link': 'http://stock.com',
                        },
                    ],
                },
            ),
        ),
        pytest.param(
            {},
            marks=pytest.mark.config(
                PERSEY_PAYMENTS_FUNDS={
                    'operator_uid': '123',
                    'funds': [
                        {
                            'fund_id': 'some_fund',
                            'name': 'name',
                            'balance_client_id': 'id',
                            'offer_link': 'offer_link',
                        },
                    ],
                },
            ),
        ),
        pytest.param(
            {},
            marks=pytest.mark.config(
                PERSEY_PAYMENTS_FUNDS={'operator_uid': '123', 'funds': []},
            ),
        ),
    ],
)
async def test_simple(
        taxi_persey_payments_web, post_kwargs, response_additional,
):
    response = await taxi_persey_payments_web.post(
        '/payments/v1/charity/sample', **post_kwargs,
    )

    assert response.status == 200

    response_json = {
        'fund_id': 'some_fund',
        'name': 'Имя фонда',
        'offer_link': 'http://fund.com',
    }
    response_json.update(response_additional)

    assert await response.json() == response_json


@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
async def test_nonexistent(taxi_persey_payments_web):
    response = await taxi_persey_payments_web.post(
        '/payments/v1/charity/sample', json={'fund_id': 'nonexistent'},
    )

    assert response.status == 400
    assert await response.json() == {
        'code': 'NO_FUNDS',
        'message': 'There is no funds to sample from',
    }


@pytest.mark.pgsql('persey_payments', files=['exclude_from_sampling.sql'])
@pytest.mark.parametrize(
    'request_json, expected_status_code, expected_response',
    [
        (
            {},
            400,
            {
                'code': 'NO_FUNDS',
                'message': 'There is no funds to sample from',
            },
        ),
        (
            {'fund_id': 'some_fund'},
            200,
            {
                'fund_id': 'some_fund',
                'name': 'Имя фонда',
                'offer_link': 'http://fund.com',
            },
        ),
    ],
)
async def test_exclude_from_sampling(
        taxi_persey_payments_web,
        request_json,
        expected_status_code,
        expected_response,
):
    response = await taxi_persey_payments_web.post(
        '/payments/v1/charity/sample', json=request_json,
    )

    assert response.status == expected_status_code
    assert await response.json() == expected_response
