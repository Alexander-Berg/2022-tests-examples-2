INSERT INTO supportai.project_configs (project_slug, call_service, audio_files_secret) VALUES
('project_ivr_framework_no_secret', 'ivr_framework', NULL),
('project_ivr_framework_with_secret', 'ivr_framework', 'THIS SECRET SHOULD NOT AFFECT ANYTHING'),
('project_voximplant_no_secret', 'voximplant', NULL),
('project_voximplant_with_secret', 'voximplant', '1234567890'),
('project_ya_telephony_no_secret', 'ya_telephony', NULL),
('project_ya_telephony_with_secret', 'ya_telephony', '1234567890');


INSERT INTO supportai.audio_files_metadata (filename, project_slug, uploaded_at) VALUES
('filename.wav', 'project_ivr_framework_no_secret', '2020-1-1 00:00:00+0000'),
('filename.wav', 'project_ivr_framework_with_secret', '2020-1-1 00:00:00+0000'),
('filename.mp3', 'project_voximplant_no_secret', '2020-1-1 00:00:00+0000'),
('filename.mp3', 'project_voximplant_with_secret', '2020-1-1 00:00:00+0000'),
('filename.wav', 'project_ya_telephony_no_secret', '2020-1-1 00:00:00+0000'),
('filename.wav', 'project_ya_telephony_with_secret', '2020-1-1 00:00:00+0000');
