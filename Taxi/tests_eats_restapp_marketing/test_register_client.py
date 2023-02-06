import pytest


TEST_UID = '100'
TEST_FIO = 'Козьма Прутков'
TEST_COUNTRY = 225
TEST_CURRENCY = 'RUB'
TEST_HEADERS = {'X-Yandex-UID': TEST_UID, 'X-Remote-IP': '1.2.3.4'}


@pytest.fixture(name='mock_register_client')
async def _mock_register_client(mockserver):
    async def do_mock_register_client(
            uid=TEST_UID,
            fio=TEST_FIO,
            country=TEST_COUNTRY,
            currency=TEST_CURRENCY,
            with_api=True,
            fails=False,
    ):
        @mockserver.json_handler('/direct-internal/clients/addOrGet')
        async def _do_mock_register_client(request):
            assert request.json['uid'] == int(uid)
            assert request.json['country'] == country
            assert request.json['currency'] == currency
            assert request.json['with_api'] == with_api

            if fio:
                assert request.json['fio'] == fio
            else:
                assert request.json['fio'] == ''

            if fails:
                return mockserver.make_response(status=500)

            if not fio or country != TEST_COUNTRY or currency != TEST_CURRENCY:
                return mockserver.make_response(
                    status=200,
                    json={
                        'success': False,
                        'code': 1000,
                        'text': (
                            'DefectInfo{path=fio, '
                            'defect=Defect{defectId=CANNOT_BE_EMPTY,'
                            ' params=null}, value=}'
                        ),
                    },
                )

            data = {
                'success': True,
                'client_id': 111111111,
                'user_id': int(uid),
            }
            if with_api:
                data['finance_token'] = 'tokentoken'

            return data

        return _do_mock_register_client

    return do_mock_register_client


async def test_register_client(
        taxi_eats_restapp_marketing,
        mock_blackbox_userinfo,
        mock_register_client,
):
    bb_handler = await mock_blackbox_userinfo()
    direct_handler = await mock_register_client()

    response = await taxi_eats_restapp_marketing.post(
        f'/4.0/restapp-front/marketing/v1/register-partner',
        headers=TEST_HEADERS,
    )

    assert bb_handler.times_called == 1
    assert direct_handler.times_called == 1

    assert response.status == 200
    assert response.json() == {'status': 'ok'}


async def test_duplicate_register_client(
        taxi_eats_restapp_marketing,
        mock_blackbox_userinfo,
        mock_register_client,
):
    bb_handler = await mock_blackbox_userinfo()
    direct_handler = await mock_register_client()

    first_response = await taxi_eats_restapp_marketing.post(
        f'/4.0/restapp-front/marketing/v1/register-partner',
        headers=TEST_HEADERS,
    )
    assert first_response.status == 200
    assert first_response.json() == {'status': 'ok'}

    second_response = await taxi_eats_restapp_marketing.post(
        f'/4.0/restapp-front/marketing/v1/register-partner',
        headers=TEST_HEADERS,
    )
    assert second_response.status == 200
    assert second_response.json() == {'status': 'ok'}

    assert bb_handler.times_called == 2
    assert direct_handler.times_called == 2


async def test_not_found_in_bb(
        taxi_eats_restapp_marketing,
        mock_blackbox_userinfo,
        mock_register_client,
):
    bb_handler = await mock_blackbox_userinfo(not_found=True)
    direct_handler = await mock_register_client(fio=None)

    response = await taxi_eats_restapp_marketing.post(
        f'/4.0/restapp-front/marketing/v1/register-partner',
        headers=TEST_HEADERS,
    )

    assert bb_handler.times_called == 1
    assert direct_handler.times_called == 1

    assert response.status == 200
    assert response.json() == {'status': 'error', 'error_slug': 'EMPTY_FIO'}


async def test_no_fio_in_bb(
        taxi_eats_restapp_marketing,
        mock_blackbox_userinfo,
        mock_register_client,
):
    bb_handler = await mock_blackbox_userinfo(fio=None)
    direct_handler = await mock_register_client(fio=None)

    response = await taxi_eats_restapp_marketing.post(
        f'/4.0/restapp-front/marketing/v1/register-partner',
        headers=TEST_HEADERS,
    )

    assert bb_handler.times_called == 1
    assert direct_handler.times_called == 1

    assert response.status == 200
    assert response.json() == {'status': 'error', 'error_slug': 'EMPTY_FIO'}


