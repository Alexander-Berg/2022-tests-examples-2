import pytest

DRIVER_LESSONS_DB = {
    frozenset({'driver_id': 'uuid0', 'park_id': 'dbid0'}.items()): [
        {'lesson_id': '5bca0c9e7bcecff318fef2aa', 'progress': 77},
        {'lesson_id': '5bca0c9e7bcecff318fef2bb', 'progress': 10},
    ],
    frozenset({'driver_id': 'uuid1', 'park_id': 'dbid0'}.items()): [
        {'lesson_id': '5bca0c9e7bcecff318fef2aa', 'progress': 0},
    ],
    frozenset({'driver_id': 'uuid2', 'park_id': 'dbid1'}.items()): [
        {'lesson_id': '5bca0c9e7bcecff318fef2aa', 'progress': 100},
    ],
}

DRIVER_LESSONS_PROGRESS_CHAINS = {
    '0_0': [
        {
            'lesson_id': '5bca0c9e7bcecff318fef2aa',
            'progress': 77,
            'driver_id': 'uuid0',
            'park_id': 'dbid0',
        },
        {
            'lesson_id': '5bca0c9e7bcecff318fef2aa',
            'progress': 0,
            'driver_id': 'uuid1',
            'park_id': 'dbid0',
        },
        {
            'lesson_id': '5bca0c9e7bcecff318fef2aa',
            'progress': 100,
            'driver_id': 'uuid2',
            'park_id': 'dbid1',
        },
    ],
    '1643893229_1': [
        {
            'lesson_id': '5bca0c9e7bcecff318fef2bb',
            'progress': 10,
            'driver_id': 'uuid0',
            'park_id': 'dbid0',
        },
    ],
    '1643893729_321': [
        {
            'lesson_id': '5bca0c9e7bcecff318fef2bb',
            'progress': 77,
            'driver_id': 'uuid0',
            'park_id': 'dbid0',
        },
    ],
    '1643893747_0': [],
}


@pytest.fixture(autouse=True)
def driver_lessons_progress_upd(mockserver):
    @mockserver.json_handler(
        '/driver-lessons'
        '/internal/driver-lessons/v1/lessons-progress/updates',
    )
    def _lessons_progress_updates_mock(request):
        if not DRIVER_LESSONS_PROGRESS_CHAINS:
            return {'lessons_progress': [], 'revision': '0_0'}
        revisions = sorted(DRIVER_LESSONS_PROGRESS_CHAINS.keys())
        last_known_revision_index = 0
        if 'last_known_revision' in request.json:
            try:
                last_known_revision_index = revisions.index(
                    request.json['last_known_revision'],
                )
            except ValueError:
                return mockserver.make_response(status=400)
        last_revision_index = last_known_revision_index
        if DRIVER_LESSONS_PROGRESS_CHAINS[
                revisions[last_known_revision_index]
        ]:
            last_revision_index += 1
        return {
            'lessons_progress': DRIVER_LESSONS_PROGRESS_CHAINS[
                revisions[last_known_revision_index]
            ],
            'revision': revisions[last_revision_index],
        }

    @mockserver.json_handler(
        '/driver-lessons'
        '/internal/driver-lessons/v1/lessons-progress/bulk-retrieve',
    )
    def _lessons_progress_bulk_mock(request):
        result = []
        for driver in request.json['drivers']:
            lessons = DRIVER_LESSONS_DB.get(frozenset(driver.items()), [])
            for lesson in lessons:
                result.append({**lesson, **driver})
        return {'lessons_progress': result}

    @mockserver.json_handler(
        '/driver-lessons'
        '/internal/driver-lessons/v1/lessons-progress/latest-revision',
    )
    def _lessons_latest_revision(_request):
        return {'revision': '1643893729_321'}


def its_because_of_support_hub_name(driver):
    assert 'details' in driver
    assert 'grocery/fetch_lessons_classes' in driver['details']
    assert 'grocery/fetch_lessons_classes' in driver['reasons']
    assert 'is_satisfied' in driver
    assert not driver['is_satisfied']
    assert driver['details']['grocery/fetch_lessons_classes'] == [
        '5bca0c9e7bcecff318fef2aa',
    ]


def training_completed(driver):
    assert 'details' in driver
    assert 'grocery/fetch_lessons_classes' not in driver['details']


@pytest.mark.config(
    CANDIDATES_SHIFT_SETTINGS={
        'eats': {'classes': ['econom', 'vip', 'uberblack']},
        'grocery': {'classes': ['lavka', 'econom', 'vip']},
    },
)
async def test_satisfy(taxi_candidates, driver_positions, experiments3):
    experiments3.add_config(
        match={
            'predicate': {
                'type': 'in_set',
                'init': {
                    'set': ['uuid2', 'uuid0', 'uuid3'],
                    'arg_name': 'driver_uuid',
                    'set_elem_type': 'string',
                },
            },
            'enabled': True,
        },
        name='grocery_courier_mandatory_lessons',
        consumers=['candidates/filters'],
        default_value={'lessons_ids': ['5bca0c9e7bcecff318fef2aa']},
    )
    # dbid1_uuid3 drivers park(clid1) deactivated
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
            {'dbid_uuid': 'dbid1_uuid3', 'position': [55, 35]},
        ],
    )
    body = {
        'driver_ids': [
            {'uuid': 'uuid0', 'dbid': 'dbid0'},
            {'uuid': 'uuid1', 'dbid': 'dbid0'},
            {'uuid': 'uuid2', 'dbid': 'dbid1'},
            {'uuid': 'uuid3', 'dbid': 'dbid1'},
            {'uuid': 'uuid8', 'dbid': 'dbid0'},
        ],
        'allowed_classes': ['lavka'],
        'order_id': 'test-order-1',
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('satisfy', json=body)
    assert response.status_code == 200
    drivers = sorted(response.json()['drivers'], key=lambda x: x['uuid'])
    # too volatile value
    assert len(drivers) == 5
    for driver in drivers:
        {
            'uuid0': its_because_of_support_hub_name,
            'uuid1': training_completed,
            'uuid2': training_completed,
            'uuid3': its_because_of_support_hub_name,
            'uuid8': training_completed,
        }[driver['uuid']](driver)
