INSERT INTO supportai.scenario_graph (
    project_slug,
    version_id,
    topic_id,
    title,
    slug,
    group_name,
    valid,
    folder_id
)
VALUES
('ya_lavka', 1, 1, 'Sample', 'sample', 'main', TRUE, NULL);

INSERT INTO supportai.features (project_slug, version_id, slug)
VALUES ('ya_lavka', 1, 'text');
