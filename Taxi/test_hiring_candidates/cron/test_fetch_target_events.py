import pytest


@pytest.mark.config(
    HIRING_CANDIDATES_TARGET_EVENTS_YT_PATH=(
        '//home/taxi-analytics/da/target_events_for_payments/target_events_inc'
    ),
)
@pytest.mark.yt(static_table_data=['yt_target_events_inc.yaml'])
async def test_fetch_default(
        cron_runner, get_all_target_events, load_json, yt_apply,
):
    # arrange
    expected_data = load_json('expected_data.json')['events']
    # act
    await cron_runner.fetch_target_events()

    # assert
    for count, inserted_event in enumerate(get_all_target_events()):
        assert inserted_event.items() >= expected_data[count].items()


@pytest.mark.config(
    HIRING_CANDIDATES_TARGET_EVENTS_YT_PATH='//home/no/data/table',
)
async def test_fetch_empty_table(
        cron_runner, get_all_target_events, load_json, yt_apply,
):
    # arrange
    expected_data = load_json('expected_data.json')
    # act
    await cron_runner.fetch_target_events()

    # assert
    inserted_events = get_all_target_events()
    assert len(inserted_events) == 1
    assert inserted_events[0].items() >= expected_data.items()


@pytest.mark.config(
    HIRING_CANDIDATES_TARGET_EVENTS_YT_PATH='//home/no/any/table',
)
@pytest.mark.xfail(raises=RuntimeError)
async def test_no_table_found(cron_runner, yt_apply):
    await cron_runner.fetch_target_events()
