WHOLE_INTERVAL_ANSWER = {
    'timeline': {
        'continuous': [
            {
                'start_point': '2021-10-21T00:00:00+00:00',
                'end_point': '2021-10-21T20:00:00+00:00',
                'entry_color': {'red': 151, 'green': 235, 'blue': 144},
                'additional_height': 0,
                'display_priority': 0,
            },
            {
                'start_point': '2021-10-21T01:00:00+00:00',
                'end_point': '2021-10-21T10:00:00+00:00',
                'entry_color': {'red': 187, 'green': 157, 'blue': 249},
                'additional_height': 2,
                'display_priority': 10,
            },
            {
                'start_point': '2021-10-21T03:00:00+00:00',
                'end_point': '2021-10-21T04:30:00+00:00',
                'entry_color': {'red': 255, 'green': 187, 'blue': 124},
                'additional_height': 0,
                'display_priority': 80,
            },
            {
                'start_point': '2021-10-21T04:00:00+00:00',
                'end_point': '2021-10-21T04:40:00+00:00',
                'entry_color': {'red': 127, 'green': 217, 'blue': 245},
                'additional_height': 1,
                'display_priority': 50,
            },
            {
                'start_point': '2021-10-21T04:50:00+00:00',
                'end_point': '2021-10-21T08:00:00+00:00',
                'entry_color': {'red': 235, 'green': 128, 'blue': 121},
                'additional_height': 0,
                'display_priority': 90,
            },
            {
                'start_point': '2021-10-21T05:00:00+00:00',
                'end_point': '2021-10-21T05:20:00+00:00',
                'entry_color': {'red': 127, 'green': 217, 'blue': 245},
                'additional_height': 1,
                'display_priority': 50,
            },
        ],
        'momentary': [],
    },
    'log': [
        {
            'timepoint': '2021-10-21T01:00:00+00:00',
            'entry_color': {'red': 187, 'green': 157, 'blue': 249},
            'title': 'Drills start',
            'short_description': '',
            'full_description': (
                'Datacenters: vla, sas.\n'
                'Projects: project100500, project100501.\n'
            ),
        },
        {
            'timepoint': '2021-10-21T03:00:00+00:00',
            'entry_color': {'red': 255, 'green': 187, 'blue': 124},
            'title': 'WARN start',
            'short_description': 'hejmdal-stable.yandex.net::template_id',
            'full_description': (
                'descr\nMonitoring: yandex_monitoring_link_address'
            ),
        },
        {
            'timepoint': '2021-10-21T04:00:00+00:00',
            'entry_color': {'red': 127, 'green': 217, 'blue': 245},
            'title': 'Deploy start',
            'short_description': '',
            'full_description': (
                'Nanny: https://nanny.yandex-team.ru/'
                'ui/#/services/catalog/direct_link'
            ),
        },
        {
            'timepoint': '2021-10-21T04:30:00+00:00',
            'entry_color': {'red': 255, 'green': 187, 'blue': 124},
            'title': 'WARN end',
            'short_description': 'hejmdal-stable.yandex.net::template_id',
            'full_description': (
                'descr\nMonitoring: yandex_monitoring_link_address'
            ),
        },
        {
            'timepoint': '2021-10-21T04:40:00+00:00',
            'entry_color': {'red': 127, 'green': 217, 'blue': 245},
            'title': 'Deploy end',
            'short_description': '',
            'full_description': (
                'Nanny: https://nanny.yandex-team.ru/'
                'ui/#/services/catalog/direct_link'
            ),
        },
        {
            'timepoint': '2021-10-21T04:50:00+00:00',
            'entry_color': {'red': 235, 'green': 128, 'blue': 121},
            'title': 'CRIT start',
            'short_description': 'direct_link::template_id',
            'full_description': 'descr',
        },
        {
            'timepoint': '2021-10-21T05:00:00+00:00',
            'entry_color': {'red': 127, 'green': 217, 'blue': 245},
            'title': 'Deploy start',
            'short_description': '',
            'full_description': (
                'Nanny: https://nanny.yandex-team.ru/'
                'ui/#/services/catalog/direct_link'
            ),
        },
        {
            'timepoint': '2021-10-21T05:20:00+00:00',
            'entry_color': {'red': 127, 'green': 217, 'blue': 245},
            'title': 'Deploy end',
            'short_description': '',
            'full_description': (
                'Nanny: https://nanny.yandex-team.ru/'
                'ui/#/services/catalog/direct_link'
            ),
        },
        {
            'timepoint': '2021-10-21T08:00:00+00:00',
            'entry_color': {'red': 235, 'green': 128, 'blue': 121},
            'title': 'CRIT end',
            'short_description': 'direct_link::template_id',
            'full_description': 'descr',
        },
        {
            'timepoint': '2021-10-21T10:00:00+00:00',
            'entry_color': {'red': 187, 'green': 157, 'blue': 249},
            'title': 'Drills end',
            'short_description': '',
            'full_description': (
                'Datacenters: vla, sas.\n'
                'Projects: project100500, project100501.\n'
            ),
        },
    ],
}

