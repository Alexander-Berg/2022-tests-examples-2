INSERT INTO chatterbox_admin.attachments_collections (
    id,
    name,
    description,
    categories,
    active
)
VALUES
    ('00000000-0000-0000-0000-000000000001', 'awesome collection', 'awesome description', '{}', FALSE),
    ('00000000-0000-0000-0000-000000000002', 'another collection', 'beautiful description', '{"taxi", "eda"}', TRUE),
    ('00000000-0000-0000-0000-000000000003', 'good collection', NULL, '{"taxi", "eda"}', TRUE);


INSERT INTO chatterbox_admin.attachments_files (
    id,
    name,
    description,
    hash,
    deleted
)
VALUES
    ('ffffffff-0000-0000-0000-000000000001', 'file_001.jpeg', 'how to be happy', 'abcdef000000', FALSE),
    ('ffffffff-0000-0000-0000-000000000002', 'file_002.jpeg', 'so close', 'abcdef000001', TRUE),
    ('ffffffff-0000-0000-0000-000000000003', 'file_003.gif', 'dance penguin', 'abcdef000002', FALSE),
    ('ffffffff-0000-0000-0000-000000000004', 'file_004.gif', 'need some sleep', 'abcdef000003', FALSE),
    ('ffffffff-0000-0000-0000-000000000005', 'file_005.jpeg', 'so sad', '0a3666a0710c08aa6d0de92ce72beeb5b93124cce1bf3701c9d6cdeb543cb73e', FALSE),
    ('ffffffff-0000-0000-0000-000000000006', 'file_006.gif', 'need some sleep', 'abcdef000004', FALSE);


INSERT INTO chatterbox_admin.attachments_collections_files(
    collection_id,
    file_id
)
VALUES
    ('00000000-0000-0000-0000-000000000001', 'ffffffff-0000-0000-0000-000000000001'),
    ('00000000-0000-0000-0000-000000000001', 'ffffffff-0000-0000-0000-000000000005'),
    ('00000000-0000-0000-0000-000000000002', 'ffffffff-0000-0000-0000-000000000001'),
    ('00000000-0000-0000-0000-000000000002', 'ffffffff-0000-0000-0000-000000000002'),
    ('00000000-0000-0000-0000-000000000002', 'ffffffff-0000-0000-0000-000000000003'),
    ('00000000-0000-0000-0000-000000000003', 'ffffffff-0000-0000-0000-000000000006');


INSERT INTO chatterbox_admin.attachments_file_tags(
    file_id,
    tag_name
)
VALUES
    ('ffffffff-0000-0000-0000-000000000001', 'happy'),
    ('ffffffff-0000-0000-0000-000000000001', 'nice'),
    ('ffffffff-0000-0000-0000-000000000001', 'fun'),
    ('ffffffff-0000-0000-0000-000000000003', 'animal'),
    ('ffffffff-0000-0000-0000-000000000003', 'fun'),
    ('ffffffff-0000-0000-0000-000000000004', 'sad'),
    ('ffffffff-0000-0000-0000-000000000005', 'sad');

INSERT INTO chatterbox_admin.logics(
    id,
    name,
    url
)
VALUES
    ('ffffffff-0000-0000-0000-000000000001', 'awesome name', 'awesome url'),
    ('ffffffff-0000-0000-0000-000000000002', 'not my name', 'not my url');


INSERT INTO chatterbox_admin.themes_logics(
    logic_id,
    theme
)
VALUES
    ('ffffffff-0000-0000-0000-000000000001', 'awesome theme'),
    ('ffffffff-0000-0000-0000-000000000002', 'awesome theme'),
    ('ffffffff-0000-0000-0000-000000000001', 'not my theme');
