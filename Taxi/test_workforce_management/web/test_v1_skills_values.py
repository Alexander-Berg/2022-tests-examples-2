import pytest

from workforce_management.common.constants import skills as skills_constants
from workforce_management.storage.postgresql import db


URI = 'v1/skills/values'
DELETE_URI = 'v1/skills/delete'
MODIFY_URI = 'v1/skills/modify'
PLAN_URI = '/v1/operators/plan/info/'
HEADERS = {'X-Yandex-UID': 'uid1', 'X-WFM-Domain': 'taxi'}
SETTINGS = {key: 1 for key in skills_constants.PROPERTIES_FIELDS}
PROPERTIES = {
    'working_on_break_after_minutes': 1,
    'late_after_minutes': 1,
    'absence_after_minutes': 1,
    'not_working_after_minutes': 1,
    'not_working_break_after_minutes': 1,
    'late_from_break_after_minutes': 1,
    'shift_paused_after_minutes': 1,
    'overtime_after_minutes': 1,
    'flap_interval_min': 1,
}


@pytest.mark.pgsql('workforce_management', files=['simple_skills.sql'])
@pytest.mark.config(WORKFORCE_MANAGEMENT_SKILLS_SETTINGS=SETTINGS)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_res',
    [
        pytest.param(
            HEADERS,
            200,
            [
                {
                    'description': '',
                    'is_active': True,
                    'name': 'hokage',
                    'properties': PROPERTIES,
                    'revision_id': '2020-10-22T14:00:00.000000 +0000',
                },
                {
                    'description': '',
                    'is_active': True,
                    'name': 'horse_archer',
                    'properties': PROPERTIES,
                    'revision_id': '2020-10-22T13:00:00.000000 +0000',
                },
                {
                    'description': '',
                    'is_active': True,
                    'name': 'order',
                    'properties': PROPERTIES,
                    'revision_id': '2020-10-22T12:00:00.000000 +0000',
                },
                {
                    'description': '',
                    'is_active': True,
                    'name': 'pokemon',
                    'properties': PROPERTIES,
                    'revision_id': '2020-10-22T14:00:00.000000 +0000',
                },
                {
                    'description': '',
                    'is_active': True,
                    'name': 'tatarin',
                    'properties': PROPERTIES,
                    'revision_id': '2020-10-22T14:00:00.000000 +0000',
                },
            ],
        ),
    ],
)
async def test_skills_values(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        expected_res,
):
    res = await taxi_workforce_management_web.get(
        URI, params=None, headers=tst_request,
    )
    assert res.status == expected_status

    if expected_status > 200:
        return

    data = await res.json()
    assert data['skills'] == expected_res


