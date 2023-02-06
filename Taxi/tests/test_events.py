import pytest
import numpy as np

from signalq_pyml.core import defaults


def make_face_info(
        base, step_num: int, speed: float = 10.0, aux_args: dict = None,
):
    aux = aux_args or {}

    new = dict(
        timestamp=step_num / 30,
        speed=speed + np.random.randn(),
        eye_angles=(0.0, 0.0),
        not_eye_scores=(0.0, 0.0),
        lon=np.random.randn(),
        lat=np.random.randn(),
        imu=aux.get('imu', defaults.imu_data),
        mouth_occluded=aux.get('mouth_occluded'),
        eyes_occluded=aux.get('eyes_occluded'),
        smoking_score=aux.get('smoking_score'),
        seatbelt_score=aux.get('seatbelt_score'),
        eyewipe_score=aux.get('eyewipe_score'),
        phone_scores=aux.get('phone_scores'),
        trash_score=aux.get('trash_score'),
    )
    new.update(base)
    return new


def test_distraction(load_json, get_pytest_signalq_config):
    from signalq_pyml import processors

    config = get_pytest_signalq_config(cv='yandex', mode='testing')

    processor = processors.Runner(config)
    face_info = load_json('single_frame_face_info.json')
    face_info['landmarks68'] = np.asarray(face_info['landmarks68'])
    face_info['head_pose'] = 0.0, 0.0, -40.0
    face_info['detection'] = 1.0, 1.0, 200.0, 150.0

    outputs = []
    for step_num in range(0, 500):
        payload = processor.process(
            **make_face_info(face_info, step_num, 10.0),
        )
        if payload is not None:
            outputs.extend(payload['events'])

    assert any(out['name'] == 'distraction' for out in outputs)


def test_eyeclose(load_json, get_pytest_signalq_config):
    from signalq_pyml import processors
    config = get_pytest_signalq_config(cv='yandex', mode='testing')

    processor = processors.Runner(config)
    face_info = load_json('single_frame_face_info.json')
    face_info['landmarks68'] = np.asarray(face_info['landmarks68'])
    face_info['head_pose'] = 0.0, 5.0, 10.0
    face_info['detection'] = 1.0, 1.0, 200.0, 150.0
    face_info['eyes_state'] = False, False

    outputs = []
    for step_num in range(0, 500):
        payload = processor.process(
            **make_face_info(face_info, step_num, 10.0),
        )
        if payload is not None:
            outputs.extend(payload['events'])

    assert any(out['name'] == 'eyeclose' for out in outputs)


def test_stuck(load_json, get_pytest_signalq_config):
    import copy

    from signalq_pyml import processors

    config = get_pytest_signalq_config(cv='yandex', mode='testing')

    processor = processors.Runner(config)
    face_info = load_json('single_frame_face_info.json')
    face_info['landmarks68'] = np.asarray(face_info['landmarks68'])
    face_info['head_pose'] = 0.0, 5.0, 10.0
    face_info['detection'] = 1.0, 1.0, 200.0, 150.0
    face_info['eyes_state'] = True, True
    face_info['speed'] = np.nan

    face_info_reset = copy.deepcopy(face_info)
    face_info_reset['head_pose'] = 0.0, 5.0, -15.0

    outputs, step_count = [], 0
    for info, steps in zip([face_info, face_info_reset], [900, 30]):
        for step_num in range(0, steps):
            face_info = make_face_info(info, step_num + step_count, 10.0)
            payload = processor.process(**face_info)
            if payload is not None:
                outputs.extend(payload['events'])
        step_count += steps

    assert any(out['name'] == 'stuck' for out in outputs)


