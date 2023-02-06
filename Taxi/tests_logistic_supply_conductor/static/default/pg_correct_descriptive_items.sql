INSERT INTO logistic_supply_conductor.descriptive_items ("name", title, "text", content_code_hint, passthrough_revision)
VALUES
('foo', 'foo', 'bar', 'free_minutes', NEXTVAL('descriptive_items_passthrough_revision_seq')),
('baz', 'bar', 'baz', NULL, NEXTVAL('descriptive_items_passthrough_revision_seq'));
