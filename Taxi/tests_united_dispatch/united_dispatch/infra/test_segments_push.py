async def test_segments_push(
        taxi_united_dispatch,
        segment_builder,
        create_segment,
        get_segment,
        exp_planner_shard,
        exp_segment_executors_selector,
):
    await exp_planner_shard()
    await exp_segment_executors_selector()

    response = await taxi_united_dispatch.post(
        '/test/segment-push', json=segment_builder(create_segment()),
    )

    assert response.status_code == 200