def test_blink(load_json, get_pytest_signalq_config):
    import copy

    from signalq_pyml import processors

    config = get_pytest_signalq_config(cv='yandex', mode='testing')

    processor = processors.Runner(config, verbose=True)
    face_info = load_json('single_frame_face_info.json')
    face_info['landmarks68'] = np.asarray(face_info['landmarks68'])
    face_info['head_pose'] = 0.0, 5.0, 10.0
    face_info['detection'] = 1.0, 1.0, 200.0, 150.0
    face_info['eyes_state'] = True, True
    face_info['eyes_scores'] = 0.0, 0.0

    face_info_closed = copy.deepcopy(face_info)
    face_info_closed['eyes_state'] = False, False
    face_info_closed['eyes_scores'] = 0.8, 0.9

    step_count = 0
    for info, steps in zip(
            [face_info, face_info_closed, face_info], [500, 10, 500],
    ):
        for step_num in range(0, steps):
            processor.process(
                **make_face_info(info, step_num + step_count, 10.0),
            )
        step_count += steps

    state = processor.get_state_dict()
    features = state[processors.features.FeatureAggregator.__name__]['cache']

    feature = features['adaptive_blink/default/time/60/count']
    assert feature != 0.0


def test_static_blink(load_json, get_pytest_signalq_config):
    import copy

    from signalq_pyml import processors

    config = get_pytest_signalq_config(cv='yandex', mode='testing')

    processor = processors.Runner(config, verbose=True)
    face_info = load_json('single_frame_face_info.json')
    face_info['landmarks68'] = np.asarray(face_info['landmarks68'])
    face_info['head_pose'] = 0.0, 5.0, 10.0
    face_info['detection'] = 1.0, 1.0, 200.0, 150.0
    face_info['eyes_state'] = True, True

    face_info_closed = copy.deepcopy(face_info)
    face_info_closed['eyes_state'] = False, False

    step_count = 0
    for info, steps in zip(
            [face_info, face_info_closed, face_info], [500, 10, 500],
    ):
        for step_num in range(0, steps):
            processor.process(
                **make_face_info(info, step_num + step_count, 10.0),
            )
        step_count += steps

    state = processor.get_state_dict()
    features = state[processors.features.FeatureAggregator.__name__]['cache']

    feature_static = features['static_head_blink/default/time/60/count']
    feature_stuck = features['stuck_blink/default/time/60/count']
    assert feature_static != 0.0 and feature_stuck != 0.0


def test_occlusion(load_json, get_pytest_signalq_config):
    from signalq_pyml import processors

    config = get_pytest_signalq_config(cv='yandex', mode='testing')

    processor = processors.Runner(config)
    face_info = load_json('single_frame_face_info.json')
    face_info['landmarks68'] = np.asarray(face_info['landmarks68'])
    face_info['head_pose'] = 0.0, 0.0, 10.0
    face_info['detection'] = 1.0, 1.0, 200.0, 150.0

    for step_num in range(0, 500):
        processor.process(
            **make_face_info(
                face_info, step_num, 10.0, aux_args={'mouth_occluded': 0.9},
            ),
        )

    state = processor.get_state_dict()
    mouth_state = state[processors.models.MouthOcclusion.__name__]['occluded']
    assert mouth_state


def test_eye_occlusion(load_json, get_pytest_signalq_config):
    from signalq_pyml import processors

    config = get_pytest_signalq_config(cv='yandex', mode='testing')

    processor = processors.Runner(config)
    face_info = load_json('single_frame_face_info.json')
    face_info['landmarks68'] = np.asarray(face_info['landmarks68'])
    face_info['head_pose'] = 0.0, 0.0, 10.0
    face_info['detection'] = 1.0, 1.0, 200.0, 150.0

    for step_num in range(0, 100):
        processor.process(
            **make_face_info(
                face_info, step_num, 10.0, aux_args={'eyes_occluded': True},
            ),
        )

    state = processor.get_state_dict()
    mouth_state = state[processors.models.EyeOcclusion.__name__]['occluded']
    assert mouth_state


def test_smoking(load_json, get_pytest_signalq_config):
    from signalq_pyml import processors

    config = get_pytest_signalq_config(cv='yandex', mode='testing')

    processor = processors.Runner(config)
    face_info = load_json('single_frame_face_info.json')
    face_info['landmarks68'] = np.asarray(face_info['landmarks68'])
    face_info['head_pose'] = 0.0, 0.0, -40.0
    face_info['detection'] = 1.0, 1.0, 200.0, 150.0

    outputs = []
    for step_num in range(0, 500):
        payload = processor.process(
            **make_face_info(
                face_info, step_num, 10.0, aux_args={'smoking_score': 0.99},
            ),
        )
        if payload is not None:
            outputs.extend(payload['events'])

    assert any(out['name'] == 'smoking' for out in outputs)


