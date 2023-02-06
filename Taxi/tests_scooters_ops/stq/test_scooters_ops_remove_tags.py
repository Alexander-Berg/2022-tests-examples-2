async def test_task(mockserver, stq_runner):
    @mockserver.json_handler('/scooter-backend/api/taxi/car/tag_remove')
    def mock_tag_remove(request):
        assert request.json['object_ids'] == ['my_lucky_vehicle']
        assert sorted(request.json['tag_names']) == ['a', 'b']
        return {}

    await stq_runner.scooters_ops_remove_tags.call(
        task_id='remove',
        kwargs={'vehicle_id': 'my_lucky_vehicle', 'tags': ['a', 'b']},
    )

    assert mock_tag_remove.times_called == 1