@pytest.mark.parametrize(
    'bb_fails, direct_fails, expected_response',
    [
        pytest.param(
            True,
            False,
            {'status': 'error', 'error_slug': 'EMPTY_FIO'},
            id='bb fails',
        ),
        pytest.param(
            False,
            True,
            {'status': 'error', 'error_slug': 'UNDEFINED_ERROR'},
            id='direct fails',
        ),
        pytest.param(
            True,
            True,
            {'status': 'error', 'error_slug': 'UNDEFINED_ERROR'},
            id='both fail',
        ),
    ],
)
async def test_bb_fails(
        taxi_eats_restapp_marketing,
        mock_blackbox_userinfo,
        mock_register_client,
        bb_fails,
        direct_fails,
        expected_response,
):
    fio = TEST_FIO
    if bb_fails:
        fio = None

    bb_handler = await mock_blackbox_userinfo(fails=bb_fails)
    direct_handler = await mock_register_client(fails=direct_fails, fio=fio)

    response = await taxi_eats_restapp_marketing.post(
        f'/4.0/restapp-front/marketing/v1/register-partner',
        headers=TEST_HEADERS,
    )

    if bb_fails:
        assert bb_handler.times_called == 3
    else:
        assert bb_handler.times_called == 1

    assert direct_handler.times_called == 1

    assert response.status == 200
    assert response.json() == expected_response


async def test_add_advert_client(
        taxi_eats_restapp_marketing,
        mock_blackbox_userinfo,
        mock_register_client,
        pgsql,
):
    bb_handler = await mock_blackbox_userinfo()
    direct_handler = await mock_register_client()

    response = await taxi_eats_restapp_marketing.post(
        f'/4.0/restapp-front/marketing/v1/register-partner',
        headers=TEST_HEADERS,
    )

    assert bb_handler.times_called == 1
    assert direct_handler.times_called == 1

    assert response.status == 200
    assert response.json() == {'status': 'ok'}

    cursor = pgsql['eats_restapp_marketing'].cursor()
    cursor.execute(
        'SELECT count(*) FROM eats_restapp_marketing.advert_clients',
    )
    assert [(1,)] == list(cursor)

    cursor.execute(
        'SELECT passport_id, client_id '
        'FROM eats_restapp_marketing.advert_clients',
    )
    assert [(TEST_HEADERS['X-Yandex-UID'], 111111111)] == list(cursor)


async def test_add_advert_client_double(
        taxi_eats_restapp_marketing,
        mock_blackbox_userinfo,
        mock_register_client,
        pgsql,
):
    bb_handler = await mock_blackbox_userinfo()
    direct_handler = await mock_register_client()

    response = await taxi_eats_restapp_marketing.post(
        f'/4.0/restapp-front/marketing/v1/register-partner',
        headers=TEST_HEADERS,
    )

    assert bb_handler.times_called == 1
    assert direct_handler.times_called == 1

    assert response.status == 200
    assert response.json() == {'status': 'ok'}

    cursor = pgsql['eats_restapp_marketing'].cursor()
    cursor.execute(
        'SELECT count(*) FROM eats_restapp_marketing.advert_clients',
    )
    assert [(1,)] == list(cursor)

    cursor.execute(
        'SELECT passport_id, client_id '
        'FROM eats_restapp_marketing.advert_clients',
    )
    assert [(TEST_HEADERS['X-Yandex-UID'], 111111111)] == list(cursor)

    response = await taxi_eats_restapp_marketing.post(
        f'/4.0/restapp-front/marketing/v1/register-partner',
        headers=TEST_HEADERS,
    )

    assert bb_handler.times_called == 2
    assert direct_handler.times_called == 2

    assert response.status == 200
    assert response.json() == {'status': 'ok'}

    cursor.execute(
        'SELECT count(*) FROM eats_restapp_marketing.advert_clients',
    )
    assert [(1,)] == list(cursor)

    cursor.execute(
        'SELECT passport_id, client_id '
        'FROM eats_restapp_marketing.advert_clients',
    )
    assert [(TEST_HEADERS['X-Yandex-UID'], 111111111)] == list(cursor)
