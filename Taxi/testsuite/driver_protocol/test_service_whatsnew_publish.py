import pytest


@pytest.mark.now('2018-01-21T23:59:00Z')
def test_publish_new_hide(taxi_driver_protocol, db):
    data = {'is_hidden': False}
    response = taxi_driver_protocol.put(
        '/service/whatsnew/publish',
        data,
        params={'id': '00000000000000000000000000000000'},
    )
    assert response.status_code == 200
    news_obj = db.misc_taximeter_news.find_one(
        {'_id': '00000000000000000000000000000000'},
    )
    assert news_obj['is_hidden'] is False


@pytest.mark.now('2018-01-21T23:59:00Z')
def test_publish_new_show(taxi_driver_protocol, db):
    data = {'is_hidden': True}
    response = taxi_driver_protocol.put(
        '/service/whatsnew/publish',
        data,
        params={'id': '00000000000000000000000000000001'},
    )
    assert response.status_code == 200
    news_obj = db.misc_taximeter_news.find_one(
        {'_id': '00000000000000000000000000000001'},
    )
    assert news_obj['is_hidden'] is True
