import freezegun
import pytest

from cron_scripts import close_expired_sessions


@pytest.fixture
def run_close_expired_sessions():
    def run(db):
        return close_expired_sessions.run(db)
    return run


@pytest.mark.parametrize(
    'config_name, exit_code, dt, count_after',
    [
        ('default', 0, '2019-12-04T09:15:56', 2),
        ('default', 0, '2019-12-05T09:15:56', 0),
        ('disabled', 0, '2019-12-05T09:15:56', 9),
        ('allow_1000', 0, '2019-12-03T09:15:56', 9),
    ]
)
def test_synchronize_organizations(
        mock_external_config,
        load_json,
        get_mongo,
        run_close_expired_sessions,
        config_name,
        exit_code,
        dt,
        count_after
):
    mock_external_config(
        load_json('external_config.json')[config_name]
    )
    db = get_mongo
    with freezegun.freeze_time(dt):
        result = run_close_expired_sessions(db)
        assert exit_code == result
        assert count_after == db.sessions.count_documents({'is_active': True})
