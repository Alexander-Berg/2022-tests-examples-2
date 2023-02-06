INSERT INTO eats_restapp_communications.send_event_data (
    event_id,
    event_type,
    event_mode,
    recipients,
    data
) VALUES (
    'fake_task-password-request-reset',
    'password-request-reset',
    'asap',
    '{"emails_types": ["my_email_type", "other_email_type"], "recipients": {"place_ids": [1, 2, 4]}}'::JSONB,
    '{}'::JSONB
), (
    'fake_task-place-onboarding-launch',
    'place-onboarding-launch',
    'asap',
    '{"emails_types": ["my_email_type", "other_email_type"], "recipients": {"place_ids": [1, 2, 4]}}'::JSONB,
    '{}'::JSONB
), (
    'fake_task-eats-partners-generate-credentials',
    'eats-partners-generate-credentials',
    'asap',
    '{"emails_types": ["my_email_type", "other_email_type"], "recipients": {"place_ids": [1, 2, 4]}}'::JSONB,
    '{}'::JSONB
), (
    'fake_task-daily-digests',
    'daily-digests',
    'asap',
    '{"emails_types": ["my_email_type", "other_email_type"], "recipients": {"place_ids": [1, 2, 4]}}'::JSONB,
    '{}'::JSONB
), (
    'fake_task-cancelled-tg-alert',
    'cancelled-tg-alert',
    'asap',
    '{"emails_types": ["my_email_type", "other_email_type"], "recipients": {"place_ids": [1, 2, 4]}}'::JSONB,
    '{}'::JSONB
);
