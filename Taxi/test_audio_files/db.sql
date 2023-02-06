INSERT INTO supportai.project_configs (project_slug, call_service) VALUES
('slug1', 'ivr_framework'), ('slug2', 'ivr_framework'), ('slug3', 'ivr_framework');

UPDATE supportai.project_configs SET audio_files_secret = '' WHERE project_slug = 'slug1';


INSERT INTO supportai.audio_files_metadata (filename, call_service, project_slug, user_filename, user_comment, uploaded_at)
VALUES
('file1.wav', 'ivr_framework', 'slug1', 'file1_user_filename', 'file1_user_comment', '2020-1-1 00:00:00+0000'),
('file2.wav', 'ivr_framework', 'slug1', 'file2_user_filename', NULL, '2020-1-1 00:00:00+0000'),
('file1.wav', 'ivr_framework', 'slug2', NULL, NULL, '2020-1-1 00:00:00+0000'),
('vox_file.mp3', 'voximplant', 'slug1', NULL, NULL, '2020-1-1 00:00:00+0000'),
('vox_file_2.mp3', 'voximplant', 'slug2', NULL, NULL, '2020-1-1 00:00:00+0000');
