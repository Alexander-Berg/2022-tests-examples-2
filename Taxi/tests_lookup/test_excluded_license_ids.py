import json

from tests_lookup import lookup_params


async def test_excluded_license_ids(acquire_candidate, mockserver):
    @mockserver.json_handler('/manual-dispatch/v1/lookup')
    def manual_dispatch(request):
        body = json.loads(request.get_data())
        assert set(body['excluded_license_ids']) == {
            'active_id',
            'excluded_license_0',
            'excluded_license_1',
            'excluded_license_2',
            'excluded_license_3',
        }
        return mockserver.make_response(status=200, json={})

    @mockserver.json_handler(
        '/excluded-drivers/excluded-drivers/v1/drivers/list',
    )
    def excluded_license_ids(request):
        assert request.args.get('personal_phone_id') == 'personal_phone_id'
        data = {
            'excluded_drivers_pd_ids': [
                'excluded_license_0',
                'excluded_license_1',
                'excluded_license_2',
                'excluded_license_3',
            ],
        }
        return mockserver.make_response(200, json=data)

    order = lookup_params.create_params(
        generation=1, version=1, tariffs=['cargo'],
    )
    order['manual_dispatch'] = {'a': 'b'}
    order['candidates'] = [{'driver_license_personal_id': 'active_id'}]

    candidate = await acquire_candidate(order)
    assert not candidate

    await excluded_license_ids.wait_call(timeout=1)
    await manual_dispatch.wait_call(timeout=1)
