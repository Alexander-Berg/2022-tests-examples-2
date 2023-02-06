class TestV1RolloutModeGet:
    async def test_get_one_view_can_deploy(self, web_app_client):
        response = await web_app_client.get(
            '/v1/rollout-mode', params={'view': 'rolling_view'},
        )
        assert response.status == 200, await response.text()
        content = await response.json()
        assert content == [{'view': 'rolling_view', 'can_deploy': True}]

    async def test_get_one_view_cannot_deploy(self, web_app_client):
        response = await web_app_client.get(
            '/v1/rollout-mode', params={'view': 'not_rolling_view'},
        )
        assert response.status == 200, await response.text()
        content = await response.json()
        assert content == [{'view': 'not_rolling_view', 'can_deploy': False}]

    async def test_get_nonexistent_view(self, web_app_client):
        response = await web_app_client.get(
            '/v1/rollout-mode', params={'view': 'not_existing_view'},
        )
        assert response.status == 404
        content = await response.json()
        assert content.get('code', None) == 'rollout_mode_not_found'

    async def test_get_multiple_views(self, web_app_client):
        response = await web_app_client.get(
            '/v1/rollout-mode',
            params={'view': 'rolling_view,not_rolling_view'},
        )

        assert response.status == 200, await response.text()
        content = await response.json()
        assert content == [
            {'view': 'rolling_view', 'can_deploy': True},
            {'view': 'not_rolling_view', 'can_deploy': False},
        ]

    async def test_get_all_views(self, web_app_client):
        response = await web_app_client.get('/v1/rollout-mode')

        assert response.status == 200, await response.text()
        content = await response.json()

        # Элементы могут быть возвращены в произвольном порядке
        assert {'view': 'rolling_view', 'can_deploy': True} in content and {
            'view': 'not_rolling_view',
            'can_deploy': False,
        } in content
