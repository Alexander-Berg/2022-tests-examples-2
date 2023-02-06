# encoding=utf8
from zoo.drivers.extractors import (QueueFeatures)


def test1():
    queue_max_window = [
        {'log_source':'orders', 'cost':4, 'timestamp':12345678},
        {'log_source':'orders', 'cost':3, 'timestamp': 12345679},
        {'log_source':'support_tagging_predictions', 'tag_1':3, 'timestamp':12345680},
        {'log_source':'support_tagging_predictions', 'tag_1':5, 'timestamp':12345682}
    ]
    w2 = QueueFeatures(queue_max_window, 2, 12345685)

    assert w2._get_sub_queue_from_source('support_tagging_predictions') == [
        {'log_source': 'support_tagging_predictions', 'tag_1': 3, 'timestamp': 12345680},
        {'log_source': 'support_tagging_predictions', 'tag_1': 5, 'timestamp': 12345682}
    ]

    assert w2.sum_aggregate('support_tagging_predictions', 'tag_1') == 8


if __name__ == '__main__':
    test1()

    # // home / taxi_ml / dev / drivers_churn / simple_time_machine_fe




