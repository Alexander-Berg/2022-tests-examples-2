import typing

from taxi import pro_app

from taxi_selfreg.components import car_checker

TAXIMETER_USER_AGENT = 'Taximeter 9.61 (1234)'


async def test_ok(web_app_client, patch):
    @patch('taxi_selfreg.components.car_checker.Component.check')
    async def _check(
            phone_pd_id: typing.Optional[str],
            app: pro_app.ProApp,
            city_name: str,
            brand: str,
            model: str,
            year: int,
            car_number: typing.Optional[str] = None,
    ):
        assert phone_pd_id == 'some_phone_pd_id'
        assert city_name == 'Москва'
        assert brand == 'Ваз'
        assert model == '2106'
        assert year == 2020
        assert car_number is None
        return None

    response = await web_app_client.get(
        '/selfreg/v1/car/check',
        headers={'User-Agent': TAXIMETER_USER_AGENT},
        params={
            'token': 'token1',
            'city': 'Москва',
            'brand': 'Ваз',
            'model': '2106',
            'year': 2020,
        },
    )

    assert response.status == 200
    assert await response.json() == {'allowed': True}


async def test_rejected(web_app_client, patch):
    @patch('taxi_selfreg.components.car_checker.Component.check')
    async def _check(
            phone_pd_id: typing.Optional[str],
            app: pro_app.ProApp,
            city_name: str,
            brand: str,
            model: str,
            year: int,
            car_number: typing.Optional[str] = None,
    ):
        assert phone_pd_id == 'some_phone_pd_id'
        assert city_name == 'Москва'
        assert brand == 'таз'
        assert model == 'шоха'
        assert year == 2020
        assert car_number is None

        return car_checker.Rejected()

    response = await web_app_client.get(
        '/selfreg/v1/car/check',
        headers={'User-Agent': TAXIMETER_USER_AGENT},
        params={
            'token': 'token1',
            'city': 'Москва',
            'brand': 'таз',
            'model': 'шоха',
            'year': 2020,
        },
    )

    assert response.status == 200
    assert await response.json() == {'allowed': False}


async def test_unauthorized(taxi_selfreg):
    response = await taxi_selfreg.get(
        '/selfreg/v1/car/check',
        headers={'User-Agent': TAXIMETER_USER_AGENT},
        params={
            'token': 'bad_token',
            'city': 'Москва',
            'brand': 'Ваз',
            'model': '2106',
            'year': 2020,
        },
    )

    assert response.status == 401
