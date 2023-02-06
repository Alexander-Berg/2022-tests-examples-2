import pytest


@pytest.mark.servicetest
@pytest.mark.now('2019-01-01T06:00:00')
@pytest.mark.pgsql('startrack_reports', files=['developers.sql'])
async def test_leaderboard_export(taxi_startrack_reports_web):
    response = await taxi_startrack_reports_web.get(
        '/leaderboard/export_to_csv/',
    )
    assert response.status == 200
    content = await response.content.read()
    assert content == (
        b'date_of_top;rank_place;index;login;additions;deletions;commits\r\n'
        b'2019-01-01;1;4.0;ydemidenko;4;0;1\r\n'
        b'2019-01-01;2;0.0;karachevda;0;0;1\r\n'
        b'2019-01-01;3;0.0;noname;0;0;0\r\n'
    )
