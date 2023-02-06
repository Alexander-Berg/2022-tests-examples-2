INSERT INTO meta.tag_names (id, name)
VALUES
       (1003, 'bla-bla'),
       (1004, 'make me laugh'),
       (1005, 'test1'),
       (1006, 'seach_text'),
       (1007, 'space space');

INSERT INTO meta.relations (topic_id, tag_name_id)
VALUES
       (2002, 1003),
       (2002, 1004),
       (2002, 1005),
       (2002, 1006),
       (2002, 1007),
       (2001, 1003);
