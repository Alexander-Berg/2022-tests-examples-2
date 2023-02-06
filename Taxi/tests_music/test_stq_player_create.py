async def test_player_create(stq_runner, mockserver):
    @mockserver.handler('/music/internal/player/create')
    def _internal_player_create(request):
        assert request.json == {
            'order_id': 'order_id',
            'alias_id': 'alias_id',
            'user_uid': 'user_uid',
            'user_id': 'user_id',
            'driver_id': 'dbid_uuid',
        }
        return mockserver.make_response('{}')

    await stq_runner.music_player_create.call(
        task_id='task-id',
        kwargs={
            'order_id': 'order_id',
            'alias_id': 'alias_id',
            'user_uid': 'user_uid',
            'user_id': 'user_id',
            'application': 'android',
            'db_id': 'dbid',
            'uuid': 'uuid',
            'tariff_class': 'business',
        },
    )
