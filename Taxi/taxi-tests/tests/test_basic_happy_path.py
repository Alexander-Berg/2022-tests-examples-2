import pytest
import requests

from taxi_tests import utils
from taxi_tests.utils import dates
from taxi_tests.utils import parks


IPHONE_USER_AGENT = (
    'ru.yandex.ytaxi/3.99.9682 (iPhone; iPhone7,1; iOS 10.1.1; Darwin)'
)
DRIVING_ERROR_MSG = 'Failed to await taxiontheway with \'driving\' status'
WAITING_ERROR_MSG = 'Failed to await taxiontheway with \'waiting\' status'
UNSUCCEEDED_ORDER_ERROR_MSG = 'Order has not been succeeded'
TRANSP_ERROR_MSG = 'Failed to await taxiontheway with \'transporting\' status'
UNCOMPLETED_ORDER_ERROR_MSG = 'Order has not been completed'
FAILED_REFERRAL_ERROR_MSG = 'Failed to get referral'


# pylint: disable=too-many-locals, too-many-branches, too-many-statements
@pytest.mark.skip(reason='TAXIBACKEND-41364')
def test_user_happy_path(
        protocol, billing, session_maker, search_maps, taximeter_control,
):
    session = session_maker(user_agent=IPHONE_USER_AGENT)
    response = protocol.launch({}, session=session)
    assert not response['authorized']

    session.init(phone='random')

    billing.change_payment_methods(
        session.yandex_uid, billing.default_paymnet_methods,
    )
    response = protocol.launch({'id': response['id']}, session=session)
    assert response['authorized']
    user_id = response['id']

    point_start = [37.6436004905, 55.7334752687]
    position_data = {'dx': 100, 'id': user_id, 'll': point_start}

    response = protocol.startup(
        dict(block_id='default', **position_data), session=session,
    )
    assert response['ok']

    protocol.promotions(
        {
            'fullscreen_banner': {'banners_seen': [], 'size_hint': 240},
            'id': user_id,
            'supported_promotions': ['tesla', 'ea2016_promo', 'nosms'],
        },
        session=session,
    )

    obj1 = search_maps.register_company(
        coordinates=point_start,
        text='%s-src-point' % user_id,
        name='Яндекс.Такси',
        address='Садовническая улица, 82с1',
    )
    response = protocol.suggest(
        {
            'action': 'pin_drop',
            'position': point_start,
            'id': user_id,
            'state': {'accuracy': 1414},
            'sticky': True,
            'supported': ['alerts'],
            'type': 'a',
        },
        session=session,
    )
    nearest_zone = response['nearest_zone']
    assert nearest_zone == 'moscow'

    protocol.expecteddestinations(
        {
            'id': user_id,
            'll': point_start,
            'with_userplaces': True,
            'zone_name': nearest_zone,
        },
        session=session,
    )

    protocol.suggestedpositions(
        dict(with_userplaces_v2=True, **position_data), session=session,
    )

    protocol.weathersuggest(position_data, session=session)
    zoneinfo = protocol.zoneinfo(
        {
            'id': user_id,
            'options': True,
            'size_hint': 240,
            'skin_version': 2,
            'supports_hideable_tariffs': True,
            'zone_name': nearest_zone,
        },
        session=session,
    )
    # Some dummy checks for now
    assert zoneinfo['country_code'] == 'RU'
    assert zoneinfo['currency_code'] == 'RUB'
    assert zoneinfo['region_id'] == 225

    try:
        protocol.email({'action': 'get', 'id': user_id}, session=session)
    except requests.HTTPError as exc:
        assert exc.response.status_code == 404
    else:
        assert False

    protocol.pricecat({'zone_name': nearest_zone}, session=session)

    response = protocol.paymentmethods({'id': user_id}, session=session)
    card_id = response['card']['available_cards'][0]['id']

    response = protocol.routestats(
        {
            'extended_description': True,
            'format_currency': True,
            'id': user_id,
            'payment': {'type': 'cash'},
            'position_accuracy': 10,
            'route': [point_start],
            'selected_class_only': False,
            'skip_estimated_waiting': False,
            'summary_version': 2,
            'supported_markup': 'tml-0.1',
            'supports_forced_surge': True,
            'supports_hideable_tariffs': True,
            'supports_no_cars_available': True,
            'surge_fake_pin': False,
            'with_title': True,
            'zone_name': nearest_zone,
        },
        session=session,
    )

    assert 'offer' not in response
    assert 'is_fixed_price' not in response
    for cls_info in response['service_levels']:
        assert 'is_fixed_price' not in cls_info

    protocol.suggesteddestinations(
        {
            'id': user_id,
            'll': point_start,
            'results': 10,
            'with_userplaces': True,
        },
        session=session,
    )

    protocol.translations({'keyset': 'cancel_state'}, session=session)

    point_dest = [37.6194, 55.7546]
    obj2 = search_maps.register_company(
        coordinates=point_dest,
        text='Красная площадь',
        name='Красная площадь',
        address='Москва, Красная площадь',
    )
    protocol.suggest(
        {
            'action': 'user_input',
            'id': user_id,
            'part': 'Красная площадь',
            'position': point_dest,
            'state': {'accuracy': 165},
            'sticky': True,
            'supported': ['alerts'],
            'type': 'b',
        },
        session=session,
    )

    response = protocol.suggest(
        {
            'action': 'finalize',
            'id': user_id,
            'position': point_dest,
            'state': {'accuracy': 165},
            'sticky': False,
            'supported': ['alerts'],
            'type': 'b',
        },
        session=session,
    )

    resp_pos_str = response['results'][0]['pos']
    resp_pos_vec = resp_pos_str.split(',')
    assert resp_pos_vec[0][: len(str(point_dest[0]))] == str(point_dest[0])
    assert resp_pos_vec[1][: len(str(point_dest[1]))] == str(point_dest[1])

    response = protocol.routestats(
        {
            'extended_description': True,
            'format_currency': True,
            'id': user_id,
            'payment': {'type': 'cash'},
            'position_accuracy': 10,
            'route': [point_start, point_dest],
            'selected_class': 'econom',
            'selected_class_only': False,
            'skip_estimated_waiting': False,
            'suggest_alternatives': True,
            'summary_version': 2,
            'supported_markup': 'tml-0.1',
            'supports_forced_surge': True,
            'supports_hideable_tariffs': True,
            'supports_no_cars_available': True,
            'surge_fake_pin': False,
            'with_title': True,
            'zone_name': nearest_zone,
        },
        session=session,
    )

    econom_sl = None
    for service_level in response['service_levels']:
        if service_level['class'] == 'econom':
            econom_sl = service_level
            break
    assert econom_sl is not None, response

    data = {
        'comment': 'manual_control-1',
        'dont_call': False,
        'dont_sms': False,
        'id': user_id,
        'offer': response['offer'],
        'parks': parks.excluded(),
        'payment': {'type': 'cash'},
        'route': [obj1.obj, obj2.obj],
        'service_level': econom_sl['service_level'],
        'started_in_emulator': False,
        'tips': {'type': 'percent', 'value': 5},
        'zone_name': 'moscow',
    }
    if 'forced_surge' in econom_sl:
        data['forced_surge'] = {'value': econom_sl['forced_surge']['value']}

    response = protocol.order(data, session=session)
    order_id = response['orderid']

    totw_request = {
        'id': user_id,
        'orderid': order_id,
        'format_currency': True,
    }

    for _ in utils.wait_for(120, DRIVING_ERROR_MSG):
        response = protocol.taxiontheway(totw_request, session=session)
        if response['status'] == 'driving':
            break
    taximeter = taximeter_control.find_by_phone(response['driver']['phone'])
    taximeter.move(obj1.coordinates)
    taximeter.requestconfirm('waiting')
    for _ in utils.wait_for(60, WAITING_ERROR_MSG):
        response = protocol.taxiontheway(totw_request, session=session)
        if response['status'] == 'waiting':
            break

    response = protocol.changecomment(
        {
            'created_time': dates.timestring(),
            'id': user_id,
            'orderid': order_id,
            'comment': 'speed-1500,wait-30',
        },
        session=session,
    )
    assert response['status'] == 'success'

    response = protocol.changeporchnumber(
        {
            'created_time': dates.timestring(),
            'id': user_id,
            'orderid': order_id,
            'porchnumber': '1',
        },
        session=session,
    )
    assert response['status'] == 'success'

    response = protocol.changeaction(
        {
            'action': 'user_ready',
            'created_time': dates.timestring(),
            'id': user_id,
            'orderid': order_id,
        },
        session=session,
    )
    assert response['status'] == 'success'

    response = protocol.changedestinations(
        {
            'created_time': dates.timestring(),
            'destinations': [obj1.obj],
            'id': user_id,
            'orderid': order_id,
        },
        session=session,
    )
    assert response['status'] == 'success'

    response = protocol.changepayment(
        {
            'created_time': dates.timestring(),
            'payment_method_type': 'card',
            'payment_method_id': card_id,
            'tips': {'type': 'percent', 'value': 5},
            'id': user_id,
            'orderid': order_id,
        },
        session=session,
    )
    assert response['status'] == 'pending'
    changepayment_id = response['change_id']

    for _ in utils.wait_for(500, UNSUCCEEDED_ORDER_ERROR_MSG):
        response = protocol.changes(
            {
                'id': user_id,
                'orders': [
                    {
                        'orderid': order_id,
                        'changes': [{'change_id': changepayment_id}],
                    },
                ],
            },
            session=session,
        )
        change_status = response['orders'][0]['changes'][0]['status']
        if change_status == 'success':
            break
        assert change_status == 'pending'

    response = protocol.taxiroute(
        {
            'build_route': False,
            'id': user_id,
            'orderid': order_id,
            'use_history': True,
        },
        session=session,
    )
    driver_point = response['driver']['coordinates']

    taximeter.requestconfirm('transporting')
    for _ in utils.wait_for(60, TRANSP_ERROR_MSG):
        response = protocol.taxiontheway(totw_request, session=session)
        if response['status'] == 'transporting':
            break

    protocol.taxiroute(
        {
            'build_route': False,
            'coordinates': driver_point,
            'id': user_id,
            'orderid': order_id,
            'timestamp': dates.timestring(),
            'use_history': True,
        },
        session=session,
    )

    taximeter.requestconfirm('complete')
    for _ in utils.wait_for(60, UNCOMPLETED_ORDER_ERROR_MSG):
        response = protocol.taxiontheway(totw_request, session=session)
        if response['status'] == 'complete':
            break

    response = protocol.updatetips(
        {
            'id': user_id,
            'orderid': order_id,
            'tips': {'type': 'percent', 'value': 15},
        },
        session=session,
    )
    assert response == {}

    response = protocol.feedback(
        {
            'call_me': False,
            'choices': {},
            'created_time': dates.timestring(),
            'id': user_id,
            'msg': '',
            'orderid': order_id,
            'rating': 5,
            'tips': {'type': 'percent', 'value': 15},
        },
        session=session,
    )
    assert response == {}

    protocol.paymentstatuses(
        {
            'filter': ['can_be_paid_by_card'],
            'format_currency': True,
            'id': user_id,
        },
        session=session,
    )
