import pytest


SUBSYSTEM_NANNY = {
    'id': 3,
    'name': {'en': 'nanny', 'ru': 'nanny'},
    'slug': 'nanny',
}
SUBSYSTEM_INTERNAL = {
    'id': 1,
    'name': {'en': 'internal', 'ru': 'internal'},
    'slug': 'internal',
}

ROLE_NANNY = {
    'id': 2,
    'name': {'en': 'nanny', 'ru': 'няня'},
    'slug': 'nanny_root',
    'subsystem_id': 3,
    'reference': {'external_slug': '1', 'type': 'project'},
}

ROLE_APPROVE = {
    'id': 3,
    'name': {'en': 'deploy approve', 'ru': 'ок выкатки'},
    'slug': 'deploy_approve',
    'subsystem_id': 1,
    'reference': {'external_slug': '1', 'type': 'service'},
}

ROLE_TEST_ADMIN = {
    'id': 4,
    'name': {'en': 'write', 'ru': 'запись'},
    'slug': 'test_admin',
    'subsystem_id': 1,
    'reference': {'external_slug': '1', 'type': 'namespace'},
}

ROLE_SERVICE_RESPONSIBLE = {
    'id': 5,
    'name': {'en': 'even more write', 'ru': 'топовая запись'},
    'slug': 'test_service_responsible',
    'subsystem_id': 1,
    'reference': {'external_slug': '2', 'type': 'namespace'},
}

ROLE_TASK_MANAGER = {
    'id': 6,
    'name': {'en': 'read', 'ru': 'чтение'},
    'slug': 'test_task_manager',
    'subsystem_id': 1,
    'reference': {'external_slug': '1', 'type': 'namespace'},
}

ROLE_TEST_USER = {
    'id': 7,
    'name': {'en': 'basic', 'ru': 'базовая'},
    'slug': 'test_user',
    'subsystem_id': 1,
    'reference': {'external_slug': '1', 'type': 'namespace'},
}

GRAND_7 = {
    'grand': {'id': 7, 'login': 'vokhcuhza', 'role_id': 5},
    'role': ROLE_SERVICE_RESPONSIBLE,
    'subsystem': SUBSYSTEM_INTERNAL,
    'related_slugs': ['approvals_user', 'approvals_view', 'test_user'],
}

GRAND_6 = {
    'grand': {'id': 6, 'login': 'vokhcuhza', 'role_id': 4},
    'role': ROLE_TEST_ADMIN,
    'subsystem': SUBSYSTEM_INTERNAL,
    'related_slugs': [
        'approvals_user',
        'approvals_view',
        'test_service_responsible',
        'test_task_manager',
        'test_user',
    ],
}

GRAND_5 = {
    'grand': {'id': 5, 'login': 'test-login-4', 'role_id': 3},
    'role': ROLE_APPROVE,
    'subsystem': SUBSYSTEM_INTERNAL,
    'related_slugs': [],
}

GRAND_4 = {
    'grand': {'id': 4, 'login': 'test-login-1', 'role_id': 3},
    'role': ROLE_APPROVE,
    'subsystem': SUBSYSTEM_INTERNAL,
    'related_slugs': [],
}

GRAND_3 = {
    'grand': {'id': 3, 'login': 'test-login-3', 'role_id': 2},
    'role': ROLE_NANNY,
    'subsystem': SUBSYSTEM_NANNY,
    'related_slugs': [],
}

GRAND_2 = {
    'grand': {'id': 2, 'login': 'test-login-2', 'role_id': 2},
    'role': ROLE_NANNY,
    'subsystem': SUBSYSTEM_NANNY,
    'related_slugs': [],
}

GRAND_1 = {
    'grand': {'id': 1, 'login': 'test-login-1', 'role_id': 2},
    'role': ROLE_NANNY,
    'subsystem': SUBSYSTEM_NANNY,
    'related_slugs': [],
}


