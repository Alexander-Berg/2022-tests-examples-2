async def test_player_delete(stq_runner, mockserver):
    @mockserver.handler('/music/internal/player/delete')
    def _internal_player_delete(request):
        assert request.json == {'order_id': 'order_id', 'alias_id': 'alias_id'}
        return mockserver.make_response('{}')

    await stq_runner.music_player_delete.call(
        task_id='task-id',
        kwargs={'order_id': 'order_id', 'alias_id': 'alias_id'},
    )
