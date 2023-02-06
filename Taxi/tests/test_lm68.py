def test_eye_width(load_json):

    from signalq_pyml.processors.common import lm68

    import numpy as np
    landmarks = np.array(load_json('single_landmarks.json'))

    left = lm68.eye_h2w(landmarks68=landmarks, side=lm68.SIDE_LEFT)
    right = lm68.eye_h2w(landmarks68=landmarks, side=lm68.SIDE_RIGHT)

    assert left > 0.25 and right > 0.25
