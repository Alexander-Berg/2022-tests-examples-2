import datetime

import pytest


@pytest.mark.skip(reason='this test requires model loading')
def test_tiredness(
        load_json, get_pytest_signalq_config, load_models, model_dir,
):
    import os

    from signalq_pyml import processors
    from signalq_pyml import get_config
    from signalq_pyml.core import types

    config = get_config(cv='yandex', mode='testing')

    tz_path = os.path.join(model_dir, 'timezone', 'tz.npz')
    config['LocalTime']['timezone_array_path'] = tz_path

    tz_processor = processors.models.LocalTime(timezone_array_path=tz_path)

    location = types.Location(lat=55.772572, lon=37.584052, speed=0.0)

    for step in range(100):
        tz_processor.process(step / 30, location)

    assert tz_processor.state.last_utc_offset_hours == 3

    utc_hour = datetime.datetime.now().hour
    local_hour = utc_hour + tz_processor.state.last_utc_offset_hours

    assert tz_processor.state.get_local_hour(0.0) == local_hour
