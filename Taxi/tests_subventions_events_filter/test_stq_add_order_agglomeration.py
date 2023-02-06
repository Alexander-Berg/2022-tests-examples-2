import pytest


@pytest.fixture(name='agglomerations')
def _mock_agglomerations(mockserver):
    class Ctx:
        def __init__(self):
            self.get_mvp_response = ''
            self.get_mvp_calls = 0

    ctx = Ctx()

    @mockserver.json_handler(
        '/taxi-agglomerations/v1/geo_nodes/get_mvp_oebs_id',
    )
    def _get_mvp(request):
        ctx.get_mvp_calls += 1
        assert request.args['tariff_zone'] == 'moscow'
        if isinstance(ctx.get_mvp_response, str):
            return {'oebs_mvp_id': ctx.get_mvp_response}
        if isinstance(ctx.get_mvp_response, int):
            return mockserver.make_response('{}', status=ctx.get_mvp_response)
        raise Exception('Invalid get_mvp_response')

    return ctx


@pytest.fixture(name='metadata_storage')
def _mock_metadata_storage(mockserver):
    class Context:
        def __init__(self):
            self.stored_data = dict()
            self.response_code = 200

    ctx = Context()

    @mockserver.json_handler('/metadata-storage/v1/metadata/store')
    def _store(request):
        assert request.args['ns'] == 'taxi:order_agglomeration'
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


@pytest.mark.parametrize(
    'get_mvp_response,expected_stored_data',
    [
        pytest.param(
            # get_mvp_response
            'MSKc',
            # expected_stored_data
            {
                'geo_nodes': [
                    'br_moscow_adm',
                    'br_moscow',
                    'br_moskovskaja_obl',
                    'br_tsentralnyj_fo',
                    'br_russia',
                    'br_root',
                ],
                'mvp': 'MSKc',
            },
            id='ok',
        ),
        pytest.param(
            # get_mvp_response
            'MSKc',
            # expected_stored_data
            {'geo_nodes': [], 'mvp': 'MSKc'},
            marks=pytest.mark.geo_nodes(
                [
                    {
                        'name': 'br_root',
                        'name_en': 'Basic Hierarchy',
                        'name_ru': 'Базовая иерархия',
                        'node_type': 'root',
                    },
                ],
            ),
            id='empty_geo_nodes',
        ),
        pytest.param(
            # get_mvp_response
            404,
            # expected_stored_data
            {'geo_nodes': []},
            marks=pytest.mark.geo_nodes(
                [
                    {
                        'name': 'br_root',
                        'name_en': 'Basic Hierarchy',
                        'name_ru': 'Базовая иерархия',
                        'node_type': 'root',
                    },
                ],
            ),
            id='empty',
        ),
    ],
)
@pytest.mark.config(
    USERVICE_AGGLOMERATIONS_CACHE_SETTINGS={
        '__default__': {
            'enabled': True,
            'log_errors': True,
            'verify_on_updates': True,
        },
    },
)
async def test_add_order_agglomeration(
        stq_runner,
        agglomerations,
        metadata_storage,
        get_mvp_response,
        expected_stored_data,
):
    agglomerations.get_mvp_response = get_mvp_response

    await stq_runner.add_order_agglomeration.call(
        task_id='task_id', kwargs={'order_id': 'order_id_1', 'zone': 'moscow'},
    )

    assert (
        metadata_storage.stored_data['order_id_1']['value']['additional_data']
        == expected_stored_data
    )


async def test_agglomeration_info_cache(
        stq_runner, agglomerations, metadata_storage,
):
    agglomerations.get_mvp_response = 'MSKc'

    await stq_runner.add_order_agglomeration.call(
        task_id='task_id', kwargs={'order_id': 'order_id_1', 'zone': 'moscow'},
    )

    await stq_runner.add_order_agglomeration.call(
        task_id='task_id', kwargs={'order_id': 'order_id_1', 'zone': 'moscow'},
    )

    assert agglomerations.get_mvp_calls == 1


async def test_add_order_agglomeration_metadata_key_duplication(
        stq_runner, agglomerations, metadata_storage,
):
    agglomerations.get_mvp_response = 'MSKc'
    metadata_storage.response_code = 409

    await stq_runner.add_order_agglomeration.call(
        task_id='task_id', kwargs={'order_id': 'order_id_1', 'zone': 'moscow'},
    )
