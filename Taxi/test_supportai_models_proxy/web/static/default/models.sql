INSERT INTO supportai.models (id, title, model_slug, version, model_settings) VALUES
(
    1,
    'Драйв',
    'ya_drive_dialog',
    '1',
    '{"model_type": "dialog_text_classification", "s3_path": null, "model_kind": "sentence_bert", "language": "ru", "preprocess_type": "one_message"}'
),
(
    2,
    'Модель онлайн школы',
    'justschool_dialog',
    '1',
    '{"model_type": "knn_one_message_text_classification", "s3_path": null, "model_kind": "knn_text_classification", "language": "ru", "preprocess_type": "one_message"}'
),                                                                                 (
    3,
    'Почта',
    'russian_post_b2b_orders_dialog',
    '1',
    '{"model_type": "label_embedding_based_on_one_message", "s3_path": null, "model_kind": "label_embedding", "language": "ru", "preprocess_type": "one_message"}'
);

ALTER SEQUENCE supportai.models_id_seq RESTART WITH 100;


INSERT INTO supportai.slots (id, worker_id, shard_id, state) VALUES
(1, 0, 'shard1', ''),
(2, 1, 'shard1', ''),
(3, 2, 'shard1', ''),
(4, 0, 'shard2', ''),
(5, 1, 'shard2', ''),
(6, 2, 'shard2', '');

ALTER SEQUENCE supportai.slots_id_seq RESTART WITH 100;


INSERT INTO supportai.model_to_slot (slot_id, model_id) VALUES
(1, 1),
(2, 2),
(3, 3);


INSERT INTO supportai.model_topics (id, model_id, slug, key_metric, threshold) VALUES
(1, 1, 'hello', 'precision', 0.6),
(2, 1, 'bye', 'precision', 0.7);

ALTER SEQUENCE supportai.model_topics_id_seq RESTART WITH 100;


INSERT INTO supportai.model_test_data (id, model_id, ground_truth_slug, probabilities) VALUES
(1, 1, 'hello', '[{"slug": "hello", "probability": 0.7}]'),
(2, 1, 'bye', '[{"slug": "hello", "probability": 0.7}]');

ALTER SEQUENCE supportai.model_test_data_id_seq RESTART WITH 100;
