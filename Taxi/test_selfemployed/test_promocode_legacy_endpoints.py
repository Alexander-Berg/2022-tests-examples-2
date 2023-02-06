# pylint: disable=redefined-outer-name,unused-variable
import pytest

from . import conftest


# Just copies tests for the properly named named endpoint


@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO referrals (park_id, driver_id, promocode)
        VALUES ('11p', '11d', 'PROMO11')
        """,
    ],
)
async def test_get_promocode(se_client):
    params = {'driver': '11d', 'park': '11p'}

    response = await se_client.get(
        '/self-employment/referral',
        headers=conftest.DEFAULT_HEADERS,
        params=params,
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'main_items': [
            {
                'horizontal_divider_type': 'full',
                'markdown': False,
                'right_icon': 'undefined',
                'title': 'Ваш промокод',
                'subtitle': 'PROMO11',
                'type': 'header',
            },
            {
                'accent': True,
                'markdown': True,
                'reverse': False,
                'title': 'Текст описания, зачем нужно делиться',
                'center': True,
                'type': 'detail',
            },
        ],
        'help_items': [
            {
                'subtitle': 'Пригласи друзей...',
                'gravity': 'left',
                'type': 'header',
            },
            {'markdown': True, 'title': '...и получи леща!', 'type': 'detail'},
            {'title': '', 'type': 'title'},
            {
                'subtitle': 'Условия для друзей',
                'gravity': 'left',
                'type': 'header',
            },
            {
                'accent': True,
                'horizontal_divider_type': 'bottom_icon',
                'left_tip': {
                    'background_color': '#FCB000',
                    'form': 'round',
                    'text': '>',
                },
                'right_icon': 'undefined',
                'title': 'Пункт 1',
                'type': 'tip_detail',
            },
            {
                'accent': True,
                'horizontal_divider_type': 'bottom_icon',
                'left_tip': {
                    'background_color': '#FCB000',
                    'form': 'round',
                    'text': '>',
                },
                'right_icon': 'undefined',
                'title': 'Пункт 2',
                'type': 'tip_detail',
            },
            {
                'accent': True,
                'horizontal_divider_type': 'bottom_icon',
                'left_tip': {
                    'background_color': '#FCB000',
                    'form': 'round',
                    'text': '>',
                },
                'title': 'Пункт 3',
                'right_icon': 'undefined',
                'type': 'tip_detail',
            },
        ],
        'promocode': 'Хочешь денег? Введи код: PROMO11',
    }


@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
async def test_get_promocode_error(se_client):
    params = {'driver': '11d', 'park': '11p'}

    response = await se_client.get(
        '/self-employment/referral',
        headers=conftest.DEFAULT_HEADERS,
        params=params,
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'main_items': [
            {
                'accent': True,
                'markdown': True,
                'reverse': False,
                'title': (
                    'Приглашать друзей и получать за них смены могут'
                    ' только самозанятые водители'
                ),
                'center': True,
                'type': 'detail',
            },
        ],
        'help_items': [
            {
                'accent': True,
                'markdown': True,
                'reverse': False,
                'title': 'Это раздел только для смз',
                'center': True,
                'type': 'detail',
            },
        ],
    }


@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO referrals (park_id, driver_id, promocode)
        VALUES ('p14', 'd14', 'PROMO11')
        """,
    ],
)
@pytest.mark.parametrize(
    'promocode,httpcode,response_data',
    [
        ('', 200, {'text': 'Плохой промокод', 'success': False}),
        ('BADPROMO', 200, {'text': 'Плохой промокод', 'success': False}),
        ('wut_01290', 200, {'text': 'Плохой промокод', 'success': False}),
        ('YATAXI2019', 200, {'text': 'Промокод ок', 'success': True}),
        ('РУССКИЙ', 200, {'text': 'Промокод ок', 'success': True}),
    ],
)
@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO profiles
            (id, from_park_id, from_driver_id, park_id, driver_id,
            created_at, modified_at)
        VALUES
            ('s11', 'old_p11', 'old_d11', 'p11', 'd11', now(), now()),
            ('s12', 'old_p12', 'old_d12', 'p12', 'd12', now(), now())
        """,
    ],
)
@pytest.mark.config(SELFEMPLOYED_MIXED_REFERRALS_ENABLED=True)
async def test_post_promocode(
        se_web_context,
        se_client,
        promocode,
        httpcode,
        response_data,
        mockserver,
):
    @mockserver.json_handler('/driver-referrals/service/save-invited-driver')
    async def save_invited_driver(request):
        if request.json['promocode'] in ['PROMO11', 'YATAXI2019', 'РУССКИЙ']:
            return mockserver.make_response(status=200, json={})
        return mockserver.make_response(status=400, json={})

    @mockserver.json_handler(
        '/driver-referrals/service/save-invited-driver-with-new-code',
    )
    async def save_invited_driver_new(request):
        assert request.json['parent']['park_id'] == 'p14'
        assert request.json['parent']['driver_id'] == 'd14'
        assert request.json['child']['park_id'] == 'p12'
        assert request.json['child']['driver_id'] == 'd12'

        return mockserver.make_response(status=200, json={})

    data = {'promocode': promocode}
    params = {'driver': 'old_d12', 'park': 'old_p12'}

    response = await se_client.post(
        '/self-employment/referral',
        headers=conftest.DEFAULT_HEADERS,
        json=data,
        params=params,
    )
    assert response.status == httpcode
    content = await response.json()
    assert content == response_data


@pytest.mark.config(
    TAXIMETER_FNS_SELF_EMPLOYMENT_PROMOCODES=['YATAXI2019', 'РУССКИЙ'],
    SELFEMPLOYED_MIXED_REFERRALS_ENABLED=False,
)
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
@pytest.mark.parametrize(
    'promocode,httpcode,response_data,db_should_update',
    [
        ('', 200, {'text': 'Плохой промокод', 'success': False}, False),
        (
            'BADPROMO',
            200,
            {'text': 'Плохой промокод', 'success': False},
            False,
        ),
        (
            'wut_01290',
            200,
            {'text': 'Плохой промокод', 'success': False},
            False,
        ),
        ('PROMO11', 200, {'text': 'Промокод ок', 'success': True}, True),
        ('YATAXI2019', 200, {'text': 'Промокод ок', 'success': True}, True),
        ('РУССКИЙ', 200, {'text': 'Промокод ок', 'success': True}, True),
    ],
)
@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO referrals (park_id, driver_id, promocode)
        VALUES ('p11', 'd11', 'PROMO11')
        """,
        """
        INSERT INTO profiles
            (id, from_park_id, from_driver_id, park_id, driver_id,
            created_at, modified_at)
        VALUES
            ('s11', 'old_p11', 'old_d11', 'p11', 'd11', now(), now()),
            ('s12', 'old_p12', 'old_d12', 'p12', 'd12', now(), now())
        """,
    ],
)
async def test_post_promocode_not_enabled_mixed_referrals(
        se_web_context,
        se_client,
        promocode,
        httpcode,
        response_data,
        db_should_update,
):
    data = {'promocode': promocode}
    params = {'driver': 'old_d12', 'park': 'old_p12'}

    response = await se_client.post(
        '/self-employment/referral',
        headers=conftest.DEFAULT_HEADERS,
        json=data,
        params=params,
    )
    assert response.status == httpcode
    content = await response.json()
    assert content == response_data

    sql = """
        SELECT reg_promocode FROM referrals
        WHERE park_id = 'p12' AND driver_id = 'd12'
    """

    async with se_web_context.pg.main_master.acquire() as con:
        rows = await con.fetch(sql)

    if db_should_update:
        assert len(rows) == 1
        assert rows[0]['reg_promocode'] == promocode
    else:
        assert not rows
