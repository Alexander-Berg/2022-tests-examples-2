async def test_basic(
        mock_segment_dispatch_journal,
        mock_dispatch_segment,
        create_segment,
        rt_robot_execute,
        execute_pg_query,
        testpoint,
):
    @testpoint('claim_watcher')
    def claim_watcher(data):
        assert data['segments'] == 1

    segment_id = create_segment()
    await rt_robot_execute('segments_journal')
    assert mock_segment_dispatch_journal.times_called
    assert claim_watcher.times_called
    assert mock_dispatch_segment.times_called

    requests_rows = execute_pg_query('select request_code from requests')
    assert requests_rows == [[segment_id]]

    events_storage_rows = execute_pg_query(
        'select event, flow, key from events_storage',
    )
    assert events_storage_rows == [['add', 'segment', segment_id]]


async def test_pull_dispatch(
        mock_segment_dispatch_journal,
        mock_dispatch_segment,
        create_segment,
        rt_robot_execute,
        pgsql,
        testpoint,
):
    @testpoint('claim_watcher')
    def claim_watcher(data):
        assert data['segments'] == 1

    segment = create_segment(
        template='cargo-dispatch/segment-pd.json',
        dropoff_point_coordinates=[37.47093137307133, 55.73323401638446],
    )
    await rt_robot_execute('segments_journal')
    assert mock_segment_dispatch_journal.times_called
    assert claim_watcher.times_called
    assert mock_dispatch_segment.times_called

    cursor = pgsql['ld'].cursor()
    cursor.execute('select request_code from requests')
    result = cursor.fetchall()

    assert result == [(segment,)]
