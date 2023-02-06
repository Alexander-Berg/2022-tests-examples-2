import pytest

URL = '/v1/tariff_settings/copy/draft/apply'

pytestmark = pytest.mark.config(  # pylint: disable=invalid-name
    TARIFF_SETTINGS_COPY_FIELDS={
        'zone': {
            'required': ['required_1'],
            'not_required': ['not_required_copy_1', 'not_required_delete_1'],
        },
        'categories_common': {
            'required': ['required_2'],
            'not_required': ['not_required_copy_2', 'not_required_delete_2'],
        },
        'category': {
            'required': ['n', 'required_3'],
            'not_required': [
                'not_required_copy_3',
                'not_required_delete_3',
                'tc',
                'client_requirements',
            ],
        },
        'outer_category_settings': ['setting1'],
    },
)


def _check_copy_fields(
        ts_destination, copy_zone_settings, copy_categories_common, categories,
):
    if copy_zone_settings:
        assert ts_destination['required_1'] == 'required_1'
        assert ts_destination['not_required_copy_1'] == 'not_required_1'
        assert 'not_required_delete_1' not in ts_destination
    else:
        assert ts_destination['required_1'] == 'old_value'
        assert ts_destination['not_required_copy_1'] == 'old_value'
        assert 'not_required_delete_1' in ts_destination

    if copy_categories_common:
        assert ts_destination['required_2'] == 'required_2'
        assert ts_destination['not_required_copy_2'] == 'not_required_2'
        assert 'not_required_delete_2' not in ts_destination
    else:
        assert ts_destination['required_2'] == 'old_value'
        assert ts_destination['not_required_copy_2'] == 'old_value'
        assert 'not_required_delete_2' in ts_destination

    for category in ts_destination['s']:
        if categories:
            if category['n'] in categories:
                assert category['required_3'] == 'required_3'
                assert category['not_required_copy_3'] == 'not_required_3'
                assert 'not_required_delete_3' not in category
                assert category['tc'] == []
            assert ts_destination['setting1']['econom'] == 'value_for_econom'
            assert 'courier' not in ts_destination['setting1']
        else:
            if category['n'] in categories:
                assert category['required_3'] == 'old_value'
                assert category['not_required_copy_3'] == 'old_value'
                assert 'not_required_delete_3' in category
            assert ts_destination['setting1']['courier'] == 'value_for_courier'
            assert 'econom' not in ts_destination['setting1']


@pytest.mark.parametrize(
    ('copy_zone_settings', 'copy_categories_common', 'categories'),
    (
        (True, False, []),
        (False, True, []),
        (False, False, ['econom', 'courier']),
        (True, True, ['econom', 'courier']),
    ),
)
@pytest.mark.parametrize('status', ('succeeded', 'partially_completed'))
async def test_normal_work(
        web_app_client,
        mongo,
        copy_zone_settings,
        copy_categories_common,
        categories,
        status,
):
    zones_count = 2
    if status == 'partially_completed':
        zones_count += 1
        categories.append('comfort')
    can_be_copied_zones = []
    for i in range(zones_count):
        zone_name = 'destination' + str(i)
        can_be_copied_zones.append(
            {'zone_name': zone_name, 'categories_to_copy': categories},
        )
    request_body = {
        'zone_from': 'source',
        'can_be_copied_zones': can_be_copied_zones,
        'copy_zone_settings': copy_zone_settings,
        'copy_categories_common': copy_categories_common,
    }
    ts_source_before = await mongo.tariff_settings.find_one({'hz': 'source'})
    response = await web_app_client.post(URL, json=request_body)
    ts_source_after = await mongo.tariff_settings.find_one({'hz': 'source'})

    assert response.status == 200
    content = await response.json()
    assert content['status'] == status
    assert ts_source_after == ts_source_before

    ts_destinations = [
        await mongo.tariff_settings.find_one({'hz': 'destination0'}),
        await mongo.tariff_settings.find_one({'hz': 'destination1'}),
    ]
    if status == 'partially_completed':
        categories.remove('comfort')
    for ts_destination in ts_destinations:
        _check_copy_fields(
            ts_destination,
            copy_zone_settings,
            copy_categories_common,
            categories,
        )


@pytest.mark.parametrize(
    ('request_body', 'response_code', 'response_message'),
    (
        (
            {
                'zone_from': 'source',
                'can_be_copied_zones': [
                    {'zone_name': 'destination0', 'categories_to_copy': []},
                ],
            },
            'empty_request',
            (
                'Should be copy_zone_settings:true or/and '
                'copy_categories_common:true or/and '
                'categories_to_copy has one or more items'
            ),
        ),
        (
            {
                'zone_from': 'source',
                'can_be_copied_zones': [
                    {
                        'zone_name': 'destination0',
                        'categories_to_copy': ['econom'],
                    },
                    {
                        'zone_name': 'destination0',
                        'categories_to_copy': ['econom'],
                    },
                ],
            },
            'duplicate_zones',
            'Duplicate of zones to which it is copied',
        ),
        (
            {
                'zone_from': 'source',
                'can_be_copied_zones': [
                    {
                        'zone_name': 'destination0',
                        'categories_to_copy': ['econom', 'econom'],
                    },
                ],
            },
            'duplicate_categories',
            'categories_to_copy has duplicate items',
        ),
        (
            {
                'zone_from': 'source',
                'can_be_copied_zones': [
                    {'zone_name': 'source', 'categories_to_copy': ['econom']},
                ],
            },
            'copy_to_itself',
            'Attempt to copy a zone to itself',
        ),
        (
            {
                'zone_from': 'wrong_source',
                'can_be_copied_zones': [
                    {
                        'zone_name': 'destination0',
                        'categories_to_copy': ['econom'],
                    },
                ],
            },
            'not_source_document',
            'tariff_settings document for zone_from was not found',
        ),
        (
            {
                'zone_from': 'source',
                'can_be_copied_zones': [
                    {
                        'zone_name': 'destination0',
                        'categories_to_copy': ['econom', 'express'],
                    },
                ],
            },
            'not_source_categories',
            (
                'In tariff_settings for zone_from '
                'there are not categories: express'
            ),
        ),
        (
            {
                'zone_from': 'source',
                'can_be_copied_zones': [
                    {
                        'zone_name': 'destination0',
                        'categories_to_copy': ['comfort'],
                    },
                ],
            },
            'cannot_copy',
            'Nothing can be copied',
        ),
        (
            {
                'zone_from': 'without_requariment_fields',
                'can_be_copied_zones': [
                    {'zone_name': 'destination0', 'categories_to_copy': []},
                ],
                'copy_zone_settings': True,
            },
            'no_required_field',
            'No required field required_1 in source zone',
        ),
    ),
)
async def test_fail(
        web_app_client, request_body, response_code, response_message,
):
    response = await web_app_client.post(URL, json=request_body)
    assert response.status == 400
    content = await response.json()
    assert content['code'] == response_code
    assert content['message'] == response_message


async def test_requirements_in_tariff(web_app_client):
    request_body = {
        'zone_from': 'source',
        'can_be_copied_zones': [
            {
                'zone_name': 'without_requariments_in_tariff',
                'categories_to_copy': ['econom', 'courier'],
            },
        ],
        'copy_zone_settings': True,
    }
    response = await web_app_client.post(URL, json=request_body)
    assert response.status == 200
    content = await response.json()
    assert content['status'] == 'partially_completed'
    assert content['problem_details'] == [
        {
            'message': (
                'For category econom in some intervals in tariff '
                'there are no requriments: animaltransport'
            ),
            'zone_name': 'without_requariments_in_tariff',
        },
    ]
