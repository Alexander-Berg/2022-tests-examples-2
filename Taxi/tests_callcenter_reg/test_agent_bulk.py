import pytest


@pytest.mark.parametrize(
    ['agents', 'expected_code', 'expected_data', 'expected_db_data'],
    (
        pytest.param(
            [{'sip_username': '1000000000', 'yandex_uid': '1000000000000000'}],
            200,
            {'1000000000000000:1000000000': 'ok'},
            [('1000000000', '1000000000000000')],
            id='add_agent',
        ),
        pytest.param(
            [
                {
                    'sip_username': '1000000000',
                    'yandex_uid': '1000000000000000',
                },
                {
                    'sip_username': '1000000001',
                    'yandex_uid': '1000000000000001',
                },
            ],
            200,
            {
                '1000000000000000:1000000000': 'ok',
                '1000000000000001:1000000001': 'ok',
            },
            [
                ('1000000000', '1000000000000000'),
                ('1000000001', '1000000000000001'),
            ],
            id='add_agents',
        ),
        pytest.param(
            [
                {
                    'sip_username': '1000000000',
                    'yandex_uid': '1000000000000000',
                },
                {
                    'sip_username': '1000000001',
                    'yandex_uid': '1000000000000001',
                },
                {
                    'sip_username': '1000010001',
                    'yandex_uid': '1000000000010001',
                },
                {
                    'sip_username': '1000010002',
                    'yandex_uid': '1000000000010002',
                },
                # sip_username in use
                {
                    'sip_username': '1000010003',
                    'yandex_uid': '1000000000000003',
                },
                # yandex_uid in use
                {
                    'sip_username': '1000000004',
                    'yandex_uid': '1000000000010004',
                },
            ],
            200,
            {
                '1000000000000000:1000000000': 'ok',
                '1000000000000001:1000000001': 'ok',
                '1000000000010001:1000010001': 'already_added',
                '1000000000010002:1000010002': 'already_added',
                '1000000000000003:1000010003': 'sip_username_in_use',
                '1000000000010004:1000000004': 'yandex_uid_in_use',
            },
            [
                ('1000000000', '1000000000000000'),
                ('1000000001', '1000000000000001'),
                ('1000010001', '1000000000010001'),
                ('1000010002', '1000000000010002'),
                ('1000010003', '1000000000010003'),
                ('1000010004', '1000000000010004'),
            ],
            id='add_agents_with_already_added',
            marks=[pytest.mark.pgsql('callcenter_reg', files=['agent.sql'])],
        ),
    ),
)
async def test_add_bulk(
        taxi_callcenter_reg,
        agents,
        expected_code,
        expected_data,
        expected_db_data,
        pgsql,
):
    response = await taxi_callcenter_reg.post(
        '/v1/agent/add_bulk', {'agents': agents},
    )
    assert response.status_code == expected_code
    res = {}
    for val in response.json()['results']:
        res[f'{val["yandex_uid"]}:{val["sip_username"]}'] = val['code']
    assert res == expected_data
    cursor = pgsql['callcenter_reg'].cursor()
    query = (
        'SELECT sip_username, yandex_uid '
        'FROM callcenter_reg.agent ORDER BY sip_username'
    )
    cursor.execute(query)
    db_res = cursor.fetchall()
    assert db_res == expected_db_data


@pytest.mark.pgsql('callcenter_reg', files=['agent.sql'])
@pytest.mark.parametrize(
    ['yandex_uids', 'expected_code', 'expected_data', 'expected_db_data'],
    (
        pytest.param(
            ['1000000000010001'],
            200,
            {'1000000000010001': 'ok'},
            [
                ('1000010002', '1000000000010002'),
                ('1000010003', '1000000000010003'),
                ('1000010004', '1000000000010004'),
            ],
            id='delete_agent',
        ),
        pytest.param(
            ['1000000000010001', '1000000000010002'],
            200,
            {'1000000000010001': 'ok', '1000000000010002': 'ok'},
            [
                ('1000010003', '1000000000010003'),
                ('1000010004', '1000000000010004'),
            ],
            id='delete_agents',
        ),
        pytest.param(
            [
                '1000000000000000',
                '1000000000000001',
                '1000000000010001',
                '1000000000010002',
            ],
            200,
            {
                '1000000000000000': 'already_deleted',
                '1000000000000001': 'already_deleted',
                '1000000000010001': 'ok',
                '1000000000010002': 'ok',
            },
            [
                ('1000010003', '1000000000010003'),
                ('1000010004', '1000000000010004'),
            ],
            id='delete_agents_with_already_deleted',
        ),
    ),
)
async def test_delete_bulk(
        taxi_callcenter_reg,
        yandex_uids,
        expected_code,
        expected_data,
        expected_db_data,
        pgsql,
):
    response = await taxi_callcenter_reg.post(
        '/v1/agent/delete_bulk', {'yandex_uids': yandex_uids},
    )
    assert response.status_code == expected_code
    res = {}
    for val in response.json()['results']:
        res[val['yandex_uid']] = val['code']
    assert res == expected_data
    cursor = pgsql['callcenter_reg'].cursor()
    query = (
        'SELECT sip_username, yandex_uid '
        'FROM callcenter_reg.agent ORDER BY sip_username'
    )
    cursor.execute(query)
    db_res = cursor.fetchall()
    assert db_res == expected_db_data
