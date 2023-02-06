INSERT INTO meta.tag_names (id, name)
VALUES
       (1000, 'tag0'),
       (1001, 'tag1'),
       (1002, 'tag2');

INSERT INTO meta.topics (id, name, description)
VALUES
       (2000, 'topic0', 'topic0_description');

INSERT INTO meta.topics (id, name, description, is_financial)
VALUES
       (2001, 'topic1', 'topic1_description', False),
       (2002, 'topic2', 'topic2_description', True);

INSERT INTO meta.endpoints (topic_id, tvm_service_name, url)
VALUES
       (2001, 'tvm_name1', 'tvm_name1.taxi.yandex.net'),
       (2002, 'tvm_name2', 'tvm_name2.taxi.yandex.net');

INSERT INTO meta.relations (topic_id, tag_name_id)
VALUES
       (2000, 1000),
       (2000, 1001),
       (2001, 1002);
