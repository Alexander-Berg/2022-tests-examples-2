import pytest


def get_agent_statuses(db):
    cursor = db.cursor()
    cursor.execute(
        f'SELECT sip_username, metaqueue, subcluster,'
        f' is_talking FROM callcenter_queues.talking_status',
    )
    return {row[0]: row[3] for row in cursor}


def get_calls_statuses(db):
    cursor = db.cursor()
    cursor.execute(
        f'SELECT asterisk_call_id, status FROM callcenter_queues.calls',
    )
    return {row[0]: row[1] for row in cursor}


CALL_IDS = {
    'dm4',
    'dm2',
    'dq4',
    'dq2',
    'dt4',
    'dt2',
    'hm4',
    'hm2',
    'hq4',
    'hq2',
    'ht4',
    'ht2',
}


@pytest.mark.pgsql('callcenter_queues', files=['insert_calls.sql'])
@pytest.mark.parametrize(
    'expected_calls',
    [
        pytest.param(
            {
                'dm4': 'queued',
                'dm2': 'queued',
                'dq4': 'queued',
                'dq2': 'queued',
                'dt4': 'talking',
                'dt2': 'talking',
                'hm4': 'queued',
                'hm2': 'queued',
                'hq4': 'queued',
                'hq2': 'queued',
                'ht4': 'talking',
                'ht2': 'talking',
            },
            marks=[
                pytest.mark.config(
                    CALLCENTER_QUEUES_CLEANER_SETTINGS={
                        'period_sec': 60,
                        'call_ttls_map': {},
                    },
                ),
            ],
            id=f'rules turned off',
        ),
        pytest.param(
            {
                'dm4': 'queued',
                'dm2': 'queued',
                'dq4': 'queued',
                'dq2': 'queued',
                'dt4': 'talking',
                'dt2': 'talking',
                'hm4': 'queued',
                'hm2': 'queued',
                'hq4': 'queued',
                'hq2': 'queued',
                'ht4': 'talking',
                'ht2': 'talking',
            },
            marks=[
                pytest.mark.config(
                    CALLCENTER_QUEUES_CLEANER_SETTINGS={
                        'period_sec': 60,
                        'call_ttls_map': {
                            '__default__': {
                                'talking_call_ttl_sec': 0,  # endless
                                'queued_call_ttl_sec': 5 * 3600,  # 5 hours
                            },
                        },
                    },
                ),
            ],
            id=f'check for endless ttl',
        ),
        pytest.param(
            {
                'dm2': 'queued',
                'dq2': 'queued',
                'dt4': 'talking',
                'dt2': 'talking',
                'hm4': 'queued',
                'hm2': 'queued',
                'hq4': 'queued',
                'hq2': 'queued',
                'ht4': 'talking',
                'ht2': 'talking',
                'dq4': 'completed',
                'dm4': 'completed',
            },
            marks=[
                pytest.mark.config(
                    CALLCENTER_QUEUES_CLEANER_SETTINGS={
                        'period_sec': 60,
                        'call_ttls_map': {
                            'disp': {
                                'queued_call_ttl_sec': 3 * 3600,  # 3 hours
                            },
                        },
                    },
                ),
            ],
            id=f'check for ttl=3h, disp only, queued only',
        ),
        pytest.param(
            {
                'dm2': 'queued',
                'dq2': 'queued',
                'dt2': 'talking',
                'hm4': 'queued',
                'hm2': 'queued',
                'hq4': 'queued',
                'hq2': 'queued',
                'ht4': 'talking',
                'ht2': 'talking',
                'dq4': 'completed',
                'dm4': 'completed',
                'dt4': 'completed',
            },
            marks=[
                pytest.mark.config(
                    CALLCENTER_QUEUES_CLEANER_SETTINGS={
                        'period_sec': 60,
                        'call_ttls_map': {
                            'disp': {
                                'talking_call_ttl_sec': 3 * 3600,  # 3 hours
                                'queued_call_ttl_sec': 3 * 3600,  # 3 hours
                            },
                        },
                    },
                ),
            ],
            id=f'check for ttl=3h, disp only',
        ),
        pytest.param(
            {
                'hm4': 'queued',
                'hm2': 'queued',
                'hq4': 'queued',
                'hq2': 'queued',
                'ht4': 'talking',
                'ht2': 'talking',
                'dq2': 'completed',
                'dm2': 'completed',
                'dq4': 'completed',
                'dm4': 'completed',
                'dt2': 'completed',
                'dt4': 'completed',
            },
            marks=[
                pytest.mark.config(
                    CALLCENTER_QUEUES_CLEANER_SETTINGS={
                        'period_sec': 60,
                        'call_ttls_map': {
                            'disp': {
                                'talking_call_ttl_sec': 3600,  # 1 hour
                                'queued_call_ttl_sec': 3600,  # 1 hour
                            },
                        },
                    },
                ),
            ],
            id=f'check for ttl=1h, disp only',
        ),
        pytest.param(
            {
                'dt2': 'talking',
                'hm2': 'completed',
                'hq2': 'completed',
                'dm2': 'completed',
                'hq4': 'completed',
                'hm4': 'completed',
                'dq4': 'completed',
                'dm4': 'completed',
                'dq2': 'completed',
                'dt4': 'completed',
                'ht2': 'completed',
                'ht4': 'completed',
            },
            marks=[
                pytest.mark.config(
                    CALLCENTER_QUEUES_CLEANER_SETTINGS={
                        'period_sec': 60,
                        'call_ttls_map': {
                            'disp': {
                                'talking_call_ttl_sec': 3 * 3600,  # 3 hours
                                # __default__ will be used = 1 hour
                            },
                            '__default__': {
                                'talking_call_ttl_sec': 3600,  # 1 hours
                                'queued_call_ttl_sec': 3600,  # 1 hours
                            },
                        },
                    },
                ),
            ],
            id=f'check for different queues',
        ),
        pytest.param(
            {
                'dm2': 'queued',
                'dq2': 'queued',
                'dt2': 'talking',
                'hm2': 'queued',
                'hq2': 'queued',
                'ht2': 'talking',
                'hq4': 'completed',
                'hm4': 'completed',
                'dq4': 'completed',
                'dm4': 'completed',
                'ht4': 'completed',
                'dt4': 'completed',
            },
            marks=[
                pytest.mark.config(
                    CALLCENTER_QUEUES_CLEANER_SETTINGS={
                        'period_sec': 60,
                        'call_ttls_map': {
                            '__default__': {
                                'talking_call_ttl_sec': 3 * 3600,  # 3 hours
                                'queued_call_ttl_sec': 3 * 3600,  # 3 hours
                            },
                        },
                    },
                ),
            ],
            id=f'check for __default__ only',
        ),
    ],
)
async def test_pg_cleaner_calls(taxi_callcenter_queues, pgsql, expected_calls):
    db = pgsql['callcenter_queues']

    await taxi_callcenter_queues.run_periodic_task('callcenter-queues-cleaner')

    assert get_calls_statuses(db) == expected_calls


