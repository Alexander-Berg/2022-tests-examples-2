import pytest


DEFAULT_LINKS = [
    ('system_main_role_1', 'system_main_role_1_permission_1'),
    ('system_main_role_2', 'system_main_role_2_permission_1'),
    ('system_main_role_3', 'system_main_role_3_permission_1'),
    ('system_main_role_3', 'system_main_role_3_permission_2'),
    ('system_second_role_1', 'system_second_role_1_2_permission_1'),
    ('system_second_role_2', 'system_second_role_1_2_permission_1'),
    ('system_second_role_2', 'system_second_role_2_permission_1'),
]


@pytest.fixture(name='assert_link_added')
def _assert_link_added(assert_permission_role_links_pg):
    async def _wrapper(added_links):
        links = DEFAULT_LINKS.copy() + added_links
        await assert_permission_role_links_pg(sorted(links))

    return _wrapper


@pytest.fixture(name='assert_link_removed')
def _assert_link_removed(assert_permission_role_links_pg):
    async def _wrapper(removed_links):
        links = set(DEFAULT_LINKS)
        for link in removed_links:
            links.remove(link)
        await assert_permission_role_links_pg(sorted(links))

    return _wrapper


@pytest.fixture(name='links_to_response')
def _links_to_response():
    def _wrapper(links):
        return [
            {'permission_slug': permission_slug, 'role_slug': role_slug}
            for role_slug, permission_slug in links
        ]

    return _wrapper


@pytest.fixture(name='links_to_errors')
def _links_to_errors(links_to_response):
    def _wrapper(links):
        return [
            {
                'code': 'invalid_link',
                'details': {'links': links_to_response(links)},
                'message': 'Permission or role do not exist',
            },
        ]

    return _wrapper


@pytest.fixture(name='assert_link_deleted')
def _assert_link_deleted(assert_permission_role_links_pg):
    async def _wrapper(permission=None):
        links = DEFAULT_LINKS.copy()
        remove_indices = []
        for index, link in enumerate(links):
            _, link_permission = link
            if link_permission == permission:
                remove_indices.append(index)
        for index in reversed(remove_indices):
            del links[index]
        await assert_permission_role_links_pg(sorted(links))

    return _wrapper