EMPTY_ANSWER = {
    'timeline': {
        'continuous': [
            {
                'start_point': '2021-10-19T21:00:00+00:00',
                'end_point': '2021-10-20T17:00:00+00:00',
                'entry_color': {'red': 151, 'green': 235, 'blue': 144},
                'additional_height': 0,
                'display_priority': 0,
            },
        ],
        'momentary': [],
    },
    'log': [],
}

EVENT_CONTAINS_REQUEST = {
    'timeline': {
        'continuous': [
            {
                'start_point': '2021-10-19T03:00:00+00:00',
                'end_point': '2021-10-19T05:00:00+00:00',
                'entry_color': {'red': 151, 'green': 235, 'blue': 144},
                'additional_height': 0,
                'display_priority': 0,
            },
            {
                'start_point': '2021-10-19T03:00:00+00:00',
                'end_point': '2021-10-19T05:00:00+00:00',
                'entry_color': {'red': 187, 'green': 157, 'blue': 249},
                'additional_height': 0,
                'display_priority': 10,
            },
        ],
        'momentary': [],
    },
    'log': [
        {
            'timepoint': '2021-10-19T00:00:00+00:00',
            'entry_color': {'red': 187, 'green': 157, 'blue': 249},
            'title': 'Drills start',
            'short_description': '',
            'full_description': (
                'Datacenters: man.\nProjects: project100500.\n'
            ),
        },
        {
            'timepoint': '2021-10-19T10:00:00+00:00',
            'entry_color': {'red': 187, 'green': 157, 'blue': 249},
            'title': 'Drills end',
            'short_description': '',
            'full_description': (
                'Datacenters: man.\nProjects: project100500.\n'
            ),
        },
    ],
}

NOT_FINISHED_EVENT = {
    'timeline': {
        'continuous': [
            {
                'start_point': '2021-10-23T03:00:00+00:00',
                'end_point': '2021-10-23T05:00:00+00:00',
                'entry_color': {'red': 151, 'green': 235, 'blue': 144},
                'additional_height': 0,
                'display_priority': 0,
            },
            {
                'start_point': '2021-10-23T03:00:00+00:00',
                'end_point': '2021-10-23T05:00:00+00:00',
                'entry_color': {'red': 187, 'green': 157, 'blue': 249},
                'additional_height': 0,
                'display_priority': 10,
            },
        ],
        'momentary': [],
    },
    'log': [
        {
            'timepoint': '2021-10-23T00:00:00+00:00',
            'entry_color': {'red': 187, 'green': 157, 'blue': 249},
            'title': 'Drills start',
            'short_description': '',
            'full_description': (
                'Datacenters: sas.\nProjects: project100501.\n'
            ),
        },
    ],
}

CURRENT_ALERT = {
    'timeline': {
        'continuous': [
            {
                'start_point': '2021-10-24T03:00:00+00:00',
                'end_point': '2021-10-24T05:00:00+00:00',
                'entry_color': {'red': 151, 'green': 235, 'blue': 144},
                'additional_height': 0,
                'display_priority': 0,
            },
            {
                'start_point': '2021-10-24T03:00:00+00:00',
                'end_point': '2021-10-24T05:00:00+00:00',
                'entry_color': {'red': 187, 'green': 157, 'blue': 249},
                'additional_height': 1,
                'display_priority': 10,
            },
            {
                'start_point': '2021-10-24T04:00:00+00:00',
                'end_point': '2021-10-24T05:00:00+00:00',
                'entry_color': {'red': 255, 'green': 187, 'blue': 124},
                'additional_height': 0,
                'display_priority': 80,
            },
        ],
        'momentary': [],
    },
    'log': [
        {
            'timepoint': '2021-10-23T00:00:00+00:00',
            'entry_color': {'red': 187, 'green': 157, 'blue': 249},
            'title': 'Drills start',
            'short_description': '',
            'full_description': (
                'Datacenters: sas.\nProjects: project100501.\n'
            ),
        },
        {
            'timepoint': '2021-10-24T04:00:00+00:00',
            'entry_color': {'red': 255, 'green': 187, 'blue': 124},
            'title': 'WARN start',
            'short_description': (
                'hejmdal-stable.yandex.net::other_template_id'
            ),
            'full_description': 'description',
        },
    ],
}


