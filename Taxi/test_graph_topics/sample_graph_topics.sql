INSERT INTO supportai.topics_folders (
    id,
    project_slug,
    version_id,
    title
)
VALUES
(1, 'ya_lavka', 1, 'Бонусы');

ALTER SEQUENCE supportai.topics_folders_id_seq RESTART WITH 2;

INSERT INTO supportai.topic_to_folder (
    version_id,
    folder_id,
    topic_id
)
VALUES
(1, 1, 2),
(1, 1, 3),
(1, 1, 4);

INSERT INTO supportai.topic_rules (
    id,
    project_slug,
    version_id,
    topic_id,
    type,
    specified,
    content,
    extra
)
VALUES
(1, 'ya_lavka', 1, 1, 'addition', 'rule', 'text contains "заказ"', '{}');

ALTER SEQUENCE supportai.topic_rules_id_seq RESTART WITH 2;

INSERT INTO supportai.features (project_slug, version_id, slug)
VALUES ('ya_lavka', 1, 'text');
