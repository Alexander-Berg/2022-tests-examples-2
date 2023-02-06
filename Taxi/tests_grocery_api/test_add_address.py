import pytest


@pytest.mark.now('2021-04-01T00:00:00+00:00')
@pytest.mark.parametrize(
    'uid',
    [
        pytest.param(None, id='no uid'),
        pytest.param('80085', id='ok ud'),
        pytest.param('8008135', id='half-ok ud'),
    ],
)
@pytest.mark.parametrize('send_to_eats', [True, False, None])
async def test_basic(
        taxi_grocery_api, uid, send_to_eats, stq, now, mockserver,
):
    location = [35.0, 53.0]
    place_id = 'some_uri'
    comment = 'Its a trap!'
    order_id = 'some_id'
    entrance = '1'
    floor = '2'
    doorcode = '4'
    flat = '42'
    doorbell_name = 'for what?'
    doorcode_extra = '228'
    building_name = 'ClubHouse'
    left_at_door = True
    city = 'Village'
    street = 'Avenue'
    house = 'X Æ A-12'
    meet_outside = False
    no_door_call = False

    body = {
        'place_id': place_id,
        'location': location,
        'comment': comment,
        'order_id': order_id,
        'entrance': entrance,
        'floor': floor,
        'flat': flat,
        'doorcode': doorcode,
        'yandex_uid': uid,
        'doorbell_name': doorbell_name,
        'doorcode_extra': doorcode_extra,
        'building_name': building_name,
        'left_at_door': left_at_door,
        'city': city,
        'street': street,
        'house': house,
        'send_to_eats': send_to_eats,
        'meet_outside': meet_outside,
        'no_door_call': no_door_call,
    }

    @mockserver.json_handler('/eats-core-integrations/users/add-address')
    def mock_eats_core(request):
        assert request.json['user_identity']['yandex_uid'] == uid

        if uid == '8008135':
            return mockserver.make_response(
                json={
                    'code': 'WTF dude',
                    'message': 'This uid is unsatisfactory',
                },
                status=400,
            )

        assert request.json['user_address']['city'] == city
        assert request.json['user_address']['floor'] == floor
        assert request.json['user_address']['house'] == house
        assert request.json['user_address']['street'] == street
        assert request.json['user_address']['location'] == location[::-1]

        return mockserver.make_response(
            json={'id': ['long_ass_id']}, status=200,
        )

    response = await taxi_grocery_api.post(
        '/internal/grocery-api/v1/add-address', json=body,
    )
    assert response.status_code == 200

    if uid is not None:
        assert stq.routehistory_grocery_order_add.times_called == 1
        stq_call = stq.routehistory_grocery_order_add.next_call()
        assert _remove_extra_params(stq_call['kwargs']) == {
            'order': {
                'order_id': order_id,
                'yandex_uid': uid,
                'place_uri': place_id,
                'created': now.isoformat() + '+0000',
                'position': location,
                'entrance': entrance,
                'floor': floor,
                'flat': flat,
                'doorcode': doorcode,
                'comment': comment,
                'doorbell_name': doorbell_name,
                'doorcode_extra': doorcode_extra,
                'building_name': building_name,
                'left_at_door': left_at_door,
                'meet_outside': meet_outside,
                'no_door_call': no_door_call,
            },
        }
        if send_to_eats is None or not send_to_eats:
            assert mock_eats_core.times_called == 0
        else:
            assert mock_eats_core.times_called == 1
    else:
        assert mock_eats_core.times_called == 0
        assert stq.routehistory_grocery_order_add.times_called == 0


def _remove_extra_params(stq_kwargs):
    _clean_kwargs = dict(stq_kwargs)
    del _clean_kwargs['log_extra']
    return _clean_kwargs
