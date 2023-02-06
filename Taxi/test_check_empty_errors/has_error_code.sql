INSERT INTO crm_admin.campaign_state_log
(id, campaign_id, state_from, state_to, updated_at, error_code, error_description)
VALUES
(1, 1234, 'VERIFY', 'VERIFY_ERROR', '2022-02-14 20:00:00', 'COULD_NOT_SUBMIT', '{"just": "test description"}');

