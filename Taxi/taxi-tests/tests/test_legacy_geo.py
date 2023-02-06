IPHONE_USER_AGENT = (
    'ru.yandex.ytaxi/3.99.9682 (iPhone; iPhone7,1; iOS 10.1.1; Darwin)'
)


# pylint: disable=too-many-locals, too-many-branches, too-many-statements
def test_user_legacy_geo(protocol, billing, session_maker, search_maps,
                         taximeter_control):
    session = session_maker(user_agent=IPHONE_USER_AGENT)
    response = protocol.launch({}, session=session)
    assert not response['authorized']
    session.init(phone='random')
    billing.change_payment_methods(session.yandex_uid,
                                   billing.default_paymnet_methods)
    response = protocol.launch({'id': response['id']}, session=session)
    assert response['authorized']
    user_id = response['id']

    point_start = [37.6436004905, 55.7334752687]
    position_data = {
        'dx': 100,
        'id': user_id,
        'll': point_start,
    }

    search_maps.register_company(coordinates=point_start,
                                 text='%s-src-point' % user_id)

    response = protocol.nearestposition(dict(
        not_sticky=True,
        supported=['pickup_points'],
        **position_data,
    ), session=session)
    point_start[:] = response['point']

    response = protocol.nearestposition(dict(
        not_sticky=False,
        supported=['pickup_points'],
        **position_data,
    ), session=session)
    point_start[:] = response['point']

    protocol.suggestedpositions(dict(
        with_userplaces_v2=True,
        **position_data,
    ), session=session)

    protocol.pickuppoints(position_data, session=session)
    response = protocol.nearestzone({
        'id': user_id,
        'point': point_start,
    }, session=session)
    nearest_zone = response['nearest_zone']
    assert nearest_zone == 'moscow'

    protocol.expecteddestinations({
        'id': user_id,
        'll': point_start,
        'with_userplaces': True,
        'zone_name': nearest_zone,
    }, session=session)

    protocol.suggesteddestinations({
        'id': user_id,
        'll': point_start,
        'results': 10,
        'with_userplaces': True,
    }, session=session)

    point_dest = [37.5, 55.8]
    obj2 = search_maps.register_company(coordinates=point_dest,
                                        text='%s-dest-point' % user_id)

    response = protocol.geosearch({
        'id': user_id,
        'll': point_dest,
        'what': obj2.text,
    }, session=session)
    dest_obj = response['objects'][0]
    point_dest = dest_obj['point']
