INSERT INTO meta.tag_names (id, name)
VALUES
       (1000, 'tag0'),
       (1001, 'tag1'),
       (1002, 'tag2'),
       (1003, 'tag3'),
       (1004, 'tag4');

INSERT INTO meta.topics (id, name, description, is_financial)
VALUES
       (2000, 'topic0', 'topic0_description', False),
       (2001, 'topic1', 'topic1_description', False),
       (2002, 'topic2', 'financial_topic', True),
       (2003, 'topic3', 'topic3_description', False);

INSERT INTO meta.relations (topic_id, tag_name_id)
VALUES
       (2000, 1000),
       (2000, 1001),
       (2001, 1002),
       (2002, 1000),
       (2002, 1002),
       (2003, 1004);

INSERT INTO meta.tag_descriptions (tag_name_id, text, updated_at, author, ticket)
VALUES
    (1000, 'description tag0', '2021-11-24 16:38:59'::timestamp, 'author_tag0', NULL),
    (1001, 'description tag1', '2021-11-24 16:39:59'::timestamp, 'author_tag1', 'TICKET-0001'),
    (1002, 'description tag2', '2021-11-24 16:48:59'::timestamp, 'author_tag2', NULL);
