INSERT INTO supportai.entities (id, project_slug, version_id, slug, title, type, extractor, extractor_parameters)
VALUES
(1, 'ya_lavka', 1, 'entity1', 'Entity 1', 'int', 'regular_expression', '{"regular_expression": "[0-9]+"}'::jsonb),
(2, 'ya_lavka', 1, 'entity2', 'Entity 2', 'str', 'choice_from_variants', '{"variants": [{"regular_expression": "a|A", "value": "A"}]}'::jsonb),
(3, 'ya_lavka', 1, 'entity3', 'Entity 3', 'bool', 'custom', '{}'::jsonb);

ALTER SEQUENCE supportai.entities_id_seq RESTART WITH 4;

INSERT INTO supportai.features (
    id,
    project_slug,
    version_id,
    slug,
    description,
    type,
    domain,
    clarification_type,
    force_question,
    clarifying_question,
    entity_id,
    entity_extract_order
)
VALUES
(1, 'ya_lavka', 1, 'feature1', 'Feature 1', 'str', '{}', 'from_text', false, NULL, 3 , 0);
