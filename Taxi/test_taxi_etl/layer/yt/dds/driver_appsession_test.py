# coding: utf-8
# pylint: disable=redefined-outer-name
import pytest

from builtins import range
from nile.api.v1 import Record, extractors as ne
from nile.api.v1.clusters import MockCluster
from nile.api.v1.local import StreamSource, ListSink

from dmp_suite import datetime_utils as dtu

from taxi_etl.layer.yt.dds.driver_appsession.impl import (
    transform_events_into_sessions,
)


def event_rec(timestamp, event_id, event, driver_uuid="DU1", application_version="1.0"):
    return Record(
        timestamp=timestamp,
        utc_event_dttm=dtu.timestamp2datetime(timestamp),
        event_id=event_id,
        appmetrica_uuid="MU1",
        taximeter_park_id="TPI1",
        driver_uuid=driver_uuid,
        event=event,
        scenario="SCE1",
        subscenario="SSCE1",
        screen="SCR1",
        application_version=application_version,
        appmetrica_device_id="MDI1",
        device_manufacturer="DMAN1",
        device_model="DMOD1",
        device_type="DTY1",
        application_platform="AP1",
        distribution="DIS1",
        application_id="AI1",
        api_key="AK1",
        os_version="OV1",
        connection_type="CT1",
    )


def session_rec(
    start_timestamp,
    end_timestamp,
    event_list,
    driver_uuid="DU1",
    application_version="1.0",
    break_reason="timeout",
):
    return Record(
        utc_start_dttm=dtu.timestamp2datetime(start_timestamp),
        utc_end_dttm=dtu.timestamp2datetime(end_timestamp),
        event_list=event_list,
        appmetrica_uuid="MU1",
        taximeter_park_id="TPI1",
        driver_uuid=driver_uuid,
        application_version=application_version,
        appmetrica_device_id="MDI1",
        first_device_manufacturer="DMAN1",
        first_device_model="DMOD1",
        first_device_type="DTY1",
        application_platform="AP1",
        distribution="DIS1",
        application_id="AI1",
        api_key="AK1",
        break_reason=break_reason,
        last_os_version="OV1",
        order_connection_type_list=[],
    )


@pytest.fixture
def mock_job():
    job = MockCluster().job()
    job.table("stub").label("events").call(
        transform_events_into_sessions, dtu.MAX_DATETIME
    ).project(ne.all(exclude=["appsession_id"])).label("sessions")
    return job


