import decimal
import typing as tp

from fleet_rent.use_cases import park_total_balances_sums


async def test_ok(patch, web_app_client):
    @patch(
        'fleet_rent.use_cases.park_total_balances_sums'
        '.ParkTotalBalancesSums.__call__',
    )
    async def _call(
            park_id: str,
            driver_profile_id: tp.Optional[str],
            states: tp.Union[tp.Tuple[str], tp.List[str], None],
    ):
        assert park_id == '7ad36bc7560449998acbe2c57a75c293'
        assert driver_profile_id == 'did'
        assert states == ['ended', 'rejected']
        return park_total_balances_sums.Result(
            currency='RUB',
            withdraw=decimal.Decimal(10),
            withhold=decimal.Decimal(14),
            cancel=decimal.Decimal(1),
        )

    response = await web_app_client.post(
        '/fleet/rent/v1/park/rents/balances/total',
        headers={
            'Accept-Language': 'ru',
            'X-Ya-User-Ticket': 'user_ticket',
            'X-Ya-User-Ticket-Provider': 'yandex',
            'X-Yandex-Login': 'abacaba',
            'X-Yandex-UID': '123',
            'X-Park-Id': '7ad36bc7560449998acbe2c57a75c293',
            'X-Real-IP': '127.0.0.1',
        },
        json={
            'filter': {
                'driver_profile_id': 'did',
                'states': ['ended', 'rejected'],
            },
        },
    )

    assert response.status == 200, await response.text()
    assert await response.json() == {
        'balances': {
            'cancel': {'amount': '1', 'currency': 'RUB'},
            'withdraw': {'amount': '10', 'currency': 'RUB'},
            'withhold': {'amount': '14', 'currency': 'RUB'},
        },
    }
