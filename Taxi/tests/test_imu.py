def test_gravitational_orientation():
    import math

    from signalq_pyml.processors import common as cm
    from signalq_pyml.core import types

    # gyro, accel, mag
    roll, pitch = cm.imu.get_gravitational_orientation_imu(
        imu=types.IMUInfo(
            gyro=(0.0, 0.0, 0.0), accel=(9.8, 0.0, 0.0), mag=(0.1, 0.0, 0.0),
        ),
    )
    assert roll == 0.0 and math.isclose(pitch, math.pi / 2)

    # gyro, accel, mag
    roll, pitch = cm.imu.get_gravitational_orientation_imu(
        imu=types.IMUInfo(
            gyro=(0.0, 0.0, 0.0), accel=(0.0, 9.8, 0.0), mag=(0.1, 0.0, 0.0),
        ),
    )
    assert pitch == 0.0 and math.isclose(roll, math.pi / 2)

    # gyro, accel, mag
    roll, pitch = cm.imu.get_gravitational_orientation_imu(
        imu=types.IMUInfo(
            gyro=(0.0, 0.0, 0.0), accel=(0.0, 0.0, 9.8), mag=(0.1, 0.0, 0.0),
        ),
    )
    assert pitch == 0.0 and math.isclose(roll, 0.0)


def test_gravity_magnitude_calibration(load_json):
    import numpy as np
    np.random.seed(42)

    from signalq_pyml import get_config_path, compose_config
    from signalq_pyml.processors import common

    diff = load_json('config.json')
    base = load_json(get_config_path(cv='yandex', mode=None))
    config = compose_config(base, diff)

    calibration = common.IMUCalibration(**config['IMUCalibration'])

    accel = np.array([0.0, 0.1, 10.1])
    gyro = np.array([0.1, 0.1, 0.0])
    mag = np.array([0.0, 0.0, 40.0])

    imu = np.array([gyro, accel, mag])

    for ts in range(0, 6000):
        time = ts / 30
        new = imu + np.random.randn(*imu.shape)
        packed = common.get_imu_from_data(imu=new)

        calibration.process(time, packed)

    assert calibration.state.accel_magnitude_calibrated
    assert 8.0 < calibration.state.accel_magnitude_mean < 12.0
