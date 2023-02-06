import pytest

from test_hiring_candidates import conftest

ROUTE = '/v1/region-by-phone'


@pytest.mark.parametrize('use_personal', (True, False))
@pytest.mark.parametrize(
    'phone, status, geo_id',
    [
        ('+79997790001', 200, 2),
        ('+79033630000', 200, 213),
        ('+79033630111', 200, 213),
        ('+79033639999', 200, 213),
        ('+79033640000', 404, 213),
        (None, 400, None),
    ],
)
@conftest.main_configuration
async def test_region_by_phone(
        taxi_hiring_candidates_web,
        mockserver,
        phone,
        use_personal,
        status,
        geo_id,
):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def retrieve_phones(request):
        return {'value': phone, 'id': request.json['id']}

    async def make_request(params, code):
        response = await taxi_hiring_candidates_web.get(ROUTE, params=params)
        assert response.status == code
        return response

    phone_id = 'aafb39cfd73148408c1950de9d09d2ba'
    if not phone:
        resp = await make_request({}, code=status)
    elif use_personal:
        resp = await make_request({'phone_id': phone_id}, code=status)
    else:
        resp = await make_request({'phone': phone}, code=status)
    if status != 200:
        return
    data = await resp.json()
    assert data
    if use_personal:
        assert data['phone_id'] == phone_id
        assert 'phone' not in data
    else:
        assert data['phone'] == phone
        assert 'phone_id' not in data

    if status == 200:
        assert data['geo_id'] == geo_id
