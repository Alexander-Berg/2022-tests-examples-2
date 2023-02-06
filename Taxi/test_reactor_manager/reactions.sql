INSERT INTO state.reactions
  (reaction_id, namespace_id, workflow_id, workflow_instance_id, path,                                   cron_string,   status,   created_at)
VALUES
  ('121',       '121',        '121',       '313',       '/taxi/reposition/reaction1', '0 0 7 * * ?', 'ACTIVE', '2018-11-26T08:00:00+0000'),
  ('122',       '221',        '122',       '323',       '/taxi/reposition/reaction2', '0 0 7 * * ?', 'PAUSED', '2018-11-26T08:00:00+0000'),
  ('123',       '321',        '123',       '333',       '/taxi/reposition/reaction3', '0 0 7 * * ?', 'ACTIVE', '2018-11-26T08:00:00+0000'),
  ('124',       '421',        '124',       '343',       '/taxi/reposition/reaction4', '0 0 7 * * ?', 'ACTIVE', '2018-11-26T08:00:00+0000');

UPDATE state.reactions_notifications SET notification_status = 'ENABLED' WHERE reaction_id = '121';
UPDATE state.reactions_notifications SET notification_status = 'DISABLED_BY_TIME' WHERE reaction_id = '124';
