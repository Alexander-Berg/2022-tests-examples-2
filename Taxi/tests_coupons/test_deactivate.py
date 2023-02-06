import pytest

from tests_coupons import util


def get_user_codes(yandex_uid, brand, user_coupons_db):
    user_coupons = user_coupons_db.find_one(
        {
            'yandex_uid': yandex_uid,
            'brand_name': {'$in': brand} if isinstance(brand, list) else brand,
        },
    )
    return [promo['code'] for promo in user_coupons['promocodes']]


async def make_deactivate_request(taxi_coupons, data):
    return await taxi_coupons.post(
        '3.0/coupondeactivate',
        json=util.remove_pa_request_data(data),
        headers=util.make_pa_headers(data, None),
    )


async def mock_and_make_req_deactivate(
        taxi_coupons, yandex_uids, code, app_name='iphone', version=None,
):
    request = {'code': code}

    if version:
        request['version'] = version

    request = util.convert_v1_request_to_3_0(request)

    pa_headers = util.mock_authorization_data(
        app_name, yandex_uids, yandex_uids[0],
    )
    request.update(pa_headers)

    return await make_deactivate_request(taxi_coupons, request)


@pytest.mark.config(COUPONS_SERVICE_ENABLED=False)
async def test_coupons_disabled(taxi_coupons):
    response = await mock_and_make_req_deactivate(
        taxi_coupons, ['4001'], 'firstpromocode',
    )
    assert response.status_code == 429


async def test_4xx(taxi_coupons, mongodb):
    response = await make_deactivate_request(taxi_coupons, None)
    assert response.status_code == 400

    response = await make_deactivate_request(taxi_coupons, {})
    assert response.status_code == 400


@pytest.mark.parametrize('collections_tag', util.USER_COUPONS_DB_MODE_PARAMS)
@pytest.mark.parametrize(
    'code,app_name,brand',
    [
        ('firstpromocode', 'iphone', 'yataxi'),
        ('yango_firstpromocode', 'yango_iphone', 'yango'),
    ],
    ids=['yataxi', 'yango'],
)
async def test_existing(
        taxi_coupons, mongodb, code, app_name, brand, collections_tag,
):

    collections = util.tag_to_user_coupons_for_write(mongodb, collections_tag)
    for collection in collections:
        assert code in get_user_codes('4013', brand, collection)

    response = await mock_and_make_req_deactivate(
        taxi_coupons, ['4013'], code, app_name=app_name,
    )

    assert response.status_code == 200

    for collection in collections:

        assert util.decode_version(response.json()['version']) == '4013:2'

        assert code not in get_user_codes('4013', brand, collection)


@pytest.mark.parametrize('collections_tag', util.USER_COUPONS_DB_MODE_PARAMS)
async def test_deleted(taxi_coupons, mongodb, collections_tag):
    collections = util.tag_to_user_coupons_for_write(mongodb, collections_tag)

    response = await mock_and_make_req_deactivate(
        taxi_coupons, ['4001'], 'MYYACODE',
    )
    assert response.status_code == 200

    for collection in collections:

        assert get_user_codes('4001', 'yataxi', collection) == [
            'firstpromocode',
            'secondpromocode',
        ]


@pytest.mark.parametrize('collections_tag', util.USER_COUPONS_DB_MODE_PARAMS)
@pytest.mark.parametrize(
    'version_in', [pytest.param(None, id='none_version_in')],
)
async def test_no_user(taxi_coupons, mongodb, version_in, collections_tag):
    version_out = ''
    if version_in:
        version_out = version_in
        encode_version = util.encode_version(version_in)
    version = encode_version if version_in else None

    response = await mock_and_make_req_deactivate(
        taxi_coupons, ['4005'], 'MYYACODE', version=version,
    )
    assert response.status_code == 200

    assert util.decode_version(response.json()['version']) == version_out

    collections = util.tag_to_user_coupons_for_write(mongodb, collections_tag)
    for collection in collections:

        user_coupons = collection.find_one(
            {'yandex_uid': '4005', 'brand_name': 'yataxi'},
        )

        assert not user_coupons


@pytest.mark.parametrize('collections_tag', util.USER_COUPONS_DB_MODE_PARAMS)
@pytest.mark.parametrize(
    'version_in',
    [
        pytest.param(None, id='none_version_in'),
        pytest.param('4010:1', id='some_version_in'),
    ],
)
async def test_multi(taxi_coupons, mongodb, version_in, collections_tag):
    uids = ['4010', '4011', '4012']
    if version_in:
        encode_version = util.encode_version(version_in)
    version = encode_version if version_in else None

    response = await mock_and_make_req_deactivate(
        taxi_coupons, uids, 'non_unique', version=version,
    )
    assert response.status_code == 200

    assert (
        util.decode_version(response.json()['version'])
        == '4010:2,4011:2,4012:2'
    )

    collections = util.tag_to_user_coupons_for_write(mongodb, collections_tag)
    for collection in collections:

        codes = []
        for uid in uids:
            codes += get_user_codes(uid, [None, 'yataxi'], collection)
        assert codes == ['something_else']


@pytest.mark.skip(
    reason='enable after fix https://st.yandex-team.ru/TAXIBACKEND-40918',
)
@pytest.mark.config(
    COUPONS_SOFT_FILTER_BRAND=['yataxi', 'yango', 'yangodeli', 'lavka'],
    APPLICATION_BRAND_RELATED_BRANDS={'yataxi': ['turboapp', 'eats']},
)
@pytest.mark.parametrize('collections_tag', util.USER_COUPONS_DB_MODE_PARAMS)
async def test_deactivate_related_brands(
        taxi_coupons, mongodb, collections_tag,
):
    uid = '1109525876'
    code = 'insrnc80728784'

    collections = util.tag_to_user_coupons_for_write(mongodb, collections_tag)
    for collection in collections:
        assert code in get_user_codes(uid, 'yataxi', collections_tag)

    body = {'coupon': code, 'id': 'a201b58bf0324c27a8f3497ae0e5bfd1'}
    app = 'app_brand=yataxi'

    response = await taxi_coupons.post(
        '3.0/coupondeactivate',
        json=body,
        headers={
            'X-Request-Application': app,
            'X-Request-Language': 'ru-RU',
            'X-YaTaxi-UserId': 'a201b58bf0324c27a8f3497ae0e5bfd1',
            'X-Yandex-UID': uid,
        },
    )

    assert response.status_code == 200

    for collection in collections:
        assert code not in get_user_codes(uid, 'yataxi', collection)
