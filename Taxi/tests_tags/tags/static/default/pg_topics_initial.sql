INSERT INTO meta.topics (id, name, description)
VALUES
       (2000, 'topic0', 'topic0_description'),
       (2001, 'topic1', 'topic1_description'),
       (2002, 'topic2', 'topic2_description');

INSERT INTO meta.relations (topic_id, tag_name_id)
VALUES
       (2000, 2000),
       (2000, 2001),
       (2001, 2001),
       (2001, 2003),
       (2001, 2004),
       (2001, 2005);
