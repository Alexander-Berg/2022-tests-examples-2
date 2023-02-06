from projects.support.learning import topics_encoder


def test_topics_encoder():
    topics = ['a', 'b', 'a', 'c', 'd']
    dttm = [
        '2021-01-01',
        '2020-12-15',
        '2021-01-01',
        '2020-12-01',
        '2020-12-01',
    ]

    encoder = topics_encoder.TopicEncoder()
    encoder.fit(topics=topics, dttms=dttm)
    assert encoder.get_number_of_topics() == 4
    assert encoder.get_topic2label_map() == {'a': 0, 'b': 1, 'c': 2, 'd': 3}
    assert encoder.transform(['a', 'd', 'b', 'b']) == [0, 3, 1, 1]
    assert encoder.transform(['a', 'e', 'b']) == [
        0,
        topics_encoder.UNKNOWN_TOPIC_LABEL,
        1,
    ]

    encoder = topics_encoder.TopicEncoder(max_topics=4)
    encoder.fit(topics=topics, dttms=dttm)
    assert encoder.get_number_of_topics() == 4
    assert encoder.get_topic2label_map() == {'a': 0, 'b': 1, 'c': 2, 'd': 3}
    assert encoder.transform(['a', 'd', 'c', 'b', 'b']) == [0, 3, 2, 1, 1]
    assert encoder.transform(['a', 'e', 'b']) == [
        0,
        topics_encoder.UNKNOWN_TOPIC_LABEL,
        1,
    ]

    encoder = topics_encoder.TopicEncoder(max_topics=3)
    encoder.fit(topics=topics, dttms=dttm)
    assert encoder.get_number_of_topics() == 3
    assert encoder.get_topic2label_map() == {
        'a': 0,
        'b': 1,
        topics_encoder.OTHER_TOPICS_NAME: 2,
    }
    assert encoder.transform(['a', 'd', 'c', 'b', 'b']) == [0, 2, 2, 1, 1]
    assert encoder.transform(['a', 'e', 'b']) == [0, 2, 1]

    encoder = topics_encoder.TopicEncoder(begin_dttm='2020-12-15')
    encoder.fit(topics=topics, dttms=dttm)
    assert encoder.get_number_of_topics() == 3
    assert encoder.get_topic2label_map() == {
        'a': 0,
        'b': 1,
        topics_encoder.OTHER_TOPICS_NAME: 2,
    }
    assert encoder.transform(['a', 'd', 'c', 'b', 'b']) == [0, 2, 2, 1, 1]
    assert encoder.transform(['a', 'e', 'b']) == [0, 2, 1]

    encoder = topics_encoder.TopicEncoder(
        max_topics=2, begin_dttm='2020-12-15',
    )
    encoder.fit(topics=topics, dttms=dttm)
    assert encoder.get_number_of_topics() == 2
    assert encoder.get_topic2label_map() == {
        'a': 0,
        topics_encoder.OTHER_TOPICS_NAME: 1,
    }
    assert encoder.transform(['a', 'd', 'c', 'b', 'b']) == [0, 1, 1, 1, 1]
    assert encoder.transform(['a', 'e', 'b']) == [0, 1, 1]

    encoder = topics_encoder.TopicEncoder(
        max_topics=3, begin_dttm='2020-12-16',
    )
    encoder.fit(topics=topics, dttms=dttm)
    assert encoder.get_number_of_topics() == 2
    assert encoder.get_topic2label_map() == {
        'a': 0,
        topics_encoder.OTHER_TOPICS_NAME: 1,
    }
    assert encoder.transform(['a', 'd', 'c', 'b', 'b']) == [0, 1, 1, 1, 1]
    assert encoder.transform(['a', 'e', 'b']) == [0, 1, 1]
