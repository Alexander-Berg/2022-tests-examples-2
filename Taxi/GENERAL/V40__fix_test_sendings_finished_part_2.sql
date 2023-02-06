CREATE OR REPLACE FUNCTION cleanup_stopped_sendings(period_to_drop interval, service_time timestamp)
    RETURNS void AS $$
DECLARE
sending_row_ record;
sending_runtime_row_ record;
sending_error text;
current_error text;
priority_name text;
BEGIN

FOR sending_row_ IN SELECT * FROM crm_scheduler.sendings WHERE service_time - time_stopped > period_to_drop LOOP
    SELECT * from crm_scheduler.sendings_runtime where sending_id_id = sending_row_.id into sending_runtime_row_;

    IF sending_runtime_row_ IS NULL THEN
        RAISE 'cleanup_stopped_sendings FAIL, can''t find sending runtime, sending %', sending_row_.id;
    END IF;

    IF check_sending_has_active_tasks(sending_row_.id) THEN
        CONTINUE;
    END IF;

    sending_error := concat(
        'Policy errors: ', array_to_json(sending_runtime_row_.policy_fail_messages), '. '
        , 'Send errors: ', array_to_json(sending_runtime_row_.send_fail_messages), '. '
        , 'Log errors: ', array_to_json(sending_runtime_row_.logs_fail_messages), '. '
    );

    DELETE FROM crm_scheduler.sendings_runtime where sending_id_id = sending_row_.id;

    IF sending_row_.test_sending THEN
        SELECT name FROM crm_scheduler.priorities WHERE id = sending_row_.priority_id INTO priority_name;
        EXECUTE 'DELETE FROM crm_scheduler.task_reported_'||priority_name||' where sending_id_id = $1' using sending_row_.id;
    END IF;

    INSERT INTO crm_scheduler.sendings_finished (id, sending_id, campaign_id
                                                , size, policy_enabled, send_enabled
                                                , successfull, error, error_details
                                                , time_finished, force_stopped)
    VALUES
    (sending_row_.id, sending_row_.sending_id, sending_row_.campaign_id
    , sending_row_.size, sending_row_.policy_enabled, sending_row_.send_enabled
    , False, sending_error, '{}', sending_row_.time_stopped, True);

    DELETE FROM crm_scheduler.sendings where id = sending_row_.id;

END LOOP;

END;
$$ language 'plpgsql';
