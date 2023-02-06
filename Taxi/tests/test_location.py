import numpy as np


def test_gps(load_json, get_pytest_signalq_config):
    from signalq_pyml import processors
    from signalq_pyml.core import types

    config = get_pytest_signalq_config(cv='yandex', mode='testing')

    loc_filter = processors.filters.LocationFilter(**config['LocationFilter'])

    collected = []

    for step_num in range(0, 1000):
        filtered = loc_filter.process(
            timestamp=step_num / 30,
            location=types.Location(lon=0.0, lat=0.0, speed=13.45454),
        )
        collected.append(filtered)

    speeds = np.asarray([payload.speed for payload in collected])
    assert np.isfinite(speeds).mean() < 0.1

    loc_filter.reset_state()

    collected = []

    for step_num in range(1000, 2000):
        filtered = loc_filter.process(
            timestamp=step_num / 30,
            location=types.Location(
                lon=np.random.random(),
                lat=np.random.random(),
                speed=13 + np.random.random(),
            ),
        )
        collected.append(filtered)

    speeds = np.asarray([payload.speed for payload in collected])
    assert np.isfinite(speeds).mean() > 0.7


def test_speed_stable(load_json, get_pytest_signalq_config):

    from signalq_pyml.core import types
    from signalq_pyml.processors.filters import location

    config = get_pytest_signalq_config(cv='yandex', mode='testing')

    loc_filter = location.LocationFilter(**config['LocationFilter'])

    num_steps = 1000
    for step_num in range(0, num_steps):
        loc_filter.process(
            timestamp=step_num / 30,
            location=types.Location(lon=0.0, lat=0.0, speed=np.nan),
        )

    assert location.LocationFilter.is_speed_stable(
        timestamp=num_steps / 30,
        window_length=5,
        low_speed=-1.0,
        location_filter_state=loc_filter.state,
    )
