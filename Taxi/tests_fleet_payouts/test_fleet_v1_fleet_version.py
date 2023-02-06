import pytest

from tests_fleet_payouts.utils import xcmp


DEFAULT_STATS = {
    'stats_period_days': 30,
    'total_work_hours': 0,
    'total_cars': 0,
}


@pytest.fixture(name='get_fleet_version')
def get_fleet_version_(taxi_fleet_payouts, mock_parks, mock_users):
    async def get_fleet_version(
            *,
            park_id='00000000000000000000000000000000',
            yandex_uid='1000',
            user_ticket_provider='yandex',
    ):
        return await taxi_fleet_payouts.get(
            'fleet/payouts/v1/fleet-version',
            headers={
                'X-Park-Id': park_id,
                'X-Yandex-UID': yandex_uid,
                'X-Ya-User-Ticket-Provider': user_ticket_provider,
                'X-Ya-User-Ticket': 'TESTSUITE-USER-TICKET',
            },
        )

    return get_fleet_version


@pytest.fixture(name='post_fleet_version_change')
def post_fleet_version_change_(taxi_fleet_payouts, mock_parks, mock_users):
    async def post_fleet_version_change(
            desired_version,
            *,
            park_id='00000000000000000000000000000000',
            yandex_uid='1000',
            user_ticket_provider='yandex',
    ):
        return await taxi_fleet_payouts.post(
            'fleet/payouts/v1/fleet-version/change',
            headers={
                'X-Park-Id': park_id,
                'X-Yandex-UID': yandex_uid,
                'X-Ya-User-Ticket-Provider': user_ticket_provider,
                'X-Ya-User-Ticket': 'TESTSUITE-USER-TICKET',
            },
            json={'desired_version': desired_version},
        )

    return post_fleet_version_change


async def test_non_park_user(get_fleet_version, post_fleet_version_change):
    response = await get_fleet_version(yandex_uid='9999')
    assert response.status_code == 403, response.text

    response = await post_fleet_version_change('basic', yandex_uid='9999')
    assert response.status_code == 403, response.text


async def test_non_park_super_user(
        get_fleet_version, post_fleet_version_change,
):
    response = await get_fleet_version(yandex_uid='1001')
    assert response.status_code == 403, response.text

    response = await post_fleet_version_change('basic', yandex_uid='1001')
    assert response.status_code == 403, response.text


async def test_yandex_team_user(get_fleet_version, post_fleet_version_change):
    response = await get_fleet_version(
        yandex_uid='9999', user_ticket_provider='yandex_team',
    )
    assert response.status_code == 200, response.text

    response = await post_fleet_version_change(
        'basic', yandex_uid='9999', user_ticket_provider='yandex_team',
    )
    assert response.status_code == 403, response.text


async def test_default_version(get_fleet_version):
    response = await get_fleet_version()
    assert response.status_code == 200, response.text
    assert response.json() == {**DEFAULT_STATS, 'current_version': 'basic'}


@pytest.mark.pgsql('fleet_payouts', files=['fleet_versions_A.sql'])
@pytest.mark.now('2020-01-01T23:59:59+03:00')
async def test_changed_version_00(get_fleet_version):
    response = await get_fleet_version()
    assert response.status_code == 200, response.text
    assert response.json() == {
        **DEFAULT_STATS,
        'current_version': 'basic',
        'pending_version': 'simple',
    }


@pytest.mark.pgsql('fleet_payouts', files=['fleet_versions_A.sql'])
@pytest.mark.now('2020-01-02T00:00:00+03:00')
async def test_changed_version_01(get_fleet_version):
    response = await get_fleet_version()
    assert response.status_code == 200, response.text
    assert response.json() == {
        **DEFAULT_STATS,
        'current_version': 'simple',
        'requested_by': 'user1000@yandex.ru',
        'requested_at': xcmp.Date('2020-01-01T12:00:00+03:00'),
        'activated_at': xcmp.Date('2020-01-02T00:00:00+03:00'),
    }


@pytest.mark.pgsql('fleet_payouts', files=['fleet_versions_B.sql'])
@pytest.mark.now('2020-03-01T23:59:59+03:00')
async def test_changed_version_02(get_fleet_version):
    response = await get_fleet_version()
    assert response.status_code == 200, response.text
    assert response.json() == {
        **DEFAULT_STATS,
        'current_version': 'simple',
        'pending_version': 'basic',
        'requested_by': 'user1000@yandex.ru',
        'requested_at': xcmp.Date('2020-01-01T12:00:00+03:00'),
        'activated_at': xcmp.Date('2020-01-02T00:00:00+03:00'),
    }


@pytest.mark.pgsql('fleet_payouts', files=['fleet_versions_B.sql'])
@pytest.mark.now('2020-03-02T00:00:00+03:00')
async def test_changed_version_03(get_fleet_version):
    response = await get_fleet_version()
    assert response.status_code == 200, response.text
    assert response.json() == {
        **DEFAULT_STATS,
        'current_version': 'basic',
        'requested_by': 'user1001@yandex.ru',
        'requested_at': xcmp.Date('2020-03-01T12:00:00+03:00'),
        'activated_at': xcmp.Date('2020-03-02T00:00:00+03:00'),
    }


