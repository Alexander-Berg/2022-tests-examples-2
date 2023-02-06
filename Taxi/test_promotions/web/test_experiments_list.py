async def test_experiments_list_ok(web_app_client, mockserver, load_json):
    @mockserver.json_handler('/taxi-exp/v1/experiments/list/')
    def _experiments(request):
        return load_json('experiments.json')

    response = await web_app_client.get('/admin/promotions/experiment_list/')
    data = await response.json()
    assert data == {'experiments': ['normal_exp']}
