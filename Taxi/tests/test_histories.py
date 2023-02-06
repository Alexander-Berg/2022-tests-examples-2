def test_array_history():
    from signalq_pyml.processors.common import histories

    history = histories.ArrayHistory(1800)

    for i in range(3602):
        history.add(i)

    easy_h = history.earliest_n(10)
    easy_t = history.latest_n(10)

    assert max(easy_t) == 3601.0 and min(easy_t) == 3592.0
    assert min(easy_h) == 1802.0 and max(easy_h) == 1811.0

    hard_h = history.earliest_n(1900)
    hard_t = history.latest_n(1900)

    assert len(hard_t) == 1800 and len(hard_h) == 1800
