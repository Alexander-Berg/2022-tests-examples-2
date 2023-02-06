import urllib

import pytest

KIBANA_FILTER_NAME = 'kibana_filter'

QUERY_WORD = {'matchstring': 'kibanning'}

QUERY_ANOTHER_WORD = {'matchstring': 'akibanning'}

QUERY_SPACES = {'matchstring': 'kibanning with spaces'}

QUERY_NEWLINES = {'matchstring': 'kibanning \n with \n  new lines'}

QUERY_FIELD = {'field': 'message', 'matchstring': 'Message matchstring'}

Q_C_SET_NO_CGROUP = {None: [QUERY_WORD]}

Q_C_SET_ONE_CGROUP = {'taxi_fake_cgroup': [QUERY_WORD]}

Q_C_SET_TWO_CGROUP = {
    'taxi_fake_cgroup': [QUERY_WORD],
    'taxi_another_fake_cgroup': [QUERY_ANOTHER_WORD],
}

Q_C_SET_MULTIPLE_QUERIES = {
    'taxi_fake_cgroup': [QUERY_WORD, QUERY_ANOTHER_WORD],
}

Q_C_SET_WHATEVER = {
    'taxi_fake_cgroup': [QUERY_WORD, QUERY_ANOTHER_WORD],
    'taxi_another_fake_cgroup': [QUERY_SPACES, QUERY_NEWLINES],
    'taxi_yet_another_fake_cgroup': [QUERY_FIELD],
}

HEADERS = {'X-YaTaxi-Api-Key': 'fake_token', 'X-Yandex-Login': 'testcreator'}


@pytest.mark.parametrize(
    'query', [QUERY_WORD, QUERY_SPACES, QUERY_NEWLINES, QUERY_FIELD],
)
async def test_kibana_line_word(web_app_client, create_filter, query, auth):
    _query = {'rules': [query]}

    await create_filter(_query, 'Very cool kibana filter')

    args = {'mode': 'kibana'}
    await auth()

    response = await web_app_client.get(
        '/v1/combine-filters/?{}'.format(urllib.parse.urlencode(args)),
        headers=HEADERS,
    )

    assert response.status == 200
    content = await response.json()

    assert 'result' in content

    parsed_url = urllib.parse.urlparse(content['result'])

    assert parsed_url.scheme == 'https'
    assert 'kibana' in parsed_url.netloc
    assert 'yandex' in parsed_url.netloc
    assert '_a' in parsed_url.fragment
    assert '_g' in parsed_url.fragment


@pytest.mark.parametrize(
    'query_cgroup_sets',
    [
        Q_C_SET_NO_CGROUP,
        Q_C_SET_ONE_CGROUP,
        Q_C_SET_TWO_CGROUP,
        Q_C_SET_MULTIPLE_QUERIES,
        Q_C_SET_WHATEVER,
    ],
)
async def test_kibana_line_word_cgroup(
        web_app_client, create_filter, query_cgroup_sets, auth,
):
    for cgroup, qset in query_cgroup_sets.items():
        for query in qset:
            _query = {'rules': [query]}

            await create_filter(
                _query, 'Very cool kibana filter', cgroup=cgroup,
            )

    await auth()
    for cgroup in query_cgroup_sets:
        args = {'mode': 'kibana', 'cgroups': [cgroup]}
        if cgroup is None:
            del args['cgroups']
        response = await web_app_client.get(
            '/v1/combine-filters/?{}'.format(urllib.parse.urlencode(args)),
            headers=HEADERS,
        )
        assert response.status == 200

        content = await response.json()
        assert 'result' in content

        parsed_url = urllib.parse.urlparse(content['result'])

        assert parsed_url.scheme == 'https'
        assert 'kibana' in parsed_url.netloc
        assert 'yandex' in parsed_url.netloc
        assert '_a' in parsed_url.fragment
        assert '_g' in parsed_url.fragment


@pytest.mark.parametrize('cgroup_param_name', ['cgroups', 'cgroup'])
async def test_kibana_many_cgroups(
        web_app_client, create_filter, cgroup_param_name, auth,
):

    for cgroup, qset in Q_C_SET_WHATEVER.items():
        for query in qset:
            _query = {'rules': [query]}

            await create_filter(
                _query, 'Very cool kibana filter', cgroup=cgroup,
            )

    cgroups = list(Q_C_SET_WHATEVER.keys())

    args1 = {'mode': 'kibana', cgroup_param_name: cgroups}

    urlargs = {
        'mode': args1['mode'],
        cgroup_param_name: ','.join(args1[cgroup_param_name]),
    }

    param_string = urllib.parse.urlencode(urlargs)

    if cgroup_param_name == 'cgroup':
        _cgroups = [f'cgroup={cgroup}' for cgroup in cgroups]
        param_string = 'mode=kibana&' + '&'.join(_cgroups)

    await auth()
    response = await web_app_client.get(
        '/v1/combine-filters/?{}'.format(param_string), headers=HEADERS,
    )

    content = await response.json()

    for cgroup in args1[cgroup_param_name]:

        for que in Q_C_SET_WHATEVER[cgroup]:
            assert urllib.parse.quote(que['matchstring']) in content['result']

    assert response.status == 200

    content = await response.json()
    assert 'result' in content

    parsed_url = urllib.parse.urlparse(content['result'])

    assert parsed_url.scheme == 'https'
    assert 'kibana' in parsed_url.netloc
    assert 'yandex' in parsed_url.netloc
    assert '_a' in parsed_url.fragment
    assert '_g' in parsed_url.fragment


async def test_kibana_servers(web_app_client, auth):

    args1 = {'mode': 'kibana'}

    urlargs = args1

    await auth()

    response = await web_app_client.get(
        '/v1/combine-filters/?{}'.format(urllib.parse.urlencode(urlargs)),
        headers=HEADERS,
    )

    assert response.status == 200
    content = await response.json()

    assert 'kibana.taxi.yandex-team.ru' in content['result']