async def test_event_log_list_incorrect(taxi_hejmdal):
    await taxi_hejmdal.run_task('tuner/initialize')

    # empty params
    response = await taxi_hejmdal.get('/v1/event-log/list', params={})
    assert response.status_code == 400
    assert response.json()['message'] == 'Missing service_id in query'

    # only service_id
    response = await taxi_hejmdal.get(
        '/v1/event-log/list', params={'service_id': 100500},
    )
    assert response.status_code == 400
    assert response.json()['message'] == 'Missing env in query'

    # service_id and env
    response = await taxi_hejmdal.get(
        '/v1/event-log/list', params={'service_id': 100500, 'env': 'unstable'},
    )
    assert response.status_code == 400
    assert response.json()['message'] == 'Missing from in query'

    # service_id, end and from
    response = await taxi_hejmdal.get(
        '/v1/event-log/list',
        params={
            'service_id': 100500,
            'env': 'unstable',
            'from': '2021-10-21T00:00:00Z',
        },
    )
    assert response.status_code == 400
    assert response.json()['message'] == 'Missing to in query'

    # unknown service
    response = await taxi_hejmdal.get(
        '/v1/event-log/list',
        params={
            'service_id': 100500,
            'env': 'stable',
            'from': '2021-10-21T00:00:00Z',
            'to': '2021-10-21T20:00:00Z',
        },
    )
    assert response.status_code == 400
    assert response.json()['message'] == 'service with id 100500 was not found'

    # no branches for server
    response = await taxi_hejmdal.get(
        '/v1/event-log/list',
        params={
            'service_id': 139,
            'env': 'prestable',
            'from': '2021-10-21T00:00:00Z',
            'to': '2021-10-21T20:00:00Z',
        },
    )
    assert response.status_code == 400
    assert (
        response.json()['message']
        == 'service with id 139 doesn\'t have prestable branches'
    )

    # Incorrect environment
    response = await taxi_hejmdal.get(
        '/v1/event-log/list',
        params={
            'service_id': 139,
            'env': 'incorrect_env',
            'from': '2021-10-21T00:00:00Z',
            'to': '2021-10-21T20:00:00Z',
        },
    )
    assert response.status_code == 400
    assert response.json()['message'] == 'Failed to parse request'

    # 'from' is greater than 'to'
    response = await taxi_hejmdal.get(
        '/v1/event-log/list',
        params={
            'service_id': 139,
            'env': 'stable',
            'from': '2021-10-21T20:00:00Z',
            'to': '2021-10-21T00:00:00Z',
        },
    )
    assert response.status_code == 400
    assert response.json()['message'] == '\'from\' must be less than \'to\''


async def test_event_log_list(taxi_hejmdal):
    await taxi_hejmdal.run_task('tuner/initialize')

    # empty answer
    response = await taxi_hejmdal.get(
        '/v1/event-log/list',
        params={
            'service_id': 139,
            'env': 'stable',
            'from': '2021-10-20T00:00:00+03',
            'to': '2021-10-20T20:00:00+03',
        },
    )
    assert response.status_code == 200
    assert response.json() == EMPTY_ANSWER

    # all events in requested interval
    response = await taxi_hejmdal.get(
        '/v1/event-log/list',
        params={
            'service_id': 139,
            'env': 'stable',
            'from': '2021-10-21T00:00:00Z',
            'to': '2021-10-21T20:00:00Z',
        },
    )
    assert response.status_code == 200
    assert response.json() == WHOLE_INTERVAL_ANSWER

    # event range contains request range
    response = await taxi_hejmdal.get(
        '/v1/event-log/list',
        params={
            'service_id': 139,
            'env': 'stable',
            'from': '2021-10-19T03:00:00Z',
            'to': '2021-10-19T05:00:00Z',
        },
    )
    assert response.status_code == 200
    assert response.json() == EVENT_CONTAINS_REQUEST

    # not finished event
    response = await taxi_hejmdal.get(
        '/v1/event-log/list',
        params={
            'service_id': 139,
            'env': 'stable',
            'from': '2021-10-23T03:00:00Z',
            'to': '2021-10-23T05:00:00Z',
        },
    )
    assert response.status_code == 200
    assert response.json() == NOT_FINISHED_EVENT

    # current alert and not finished previous drills
    response = await taxi_hejmdal.get(
        '/v1/event-log/list',
        params={
            'service_id': 139,
            'env': 'stable',
            'from': '2021-10-24T03:00:00Z',
            'to': '2021-10-24T05:00:00Z',
        },
    )
    assert response.status_code == 200
    assert response.json() == CURRENT_ALERT
