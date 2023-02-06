import pytest

import tests_combo_matcher.utils as utils


@pytest.mark.pgsql('combo_matcher', files=['order_meta.sql'])
@pytest.mark.now('2021-9-9T01:48:00+00:00')
@pytest.mark.config(ROUTER_SELECT=[{'routers': ['linear-fallback']}])
async def test_order_matcher(taxi_combo_matcher, pgsql, testpoint, load_json):
    @testpoint('log_order_match_to_yt')
    def log_to_yt(data):
        return data

    await taxi_combo_matcher.run_task('order-matcher')

    matchings = await utils.select_matchings(pgsql, with_combo_info=True)
    assert len(matchings) == 1
    matching = matchings[0]
    combo_info = matching.pop('combo_info')

    assert matching == {
        'id': 1,
        'orders': ['order_id0', 'order_id1'],
        'performer': None,
    }
    assert combo_info['batch_id'] == 'order_id0'

    order_meta = await utils.select_order_meta(pgsql)

    assert sorted(order_meta, key=lambda x: x['order_id']) == [
        {
            'order_id': 'order_id0',
            'revision': 0,
            'status': 'matched',
            'matching_id': 1,
            'candidate': None,
            'times_dispatched': 0,
            'times_matched': 1,
        },
        {
            'order_id': 'order_id1',
            'revision': 0,
            'status': 'matched',
            'matching_id': 1,
            'candidate': None,
            'times_dispatched': 0,
            'times_matched': 1,
        },
    ]

    assert log_to_yt.times_called == 1
    match_log = log_to_yt.next_call()['data']
    match_log.pop('timestamp')

    assert match_log == load_json('match_log.json')
