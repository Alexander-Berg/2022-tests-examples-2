async def test_empty(
        mockserver, taxi_clowny_search_web, mock_clown, import_clown,
):
    @mockserver.json_handler('/clownductor/api/projects')
    async def mock_cd_projects(request):
        return []

    await import_clown()
    assert mock_cd_projects.times_called == 1
    response = await taxi_clowny_search_web.post(
        '/v1/clusters/list', headers={'content-type': 'application/json'},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {'clusters': []}

    response = await taxi_clowny_search_web.post(
        '/v1/hosts/list', headers={'content-type': 'application/json'},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {'hosts': []}


async def test_nonempty(
        mockserver, taxi_clowny_search_web, mock_clown, import_clown,
):
    await import_clown()
    response = await taxi_clowny_search_web.post(
        '/v1/clusters/list', headers={'content-type': 'application/json'},
    )
    assert response.status == 200
    body = await response.json()
    assert set(body['clusters']) == {'alpha', 'beta', 'gamma', 'delta'}

    response = await taxi_clowny_search_web.post(
        '/v1/hosts/list', headers={'content-type': 'application/json'},
    )
    assert response.status == 200
    body = await response.json()
    assert set(body['hosts']) == {
        'taxi-clowny-search-1540549476-1.man.yp-c.yandex.net',
        'taxi-clowny-search-1540549476-2.man.yp-c.yandex.net',
        'taxi-clowny-search-2532318393-1.man.yp-c.yandex.net',
        'taxi-clowny-search-2532318393-2.man.yp-c.yandex.net',
        'taxi-clowny-search-2916928632-1.man.yp-c.yandex.net',
        'taxi-clowny-search-2916928632-2.man.yp-c.yandex.net',
        'taxi-clowny-search-3805920270-1.man.yp-c.yandex.net',
        'taxi-clowny-search-3805920270-2.man.yp-c.yandex.net',
        'taxi-clowny-search-5239119571-1.man.yp-c.yandex.net',
        'taxi-clowny-search-5239119571-2.man.yp-c.yandex.net',
        'taxi-clowny-search-6230888488-1.man.yp-c.yandex.net',
        'taxi-clowny-search-6230888488-2.man.yp-c.yandex.net',
        'taxi-clowny-search-6615498727-1.man.yp-c.yandex.net',
        'taxi-clowny-search-6615498727-2.man.yp-c.yandex.net',
        'taxi-clowny-search-7504490365-1.man.yp-c.yandex.net',
        'taxi-clowny-search-7504490365-2.man.yp-c.yandex.net',
    }


async def test_packages(
        mockserver, taxi_clowny_search_web, mock_clown, import_clown, report,
):

    await import_clown()
    response = await taxi_clowny_search_web.post(
        '/v1/packages/list', headers={'content-type': 'application/json'},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {'packages': []}

    await report(
        package_name='pilorama', fqdn='example.com', package_version='1.0',
    )
    response = await taxi_clowny_search_web.post(
        '/v1/packages/list', headers={'content-type': 'application/json'},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {'packages': ['pilorama']}
