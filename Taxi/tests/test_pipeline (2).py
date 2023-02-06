from signalq_pyml.core import types
from signalq_pyml import processors


def smoke_state_node(processor: processors.Runner, load_json):
    import json
    import numpy as np

    np.random.seed(42)

    face_info = load_json('single_frame_face_info.json')
    face_info['landmarks68'] = np.asarray(face_info['landmarks68'])
    face_info = {
        k: np.array(v) if isinstance(v, list) else v
        for k, v in face_info.items()
    }

    face_info['head_pose'] = 0.0, 0.0, -40.0
    face_info['detection'] = 1.0, 1.0, 200.0, 150.0

    imu = types.IMUInfo(
        accel=(0.0, 0.0, 9.81), gyro=(0.0, 0.0, 0.0), mag=(0.0, 1.0, 0.0),
    )

    imu_data = imu.gyro, imu.accel, imu.mag

    outputs = []

    for step_num in range(0, 2000):
        payload = processor.process(
            timestamp=step_num / 30,
            speed=10.0 + np.random.random(),
            eye_angles=(0.0, 0.0),
            lon=np.random.randn(),
            lat=np.random.randn(),
            imu=np.asarray(imu_data),
            mouth_occluded=None,
            eyes_occluded=None,
            eyewipe_score=None,
            smoking_score=None,
            seatbelt_score=None,
            **face_info,
        )

        if payload is not None:
            outputs.extend(payload['events'])

    face_info['head_pose'] = 0.0, 0.0, 0.0
    face_info['eyes_state'] = False, False

    for step_num in range(2000, 3000):
        payload = processor.process(
            timestamp=step_num / 30,
            speed=10.0 + np.random.random(),
            eye_angles=(0.0, 0.0),
            lon=np.random.randn(),
            lat=np.random.randn(),
            imu=np.asarray(imu_data),
            mouth_occluded=None,
            eyes_occluded=None,
            eyewipe_score=None,
            smoking_score=None,
            seatbelt_score=None,
            **face_info,
        )

        if payload is not None:
            outputs.extend(payload['events'])

    face_info['head_pose'] = 0.0, 0.0, 10.0
    face_info['eyes_state'] = True, True

    for step_num in range(3000, 4000):
        payload = processor.process(
            timestamp=step_num / 30,
            speed=10.0 + np.random.random(),
            eye_angles=(0.0, 0.0),
            lon=np.random.randn(),
            lat=np.random.randn(),
            imu=np.asarray(imu_data),
            mouth_occluded=None,
            eyes_occluded=None,
            eyewipe_score=None,
            smoking_score=None,
            seatbelt_score=None,
            **face_info,
        )

        if payload is not None:
            outputs.extend(payload['events'])

    face_info['head_pose'] = 0.0, 0.0, 0.0
    face_info['detection_result'] = False
    face_info['eyes_state'] = True, True

    for step_num in range(4000, 6000):
        payload = processor.process(
            timestamp=step_num / 30,
            speed=10.0 + np.random.random(),
            eye_angles=(0.0, 0.0),
            lon=np.random.randn(),
            lat=np.random.randn(),
            imu=np.asarray(imu_data),
            mouth_occluded=None,
            eyes_occluded=False,
            eyewipe_score=None,
            smoking_score=None,
            seatbelt_score=None,
            **face_info,
        )

        if payload is not None:
            outputs.extend(payload['events'])

    assert all(out.get('payload') is not None for out in outputs)
    assert all(out.get('info') is not None for out in outputs)

    state = processor.get_state_dict()
    features = state[processors.features.FeatureAggregator.__name__]['cache']
    assert features['stuck/default/time/600/count'] > 0.0

    json.dumps(state)  # check if no error
    return outputs, state


def test_state_node(load_json, get_pytest_signalq_config):
    config = get_pytest_signalq_config(cv='yandex', mode='testing')

    processor = processors.Runner(config)

    outputs, state = smoke_state_node(processor, load_json)
    assert len(outputs) > 7


def test_init_from_product(load_json, get_pytest_signalq_config):
    product = load_json('product.json')
    config = get_pytest_signalq_config(cv='yandex', mode='testing')

    processor = processors.Runner(config=config, product=product)
    assert processor is not None


def test_init_from_state(load_json, get_pytest_signalq_config):
    state_dict = load_json('state_example.json')
    config = get_pytest_signalq_config(cv='yandex', mode='testing')

    processor = processors.Runner(config)
    processor.load_state(state_dict)

    outputs, state = smoke_state_node(processor, load_json)

    assert len(outputs) >= 6


def test_partial_init_from_state(load_json, get_pytest_signalq_config):
    state_dict = load_json('state_example.json')

    config = get_pytest_signalq_config(cv='yandex', mode='testing')
    processor = processors.Runner(config)
    processor.load_invariants(state_dict)

    outputs, state = smoke_state_node(processor, load_json)

    assert len(outputs) >= 6


def test_separate_thresholds(load_json, get_pytest_signalq_config):
    from signalq_pyml import get_config_path, compose_config

    diff = load_json('config.json')
    base = load_json(get_config_path(cv='yandex', mode=None))
    config = compose_config(base, diff)
    config = get_pytest_signalq_config(config=config)

    processor = processors.Runner(config)

    outputs, state = smoke_state_node(processor, load_json)

    assert all(
        (
            outputs[3]['name'] == 'distraction',
            outputs[3]['payload']['flag'],
            not outputs[3]['info']['signal'],
            outputs[3]['info']['send'],
        ),
    )

    assert all(
        (
            outputs[4]['name'] == 'distraction',
            outputs[4]['payload']['flag'],
            outputs[4]['info']['signal'],
            outputs[4]['info']['send'],
        ),
    )
