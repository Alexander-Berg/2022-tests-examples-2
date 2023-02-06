import datetime

from dmp_suite.maintenance.monitoring.utils import WindowCounter


def test_window_counter(freezer):
    cnt = WindowCounter()

    cnt.increment()
    freezer.tick(datetime.timedelta(seconds=15))
    cnt.increment()
    freezer.tick(datetime.timedelta(seconds=5))
    cnt.increment()
    freezer.tick(datetime.timedelta(seconds=5))

    assert cnt.value() == 3

    # По прошествии пяти минут с момента первого инкремента,
    # он должен перестать учитываться
    freezer.tick(datetime.timedelta(seconds=5 * 60 - 20 + 1))
    assert cnt.value() == 2

