import pytest

ENDPOINT = '/v1/parks-rating/tier-by-clid'


@pytest.mark.pgsql('fleet_reports', files=('dump.sql',))
@pytest.mark.parametrize(
    'req, res',
    [
        ({'clid': 'test_clid_1', 'at': '2021-05-26'}, {'tier': 'weak'}),
        ({'clid': 'test_clid_1', 'at': '2021-05-20'}, {'tier': 'weak'}),
        ({'clid': 'test_clid_1', 'at': '2021-06-19'}, {'tier': 'weak'}),
        ({'clid': 'test_clid_1', 'at': '2021-04-21'}, {'tier': 'bronze'}),
        ({'clid': 'test_clid_2', 'at': '2021-04-26'}, {'tier': 'unknown'}),
        ({'clid': 'test_clid_2', 'at': '2021-05-26'}, {'tier': 'gold'}),
        ({'clid': 'test_clid_3', 'at': '2021-05-18'}, {'tier': 'weak'}),
        ({'clid': 'test_clid_3', 'at': '2021-06-26'}, {'tier': 'bronze'}),
        ({'clid': 'test_clid_4', 'at': '2021-05-26'}, {'tier': 'unknown'}),
        ({'clid': 'test_clid_5', 'at': '2021-07-26'}, {'tier': 'unknown'}),
    ],
)
async def test_by_params(web_app_client, headers, req, res, pgsql):
    response = await web_app_client.get(ENDPOINT, headers=headers, params=req)

    assert response.status == 200

    data = await response.json()
    assert data == res

    # костыль, dump.sql выполняется на каждую итерацию
    # и падает с ошибкой дублирования
    with pgsql['fleet_reports'].cursor() as cursor:
        cursor.execute(
            """
            DROP TABLE yt.report_parks_rating_by_clid_2021_04;
            DROP TABLE yt.report_parks_rating_by_clid_2021_05;
            DROP TABLE yt.report_parks_rating_by_clid_2021_06;
            """,
        )
