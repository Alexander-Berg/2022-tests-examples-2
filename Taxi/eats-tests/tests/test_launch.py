def test_launch_register_failed(launch):
    launch.set_host('http://eats-launch.eda.yandex.net')

    response = launch.launch_native(
        session_eater_id=1,
        passport_eater_id=124,
        passport_uid=111,
    )

    # failed due to /eater/v1/passport/register core-request
    assert response.status_code == 500


def test_launch_experiments_ok(launch):
    launch.set_host('http://eats-launch.eda.yandex.net')

    response = launch.launch_experiments(
        data={'consumer': 'eda_ab_service'},
    )

    assert response.status_code == 200
