INSERT INTO meta.tag_names (id, name)
VALUES
       (1000, 'tag0'),
       (1001, 'tag1'),
       (1002, 'tag2'),
       (1003, 'tag3');

INSERT INTO meta.tag_descriptions (tag_name_id, text, updated_at, author, ticket)
VALUES
       (1001, 'tag1_description', '2021-11-24 16:38:59'::timestamp, 'author_tag1', NULL),
       (1002, 'tag2_description', '2021-11-24 15:38:59'::timestamp, 'author_tag2', 'TICKET-0001');