@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_skills.sql', 'simple_skills_edges.sql'],
)
@pytest.mark.config(WORKFORCE_MANAGEMENT_SKILLS_SETTINGS=SETTINGS)
@pytest.mark.parametrize(
    'tst_request, expected_status',
    [
        pytest.param(
            {
                'alias': 'hitman',
                'description': 'makes a living by killing people',
                'is_active': True,
                'name': 'killer',
                'properties': {
                    'absence_after_minutes': 240,
                    'late_after_minutes': 5,
                },
            },
            200,
        ),
        pytest.param(
            {
                'name': 'horse_archer',
                'description': 'conquers worlds and cant be caught in any way',
                'is_active': True,
            },
            409,
        ),
        pytest.param(
            {
                'name': 'horse_archer',
                'description': 'conquers worlds and cant be caught in any way',
                'is_active': True,
                'revision_id': '2020-08-25T21:00:00.000000 +0000',
            },
            409,
        ),
        pytest.param(
            {
                'description': 'conquers worlds and cant be caught in any way',
                'is_active': True,
                'name': 'horse_archer',
                'properties': {
                    'absence_after_minutes': 240,
                    'late_after_minutes': 5,
                },
                'revision_id': '2020-10-22T13:00:00.000000 +0000',
            },
            200,
        ),
        pytest.param(
            {
                'description': 'conquers worlds and cant be caught in any way',
                'is_active': True,
                'name': 'horse_archer',
                'properties': {
                    'absence_after_minutes': 45,
                    'late_after_minutes': 15,
                },
                'revision_id': '2020-10-22T13:00:00.000000 +0000',
            },
            200,
        ),
        pytest.param(
            {
                'description': 'conquers worlds and cant be caught in any way',
                'is_active': True,
                'name': 'horse_archer',
                'revision_id': '2020-10-22T13:00:00.000000 +0000',
            },
            200,
            id='no_properties',
        ),
        pytest.param(
            {
                'name': 'tatarin',
                'description': '',
                'is_active': True,
                'children': {
                    'upsert': [{'name': 'pokemon'}, {'name': 'order'}],
                    'remove': ['hokage'],
                },
                'revision_id': '2020-10-22T14:00:00.0 +0000',
            },
            200,
            id='modify_children',
        ),
        pytest.param(
            {
                'name': 'hokage',
                'description': '',
                'is_active': True,
                'children': {'replace': [{'name': 'pokemon'}]},
                'revision_id': '2020-10-22T14:00:00.0 +0000',
            },
            200,
            id='replace_children',
        ),
        pytest.param(
            {
                'name': 'hokage',
                'description': '',
                'is_active': True,
                'children': {'replace': []},
                'revision_id': '2020-10-22T14:00:00.0 +0000',
            },
            200,
            id='replace_children_empty',
        ),
        pytest.param(
            {
                'name': 'order1000',
                'description': '',
                'children': {'replace': [{'name': 'pokemon'}]},
            },
            200,
            id='create_group',
        ),
        pytest.param(
            {
                'name': 'pokemon',
                'children': {'upsert': [{'name': 'tatarin'}]},
                'revision_id': '2020-10-22T14:00:00.0 +0000',
            },
            400,
            id='modify_children_cycle',
        ),
        pytest.param(
            {
                'name': 'pokemon',
                'children': {'upsert': [{'name': 'order1000'}]},
                'revision_id': '2020-10-22T14:00:00.0 +0000',
            },
            404,
            id='modify_missing_skill_1',
        ),
        pytest.param(
            {
                'name': 'pokemon',
                'children': {'remove': ['order1000']},
                'revision_id': '2020-10-22T14:00:00.0 +0000',
            },
            404,
            id='modify_missing_skill_2',
        ),
    ],
)
async def test_modify(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
):
    res = await taxi_workforce_management_web.post(
        MODIFY_URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status

    if expected_status > 200:
        return

    data = await res.json()
    assert data.pop('revision_id')
    req_skill = data['name']
    tst_request.pop('revision_id', None)
    is_active = data.pop('is_active', None)
    tst_request.pop('is_active', None)
    if is_active is None:
        assert data['is_active']
    req_children = tst_request.pop('children', None)
    assert data == tst_request

    if req_children:
        res = await taxi_workforce_management_web.get(
            URI, headers=HEADERS, params={'name': req_skill},
        )
        data = await res.json()

        def names(records):
            for record in records:
                yield record['name']

        children = next(
            set(names(skill.get('children', [])))
            for skill in data['skills']
            if skill['name'] == req_skill
        )

        skills = set(names(data['skills']))

        replaced = req_children.get('replace')
        if replaced is not None:
            expected_children = set(names(replaced))
            assert children == expected_children
        else:
            expected_children = set(names(req_children.get('upsert', [])))
            assert expected_children.issubset(children)
            removed = req_children.get('removed')
            if removed:
                removed_children = set(names(removed))
                assert not removed_children.issubset(children)
                expected_children -= removed_children

        assert expected_children.issubset(skills)

    res = await taxi_workforce_management_web.post(
        PLAN_URI, json={'skills': [req_skill]},
    )
    assert res.status == 200
    data = await res.json()

    if req_children:
        assert not data['items']
    else:
        assert data['items']


@pytest.mark.pgsql('workforce_management', files=['simple_skills.sql'])
@pytest.mark.config(WORKFORCE_MANAGEMENT_SKILLS_SETTINGS=SETTINGS)
@pytest.mark.parametrize(
    'tst_request, expected_status,',
    [
        ({'name': 'killer'}, 400),
        (
            {
                'name': 'horse_archer',
                'revision_id': '2020-08-25T21:00:00.000000 +0000',
            },
            409,
        ),
        (
            {
                'name': 'horse_archer',
                'revision_id': '2020-10-22T13:00:00.000000 +0000',
            },
            400,  # exist plan with relation to this skill
        ),
        (
            {
                'name': 'pokemon',
                'revision_id': '2020-10-22T14:00:00.000000 +0000',
            },
            200,
        ),
        (
            {
                'name': 'tatarin',
                'revision_id': '2020-10-22T14:00:00.000000 +0000',
            },
            200,
        ),
        (
            {
                'name': 'hokage',
                'revision_id': '2020-10-22T14:00:00.000000 +0000',
            },
            200,
        ),
    ],
)
async def test_delete(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
):
    res = await taxi_workforce_management_web.post(
        DELETE_URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status
    success = expected_status <= 200

    res = await taxi_workforce_management_web.get(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == 200

    data = await res.json()

    found = any(
        [skill['name'] == tst_request['name'] for skill in data['skills']],
    )

    assert not found or not success

    operators_db = db.OperatorsRepo(web_context)
    master_pool = await operators_db.master
    async with master_pool.acquire() as conn:
        res = await operators_db.get_deleted_skills(
            conn, names=[tst_request['name']],
        )
        if success:
            assert res
        else:
            assert not res
