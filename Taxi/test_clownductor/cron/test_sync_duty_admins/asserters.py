def assert_update_namespace(
        update_namespace_handler, fqdn_map, additions, removes=None,
):
    removes = iter(removes or [[], [], [], []])
    additions = iter(additions or [['some_admin'], ['some_admin'], [], []])
    call_num = 0
    while update_namespace_handler.has_calls:
        call = update_namespace_handler.next_call()
        body = call['request'].json
        supers = fqdn_map.pop(body['meta']['id'])

        for to_remove in next(removes):
            supers.remove(to_remove)
        supers.extend(next(additions))
        supers.sort()
        expected = {
            'id': body['meta']['id'],
            'auth': {
                'type': 'STAFF',
                'staff': {'owners': {'logins': supers, 'groupIds': ['50889']}},
            },
        }
        err_msg = (
            f'failed on {call_num}, id: {body["meta"]["id"]}, '
            f'{body["meta"]} != {expected}'
        )
        assert body['meta'] == expected, err_msg
        call_num += 1
    assert not fqdn_map


def assert_get_namespace(get_namespace_handler):
    assert get_namespace_handler.times_called == 3
    fqdns = {
        'test-service-1.taxi.yandex.net',
        'test-service-1.taxi.tst.yandex.net',
        'test-service-2.taxi.yandex.net',
    }

    while get_namespace_handler.has_calls:
        call = get_namespace_handler.next_call()
        fqdns.remove(call['request'].json['id'])
    assert not fqdns


def assert_abc_members(abc_members_handler, with_project_owners: bool):
    post_count = 3 if with_project_owners else 2
    post_admin_count = 2
    check_retrieve_count = 5
    assert abc_members_handler.times_called == (
        (post_count + post_admin_count + (1 if with_project_owners else 0))
        * check_retrieve_count
    ), 'abc_members_handler calls miss count'

    for _ in range(check_retrieve_count):
        call = abc_members_handler.next_call()
        request = call['request']
        assert request.query['service__is_exportable'] == 'true,false'
        assert request.query['service'] == '1337'
        assert request.query['role__in'] == '1259'
        assert request.query['fields'] == 'person.login,id'

        call = abc_members_handler.next_call()
        request = call['request']
        assert request.method == 'GET'

        if with_project_owners:
            admins = iter(['project_login_21'])
            call = abc_members_handler.next_call()
            request = call['request']
            assert request.method == 'POST'
            assert request.json == {
                'service': 1337,
                'person': next(admins),
                'role': 1258,
            }

        persons_ = [
            'd1mbas-mdb',
            'd1mbas-mdb-super',
            'test_maintainers_21',
            'test_maintainers_22',
        ]
        if with_project_owners:
            persons_.insert(2, 'project_login_21')

        persons = iter(persons_)
        for _ in range(post_count):
            call = abc_members_handler.next_call()
            request = call['request']
            assert request.method == 'POST'
            assert request.json == {
                'service': 1337,
                'person': next(persons),
                'role': 1259,
            }

    assert not abc_members_handler.has_calls


def assert_abc_delete_members(
        abc_delete_member_handler, delete_enabled, duty_service_die,
):
    if duty_service_die or not delete_enabled:
        assert abc_delete_member_handler.times_called == 0
        return
    assert abc_delete_member_handler.times_called == 35
    assert abc_delete_member_handler.deleted_member_ships == {2, 3, 4, 5}


def assert_nanny_attrs(
        nanny_mock,
        added,
        removes=None,
        expected_logins=None,
        expected_groups=None,
        developers=None,
        evicters=None,
):
    assert nanny_mock.times_called == 2
    call = nanny_mock.next_call()
    assert call['request'].method == 'GET'

    request = nanny_mock.next_call()['request']
    assert request.method == 'PUT'
    assert request.json['comment'] == 'Sync duty admins'
    request_logins = request.json['content']['owners']['logins']
    expected_logins = expected_logins or ['test-nanny-1', 'test-nanny-2']
    expected_logins.append('robot-taxi-clown')
    expected_logins += added
    for to_remove in removes or []:
        expected_logins.remove(to_remove)
    assert request_logins == sorted(
        expected_logins,
    ), f'{request_logins}, {request.url}'
    request_groups = request.json['content']['owners']['groups']
    if expected_groups is None:
        expected_groups = []
    assert (
        request_groups == expected_groups
    ), f'{request_groups}, {request.url}'

    requested_developers = request.json['content']['developers']
    if developers is not None:
        assert (
            requested_developers == developers
        ), f'{requested_developers}, {request.url}'

    requested_evicters = request.json['content']['evicters']
    if evicters is not None:
        assert (
            requested_evicters == evicters
        ), f'{requested_evicters}, {request.url}'


def nanny_attrs_get(content_logins=None):
    response = {
        '_id': 'hrb4uavyouhlmdpu6tzucae3',
        'change_info': {
            'author': 'karachevda',
            'comment': 'Initial commit',
            'ctime': 1558088809784,
        },
        'content': {
            'owners': {
                'groups': ['1'],
                'logins': ['test-nanny-1', 'test-nanny-2'],
            },
        },
    }
    if content_logins:
        response['content']['owners']['logins'] = content_logins
    return response


def assert_balancers(balancers_get_handler):
    times_called = 4
    assert balancers_get_handler.times_called == times_called
    service_ids = {'1', '2', '6', '11'}

    for _ in range(times_called):
        call = balancers_get_handler.next_call()
        service_ids.remove(call['request'].query['service_id'])

    assert not service_ids


def assert_duty_group(duty_group_handler):
    assert duty_group_handler.times_called == 2
    group_ids = {'1b69be79c5755f678048a169', '2b69be79c5755f678048a169'}

    call = duty_group_handler.next_call()
    group_ids.remove(call['request'].query['group_id'])

    call = duty_group_handler.next_call()
    group_ids.remove(call['request'].query['group_id'])

    assert not group_ids
