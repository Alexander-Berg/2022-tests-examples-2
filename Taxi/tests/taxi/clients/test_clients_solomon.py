import pytest

from taxi.clients import solomon


@pytest.mark.parametrize(
    'sensors, is_valid',
    [
        ([(12, {'arg': 33})], False),
        ([(12, {'arg': '3' * 198})], True),
        ([(12, {'arg': '3' * 200})], False),
        ([(12, {'a' * 33: '3'})], False),
        ([(12, {'a' * i: '1' for i in range(1, 18)})], False),
        ([(12, {str(i): '3'}) for i in range(0, 10001)], True),
    ],
)
def test_data_correctness(sensors, is_valid):
    data = solomon.SolomonPushData('tst_app')
    for sensor in sensors:
        data.add_igauge_sensor(sensor[0], **sensor[1])

    try:
        data.check_and_raise()
    except ValueError:
        assert not is_valid
    else:
        assert is_valid
