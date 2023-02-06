import pytest

from cron_scripts import synchronize_organizations


@pytest.fixture
def run_synchronize_organizations():
    def run(db):
        return synchronize_organizations.run(db)
    return run


@pytest.mark.parametrize(
    'config_name, exit_code, delta',
    [
        ('default', 0, 0),
        ('lost_one', 1, None),
        ('new_one', 0, 1),
        ('new_one_and_update_one', 0, 1),
        ('update_one', 0, 0),
        ('broken_tag', 1, None),
        ('not_unique', 1, None),
        ('missed_tag', 1, None),
    ],
)
def test_synchronize_organizations(
        mock_external_config,
        load_json,
        get_mongo,
        patch,
        run_synchronize_organizations,
        config_name,
        exit_code,
        delta
):
    @patch('infranaim.clients.telegram.Telegram.send_message')
    def _telegram(*args, **kwargs):
        return None

    mock_external_config(
        load_json('external_config.json')[config_name]
    )
    db = get_mongo

    count = db.organizations.count_documents({})

    result = run_synchronize_organizations(db)
    assert exit_code == result

    if exit_code == 0:
        assert count + delta == db.organizations.count_documents({})
