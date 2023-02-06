import pytest


EATS_PICS_SUBSCRIBE_HANDLER = '/eats-pics/v1/subscribe'
PERIODIC_NAME = 'picture-on-change-subscriber'


@pytest.mark.config(
    EATS_NOMENCLATURE_PICTURE_ON_CHANGE_SUBSCRIBER={
        'subscribe_batch_size': 500,
    },
)
async def test_picture_on_change_subscriber(
        taxi_eats_nomenclature, pgsql, testpoint, mockserver,
):
    @testpoint(f'{PERIODIC_NAME}-finished')
    def finished_testpoint(param):
        pass

    batch_size = 500
    total_count = 3000

    # set current data
    urls_to_subscribe = set()
    urls_not_to_subscribe = set()
    for i in range(total_count):
        url = f'url_{i}'
        if i % 2 != 0:
            sql_add_picture(pgsql, url, True, True)
            urls_not_to_subscribe.add(url)
        else:
            if i % 4 == 0:
                sql_add_picture(pgsql, url, False, False)
                urls_not_to_subscribe.add(url)
            else:
                sql_add_picture(pgsql, url, False, True)
                urls_to_subscribe.add(url)

    requested_urls = set()

    @mockserver.json_handler(EATS_PICS_SUBSCRIBE_HANDLER)
    def _mock_eats_pics_subscribe(request):
        assert request.json['client_name'] == 'eats-nomenclature'
        assert set(request.json['items']).issubset(urls_to_subscribe)
        assert len(request.json['items']) <= batch_size
        for requested_url in request.json['items']:
            requested_urls.add(requested_url)
        return mockserver.make_response('OK', 204)

    # subscribe pictures in eats-pics
    await taxi_eats_nomenclature.run_distlock_task(PERIODIC_NAME)

    # check merged data
    db_pictures = sql_get_pictures(pgsql)
    for db_picture in db_pictures:
        url, has_active_subscription, needs_subscription = db_picture
        if url in urls_to_subscribe:
            assert has_active_subscription is True
            assert needs_subscription is True
        else:
            assert url in urls_not_to_subscribe

    assert _mock_eats_pics_subscribe.has_calls
    assert finished_testpoint.times_called == 1
    assert requested_urls == urls_to_subscribe


async def test_unknown_client(
        taxi_eats_nomenclature, pgsql, testpoint, mockserver,
):
    @testpoint(f'{PERIODIC_NAME}-finished')
    def finished_testpoint(param):
        pass

    # set current data
    sql_add_picture(pgsql, 'url_1', True, True)
    sql_add_picture(pgsql, 'url_2', False, True)
    sql_add_picture(pgsql, 'url_3', False, True)
    sql_add_picture(pgsql, 'url_4', True, True)

    old_sql_pictures = sql_get_pictures(pgsql)

    @mockserver.json_handler(EATS_PICS_SUBSCRIBE_HANDLER)
    def _mock_eats_pics_subscribe(request):
        return mockserver.make_response('Not Found', 404)

    # subscribe pictures in eats-pics
    await taxi_eats_nomenclature.run_distlock_task(PERIODIC_NAME)

    # data is not changed
    assert sql_get_pictures(pgsql) == old_sql_pictures

    assert _mock_eats_pics_subscribe.has_calls
    assert finished_testpoint.times_called == 1


@pytest.mark.config(
    EATS_NOMENCLATURE_PICTURE_ON_CHANGE_SUBSCRIBER={'enabled': False},
)
async def test_periodic_disabled(
        taxi_eats_nomenclature, pgsql, testpoint, mockserver,
):
    @testpoint(f'{PERIODIC_NAME}-finished')
    def finished_testpoint(param):
        pass

    @testpoint(f'{PERIODIC_NAME}-disabled')
    def disabled_testpoint(param):
        pass

    # set current data
    sql_add_picture(pgsql, 'url_1', True, True)
    sql_add_picture(pgsql, 'url_2', False, True)
    sql_add_picture(pgsql, 'url_3', False, True)
    sql_add_picture(pgsql, 'url_4', True, True)

    old_sql_pictures = sql_get_pictures(pgsql)

    @mockserver.json_handler(EATS_PICS_SUBSCRIBE_HANDLER)
    def _mock_eats_pics_subscribe(request):
        return mockserver.make_response('OK', 204)

    # subscribe pictures in eats-pics
    await taxi_eats_nomenclature.run_distlock_task(PERIODIC_NAME)

    # data is not changed
    assert sql_get_pictures(pgsql) == old_sql_pictures

    assert not _mock_eats_pics_subscribe.has_calls
    assert not finished_testpoint.has_calls
    assert disabled_testpoint.times_called == 1


async def test_periodic_metrics(mockserver, verify_periodic_metrics):
    @mockserver.json_handler(EATS_PICS_SUBSCRIBE_HANDLER)
    def _mock_eats_pics_subscribe(request):
        return mockserver.make_response('OK', 204)

    await verify_periodic_metrics(PERIODIC_NAME, is_distlock=True)


def sql_add_picture(pgsql, url, has_active_subscription, needs_subscription):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        insert into eats_nomenclature.pictures
        (url, has_active_subscription, needs_subscription)
        values ('{url}', {has_active_subscription}, {needs_subscription})
        """,
    )


def sql_get_pictures(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        """
        select url, has_active_subscription, needs_subscription
        from eats_nomenclature.pictures
        """,
    )
    return set(cursor)
