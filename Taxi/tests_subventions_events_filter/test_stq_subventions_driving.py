import pytest


@pytest.fixture(name='metadata_storage')
def _mock_metadata_storage(mockserver):
    class Context:
        def __init__(self):
            self.stored_data = dict()
            self.response_code = 200

    ctx = Context()

    @mockserver.json_handler('/metadata-storage/v1/metadata/store')
    def _store(request):
        assert request.args['ns'] == 'taxi:subvention_geoareas'
        if ctx.response_code == 200:
            order_id = request.args['id']
            ctx.stored_data[order_id] = request.json
            return {}
        if ctx.response_code == 409:
            return mockserver.make_response(
                '{"message":"key already in storage","code":"409"}',
                status=ctx.response_code,
            )
        raise Exception('Invalid response_code')

    return ctx


SG_LEFT = {
    '_id': 'lower_left_id',
    'name': 'lower_left_name',
    'created': '2020-02-01T00:00:00+00:00',
    'area': 0.1,
}
SG_CENTER = {
    '_id': 'big_center_id',
    'name': 'big_center_name',
    'created': '2020-02-02T00:00:00+00:00',
    'area': 0.5,
}
SG_RIGHT = {
    '_id': 'upper_right_id',
    'name': 'upper_right_name',
    'created': '2020-02-03T00:00:00+00:00',
    'area': 0.2,
}


@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
@pytest.mark.parametrize(
    'driver_point, expected_subvention_geoareas',
    [
        ([1.5, 1.5], [SG_CENTER]),
        ([0.5, 0.5], [SG_LEFT, SG_CENTER]),
        ([2.5, 2.5], [SG_CENTER, SG_RIGHT]),
        ([4, 4], [SG_RIGHT]),
        ([10, 10], []),
        (None, None),
    ],
)
async def test_subventions_driving(
        stq_runner,
        metadata_storage,
        driver_point,
        expected_subvention_geoareas,
):
    kwargs = {
        'order_id': 'order_id_1',
        'dbid': 'dbid1',
        'uuid': 'uuid1',
        'status': 'pending',
    }
    if driver_point is not None:
        kwargs['driver_point'] = driver_point

    await stq_runner.subventions_driving.call(task_id='task_id', kwargs=kwargs)

    if expected_subvention_geoareas is None:
        assert metadata_storage.stored_data == {}
        return

    stored_data = metadata_storage.stored_data['order_id_1_dbid1_uuid1'][
        'value'
    ]['additional_data']

    if expected_subvention_geoareas == []:
        assert stored_data['subvention_geoareas'] == []
        return

    subvention_geoareas = sorted(
        stored_data['subvention_geoareas'], key=lambda d: d['name'],
    )
    expected_subvention_geoareas = sorted(
        expected_subvention_geoareas, key=lambda d: d['name'],
    )
    assert subvention_geoareas == expected_subvention_geoareas
