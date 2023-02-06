import urllib.parse

import const


def create_stops_nearby_request(
        position,
        distance_meters,
        pickup_points_type,
        transfer_type,
        routers,
        transport_types,
        fetch_lines,
):
    return {
        'position': position,
        'distance_threshold_meters': distance_meters,
        'pickup_points_type': pickup_points_type,
        'transfer_type': transfer_type,
        'router_params': routers,
        'transport_types': transport_types,
        'fetch_lines': fetch_lines,
    }


def check_vtb_authorization(request):
    assert request.headers['X-Api-Key'] == 'yandex_taxi'


def get_maas_tariffs():
    maas_tariff_m = const.MAAS_TARIFF_SETTINGS.copy()
    maas_tariff_m['composite_maas_tariff_id'] = 'outer_maas_tariff_m'

    maas_tariff_s = const.MAAS_TARIFF_SETTINGS.copy()
    maas_tariff_s['composite_maas_tariff_id'] = 'outer_maas_tariff_s'

    return {'tariff_m': maas_tariff_m, 'tariff_s': maas_tariff_s}


URL_TO_SUPPORT = 'https://smartcity-stage.intervale.ru/maas/'


def check_support_url(
        url: str,
        issue: str,
        lang: str = 'ru',
        maas_user_id: str = 'maas-user-id',
        partner_id: str = 'YG',
        redirect_uri: str = 'https://canceled-payment',
):

    parsed_url = urllib.parse.urlparse(url)
    parsed_expected_url = urllib.parse.urlparse(URL_TO_SUPPORT)

    assert parsed_url.scheme == 'https'
    assert parsed_url.netloc == parsed_expected_url.netloc
    assert parsed_url.path == parsed_expected_url.path

    query = urllib.parse.parse_qs(parsed_url.query)

    assert query['issue'][0] == issue
    assert query['lang'][0] == lang
    assert query['maas_user_id'][0] == maas_user_id
    assert query['id'][0] == partner_id
    assert query['redirectURI'][0] == redirect_uri
