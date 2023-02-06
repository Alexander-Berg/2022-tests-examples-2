import pytest


@pytest.mark.now('2019-11-11T12:00:00+0')
@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
@pytest.mark.parametrize(
    [
        'yandex_uid',
        'expected_zone_name',
        'stq_args',
        'expected_cache',
        'zalogin_resp',
        'zalogin_called',
        'zalogin_no_uid',
        'expected_seen_bound_uids',
    ],
    [
        (
            'portal_uid',
            'moscow',
            (
                'order1',
                {'$oid': 'cccccccccccccccccccccccc'},
                'android',
                'moscow',
                'portal_uid',
                'portal',
                'ru',
            ),
            'expected_cache_portal.json',
            'zalogin_resp_portal.json',
            1,
            False,
            [['portal_uid', 'phonish_uid']],
        ),
        (
            'portal_uid',
            'moscow',
            (
                'order1',
                {'$oid': 'cccccccccccccccccccccccc'},
                'android',
                'moscow',
                'portal_uid',
                'portal',
                'ru',
            ),
            'expected_cache_bound_no_subs.json',
            'zalogin_resp_bound_no_subs.json',
            1,
            False,
            [['portal_uid', 'phonish_no_subs_uid']],
        ),
        (
            'phonish_uid',
            'moscow',
            (
                'order1',
                {'$oid': 'af35af35af35af35af35af35'},
                'android',
                'moscow',
                'phonish_uid',
                'phonish',
                'ru',
            ),
            'expected_cache_phonish.json',
            None,
            0,
            False,
            [],
        ),
        (
            'phonish_uid',
            'moscow',
            (
                'order1',
                {'$oid': 'af35af35af35af35af35af35'},
                'android',
                'moscow',
                'phonish_uid',
                None,
                'ru',
            ),
            'expected_cache_phonish.json',
            'zalogin_resp_phonish.json',
            1,
            False,
            [],
        ),
        (
            'phonish_no_subs_uid',
            'moscow',
            (
                'order1',
                {'$oid': 'dddddddddddddddddddddddd'},
                'android',
                'moscow',
                'phonish_no_subs_uid',
                'phonish',
                'ru',
            ),
            'expected_cache_phonish_no_subs.json',
            None,
            0,
            False,
            [],
        ),
        (
            'phonish_uid',
            'baku',
            (
                'order1',
                {'$oid': 'af35af35af35af35af35af35'},
                'android',
                'baku',
                'phonish_uid',
                'phonish',
                'ru',
            ),
            'expected_cache_empty.json',
            None,
            0,
            False,
            [],
        ),
        (
            'phonish_uid',
            'elbashy',
            (
                'order1',
                {'$oid': 'af35af35af35af35af35af35'},
                'android',
                'elbashy',
                'phonish_uid',
                'phonish',
                'ru',
            ),
            'expected_cache_empty.json',
            None,
            0,
            False,
            [],
        ),
        (
            'portal_uid',
            'moscow',
            (
                'order1',
                {'$oid': 'cccccccccccccccccccccccc'},
                'android',
                'moscow',
                'portal_uid',
                'portal',
                'ru',
            ),
            'expected_cache_no_uid_portal.json',
            None,
            1,
            True,
            [],
        ),
        (
            'portal_with_subs_uid',
            'moscow',
            (
                'order1',
                {'$oid': 'cccccccccccccccccccccccc'},
                'android',
                'moscow',
                'portal_with_subs_uid',
                'portal',
                'ru',
            ),
            'expected_cache_no_uid_portal_with_subs.json',
            None,
            1,
            True,
            [],
        ),
        (
            'phonish_uid',
            'moscow',
            (
                'order1',
                {'$oid': 'af35af35af35af35af35af35'},
                'android',
                'moscow',
                'phonish_uid',
                None,
                'ru',
            ),
            'expected_cache_phonish.json',
            None,
            1,
            True,
            [],
        ),
        (
            'phonish_no_subs_uid',
            'moscow',
            (
                'order1',
                {'$oid': 'dddddddddddddddddddddddd'},
                'android',
                'moscow',
                'phonish_no_subs_uid',
                None,
                'ru',
            ),
            'expected_cache_phonish_no_subs.json',
            None,
            1,
            True,
            [],
        ),
        (
            'portal_uid',
            'moscow',
            (
                'order1',
                {'$oid': 'cccccccccccccccccccccccc'},
                'android',
                'moscow',
                'portal_uid',
                'portal',
                'ru',
            ),
            'expected_cache_portal.json',
            'zalogin_resp_repeated_bounds.json',
            1,
            False,
            [['portal_uid', 'phonish_uid']],
        ),
    ],
)
async def test_simple(
        mockserver,
        load_json,
        stq_runner,
        mock_zalogin,
        mock_tariffs,
        get_ride_subs_cache,
        get_seen_bound_uids,
        yandex_uid,
        expected_zone_name,
        stq_args,
        expected_cache,
        zalogin_resp,
        zalogin_called,
        zalogin_no_uid,
        expected_seen_bound_uids,
):
    zalogin_mock = mock_zalogin(yandex_uid, zalogin_resp, zalogin_no_uid)
    tariffs_mock = mock_tariffs(expected_zone_name)

    await stq_runner.persey_payments_ride_subs_fetch.call(
        task_id='1', args=stq_args,
    )

    assert zalogin_mock.times_called == zalogin_called
    assert tariffs_mock.times_called == 1
    assert get_ride_subs_cache() == load_json(expected_cache)
    assert get_seen_bound_uids() == expected_seen_bound_uids


@pytest.mark.now('2019-11-11T12:00:00+0')
@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
async def test_tariffs_cache(
        mockserver, stq_runner, mock_tariffs, get_ride_subs_cache,
):
    stq_args = (
        'order1',
        'af35af35af35af35af35af35',
        'android',
        'moscow',
        'phonish_uid',
        'phonish',
        'ru',
    )
    tariffs_mock = mock_tariffs('moscow')

    for _ in range(3):
        await stq_runner.persey_payments_ride_subs_fetch.call(
            task_id='1', args=stq_args,
        )

    assert tariffs_mock.times_called == 1
    assert len(get_ride_subs_cache()['cache']) == 3
