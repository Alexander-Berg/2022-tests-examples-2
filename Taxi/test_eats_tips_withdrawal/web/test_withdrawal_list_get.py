import pytest

from test_eats_tips_withdrawal import conftest


RUB_CURRENCY_FORMAT = {
    'code': 'RUB',
    'sign': '₽',
    'template': '$VALUE$&nbsp$SIGN$$CURRENCY$',
    'text': 'руб.',
}
OUTPUT = {
    'pg': {
        'old': {
            'amount': {'currency': RUB_CURRENCY_FORMAT, 'price_value': '20'},
            'fee': {'currency': RUB_CURRENCY_FORMAT, 'price_value': '0'},
            'card_pan': 'some_pan1',
            'created_at': '2021-06-22T18:10:20+03:00',
            'id': '1',
            'status': 'error',
        },
        'success0': {
            'amount': {
                'currency': RUB_CURRENCY_FORMAT,
                'price_value': '20.10',
            },
            'fee': {'currency': RUB_CURRENCY_FORMAT, 'price_value': '10'},
            'card_pan': 'some_pan2',
            'created_at': '2021-06-22T19:10:23+03:00',
            'id': '2',
            'status': 'success',
        },
        'manual': {
            'amount': {
                'currency': RUB_CURRENCY_FORMAT,
                'price_value': '20.50',
            },
            'fee': {'currency': RUB_CURRENCY_FORMAT, 'price_value': '0'},
            'card_pan': 'some_pan3',
            'created_at': '2021-06-22T19:10:24+03:00',
            'id': '3',
            'status': 'manual',
        },
        'success1': {
            'amount': {
                'currency': RUB_CURRENCY_FORMAT,
                'price_value': '20.20',
            },
            'fee': {'currency': RUB_CURRENCY_FORMAT, 'price_value': '0'},
            'card_pan': 'some_pan4',
            'created_at': '2021-06-22T19:10:25+03:00',
            'id': '4',
            'status': 'success',
        },
        'success2': {
            'amount': {
                'currency': RUB_CURRENCY_FORMAT,
                'price_value': '20.70',
            },
            'fee': {'currency': RUB_CURRENCY_FORMAT, 'price_value': '20'},
            'card_pan': 'some_pan5',
            'created_at': '2021-06-22T19:10:26+03:00',
            'id': '5',
            'status': 'success',
        },
        'new': {
            'amount': {'currency': RUB_CURRENCY_FORMAT, 'price_value': '20'},
            'fee': {'currency': RUB_CURRENCY_FORMAT, 'price_value': '0'},
            'card_pan': 'some_pan6',
            'created_at': '2021-06-22T20:10:30+03:00',
            'id': '6',
            'status': 'error',
        },
    },
}


def date_sorted(values):
    return sorted(values, key=lambda x: x['created_at'], reverse=True)


@pytest.mark.parametrize(
    'recipient_id, limit, date_from, date_to, expected_result',
    [
        pytest.param(
            conftest.USER_ID_2,
            None,
            '2021-06-21T19:00:00.07+03:00',
            '2021-06-23T19:30:30.07+03:00',
            date_sorted(OUTPUT['pg'].values()),
            id='pg all',
        ),
        pytest.param(
            conftest.USER_ID_2,
            None,
            None,
            '2021-06-23T19:30:30.07+03:00',
            date_sorted(OUTPUT['pg'].values()),
            id='pg all fromless',
        ),
        pytest.param(
            conftest.USER_ID_2,
            None,
            '2021-06-22T19:00:00.07+03:00',
            '2021-06-22T20:30:30.07+03:00',
            date_sorted(OUTPUT['pg'].values())[:-1],
            id='pg without old no limit',
        ),
        pytest.param(
            conftest.USER_ID_2,
            3,
            '2021-06-22T19:00:00.07+03:00',
            '2021-06-22T20:30:30.07+03:00',
            date_sorted(OUTPUT['pg'].values())[:3],
            id='pg without old limit 3',
        ),
        pytest.param(
            conftest.USER_ID_2,
            None,
            '2021-06-22T19:00:00.07+03:00',
            '2021-06-22T19:30:30.07+03:00',
            date_sorted(OUTPUT['pg'].values())[1:5],
            id='pg middle date range',
        ),
        pytest.param(
            conftest.USER_ID_2,
            3,
            None,
            '2021-06-22T19:30:30.07+03:00',
            date_sorted(OUTPUT['pg'].values())[1:4],
            id='pg fromless limit 3',
        ),
        pytest.param(
            conftest.USER_ID_2,
            3,
            None,
            '2021-06-22T19:00:00.07+03:00',
            date_sorted(OUTPUT['pg'].values())[-1:],
            id='pg fromless before middle limit 3',
        ),
    ],
)
@pytest.mark.now('2021-06-22T19:40:25.077345+03:00')
@pytest.mark.mysql('chaevieprosto', files=['mysql_chaevieprosto.sql'])
@pytest.mark.pgsql('eats_tips_withdrawal', files=['pg.sql'])
async def test_withdrawal_list(
        mock_eats_tips_partners,
        web_app_client,
        web_context,
        recipient_id,
        limit,
        date_from,
        date_to,
        expected_result,
):
    params = {'recipient_id': recipient_id, 'date_to': date_to}
    if date_from is not None:
        params['date_from'] = date_from
    if limit is not None:
        params['limit'] = limit
    response = await web_app_client.get(
        '/internal/v1/withdrawal/list', params=params,
    )
    assert response.status == 200
    content = await response.json()
    assert content == {'withdrawals': expected_result}
