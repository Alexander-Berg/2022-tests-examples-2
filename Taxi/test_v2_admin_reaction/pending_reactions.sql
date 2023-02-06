INSERT INTO state.reactions
  (reaction_id, namespace_id, workflow_id, workflow_instance_id,                                path,                                   cron_string,   status,   created_at)
VALUES
  ('121',           '221',     '321',      'cloned-e648e648-7b9a-496b-bf50-fd27d55326f6',       '/taxi/reposition/reaction1', '0 0 7 * * ?', 'PENDING', '2018-11-26T08:00:00+0000'),
  ('tmp_122',       '',        '322',      '322',                                               '/taxi/reposition/reaction2', '0 0 7 * * ?', 'PENDING', '2018-11-26T08:00:00+0000');
