async def test_use_yateam_bb(taxi_femida_authproxy, mockserver):
    @mockserver.json_handler('/blackbox')
    def mock_blackbox(request):
        return {}

    @mockserver.json_handler('/blackbox-team')
    def mock_blackbox_team(request):
        return {}

    await taxi_femida_authproxy.post(
        '/_api/hire_orders/', json={}, headers={'Authorization': 'Bearer 123'},
    )

    assert mock_blackbox_team.has_calls
    assert not mock_blackbox.has_calls