@pytest.fixture(name='data_fill', autouse=True)
async def _data_fill(add_subsystem, add_role, add_grand):
    nanny_id = await add_subsystem('nanny')
    nanny_root_name = ('nanny', 'няня')
    nanny_root_help = ('nanny help', 'няня помощь')
    await add_role(
        'nanny_root',
        '1',
        'namespace',
        nanny_id,
        nanny_root_name,
        nanny_root_help,
    )
    project_role_id = await add_role(
        'nanny_root',
        '1',
        'project',
        nanny_id,
        nanny_root_name,
        nanny_root_help,
    )
    await add_grand('test-login-1', project_role_id)
    await add_grand('test-login-2', project_role_id)
    await add_grand('test-login-3', project_role_id)

    clown_id = await add_subsystem('internal')
    deploy_name = ('deploy approve', 'ок выкатки')
    deploy_help = ('Allows to approve release', 'Даёт право на аппрув релиза')
    deploy_role_id = await add_role(
        'deploy_approve', '1', 'service', clown_id, deploy_name, deploy_help,
    )
    await add_grand('test-login-1', deploy_role_id)
    await add_grand('test-login-4', deploy_role_id)

    write_id = await add_role(
        ROLE_TEST_ADMIN['slug'],
        '1',
        'namespace',
        clown_id,
        ('write', 'запись'),
        ('write', 'запись'),
    )
    write_id_2 = await add_role(
        ROLE_SERVICE_RESPONSIBLE['slug'],
        '2',
        'namespace',
        clown_id,
        ('even more write', 'топовая запись'),
        ('even more write', 'топовая запись'),
    )
    await add_role(
        ROLE_TASK_MANAGER['slug'],
        '1',
        'namespace',
        clown_id,
        ('read', 'чтение'),
        ('read', 'чтение'),
    )
    await add_role(
        ROLE_TEST_USER['slug'],
        '1',
        'namespace',
        clown_id,
        ('basic', 'базовая'),
        ('basic', 'базовая'),
    )
    await add_grand('vokhcuhza', write_id)
    await add_grand('vokhcuhza', write_id_2)


async def test_retrieve(grands_retrieve):
    response = await grands_retrieve()
    data = await response.json()
    assert response.status == 200, data
    assert data == {
        'grands': [
            GRAND_7,
            GRAND_6,
            GRAND_5,
            GRAND_4,
            GRAND_3,
            GRAND_2,
            GRAND_1,
        ],
    }


async def test_filter_login(grands_retrieve):
    response = await grands_retrieve(filters={'login': 'test-login-1'})
    data = await response.json()
    assert response.status == 200, data
    assert data == {'grands': [GRAND_4, GRAND_1]}


async def test_filter_login_and_role(grands_retrieve):
    response = await grands_retrieve(
        filters={'login': 'test-login-1', 'roles': ['deploy_approve']},
    )
    data = await response.json()
    assert response.status == 200, data
    assert data == {'grands': [GRAND_4]}


async def test_cursor(grands_retrieve):
    response = await grands_retrieve(limit=2)
    data = await response.json()
    assert response.status == 200, data
    assert data == {'grands': [GRAND_7, GRAND_6], 'cursor': {'older_than': 6}}


async def test_cursor_end(grands_retrieve):
    response = await grands_retrieve(limit=2, cursor={'older_than': 2})
    data = await response.json()
    assert response.status == 200, data
    assert data == {'grands': [GRAND_1]}


async def test_roles_relation_several_roles(grands_retrieve):
    response = await grands_retrieve(filters={'login': 'vokhcuhza'})
    data = await response.json()
    assert response.status == 200, data
    assert data == {'grands': [GRAND_7, GRAND_6]}


async def test_related_role(grands_retrieve):
    response = await grands_retrieve(
        filters={'related_role': 'test_service_responsible'},
    )
    data = await response.json()
    assert response.status == 200, data
    assert data == {'grands': [GRAND_7, GRAND_6]}


async def test_external_refs(grands_retrieve):
    response = await grands_retrieve(
        filters={
            'references': [
                {'type': 'namespace', 'external_slug': '1'},
                {'type': 'service', 'external_slug': '1'},
                {'type': 'project', 'external_slug': 'nonono'},
            ],
        },
    )
    data = await response.json()
    assert response.status == 200, data
    assert data == {'grands': [GRAND_6, GRAND_5, GRAND_4]}


async def test_external_refs_and_related_role(grands_retrieve):
    response = await grands_retrieve(
        filters={
            'references': [
                {'type': 'namespace', 'external_slug': '1'},
                {'type': 'service', 'external_slug': '1'},
            ],
            'related_role': 'test_user',
        },
    )
    data = await response.json()
    assert response.status == 200, data
    assert data == {'grands': [GRAND_6]}
