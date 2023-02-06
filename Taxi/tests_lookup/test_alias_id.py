import bson

from tests_lookup import lookup_params
from tests_lookup import mock_candidates


async def test_different_aliases(acquire_candidate, mockserver):
    @mockserver.json_handler('/candidates/order-search')
    def _order_search(request):
        # some sample answer from testing
        result = mock_candidates.make_candidates()
        result['candidates'] = result['candidates'][:1]
        result['candidates'][0]['due'] = 1571217150
        result['candidates'][0]['clid'] = 'clid1'
        return result

    request = lookup_params.create_params(generation=1, version=1, wave=1)
    request['aliases'] = [
        {'id': 'alias_id_1', 'due': 1571217120, 'generation': 1},
    ]
    request['candidates'] = [
        {
            'alias_id': 'alias_id_1',
            'driver_id': 'clid0_uuid0',
            'car_number': 'c_n',
            'db_id': 'dbid0',
            'driver_license_personal_id': 'id',
        },
    ]
    candidate = await acquire_candidate(request)
    assert candidate['alias_id'] is not None
    assert candidate['alias_id'] != 'alias_id_1'


async def test_same_alias(acquire_candidate, mockserver):
    @mockserver.json_handler('/candidates/order-search')
    def _order_search(request):
        # some sample answer from testing
        result = mock_candidates.make_candidates()
        result['candidates'] = result['candidates'][:1]
        result['candidates'][0]['due'] = 1571217120
        result['candidates'][0]['clid'] = 'clid1'
        return result

    request = lookup_params.create_params(generation=1, version=1, wave=1)
    request['aliases'] = [
        {'id': 'alias_id_1', 'due': 1571217120, 'generation': 1},
    ]
    request['order']['request']['due'] = 1571217120
    request['candidates'] = [
        {
            'alias_id': 'alias_id_1',
            'driver_id': 'clid0_uuid0',
            'car_number': 'c_n',
            'db_id': 'dbid0',
            'driver_license_personal_id': 'id',
        },
    ]
    candidate = await acquire_candidate(request)
    assert candidate['alias_id'] == 'alias_id_1'


async def test_park_alias(acquire_candidate, mockserver):
    @mockserver.json_handler('/candidates/order-search')
    def _order_search(request):
        # some sample answer from testing
        result = mock_candidates.make_candidates()
        result['candidates'] = result['candidates'][:1]
        result['candidates'][0]['due'] = 1571217120
        result['candidates'][0]['clid'] = 'clid0'
        return result

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/event/new_driver_found',
    )
    def order_core_event(request):
        body = bson.BSON.decode(request.get_data())
        aliases = body['extra_update']['$push']['aliases']
        assert aliases['id'] is not None
        assert aliases['id'] != 'alias_id_1'
        return mockserver.make_response('', 200)

    request = lookup_params.create_params(generation=1, version=1, wave=1)
    request['aliases'] = [
        {'id': 'alias_id_1', 'due': 1571217120, 'generation': 1},
    ]
    request['order']['request']['due'] = 1571217120
    request['candidates'] = [
        {
            'alias_id': 'alias_id_1',
            'driver_id': 'clid0_uuid0',
            'car_number': 'c_n',
            'db_id': 'dbid0',
            'driver_license_personal_id': 'id',
        },
    ]
    await acquire_candidate(request)

    assert order_core_event.has_calls


async def test_multioffer_alias(acquire_candidate, mockserver):
    @mockserver.json_handler('/candidates/order-search')
    def _order_search(request):
        # some sample answer from testing
        result = mock_candidates.make_candidates()
        result['candidates'] = result['candidates'][:1]
        result['candidates'][0]['due'] = 1571217120
        result['candidates'][0]['metadata'] = {
            'multioffer': {'alias_id': 'multioffer_id'},
        }
        return result

    request = lookup_params.create_params(generation=1, version=1, wave=1)
    request['aliases'] = []
    request.pop('candidates', None)
    candidate = await acquire_candidate(request)
    assert candidate['alias_id'] is not None
    assert candidate['alias_id'] == 'multioffer_id'


async def test_indexed_candidates_alias(acquire_candidate, mockserver):
    @mockserver.json_handler('/candidates/order-search')
    def _order_search(request):
        # some sample answer from testing
        result = mock_candidates.make_candidates()
        result['candidates'] = result['candidates'][:1]
        result['candidates'][0]['due'] = 1571217120
        result['candidates'][0]['clid'] = 'clid0'
        return result

    request = lookup_params.create_params(generation=2, version=1, wave=1)
    request['aliases'] = [
        {'id': 'alias_id_1', 'due': 1571217120, 'generation': 1},
    ]
    request['order']['request']['due'] = 1571217120
    request['indexed_candidates'] = [
        {
            'alias_id': 'alias_id_1',
            'driver_id': 'clid0_uuid0',
            'car_number': 'c_n',
            'db_id': 'dbid0',
            'driver_license_personal_id': 'id',
        },
    ]
    candidate = await acquire_candidate(request)
    assert candidate['alias_id'] is not None
    assert candidate['alias_id'] != 'alias_id_1'
