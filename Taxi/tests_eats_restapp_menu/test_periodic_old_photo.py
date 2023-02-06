# pylint: disable=redefined-outer-name
import pytest


@pytest.fixture(name='mock_avatars_delete_200')
def _mock_avatars_delete_200(mockserver, request):
    @mockserver.json_handler(
        r'/avatars-mds/delete-eda/(?P<group_id>\w+)/(?P<imagename>\w+)',
        regex=True,
    )
    def _mock_avatars(request, group_id, imagename):
        return mockserver.make_response(status=200)

    return _mock_avatars


@pytest.fixture(name='mock_avatars_delete_202')
def mock_avatars_delete_202(mockserver, request):
    @mockserver.json_handler(
        r'/avatars-mds/delete-eda/(?P<group_id>\w+)/(?P<imagename>\w+)',
        regex=True,
    )
    def _mock_avatars(request, group_id, imagename):
        return mockserver.make_response(status=202)

    return _mock_avatars


@pytest.fixture(name='mock_avatars_delete_404')
def mock_avatars_delete_404(mockserver, request):
    @mockserver.json_handler(
        r'/avatars-mds/delete-eda/(?P<group_id>\w+)/(?P<imagename>\w+)',
        regex=True,
    )
    def _mock_avatars(request, group_id, imagename):
        return mockserver.make_response(status=404)

    return _mock_avatars


@pytest.fixture()
def get_cursor(pgsql):
    def create_cursor():
        return pgsql['eats_restapp_menu'].dict_cursor()

    return create_cursor


@pytest.fixture()
def get_picture_by_identity(get_cursor):
    def do_get_picture_by_identity(identity):
        cursor = get_cursor()
        cursor.execute(
            'SELECT * FROM eats_restapp_menu.pictures '
            'WHERE avatarnica_identity = %s',
            [identity],
        )
        return cursor.fetchall()

    return do_get_picture_by_identity


async def test_periodic_old_photo_empty(taxi_eats_restapp_menu, stq):
    await taxi_eats_restapp_menu.run_periodic_task(
        'delete-old-picture-periodic',
    )

    assert stq.eats_restapp_menu_photo_delete.times_called == 0


async def test_periodic_old_photo_happy_path(
        taxi_eats_restapp_menu, mocked_time, stq,
):
    mocked_time.sleep(108000000)
    # 30000-часов значение больше чем период жизни
    # удалённого изображения (по умолчанию 3 года)

    await taxi_eats_restapp_menu.invalidate_caches()

    await taxi_eats_restapp_menu.run_periodic_task(
        'delete-old-picture-periodic',
    )

    assert stq.eats_restapp_menu_photo_delete.times_called == 1
    stq_param = stq.eats_restapp_menu_photo_delete.next_call()
    assert stq_param['args'] == []
    assert stq_param['eta']
    assert stq_param['id']
    assert stq_param['kwargs']['identity'] == '123/1237'
    assert stq_param['queue'] == 'eats_restapp_menu_photo_delete'


async def test_delete_photo_stq(
        stq_runner, mock_avatars_delete_200, get_picture_by_identity,
):
    await stq_runner.eats_restapp_menu_photo_delete.call(
        task_id='fake_task', kwargs={'identity': '123/1237'},
    )

    assert mock_avatars_delete_200.times_called == 1
    pictures = get_picture_by_identity('123/1237')
    assert pictures[0]['status'] == 'permanently_deleted'
    assert pictures[1]['status'] == 'permanently_deleted'


async def test_delete_photo_stq_202(
        stq_runner, mock_avatars_delete_202, get_picture_by_identity,
):
    await stq_runner.eats_restapp_menu_photo_delete.call(
        task_id='fake_task', kwargs={'identity': '123/1237'},
    )

    assert mock_avatars_delete_202.times_called == 1
    pictures = get_picture_by_identity('123/1237')
    assert pictures[0]['status'] == 'deleted'
    assert pictures[1]['status'] == 'deleted'


async def test_delete_photo_stq_404(
        stq_runner, mock_avatars_delete_404, get_picture_by_identity,
):
    await stq_runner.eats_restapp_menu_photo_delete.call(
        task_id='fake_task', kwargs={'identity': '123/1237'},
    )

    assert mock_avatars_delete_404.times_called == 1
    pictures = get_picture_by_identity('123/1237')
    assert pictures[0]['status'] == 'permanently_deleted'
    assert pictures[1]['status'] == 'permanently_deleted'
