async def wait_workers(taxi_invites, testpoint):
    @testpoint('metrics_collector-started')
    def worker_started(data):
        return

    @testpoint('metrics_collector-finished')
    def worker_finished(data):
        return data

    await taxi_invites.enable_testpoints()

    await worker_started.wait_call()
    return (await worker_finished.wait_call())['data']


def to_metrics_object(club_metrics):
    result = {'$meta': {'solomon_children_labels': 'club_name'}}
    for club, metrics in club_metrics:
        result[club] = {'total_members_count': metrics[0]}

    return result


async def test_invites_metrics(taxi_invites, testpoint, taxi_config):
    await taxi_invites.invalidate_caches()
    data = await wait_workers(taxi_invites, testpoint)

    expected_data = to_metrics_object(
        [('yandex_go', [4]), ('yet_another_club', [3])],
    )

    assert data == expected_data