@pytest.mark.pgsql('callcenter_queues', files=['insert_talking_status.sql'])
@pytest.mark.parametrize(
    'expected_operators',
    [
        pytest.param(
            {'dt2': True, 'dt4': True, 'ht2': True, 'ht4': True},
            marks=[
                pytest.mark.config(
                    CALLCENTER_QUEUES_CLEANER_SETTINGS={
                        'period_sec': 60,
                        'call_ttls_map': {},
                    },
                ),
            ],
            id=f'rules turned off',
        ),
        pytest.param(
            {'dt2': True, 'dt4': True, 'ht2': True, 'ht4': True},
            marks=[
                pytest.mark.config(
                    CALLCENTER_QUEUES_CLEANER_SETTINGS={
                        'period_sec': 60,
                        'call_ttls_map': {
                            '__default__': {
                                'talking_call_ttl_sec': 0,  # endless
                                'queued_call_ttl_sec': 5 * 3600,  # 5 hours
                            },
                        },
                    },
                ),
            ],
            id=f'check for endless ttl',
        ),
        pytest.param(
            {'dt2': True, 'dt4': True, 'ht2': True, 'ht4': True},
            marks=[
                pytest.mark.config(
                    CALLCENTER_QUEUES_CLEANER_SETTINGS={
                        'period_sec': 60,
                        'call_ttls_map': {
                            'disp': {
                                'queued_call_ttl_sec': 3 * 3600,  # 3 hours
                            },
                        },
                    },
                ),
            ],
            id=f'check for ttl=3h, disp only, queued only',
        ),
        pytest.param(
            {'dt2': True, 'dt4': False, 'ht2': True, 'ht4': True},
            marks=[
                pytest.mark.config(
                    CALLCENTER_QUEUES_CLEANER_SETTINGS={
                        'period_sec': 60,
                        'call_ttls_map': {
                            'disp': {
                                'talking_call_ttl_sec': 3 * 3600,  # 3 hours
                                'queued_call_ttl_sec': 3 * 3600,  # 3 hours
                            },
                        },
                    },
                ),
            ],
            id=f'check for ttl=3h, disp only',
        ),
        pytest.param(
            {'dt2': False, 'dt4': False, 'ht2': True, 'ht4': True},
            marks=[
                pytest.mark.config(
                    CALLCENTER_QUEUES_CLEANER_SETTINGS={
                        'period_sec': 60,
                        'call_ttls_map': {
                            'disp': {
                                'talking_call_ttl_sec': 3600,  # 1 hour
                                'queued_call_ttl_sec': 3600,  # 1 hour
                            },
                        },
                    },
                ),
            ],
            id=f'check for ttl=1h, disp only',
        ),
        pytest.param(
            {'dt2': True, 'dt4': False, 'ht2': False, 'ht4': False},
            marks=[
                pytest.mark.config(
                    CALLCENTER_QUEUES_CLEANER_SETTINGS={
                        'period_sec': 60,
                        'call_ttls_map': {
                            'disp': {
                                'talking_call_ttl_sec': 3 * 3600,  # 3 hours
                                # __default__ will be used = 1 hour
                            },
                            '__default__': {
                                'talking_call_ttl_sec': 3600,  # 1 hours
                                'queued_call_ttl_sec': 3600,  # 1 hours
                            },
                        },
                    },
                ),
            ],
            id=f'check for different queues',
        ),
        pytest.param(
            {'dt2': True, 'dt4': False, 'ht2': True, 'ht4': False},
            marks=[
                pytest.mark.config(
                    CALLCENTER_QUEUES_CLEANER_SETTINGS={
                        'period_sec': 60,
                        'call_ttls_map': {
                            '__default__': {
                                'talking_call_ttl_sec': 3 * 3600,  # 3 hours
                                'queued_call_ttl_sec': 3 * 3600,  # 3 hours
                            },
                        },
                    },
                ),
            ],
            id=f'check for __default__ only',
        ),
    ],
)
async def test_pg_cleaner_operators(
        taxi_callcenter_queues, pgsql, expected_operators,
):
    db = pgsql['callcenter_queues']

    await taxi_callcenter_queues.run_periodic_task('callcenter-queues-cleaner')

    assert get_agent_statuses(db) == expected_operators