@pytest.mark.now('2020-07-01T12:00:00+03:00')
async def test_change_default_to_simple(
        get_fleet_version, post_fleet_version_change,
):
    response = await post_fleet_version_change('simple')
    assert response.status_code == 204, response.text

    response = await get_fleet_version()
    assert response.status_code == 200, response.text
    assert response.json() == {
        **DEFAULT_STATS,
        'current_version': 'basic',
        'pending_version': 'simple',
    }


@pytest.mark.now('2020-07-01T12:00:00+03:00')
async def test_change_default_to_basic(
        get_fleet_version, post_fleet_version_change,
):
    response = await post_fleet_version_change('basic')
    assert response.status_code == 204, response.text

    response = await get_fleet_version()
    assert response.status_code == 200, response.text
    assert response.json() == {**DEFAULT_STATS, 'current_version': 'basic'}


@pytest.mark.pgsql('fleet_payouts', files=['fleet_versions_A.sql'])
@pytest.mark.now('2020-07-01T12:00:00+03:00')
async def test_change_simple_to_simple(
        get_fleet_version, post_fleet_version_change,
):
    response = await post_fleet_version_change('simple')
    assert response.status_code == 204, response.text

    response = await get_fleet_version()
    assert response.status_code == 200, response.text
    assert response.json() == {
        **DEFAULT_STATS,
        'current_version': 'simple',
        'requested_by': 'user1000@yandex.ru',
        'requested_at': xcmp.Date('2020-01-01T12:00:00+03:00'),
        'activated_at': xcmp.Date('2020-01-02T00:00:00+03:00'),
    }


@pytest.mark.pgsql('fleet_payouts', files=['fleet_versions_A.sql'])
@pytest.mark.now('2020-07-01T12:00:00+03:00')
async def test_change_simple_to_basic(
        get_fleet_version, post_fleet_version_change,
):
    response = await post_fleet_version_change('basic')
    assert response.status_code == 204, response.text

    response = await get_fleet_version()
    assert response.status_code == 200, response.text
    assert response.json() == {
        **DEFAULT_STATS,
        'current_version': 'simple',
        'pending_version': 'basic',
        'requested_by': 'user1000@yandex.ru',
        'requested_at': xcmp.Date('2020-01-01T12:00:00+03:00'),
        'activated_at': xcmp.Date('2020-01-02T00:00:00+03:00'),
    }


@pytest.mark.pgsql('fleet_payouts', files=['fleet_versions_B.sql'])
@pytest.mark.now('2020-07-01T12:00:00+03:00')
async def test_change_basic_to_simple(
        get_fleet_version, post_fleet_version_change,
):
    response = await post_fleet_version_change('simple')
    assert response.status_code == 204, response.text

    response = await get_fleet_version()
    assert response.status_code == 200, response.text
    assert response.json() == {
        **DEFAULT_STATS,
        'current_version': 'basic',
        'pending_version': 'simple',
        'requested_by': 'user1001@yandex.ru',
        'requested_at': xcmp.Date('2020-03-01T12:00:00+03:00'),
        'activated_at': xcmp.Date('2020-03-02T00:00:00+03:00'),
    }


@pytest.mark.pgsql('fleet_payouts', files=['fleet_versions_B.sql'])
@pytest.mark.now('2020-07-01T12:00:00+03:00')
async def test_change_basic_to_basic(
        get_fleet_version, post_fleet_version_change,
):
    response = await post_fleet_version_change('basic')
    assert response.status_code == 204, response.text

    response = await get_fleet_version()
    assert response.status_code == 200, response.text
    assert response.json() == {
        **DEFAULT_STATS,
        'current_version': 'basic',
        'requested_by': 'user1001@yandex.ru',
        'requested_at': xcmp.Date('2020-03-01T12:00:00+03:00'),
        'activated_at': xcmp.Date('2020-03-02T00:00:00+03:00'),
    }


@pytest.mark.pgsql('fleet_payouts', files=['fleet_versions_B.sql'])
@pytest.mark.now('2020-03-01T23:54:59.999999+03:00')
async def test_change_before_previous_activated(
        get_fleet_version, post_fleet_version_change,
):
    response = await post_fleet_version_change('simple')
    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': '400',
        'message': 'The change has already been requested.',
    }


@pytest.mark.pgsql('fleet_payouts', files=['fleet_versions_B.sql'])
@pytest.mark.now('2020-03-31T23:54:59.999999+03:00')
async def test_downgrade_restriction(post_fleet_version_change):
    response = await post_fleet_version_change('simple')
    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': '400',
        'message': 'Dowgrade is not allowed until 2020-03-31T21:00:00+0000.',
    }
