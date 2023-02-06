INSERT INTO supportai.models (id, title, model_slug, version, s3_path, language, preprocess_type, model_arch) VALUES
(1, 'Драйв', 'ya_drive_dialog', '1', NULL,'ru', 'one_message', 'dialog_text_classification'),
(2, 'Модель онлайн школы', 'justschool_dialog', '1', NULL, 'ru', 'one_message', 'knn_text_classification'),
(3, 'Почта', 'russian_post_b2b_orders_dialog', '1', NULL, 'ru', 'one_message', 'label_embedding'),
(4, 'Такси', 'taxi_client_dialog', '1', NULL, 'ru', 'united_message', 'text_classification'),
(5, 'ДМ', 'detmir_dialog', '1', NULL, 'ru', 'one_message', 'text_classification'),
(6, 'ДМ', 'detmir_dialog', '2', NULL, 'ru', 'one_message', 'text_classification'),
(7, 'ДМ', 'detmir_dialog', '3', NULL, 'ru', 'one_message', 'text_classification'),
(8, 'ДМ', 'detmir_dialog', '4', NULL, 'ru', 'one_message', 'text_classification'),
(9, 'ДМ стабильная', 'detmir_dialog', '5', NULL, 'ru', 'one_message', 'text_classification'),
(10, 'Модель генотека', 'genotek_dialog', '1', NULL, 'ru', 'one_message', 'sentence_bert'),
(11, 'Модель приветствий', 'dialog_act_hello', '1', NULL, 'ru', 'one_message', 'bert_binary_clf'),
(12, 'Модель c S3', 'genotek_dialog', '2', 'some_s3_path', 'ru', 'one_message', 'sentence_bert'),
(13, 'Модель useresponse', 'useresponse_search', '1', NULL, 'en', 'one_message', 'qa'),
(14, 'Модель сентимента', 'sentiment', '1', NULL, 'ru', 'one_message', 'bert_multihead_clf'),
(15, 'Embedder', 'sbert_embedder', '1', NULL, 'ru', 'one_message', 'sbert_embedder')
;

ALTER SEQUENCE supportai.models_id_seq RESTART WITH 25;

INSERT INTO supportai.workers (id, model_id, worker_id, shard_id) VALUES
(1, 1, 5, 'shard1'),
(2, 2, 4, 'shard1'),
(3, 3, 3, 'shard1'),
(4, 4, 2, 'shard1'),
(5, 9, 1, 'shard1'),
(6, 3, 0, 'shard1'),
(7, 3, 0, 'shard2'),
(8, 10, 6, 'shard1'),
(9, 11, 7, 'shard1'),
(10, 12, 8, 'shard1'),
(11, 13, 9, 'shard1'),
(13, 14, 10, 'shard1'),
(12, 15, 11, 'shard1')
;

ALTER SEQUENCE supportai.workers_id_seq RESTART WITH 25;