@pytest.mark.pgsql('callcenter_queues', files=['insert_calls_for_limit.sql'])
@pytest.mark.config(
    CALLCENTER_QUEUES_CLEANER_SETTINGS={
        'period_sec': 60,
        'call_ttls_map': {
            'disp': {'queued_call_ttl_sec': 4 * 3600},  # 4 hours
        },
    },
)
# chunk-size is 10
async def test_pg_cleaner_calls_limit(taxi_callcenter_queues, pgsql):
    db = pgsql['callcenter_queues']

    await taxi_callcenter_queues.run_periodic_task('callcenter-queues-cleaner')

    assert get_calls_statuses(db) == {
        '1': 'completed',
        '2': 'completed',
        '3': 'completed',
        '4': 'completed',
        '5': 'completed',
        '6': 'completed',
        '7': 'completed',
        '8': 'completed',
        '9': 'completed',
        '10': 'completed',
        '11': 'queued',
    }


@pytest.mark.now('2020-11-01T11:00:00.00Z')
@pytest.mark.pgsql('callcenter_queues', files=['insert_routed_calls.sql'])
@pytest.mark.parametrize(
    'expected_guids_left',
    [
        pytest.param(
            {'call_guid_1', 'call_guid_2', 'call_guid_3'},
            marks=[
                pytest.mark.config(
                    CALLCENTER_QUEUES_CLEANER_SETTINGS={
                        'period_sec': 60,
                        'call_ttls_map': {},
                        'delete_hanged_routed_calls': False,
                    },
                ),
            ],
            id='Disabled',
        ),
        pytest.param(
            {'call_guid_1', 'call_guid_2', 'call_guid_3'},
            id='Disabled by default',
        ),
        pytest.param(
            {'call_guid_2', 'call_guid_3'},
            marks=[
                pytest.mark.config(
                    CALLCENTER_QUEUES_CLEANER_SETTINGS={
                        'period_sec': 60,
                        'call_ttls_map': {},
                        'delete_hanged_routed_calls': True,
                    },
                    CALLCENTER_QUEUES_BALANCE_ROUTED_CALL_TTL=1200,  # 20min
                ),
            ],
            id='Enabled, TTL=20min',
        ),
        pytest.param(
            {'call_guid_3'},
            marks=[
                pytest.mark.config(
                    CALLCENTER_QUEUES_CLEANER_SETTINGS={
                        'period_sec': 60,
                        'call_ttls_map': {},
                        'delete_hanged_routed_calls': True,
                    },
                    CALLCENTER_QUEUES_BALANCE_ROUTED_CALL_TTL=600,  # 10min
                ),
            ],
            id='Enabled, TTL=10min',
        ),
    ],
)
async def test_routed_calls_cleanup(
        taxi_callcenter_queues, pgsql, expected_guids_left,
):
    await taxi_callcenter_queues.run_periodic_task('callcenter-queues-cleaner')

    db = pgsql['callcenter_queues']
    cursor = db.cursor()
    cursor.execute('SELECT call_guid FROM callcenter_queues.routed_calls')
    guids_left = {row[0] for row in cursor}

    assert guids_left == expected_guids_left
