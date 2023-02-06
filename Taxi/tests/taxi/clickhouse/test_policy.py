#  pylint: disable=W0212
HOSTS = ['less_awesome_db.db.yandex.net', 'super_awesome_db.db.yandex.net']
BASE_ANSWER = {
    'statistics': {'elapsed': 0.5, 'rows_read': 100, 'bytes_read': 10},
    'meta': [],
    'data': [],
    'rows': 1,
}


async def test_base(
        mock_clickhouse_host, clickhouse_connection, policy, response_mock,
):
    failed_request = True

    def ok_response(*args, **kwargs):
        return response_mock(json={})

    def failed_response(*args, **kwargs):
        nonlocal failed_request
        if failed_request:
            return response_mock(status=500)
        return response_mock(json={})

    mock_clickhouse_host(
        clickhouse_response=failed_response,
        request_url=f'https://{HOSTS[0]}:8443/?database=test_db',
    )
    mock_clickhouse_host(
        clickhouse_response=ok_response,
        request_url=f'https://{HOSTS[1]}:8443/?database=test_db',
    )
    conn = clickhouse_connection()
    test_policy = policy(conn=conn)
    for host in HOSTS:
        for _ in range(test_policy.host_status[host]['dead_threshold'] + 1):
            await test_policy._update_host_status(host)

    assert not test_policy.host_status[HOSTS[0]]['alive']
    assert test_policy.host_status[HOSTS[1]]['alive']
    assert test_policy.host_list == [HOSTS[1]]

    failed_request = False
    for host in HOSTS:
        await test_policy._update_host_status(host)

    assert test_policy.host_status[HOSTS[0]]['alive']
    assert test_policy.host_status[HOSTS[1]]['alive']
    assert sorted(test_policy.host_list) == HOSTS
