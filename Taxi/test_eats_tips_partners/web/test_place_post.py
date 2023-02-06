import http
import uuid

from aiohttp import web
import pytest


PERSONAL_PHONE_MAP = {
    'ok_phone_id': '+79000000000',
    'deleted_partner': '+79000000001',
    'phone_id_13': '+79000000000',
}


def _format_partner_place_info(
        partner_alias='0000100',
        place_alias='3000000',
        place_partner_alias='3000010',
):
    return {
        'partner_id': uuid.UUID(
            f'00000000-0000-0000-0000-{partner_alias[:-1].zfill(12)}',
        ),
        'partner_alias': partner_alias,
        'place_alias': place_alias,
        'place_partner_alias': place_partner_alias,
    }


def _format_place_register_request(
        *,
        title='ВайВай',
        inn='1234567890',
        address='Казань, Вайвайская, 12',
        website=None,
):
    request = {'title': title, 'inn': inn, 'address': address}
    if website:
        request['website'] = website
    return request


@pytest.mark.parametrize(
    ('params', 'partner_place_info', 'expected_code'),
    (
        pytest.param(
            _format_place_register_request(),
            _format_partner_place_info(),
            http.HTTPStatus.OK,
            id='ok',
        ),
        pytest.param(
            _format_place_register_request(website='www.yandex.ru'),
            _format_partner_place_info(),
            http.HTTPStatus.OK,
            id='ok-website',
        ),
        pytest.param(
            _format_place_register_request(),
            _format_partner_place_info(partner_alias='0000150'),
            http.HTTPStatus.BAD_REQUEST,
            id='no-phone-id',
        ),
        pytest.param(
            _format_place_register_request(),
            _format_partner_place_info(partner_alias='0001310'),
            http.HTTPStatus.BAD_REQUEST,
            id='no-partner',
        ),
        pytest.param(
            _format_place_register_request(),
            _format_partner_place_info(partner_alias='0000130'),
            http.HTTPStatus.TOO_MANY_REQUESTS,
            id='partner-reached-place-limit',
        ),
    ),
)
@pytest.mark.config(
    EATS_TIPS_PARTNERS_PLACE_REGISTER_SETTINGS={'places_limit': 1},
)
@pytest.mark.pgsql('eats_tips_partners', files=['pg.sql'])
async def test_place_post(
        taxi_eats_tips_partners_web,
        mock_tvm_rules,
        web_context,
        mockserver,
        params,
        partner_place_info,
        expected_code,
):
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    async def _mock_phones_retrieve(request):
        value = PERSONAL_PHONE_MAP.get(request.json['id'])
        if value:
            return {'value': value, 'id': request.json['id']}
        return web.json_response({}, status=http.HTTPStatus.NOT_FOUND)

    response = await taxi_eats_tips_partners_web.post(
        '/v1/place',
        json=params,
        headers={'X-Tips-Partner-Id': str(partner_place_info['partner_id'])},
    )
    assert response.status == expected_code
    if response.status == http.HTTPStatus.OK:
        await _check_pg(web_context, params, partner_place_info)


async def _check_pg(web_context, params, partner_place_info):
    place_alias = partner_place_info['place_alias']
    place_partner_alias = partner_place_info['place_partner_alias']
    async with web_context.pg.replica_pool.acquire() as conn:
        row = await conn.fetchrow(
            f"""
            select
                title,
                address,
                inn,
                owner,
                website
            from eats_tips_partners.place
            where alias = '{place_alias}';
            """,
        )
        assert dict(row) == {
            'title': params['title'],
            'address': params['address'],
            'inn': params['inn'],
            'owner': partner_place_info['partner_id'],
            'website': params.get('website'),
        }

        row = await conn.fetchrow(
            f"""
                    select migrated, type
                    from eats_tips_partners.alias
                    where alias = '{place_alias}';""",
        )
        assert dict(row) == {'migrated': True, 'type': 'place'}

        row = await conn.fetchrow(
            f"""
                    select migrated, type
                    from eats_tips_partners.alias
                    where alias = '{place_partner_alias}';""",
        )
        assert dict(row) == {'migrated': True, 'type': 'place_partner'}

        row = await conn.fetchrow(
            f"""
                    select partner_id, roles
                    from eats_tips_partners.places_partners
                    where alias = '{place_partner_alias}';""",
        )
        assert dict(row) == {
            'partner_id': partner_place_info['partner_id'],
            'roles': ['admin'],
        }
