import pytest


NON_EXISTENT_OPTION_ID = '03c75720-726c-4c21-b8fc-7bc13913fb32'


@pytest.mark.pgsql('autoaccept', files=['driver_option.sql'])
async def test_admin_driver_options_get(taxi_autoaccept, load_json):
    response = await taxi_autoaccept.get('v1/admin/driver-options')
    expected_response = load_json('admin_driver_options_get.json')

    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.parametrize(
    'request_json, status_code',
    [
        ({'name': 'new_option'}, 201),
        (
            {
                'name': 'new_option',
                'checked_by_default': True,
                'visible': True,
                'enabled': False,
            },
            201,
        ),
        ({'name': 'name0'}, 500),  # Non-unique name
        ({'name': 'non conforming name'}, 500),
    ],
)
@pytest.mark.pgsql('autoaccept', files=['driver_option.sql'])
async def test_admin_driver_options_post(
        taxi_autoaccept, load_json, request_json, status_code,
):
    post_response = await taxi_autoaccept.post(
        'v1/admin/driver-options', json=request_json,
    )
    assert post_response.status_code == status_code

    if status_code != 201:
        return

    assert 'id' in post_response.json()

    new_option = {
        'id': post_response.json()['id'],
        'name': request_json['name'],
        'checked_by_default': (
            request_json['checked_by_default']
            if 'checked_by_default' in request_json
            else False
        ),
        'visible': (
            request_json['visible'] if 'visible' in request_json else True
        ),
        'enabled': (
            request_json['enabled'] if 'enabled' in request_json else True
        ),
    }

    expected_response = load_json('admin_driver_options_get.json')
    expected_response['driver_options'].append(new_option)

    get_response = await taxi_autoaccept.get('v1/admin/driver-options')

    assert get_response.status_code == 200
    assert get_response.json() == expected_response


def _find(lst, key, value):
    for i, dic in enumerate(lst):
        if dic[key] == value:
            return i
    return -1


def _splice(lst, pos, other):
    if pos == other:
        return lst
    if pos < other:
        return lst[0:pos] + lst[pos + 1 : other] + [lst[pos]] + lst[other:]

    return lst[0:other] + [lst[pos]] + lst[other:pos] + lst[pos + 1 :]


@pytest.mark.parametrize(
    'request_json, status_code',
    [
        (
            {'id': '3f333df6-90a4-4fda-8dd3-9485d27cee36', 'name': 'new_name'},
            200,
        ),
        (
            {'id': 'ea6dd426-cc33-40bf-a354-0c6ec7ae449a', 'visible': False},
            200,
        ),
        (
            {
                'id': '3f333df6-90a4-4fda-8dd3-9485d27cee36',
                'next_id': '40e6215d-b5c6-4896-987c-f30f3678f608',
            },
            200,
        ),
        ({'id': '3f333df6-90a4-4fda-8dd3-9485d27cee36', 'next_id': ''}, 200),
        ({'id': NON_EXISTENT_OPTION_ID, 'name': 'new_name'}, 404),
        (
            {
                'id': '3f333df6-90a4-4fda-8dd3-9485d27cee36',
                'next_id': NON_EXISTENT_OPTION_ID,
            },
            404,
        ),
        (
            {'id': '3f333df6-90a4-4fda-8dd3-9485d27cee36', 'name': 'name2'},
            500,  # Non-unique name
        ),
    ],
)
@pytest.mark.pgsql('autoaccept', files=['driver_option.sql'])
async def test_admin_driver_options_put(
        taxi_autoaccept, load_json, request_json, status_code,
):
    put_response = await taxi_autoaccept.put(
        'v1/admin/driver-options', json=request_json,
    )
    assert put_response.status_code == status_code

    if status_code != 200:
        return

    expected_response = load_json('admin_driver_options_get.json')

    pos = _find(expected_response['driver_options'], 'id', request_json['id'])

    for key in request_json:
        if key != 'next_id':
            expected_response['driver_options'][pos][key] = request_json[key]

    if 'next_id' in request_json:
        other = len(expected_response['driver_options'])
        if request_json['next_id'] != '':
            other = _find(
                expected_response['driver_options'],
                'id',
                request_json['next_id'],
            )
        expected_response['driver_options'] = _splice(
            expected_response['driver_options'], pos, other,
        )

    get_response = await taxi_autoaccept.get('v1/admin/driver-options')

    assert get_response.status_code == 200
    assert get_response.json() == expected_response


@pytest.mark.parametrize(
    'option_id, status_code',
    [
        ('3f333df6-90a4-4fda-8dd3-9485d27cee36', 200),
        ('ea6dd426-cc33-40bf-a354-0c6ec7ae449a', 200),
        ('6ecd8c99-4036-403d-bf84-cf8400f67836', 200),
        (NON_EXISTENT_OPTION_ID, 404),
    ],
)
@pytest.mark.pgsql(
    'autoaccept', files=['driver_option.sql', 'driver_option_value.sql'],
)
async def test_admin_driver_options_delete(
        taxi_autoaccept, load_json, option_id, status_code,
):
    del_response = await taxi_autoaccept.delete(
        'v1/admin/driver-options', params={'id': option_id},
    )
    assert del_response.status_code == status_code

    response = load_json('admin_driver_options_get.json')

    expected_driver_options = []

    for option in response['driver_options']:
        if option['id'] != option_id:
            expected_driver_options.append(option)

    get_response = await taxi_autoaccept.get('v1/admin/driver-options')

    assert get_response.status_code == 200
    assert 'driver_options' in get_response.json()
    assert get_response.json()['driver_options'] == expected_driver_options