def test_seatbelt(load_json, get_pytest_signalq_config):
    from signalq_pyml import processors

    config = get_pytest_signalq_config(cv='yandex', mode='testing')

    processor = processors.Runner(config)
    face_info = load_json('single_frame_face_info.json')
    face_info['landmarks68'] = np.asarray(face_info['landmarks68'])
    face_info['head_pose'] = 0.0, 0.0, -40.0
    face_info['detection'] = 1.0, 1.0, 200.0, 150.0

    outputs = []
    for step_num in range(0, 11000):
        payload = processor.process(
            **make_face_info(
                face_info,
                step_num,
                10.0,
                aux_args={'seatbelt_score': 0.00001},
            ),
        )
        if payload is not None:
            outputs.extend(payload['events'])

    assert any(out['name'] == 'seatbelt' for out in outputs)


def test_wipe(load_json, get_pytest_signalq_config):
    from signalq_pyml import processors

    config = get_pytest_signalq_config(cv='yandex', mode='testing')

    processor = processors.Runner(config)
    face_info = load_json('single_frame_face_info.json')
    face_info['landmarks68'] = np.asarray(face_info['landmarks68'])
    face_info['head_pose'] = 0.0, 0.0, 0.0
    face_info['detection'] = 1.0, 1.0, 200.0, 150.0

    outputs = []

    for step_num in range(0, 500):
        processor._processors['Yawn'].state.last_timestamp = step_num / 30
        payload = processor.process(
            **make_face_info(
                face_info, step_num, 10.0, aux_args={'eyewipe_score': 1e-11},
            ),
        )
        if payload is not None:
            outputs.extend(payload['events'])

    for step_num in range(500, 1000):
        processor._processors['Yawn'].state.last_timestamp = step_num / 30
        payload = processor.process(
            **make_face_info(
                face_info, step_num, 10.0, aux_args={'eyewipe_score': 0.999},
            ),
        )
        if payload is not None:
            outputs.extend(payload['events'])

    assert any(out['name'] == 'eye_touching' for out in outputs)


def test_camera_pose(load_json, get_pytest_signalq_config):
    from signalq_pyml import processors

    config = get_pytest_signalq_config(cv='yandex', mode='testing')

    processor = processors.Runner(config)
    face_info = load_json('single_frame_face_info.json')
    face_info['landmarks68'] = np.asarray(face_info['landmarks68'])

    zero_dof3 = (0.0, 0.0, 0.0)
    bad_pose_imu = (2.4, 9.6, 0.0)

    outputs = []
    for step_num in range(0, 1000):
        payload = processor.process(
            **make_face_info(
                face_info,
                step_num,
                10.0,
                aux_args={'imu': (zero_dof3, bad_pose_imu, zero_dof3)},
            ),
        )
        if payload is not None:
            outputs.extend(payload['events'])

    assert any(out['name'] == 'bad_camera_pose' for out in outputs)


def test_phone(load_json, get_pytest_signalq_config):
    from signalq_pyml import processors

    config = get_pytest_signalq_config(cv='yandex', mode='testing')

    processor = processors.Runner(config)
    face_info = load_json('single_frame_face_info.json')
    face_info['landmarks68'] = np.asarray(face_info['landmarks68'])
    face_info['head_pose'] = 0.0, 0.0, 10.0
    face_info['detection'] = 1.0, 1.0, 200.0, 150.0

    outputs = []
    for step_num in range(0, 10000):
        payload = processor.process(
            **make_face_info(
                face_info,
                step_num,
                10.0,
                aux_args={'phone_scores': (0.0, 0.99)},
            ),
        )
        if payload is not None:
            outputs.extend(payload['events'])

    assert any(out['name'] == 'phone' for out in outputs)
    assert any(out['name'] == 'best_shot' for out in outputs)


