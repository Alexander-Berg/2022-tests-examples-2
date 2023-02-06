async def test_fill_tvm_tier(
        mockserver, taxi_hejmdal, pgsql, load_json, testpoint,
):
    @mockserver.json_handler('/clownductor/v1/services/')
    async def _mock_services(request):
        return load_json('clownductor_services_response.json')

    @mockserver.json_handler('/clownductor/v1/services/search/')
    async def _mock_services_search(request):
        return load_json('clownductor_services_search_response.json')

    @mockserver.json_handler('/clownductor/v1/branches/')
    async def _mock_branches(request):
        return []

    @mockserver.json_handler('/clownductor/v1/parameters/service_values/')
    async def _mock_parameters_service_values(request):
        return {
            'subsystems': [
                {
                    'subsystem_name': 'service_info',
                    'parameters': [{'name': 'critical_class', 'value': 'A'}],
                },
            ],
        }

    @mockserver.json_handler('/dorblu/api/groups')
    async def _mock_dorblu(request):
        return {}

    @mockserver.json_handler('/clowny-perforator/v1.0/services/retrieve')
    async def _mock_clowny_perforator(request):
        assert request.json['clown_ids'][0] == 2
        return {
            'services': [
                {
                    'id': 156,
                    'tvm_name': 'test_service_tvm_name',
                    'is_internal': True,
                    'environments': [
                        {
                            'id': 160,
                            'env_type': 'production',
                            'tvm_id': 2015277,
                        },
                        {'id': 765, 'env_type': 'testing', 'tvm_id': 2015275},
                    ],
                    'clown_service': {'clown_id': 2, 'project_id': 39},
                },
            ],
        }

    @testpoint('services-update-finished')
    def services_update_finish(data):
        pass

    async with taxi_hejmdal.spawn_task('distlock/services_component'):
        await services_update_finish.wait_call()

    cursor = pgsql['hejmdal'].cursor()
    query = """
            select tvm_name, service_tier from services where id=2
    """
    cursor.execute(query)
    db_res = cursor.fetchall()
    assert db_res[0][0] == 'test_service_tvm_name'
    assert db_res[0][1] == 'A'
