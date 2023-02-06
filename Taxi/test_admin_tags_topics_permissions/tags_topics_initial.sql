INSERT INTO meta.tag_names (id, name)
VALUES
       (1000, 'topic_tag1'),
       (1001, 'topic_tag0'),
       (1002, 'finance_topic_tag'),
       (1003, 'no_topic_tag'),
       (1004, 'multi_topic_tag'),
       (1005, 'audited_tag');

INSERT INTO meta.topics (id, name, description, is_financial)
VALUES
       (2000, 'topic', 'topic_description', False),
       (2002, 'finance_topic', 'topic2_description', True),
       (2004, 'audited_topic', 'should_be_audited', False);

INSERT INTO meta.relations (topic_id, tag_name_id)
VALUES
       (2000, 1000),
       (2000, 1001),
       (2002, 1002),
       (2000, 1004),
       (2002, 1004),
       (2004, 1005);
