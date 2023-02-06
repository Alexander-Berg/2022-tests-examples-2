import copy

import pytest

URI = '/v1/access-groups/values'
CURSOR = {'greater_than_slug': 'new_cursor'}
HEADERS = {'X-WFM-Domain': 'taxi'}


@pytest.mark.parametrize(
    'groups', [([{'id': 0, 'name': 'name', 'slug': 'slug'}])],
)
async def test_base(taxi_workforce_management_web, mockserver, groups):
    @mockserver.json_handler('/access-control/v1/admin/groups/retrieve/')
    def get_groups(request, *args, **kwargs):
        if request.json.get('cursor', {}).get('greater_than_slug'):
            assert request.json['cursor'] == CURSOR
            return {'cursor': CURSOR, 'groups': []}
        ac_groups = copy.deepcopy(groups)
        for group in ac_groups:
            group['system'] = 'workforce-management'
        return {'cursor': CURSOR, 'groups': ac_groups}

    res = await taxi_workforce_management_web.post(
        URI, json={'limit': 100}, headers=HEADERS,
    )
    assert res.status == 200
    data = await res.json()
    assert data['groups'] == groups
    assert get_groups.times_called