@pytest.mark.parametrize(
    "given_events, expect_sessions",
    [
        pytest.param(
            [event_rec(0, "A", "Accept")],
            [session_rec(0, 0, ["A"])],
            id="when_single_event",
        ),
        pytest.param(
            [
                event_rec(0, "A", "Accept"),
                event_rec(100, "B", "Show"),
                event_rec(200, "C", "Show"),
            ],
            [session_rec(0, 200, ["A", "B", "C"])],
            id="when_next_event_before_timeout",
        ),
        pytest.param(
            [
                event_rec(0, "A", "Accept"),
                event_rec(100, "B", "Show"),
                event_rec(2000, "C", "Show"),
            ],
            [session_rec(0, 100, ["A", "B"]), session_rec(2000, 2000, ["C"])],
            id="when_next_event_after_timeout",
        ),
        pytest.param(
            [
                event_rec(0, "A", "Accept"),
                event_rec(100, "B", "Show"),
                event_rec(1900, "C", "Show"),
            ],
            [session_rec(0, 1900, ["A", "B", "C"])],
            id="when_next_event_coincides_with_timeout",
        ),
        pytest.param(
            [event_rec(t, str(t), "Accept") for t in range(0, 24 * 3600 + 901, 900)],
            [
                session_rec(
                    0, 24 * 3600, [str(t) for t in range(0, 24 * 3600 + 1, 900)],
                    break_reason="session_duration",
                ),
                session_rec(24 * 3600 + 900, 24 * 3600 + 900, [str(24 * 3600 + 900)]),
            ],
            id="when_max_duration_reached",
        ),
        pytest.param(
            [
                event_rec(0, "A", "Accept"),
                event_rec(100, "B", "Logout.FromAccount"),
                event_rec(200, "C", "Accept"),
            ],
            [session_rec(0, 100, ["A", "B"], break_reason="logout"), session_rec(200, 200, ["C"])],
            id="when_logout",
        ),
        pytest.param(
            [
                event_rec(0, "A", "Accept"),
                event_rec(100, "B", "Show"),
                event_rec(200, "C", "Show", application_version="2.0"),
            ],
            [
                session_rec(0, 100, ["A", "B"], break_reason="application_version_change"),
                session_rec(200, 200, ["C"], application_version="2.0"),
            ],
            id="when_version_changed",
        ),
        pytest.param(
            [
                event_rec(0, "A", "Accept"),
                event_rec(100, "B", "Show"),
                event_rec(200, "C", "Show", driver_uuid="DU2"),
            ],
            [
                session_rec(0, 100, ["A", "B"], break_reason="reset_driver_profile"),
                session_rec(200, 200, ["C"], driver_uuid="DU2"),
            ],
            id="when_driver_uuid_changed",
        ),
        pytest.param(
            [
                event_rec(0, "A", "Accept"),
                event_rec(100, "B", "Show"),
                event_rec(200, "C", "Show", driver_uuid=None),
            ],
            [session_rec(0, 200, ["A", "B", "C"])],
            id="when_last_driver_uuid_is_null",
        ),
        pytest.param(
            [
                event_rec(0, "A", "Accept"),
                event_rec(100, "B", "Show", driver_uuid=None),
                event_rec(200, "C", "Accept"),
            ],
            [session_rec(0, 200, ["A", "B", "C"])],
            id="when_middle_driver_uuid_is_null",
        ),
        pytest.param(
            [
                event_rec(0, "A", "Accept", driver_uuid=None),
                event_rec(100, "B", "Show"),
                event_rec(200, "C", "Accept"),
            ],
            [session_rec(0, 200, ["A", "B", "C"])],
            id="when_first_driver_uuid_is_null",
        ),
        pytest.param(
            [
                event_rec(0, "A", "Accept"),
                event_rec(100, "B", "Show"),
                event_rec(200, "C", "Show", driver_uuid=None),
                event_rec(300, "D", "Show", driver_uuid="DU2"),
            ],
            [
                session_rec(0, 200, ["A", "B", "C"], break_reason="reset_driver_profile"),
                session_rec(300, 300, ["D"], driver_uuid="DU2"),
            ],
            id="when_driver_uuid_changed_after_null",
        ),
        pytest.param(
            [
                event_rec(0, "A", "Accept"),
                event_rec(100, "B", "Show"),
                event_rec(100, "C", "Logout.FromAccount"),
                event_rec(200, "D", "Accept"),
            ],
            [session_rec(0, 100, ["A", "B", "C"], break_reason="logout"), session_rec(200, 200, ["D"])],
            id="when_some_event_and_logout_in_a_moment",
        ),
        pytest.param(
            [
                event_rec(0, "A", "Accept"),
                event_rec(100, "B", "Logout.FromAccount"),
                event_rec(100, "C", "Accept"),
                event_rec(200, "D", "Accept"),
            ],
            [session_rec(0, 100, ["A", "B", "C"], break_reason="logout"), session_rec(200, 200, ["D"])],
            id="when_logout_and_some_event_in_a_moment",
        ),
        pytest.param(
            [
                event_rec(0, "A", "Accept"),
                event_rec(100, "B", "Logout.FromAccount"),
                event_rec(100, "C", "Logout.FromAccount"),
                event_rec(200, "D", "Accept"),
            ],
            [session_rec(0, 100, ["A", "B", "C"], break_reason="logout"), session_rec(200, 200, ["D"])],
            id="when_two_logouts_in_a_moment",
        ),
        pytest.param(
            [
                event_rec(0, "A", "Accept"),
                event_rec(100, "B", "Accept"),
                event_rec(100, "C", "Accept", driver_uuid="DU2"),
                event_rec(200, "D", "Accept", driver_uuid="DU2"),
            ],
            [
                session_rec(0, 100, ["A", "B", "C"], break_reason="reset_driver_profile"),
                session_rec(200, 200, ["D"], driver_uuid="DU2"),
            ],
            id="when_driver_uuid_changes_in_a_moment",
        ),
    ],
)
def test_transform_events_into_states(given_events, expect_sessions, mock_job):
    sessions = []
    mock_job.local_run(
        sources={"events": StreamSource(given_events)},
        sinks={"sessions": ListSink(sessions)},
    )
    assert sessions == expect_sessions