def test_trash_frames(load_json, get_pytest_signalq_config):
    from signalq_pyml import processors

    config = get_pytest_signalq_config(cv='yandex', mode='testing')

    processor = processors.Runner(config)
    face_info = load_json('single_frame_face_info.json')
    face_info['landmarks68'] = np.asarray(face_info['landmarks68'])
    face_info['head_pose'] = 0.0, 0.0, 10.0
    face_info['detection'] = 1.0, 1.0, 200.0, 150.0
    face_info['detection_result'] = 0

    outputs = []
    for step_num in range(0, 3000):
        payload = processor.process(
            **make_face_info(
                face_info, step_num, 10.0, aux_args={'trash_score': 0.99},
            ),
        )
        if payload is not None:
            outputs.extend(payload['events'])

    assert any(out['name'] == 'trash_frames' for out in outputs)


def test_camera_overturn(load_json, open_file, get_pytest_signalq_config):
    from signalq_pyml import processors
    from signalq_pyml.processors.common import histories

    config = get_pytest_signalq_config(cv='yandex', mode='testing')

    processor = processors.Runner(config)
    face_info = load_json('single_frame_face_info.json')
    face_info['landmarks68'] = np.asarray(face_info['landmarks68'])

    b64_imus = open_file('imu-overturn.b64', mode='r', encoding=None).read()
    imus = histories.decompress_array(b64_imus)

    outputs = []
    for step_num, imu_arr in enumerate(imus):
        payload = processor.process(
            **make_face_info(
                face_info, step_num, 10.0, aux_args={'imu': imu_arr},
            ),
        )
        if payload is not None:
            outputs.extend(payload['events'])

    assert any(out['name'] == 'camera_overturn' for out in outputs)


@pytest.mark.skip(reason='this test requires model loading')
def test_tiredness(
        load_json, get_pytest_signalq_config, load_models, model_dir,
):
    import os

    from signalq_pyml import processors
    from signalq_pyml import get_config

    model_path = os.path.join(model_dir, 'tiredness', 'tired-model.bin')
    meta_path = os.path.join(model_dir, 'tiredness', 'tired-meta.json')
    tz_path = os.path.join(model_dir, 'timezone', 'tz.npz')

    config = get_config(cv='yandex', mode='testing')

    config['Drowsiness']['model_path'] = model_path
    config['Drowsiness']['meta_path'] = meta_path
    config['LocalTime']['timezone_array_path'] = tz_path

    config = get_pytest_signalq_config(
        cv='yandex', mode='testing', config=config,
    )

    processor = processors.Runner(config)
    face_info = load_json('single_frame_face_info.json')
    face_info['landmarks68'] = np.asarray(face_info['landmarks68'])

    outputs = []
    for step_num in range(3000):
        payload = processor.process(
            **make_face_info(face_info, step_num, 10.0),
        )
        if payload is not None:
            outputs.extend(payload['events'])

    # TODO: fix dummy check
    assert True


@pytest.mark.skip(reason='this test requires model loading')
def test_model_processors(
        load_json, get_pytest_signalq_config, load_models, model_dir,
):
    import os

    from signalq_pyml import processors
    from signalq_pyml import get_config

    model_path = os.path.join(model_dir, 'tiredness', 'tired-model.bin')
    meta_path = os.path.join(model_dir, 'tiredness', 'tired-meta.json')
    tz_path = os.path.join(model_dir, 'timezone', 'tz.npz')
    acc_path = os.path.join(model_dir, 'acceleration', 'tz.npz')

    config = get_config(cv='yandex', mode='testing')

    config['Drowsiness']['model_path'] = model_path
    config['Drowsiness']['meta_path'] = meta_path
    config['LocalTime']['timezone_array_path'] = tz_path
    config['Acceleration']['model_path'] = acc_path

    config = get_pytest_signalq_config(
        cv='yandex', mode='testing', config=config,
    )

    processor = processors.Runner(config)
    face_info = load_json('single_frame_face_info.json')
    face_info['landmarks68'] = np.asarray(face_info['landmarks68'])

    outputs = []
    for step_num in range(3000):
        payload = processor.process(
            **make_face_info(face_info, step_num, 10.0),
        )
        if payload is not None:
            outputs.extend(payload['events'])

    assert True  # dummy check over here
