import datetime

from clowny_search.generated.cron import run_cron  # noqa: I100


HOST_0 = 'taxi-clowny-search-7504490365-1.man.yp-c.yandex.net'

PILORAMA_10_11 = {
    'hostname': HOST_0,
    'cluster-name': 'beta',
    'package-name': 'pilorama',
    'package-version': '2.0',
}

HOST_1 = 'taxi-clowny-search-3805920270-2.man.yp-c.yandex.net'

PILORAMA_11_11 = {
    'hostname': HOST_1,
    'cluster-name': 'beta',
    'package-name': 'pilorama',
    'package-version': '1.0',
}


def sidecar_key(data: dict):
    return (
        data['hostname'],
        data['cluster-name'],
        data['package-name'],
        data['package-version'],
    )


def assert_eq(dc1, dc2) -> None:
    assert sorted(dc1, key=sidecar_key) == sorted(dc2, key=sidecar_key)


async def test_empty(mockserver, search, import_clown):
    @mockserver.json_handler('/clownductor/api/projects')
    async def mock_cd_projects(request):
        return []

    await import_clown()
    assert await search() == []

    assert mock_cd_projects.times_called == 1


async def test_report_happy_path(report, search, mock_clown):
    fqdn = HOST_1

    # empty search result as we have no imported data
    assert await search() == []

    # push data
    await report(package_name='pilorama', fqdn=fqdn, package_version='1.0')

    assert_eq(await search(), [PILORAMA_11_11])


async def test_report_unregistered(report, search, mock_clown):
    # push data
    await report(fqdn='unknown.com')

    # empty search result as we don't know anything about 'unknown.com'
    assert await search() == []


async def test_report_multiple(report, search, mock_clown):
    # push data
    await report(fqdn=HOST_1)
    await report(fqdn=HOST_0, package_version='2.0')

    # empty search result as we don't know anything about 'unknown.com'
    result = await search()

    expect = [PILORAMA_11_11, PILORAMA_10_11]
    assert_eq(result, expect)


async def test_report_update(report, search, mock_clown):
    fqdn = HOST_1

    # push data
    await report(package_name='pilorama', fqdn=fqdn, package_version='1.0')
    await report(package_name='pilorama', fqdn=fqdn, package_version='1.1')
    assert await search() == [
        {
            'package-name': 'pilorama',
            'package-version': '1.1',
            'hostname': fqdn,
            'cluster-name': 'beta',
        },
    ]


async def test_arg_sidecar_name(report, search, mock_clown):
    # push data
    await report(fqdn=HOST_1)
    await report(fqdn=HOST_0, package_version='2.0')

    result = await search(package_name='pilorama')
    expect = [PILORAMA_11_11, PILORAMA_10_11]
    assert_eq(result, expect)

    result = await search(package_name='ratelimiter')
    assert result == []


async def test_arg_sidecar_version(report, search, mock_clown):
    # push data
    await report(fqdn=HOST_1)
    await report(fqdn=HOST_0, package_version='2.0')

    result = await search(package_version='1.0')
    assert_eq(result, [PILORAMA_11_11])


async def test_arg_sidecar_fqdn(report, search, mock_clown):
    # push data
    await report(fqdn=HOST_1)
    await report(fqdn=HOST_0, package_version='2.0')

    result = await search(fqdn=HOST_1)
    assert_eq(result, [PILORAMA_11_11])


async def test_arg_sidecar_cluster(report, search, mock_clown):
    # push data
    await report(fqdn=HOST_1)
    await report(fqdn=HOST_0, package_version='2.0')

    result = await search(cluster_name='beta')
    assert_eq(result, [PILORAMA_11_11, PILORAMA_10_11])

    result = await search(cluster_name='alpha')
    assert_eq(result, [])


async def test_pagination_1page(report, cs_web, mock_clown):
    await report(fqdn=HOST_1)
    await report(fqdn=HOST_0, package_version='2.0')

    # page-size == count(*) == 2
    response = await cs_web.package_search(page_size=2)
    body = await response.json()
    assert body['results'] == [PILORAMA_11_11, PILORAMA_10_11]
    cursor = body['cursor']

    response = await cs_web.package_search(cursor=cursor, page_size=2)
    body = await response.json()
    assert body == {'results': []}


async def test_pagination_2page(report, cs_web, mock_clown):
    await report(fqdn=HOST_1)
    await report(fqdn=HOST_0, package_version='2.0')

    # page-size == 1 == count(*)/2
    response = await cs_web.package_search(page_size=1)
    body = await response.json()
    assert body['results'] == [PILORAMA_11_11]
    cursor = body['cursor']

    response = await cs_web.package_search(cursor=cursor, page_size=1)
    body = await response.json()
    assert body['results'] == [PILORAMA_10_11]
    cursor = body['cursor']

    response = await cs_web.package_search(cursor=cursor, page_size=1)
    body = await response.json()
    assert body == {'results': []}


async def test_query_and_cursor(cs_web):
    response = await cs_web.package_search(
        query={'fqdn': 'example.com'}, cursor='abc',
    )
    assert response.status == 400
    assert await response.json() == {
        'code': 'CURSOR_AND_QUERY',
        'message': '"cursor" and "query" are mutually exclusive',
    }


async def test_query_and_cursor_empty(cs_web):
    response = await cs_web.package_search(query={}, cursor='')
    assert response.status == 400
    assert await response.json() == {
        'code': 'CURSOR_AND_QUERY',
        'message': '"cursor" and "query" are mutually exclusive',
    }


async def test_invalid_cursor(cs_web):
    response = await cs_web.package_search(cursor='abc')
    assert response.status == 400
    assert await response.json() == {
        'code': 'INVALID_CURSOR',
        'message': 'cursor value is not parseable',
    }


async def test_outdated_report(
        taxi_clowny_search_web, report, search, mock_clown, mocked_time,
):
    fqdn = HOST_1

    # set() changes mocked time for web, but not for cron
    mocked_time.set(datetime.datetime.now() - datetime.timedelta(days=10))

    await report(package_name='pilorama', fqdn=fqdn, package_version='1.0')
    assert_eq(await search(), [PILORAMA_11_11])

    # cron is to delete outdated 'pilorama' version
    await run_cron.main(['clowny_search.crontasks.import_clown'])
    assert_eq(await search(), [])
