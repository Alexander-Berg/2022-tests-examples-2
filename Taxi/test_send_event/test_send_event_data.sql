INSERT INTO eats_restapp_communications.send_event_data (
    event_id,
    event_type,
    event_mode,
    recipients,
    data,
    masked_data,
    deleted_at
) VALUES (
    'fake_task',
    'password-request-reset',
    'asap',
    '{"emails_types": [], "recipients": {"partnerish_uuids": ["1a"]}}'::JSONB,
    '{}'::JSONB,
    NULL,
    NULL
), (
    'specific_task',
    'password-request-reset',
    'asap',
    '{"emails_types": [], "recipients": {"specific": ["special_recipient"]}}'::JSONB,
    '{}'::JSONB,
    NULL,
    NULL
), (
    'place_ids_task',
    'password-request-reset',
    'asap',
    '{"emails_types": ["my_email_type"], "recipients": {"place_ids": [1, 2, 3]}}'::JSONB,
    '{}'::JSONB,
    NULL,
    NULL
), (
    'all_partnerts_task',
    'password-request-reset',
    'asap',
    '{"emails_types": ["all_partners"], "recipients": {"place_ids": [1, 2, 3, 5]}}'::JSONB,
    '{}'::JSONB,
    NULL,
    NULL
), (
    'all_types_fake_task',
    'password-request-reset',
    'asap',
    '{"emails_types": ["my_email_type"], "recipients": {"place_ids": [1]}}'::JSONB,
    '{}'::JSONB,
    NULL,
    NULL
), (
    'restart_task',
    'password-request-reset',
    'asap',
    '{"emails_types": ["my_email_type"], "recipients": {"emails": ["valid_email", "invalid_email"]}}'::JSONB,
    '{}'::JSONB,
    NULL,
    NULL
), (
    'emails_types_task',
    'password-request-reset',
    'asap',
    '{"emails_types": ["my_email_type", "other_email_type"], "recipients": {"place_ids": [1, 2, 4]}}'::JSONB,
    '{}'::JSONB,
    NULL,
    NULL
), (
    'finished_task',
    'password-request-reset',
    'asap',
    '{"emails_types": [], "recipients": {"place_ids": [1, 2]}}'::JSONB,
    '{}'::JSONB,
    NULL,
    '2022-07-13 00:00:00'::TIMESTAMPTZ
), (
    'delayed_task',
    'password-request-reset',
    'delayed',
    '{"emails_types": [], "recipients": {"place_ids": [1, 2]}}'::JSONB,
    '{}'::JSONB,
    NULL,
    NULL
), (
    'task_with_data',
    'password-request-reset',
    'asap',
    '{"emails_types": [], "recipients": {"partner_ids": [1, 2]}}'::JSONB,
    '{"some": "value"}'::JSONB,
    NULL,
    NULL
), (
    'task_with_masked_data',
    'password-request-reset',
    'asap',
    '{"emails_types": [], "recipients": {"partner_ids": [1, 2]}}'::JSONB,
    '{}'::JSONB,
    'personal_doc_id',
    NULL
), (
    'delayed_task_with_data',
    'password-request-reset',
    'delayed',
    '{"emails_types": [], "recipients": {"place_ids": [1, 2]}}'::JSONB,
    '{"key": "value", "some": ["a", "b"], "keep": "this"}'::JSONB,
    NULL,
    NULL
), (
    'delayed_task_with_masked_data',
    'password-request-reset',
    'delayed',
    '{"emails_types": [], "recipients": {"place_ids": [1, 2]}}'::JSONB,
    '{}'::JSONB,
    'personal_doc_id',
    NULL
), (
    'delayed_task_finished',
    'password-request-reset',
    'delayed',
    '{"emails_types": [], "recipients": {"place_ids": [1, 2]}}'::JSONB,
    '{"some": "value"}'::JSONB,
    NULL,
    '2022-07-13 00:00:00'::TIMESTAMPTZ
);
