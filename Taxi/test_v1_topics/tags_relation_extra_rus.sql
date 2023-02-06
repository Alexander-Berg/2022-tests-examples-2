INSERT INTO meta.topics (id, name, description, is_financial)
VALUES
       (2003, 'rus_топик', 'rus_description', False);

INSERT INTO meta.tag_names (id, name)
VALUES
       (1008, 'rus_тег');

INSERT INTO meta.relations (topic_id, tag_name_id)
VALUES
       (2003, 1008);

