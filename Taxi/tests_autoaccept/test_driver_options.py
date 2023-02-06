import pytest

from tests_autoaccept import utils as test_utils


@pytest.mark.pgsql(
    'autoaccept', files=['driver_option.sql', 'driver_option_value.sql'],
)
@pytest.mark.config(
    AUTOACCEPT_OPTION_OVERRIDE_BY_DRIVER_TAGS=[
        {
            'rule': {'any_of': ['driver_fix']},
            'value': [
                {'name': 'name4', 'visible': True},
                {'name': 'name0', 'checked': False, 'enabled': False},
            ],
        },
    ],
)
async def test_driver_options_list(taxi_autoaccept, load_json):
    response = await taxi_autoaccept.get(
        'driver/v1/autoaccept/v1/options',
        headers=test_utils.get_auth_headers('dbid0', 'uuid0'),
    )

    assert response.status_code == 200
    expected_response = load_json('get_response.json')

    def sort_by_id(x):
        return sorted(x['ui']['items'], key=lambda el: el['id'])

    assert sort_by_id(response.json()) == sort_by_id(expected_response)


@pytest.mark.pgsql(
    'autoaccept', files=['driver_option.sql', 'driver_option_value.sql'],
)
async def test_driver_options_update(taxi_autoaccept, pgsql, load_json):
    json_body = {
        'options': [
            {'id': '3f333df6-90a4-4fda-8dd3-9485d27cee36', 'checked': False},
            {'id': '0e37df36-f698-11e6-8dd4-cb9ced3df976', 'checked': True},
        ],
    }
    response = await taxi_autoaccept.post(
        'driver/v1/autoaccept/v1/options',
        json=json_body,
        headers=test_utils.get_auth_headers('dbid0', 'uuid0'),
    )

    assert response.status_code == 200
    expected_response = load_json('post_response.json')
    assert response.json() == expected_response

    cursor = pgsql['autoaccept'].cursor()
    cursor.execute(
        'select park_id, driver_profile_id, option_id, checked '
        'from autoaccept.driver_option_value order by option_id',
    )
    colnames = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    option_values = [dict(zip(colnames, row)) for row in rows]

    assert option_values == [
        {
            'park_id': 'dbid0',
            'driver_profile_id': 'uuid0',
            'option_id': '0e37df36-f698-11e6-8dd4-cb9ced3df976',
            'checked': True,
        },
        {
            'park_id': 'dbid0',
            'driver_profile_id': 'uuid0',
            'option_id': '3f333df6-90a4-4fda-8dd3-9485d27cee36',
            'checked': False,
        },
        {
            'park_id': 'dbid0',
            'driver_profile_id': 'uuid0',
            'option_id': '40e6215d-b5c6-4896-987c-f30f3678f608',
            'checked': False,
        },
        {
            'park_id': 'dbid0',
            'driver_profile_id': 'uuid0',
            'option_id': 'ea6dd426-cc33-40bf-a354-0c6ec7ae449a',
            'checked': True,
        },
    ]


@pytest.mark.pgsql('autoaccept', files=['driver_option.sql'])
@pytest.mark.config(AUTOACCEPT_TAGS_UPLOAD_ENABLED=True)
async def test_driver_options_tags_upload(taxi_autoaccept, mockserver):
    data = {
        'request': [
            [{'id': '6ecd8c99-4036-403d-bf84-cf8400f67836', 'checked': False}],
            [
                {
                    'id': '3f333df6-90a4-4fda-8dd3-9485d27cee36',
                    'checked': True,
                },
                {
                    'id': '0e37df36-f698-11e6-8dd4-cb9ced3df976',
                    'checked': True,
                },
            ],
            [
                {
                    'id': '3f333df6-90a4-4fda-8dd3-9485d27cee36',
                    'checked': False,
                },
                {
                    'id': '0e37df36-f698-11e6-8dd4-cb9ced3df976',
                    'checked': False,
                },
            ],
            [
                {
                    'id': '40e6215d-b5c6-4896-987c-f30f3678f608',
                    'checked': True,
                },
                {
                    'id': '0e37df36-f698-11e6-8dd4-cb9ced3df976',
                    'checked': False,
                },
            ],
        ],
        'tags_response': [
            {'append': [], 'remove': ['autoaccept_name4']},
            {'append': ['autoaccept_name0', 'autoaccept_name1'], 'remove': []},
            {'append': [], 'remove': ['autoaccept_name0', 'autoaccept_name1']},
            {'append': ['autoaccept_name3'], 'remove': ['autoaccept_name1']},
        ],
    }

    @mockserver.json_handler('/tags/v2/upload')
    def _v2_upload(request):
        append = []
        remove = []

        for tag in request.json.get('append', [{'tags': []}])[0]['tags']:
            append.append(tag['name'])
        for tag in request.json.get('remove', [{'tags': []}])[0]['tags']:
            remove.append(tag['name'])

        assert data['tags_response'][iteration]['append'] == append
        assert data['tags_response'][iteration]['remove'] == remove

        return mockserver.make_response(status=200)

    for iteration in range(len(data['request'])):
        response = await taxi_autoaccept.post(
            'driver/v1/autoaccept/v1/options',
            json={'options': data['request'][iteration]},
            headers=test_utils.get_auth_headers('dbid0', 'uuid0'),
        )
        assert response.status_code == 200
