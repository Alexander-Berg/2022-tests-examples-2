-- moved repeated code to function
-- and added deleting reported tasks for finishing test_sendings
CREATE OR REPLACE FUNCTION remove_sending_using_sending_finished_task(task_id bigint
                                    , sending_id_ UUID
                                    , report_time timestamp)
RETURNS void AS $$
DECLARE
task_record record;
sending record;
priority_name text;
BEGIN
    SELECT * FROM crm_scheduler.task_pool_sending_finished WHERE id = task_id INTO task_record;
    IF task_record IS NULL THEN
        RAISE 'remove_sending_using_sending_finished_task: can''t get sending_finished task with task_id = %', task_id;
    END IF;

    SELECT * from crm_scheduler.sendings where sending_id = sending_id_ INTO sending;
    IF sending is NULL THEN
        RAISE 'we have no sending with sending_id = %', sending_id_;
    END IF;

    SELECT name FROM crm_scheduler.priorities WHERE id = sending.priority_id INTO priority_name;

    INSERT INTO crm_scheduler.sendings_finished
            (id, sending_id, campaign_id
            , size, policy_enabled
            , send_enabled, successfull
            , error, error_details
            , time_finished)
            VALUES
            (sending.id, sending.sending_id, sending.campaign_id
            , sending.size, sending.policy_enabled
            , sending.send_enabled, task_record.successfull
            , task_record.error, task_record.error_details
            , report_time);

    IF sending.test_sending THEN
        EXECUTE 'DELETE FROM crm_scheduler.task_reported_'||priority_name||' where sending_id_id = $1' using sending.id;
    END IF;

    DELETE FROM crm_scheduler.sendings_runtime WHERE sending_id_id = sending.id;
    DELETE FROM crm_scheduler.task_pool_sending_finished WHERE id = task_record.id;
    DELETE FROM crm_scheduler.sendings WHERE id = sending.id;
END;
$$ language 'plpgsql';

-- last change: V26__make_logs_determined.sql
-- here: moved repeated code to function remove_sending_using_sending_finished_task
CREATE OR REPLACE FUNCTION report_task_finished_v4(task_id bigint
                                    , policy_allowed integer
                                    , logs_saved integer
                                    , sending_id_ UUID
                                    , report_time timestamp
                                    , error text)
    RETURNS void AS $$
DECLARE
task_info record;
task_record record;
summ_task_size integer;
iter_size integer;
insert_query text;
column_increese_counter text;
column_error_append text;
task_total_size integer;
sending record;
BEGIN

    INSERT INTO crm_scheduler.log_task_reported VALUES(task_id, policy_allowed, logs_saved, error, now());

    --HAVE MAX 1 ROW!
    FOR task_info IN SELECT * FROM get_task_in_progress_state(task_id, sending_id_) LOOP
        EXECUTE 'SELECT * FROM '||task_info.task_table||' WHERE id = $1' USING task_id INTO task_record;
        IF task_record IS NULL THEN
            RAISE 'report_task_finished_v4 can''t get % task from sending %', task_id, sending_id_;
        END IF;

        --check if we have active sending
        SELECT * from crm_scheduler.sendings where sending_id = sending_id_ INTO sending;
        IF sending is NULL THEN
            --we have task on non active sending.
            --need to check if we have sending with force_stopped in sendings_finished
            --if we have than we ignore this report cuz it just leftover after forced stop
            IF (SELECT 1 FROM crm_scheduler.sendings_finished where sending_id = sending_id_ AND force_stopped = True) THEN
                --just ignoring this report and exit
                RETURN;
            END IF;
            --we have task on non active sending and it have not been forced to stop, raise error
            RAISE 'we have no active sending with sending_id = %', sending_id_;
        END IF;

         IF sending.is_active IS NULL OR sending.is_active = FALSE THEN
            -- ignoring policy finished tasks, but not others
            IF task_info.task_type_str = 'crm_policy' THEN
                RETURN;
            END IF;
        END IF;

        --check if we are finishing sending
        IF task_info.task_type_str = 'sending_finished' THEN
            --we have active sending need to save it
            PERFORM remove_sending_using_sending_finished_task(task_id, sending_id_, report_time);
            RETURN;
        END IF;


        IF task_info.task_type_str = 'logs' AND error IS NOT NULL THEN
            RAISE WARNING 'Failed log Task %, error: %',task_id, error;
            -- we have no flow where logs can be failed only restarted!
            PERFORM restart_tasks('logs'::text, ARRAY[task_id]);
            RETURN;
        END IF;


        insert_query = 'INSERT INTO crm_scheduler.task_reported_'||task_info.priority_name||'('
                    ||'id, sending_id_id, scope_start, scope_end'
                    ||', start_offset, size, last_job_task_type_id, payload_int, channel_to_send_name, time_reported, processed) '
                    ||'VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, -1);';


        IF policy_allowed IS NULL THEN
            policy_allowed = 0;
        END IF;

        IF logs_saved IS NULL THEN
            logs_saved = 0;
        END IF;

        EXECUTE insert_query using task_id, task_info.sending_id_id, task_record.scope_start, task_record.scope_end
            ,  task_record.start_offset, task_record.size, task_info.task_type_id
            , policy_allowed, task_info.channel_name, report_time;

        EXECUTE 'DELETE from '||task_info.task_table|| ' where id = $1' using task_id;

        INSERT INTO crm_scheduler.sendings_runtime(sending_id_id, size, sending_started) VALUES(task_info.sending_id_id, task_info.sending_total_size, report_time)
            ON CONFLICT (sending_id_id) DO NOTHING;

        PERFORM 1 FROM crm_scheduler.sendings_runtime WHERE sending_id_id = task_info.sending_id_id FOR UPDATE;


        WITH X AS(
            SELECT unnest(task_record.size) AS VALOR
        )
        SELECT SUM(VALOR) FROM X INTO task_total_size;

        IF task_info.task_type_str = 'crm_policy' THEN
            IF error IS NULL THEN
                column_increese_counter = 'policy_summ_success';
            ELSE
                column_increese_counter = 'policy_summ_failed';
                column_error_append = 'policy_fail_messages';
            END IF;
        END IF;

        -- we check earlear if error is not null
        -- , only success here is expected
        IF task_info.task_type_str = 'logs' THEN
            task_total_size := logs_saved;
            column_increese_counter = 'logs_success';
        END IF;


        IF column_increese_counter IS NULL THEN
            IF error IS NULL THEN
                column_increese_counter = 'send_to_channel_success';
            ELSE
                column_increese_counter = 'send_to_channel_failed';
                column_error_append = 'send_fail_messages';
            END IF;
        END IF;


        EXECUTE 'UPDATE crm_scheduler.sendings_runtime SET '
            ||column_increese_counter||' = '||column_increese_counter||' + '||task_total_size
            ||' WHERE sending_id_id = '||task_info.sending_id_id;

        IF column_error_append IS NOT NULL THEN
                    EXECUTE 'UPDATE crm_scheduler.sendings_runtime SET '||column_error_append
                        ||' = array_append('|| column_error_append ||', $1) '
                        ||' where sending_id_id = $2' using error, task_info.sending_id_id;
        END IF;
    END LOOP;

END;
$$ language 'plpgsql';

-- last change: V34__report_task_finished_store_logs_saved.sql
-- here: moved repeated code to function remove_sending_using_sending_finished_task
CREATE OR REPLACE FUNCTION report_task_finished_v5(task_id bigint
                                    , filter_approved integer
                                    , logs_saved integer
                                    , sending_id_ UUID
                                    , report_time timestamp
                                    , error text)
    RETURNS void AS $$
DECLARE
task_info record;
task_record record;
insert_query text;
column_increase_counter text;
column_error_append text;
task_total_size integer;
sending record;
BEGIN

-- strange format for historical reasons

execute 'INSERT INTO crm_scheduler.log_task_reported(task_id, filter_approved, logs_saved, error, time) VALUES($1, $2, $3, $4, $5)' using task_id, filter_approved, logs_saved, error, now();

--HAVE MAX 1 ROW!
FOR task_info IN SELECT * FROM get_task_in_progress_state_v2(task_id, sending_id_) LOOP
    EXECUTE 'SELECT * FROM '||task_info.task_table||' WHERE id = $1' USING task_id INTO task_record;

IF task_record IS NULL THEN
        RAISE 'report_task_finished_v5 can''t get % task from sending %', task_id, sending_id_;
END IF;

    --check if we have active sending
SELECT * from crm_scheduler.sendings where sending_id = sending_id_ INTO sending;
IF sending is NULL THEN
        --we have task on non active sending.
        --need to check if we have sending with force_stopped in sendings_finished
        --if we have than we ignore this report cuz it just leftover after forced stop
        IF (SELECT 1 FROM crm_scheduler.sendings_finished where sending_id = sending_id_ AND force_stopped = True) THEN
            --just ignoring this report and exit
            RETURN;
END IF;
        --we have task on non active sending and it have not been forced to stop, raise error
        RAISE 'we have no active sending with sending_id = %', sending_id_;
END IF;

    IF sending.is_active IS NULL OR sending.is_active = FALSE THEN
        -- ignoring policy finished tasks, but not others
        IF task_info.task_type_str = 'crm_policy' THEN
            RETURN;
END IF;
END IF;

    --check if we are finishing sending
    IF task_info.task_type_str = 'sending_finished' THEN
        --we have active sending need to save it
        PERFORM remove_sending_using_sending_finished_task(task_id, sending_id_, report_time);
        RETURN;
    END IF;

    IF task_info.task_type_str = 'logs' AND error IS NOT NULL THEN
        RAISE WARNING 'Failed log Task %, error: %',task_id, error;
        -- we have no flow where logs can be failed only restarted!
        PERFORM restart_tasks('logs'::text, ARRAY[task_id]);
        RETURN;
END IF;


    insert_query = 'INSERT INTO crm_scheduler.task_reported_'||task_info.priority_name||'('
                ||'id, sending_id_id, scope_start, scope_end'
                ||', start_offset, size, last_job_task_type_id, channel_to_send_name, time_reported, processed, step_num, filter_approved, payload_int) '
                ||'VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, 0, $10, $11, 0);';


    IF filter_approved IS NULL THEN
        filter_approved = 0;
END IF;

        IF logs_saved IS NULL THEN
            logs_saved = 0;
END IF;

EXECUTE insert_query using task_id, task_info.sending_id_id, task_record.scope_start, task_record.scope_end
    ,  task_record.start_offset, task_record.size, task_info.task_type_id
    , task_info.channel_name, report_time, task_info.step_num, filter_approved;

EXECUTE 'DELETE from '||task_info.task_table||' where id = $1' using task_id;

INSERT INTO crm_scheduler.sendings_runtime(sending_id_id, size, sending_started) VALUES(task_info.sending_id_id, task_info.sending_total_size, report_time)
    ON CONFLICT (sending_id_id) DO NOTHING;

WITH X AS(
    SELECT unnest(task_record.size) AS VALOR
)
SELECT SUM(VALOR) FROM X INTO task_total_size;

IF task_info.task_type_str = 'crm_policy' THEN
        IF error IS NULL THEN
            column_increase_counter = 'policy_summ_success';
ELSE
            column_increase_counter = 'policy_summ_failed';
            column_error_append = 'policy_fail_messages';
END IF;
END IF;

    -- we check earlear if error is not null
    -- , only success here is expected
    IF task_info.task_type_str = 'logs' THEN
        task_total_size := logs_saved;
        column_increase_counter = 'logs_success';
END IF;

    IF column_increase_counter IS NULL THEN
        IF error IS NULL THEN
            column_increase_counter = 'send_to_channel_success';
ELSE
            column_increase_counter = 'send_to_channel_failed';
            column_error_append = 'send_fail_messages';
END IF;
END IF;

EXECUTE 'UPDATE crm_scheduler.sendings_runtime SET '
    ||column_increase_counter||' = '||column_increase_counter||' + '||task_total_size
    ||' WHERE sending_id_id = '||task_info.sending_id_id;

IF column_error_append IS NOT NULL THEN
        EXECUTE 'UPDATE crm_scheduler.sendings_runtime SET '||column_error_append
            ||' = array_append('|| column_error_append ||', $1) '
            ||' where sending_id_id = $2' using error, task_info.sending_id_id;
END IF;
END LOOP;
END;
$$ language 'plpgsql';

-- last change: V38__fix_failed_retries.sql
-- here: moved repeated code to function remove_sending_using_sending_finished_task
CREATE OR REPLACE FUNCTION delete_failed_tasks_v2(task_type_name text, tasks_ids bigint[])
    RETURNS void AS $$
DECLARE
task_id bigint;
size integer;
sending_id_id_ integer;
column_to_update text;
column_to_update_message text;
task_total_size integer;
task record;
sending_size integer;
sending record;
BEGIN

IF task_type_name = 'sending_finished' THEN
    RAISE NOTICE 'delete_failed_tasks: Deleting sending_finished tasks: %', tasks_ids;

    FOREACH task_id in ARRAY tasks_ids LOOP
        SELECT * FROM crm_scheduler.task_pool_sending_finished WHERE id = task_id INTO task;
        SELECT * FROM crm_scheduler.sendings WHERE sending_id = task.sending_id INTO sending;

        -- logic copied from report_task_finished_v4 function
        -- migration V26__make_logs_determined.sql

        -- We have task on non active sending, it's leftover after forced stop
        IF sending is NULL THEN
            RAISE NOTICE 'delete_failed_tasks: Cant find sending with id_id = %', task.sending_id_id;
            CONTINUE;
        END IF;

        -- Also non active sending case
        IF sending.is_active IS NULL OR sending.is_active = FALSE THEN
            CONTINUE;
        END IF;

        UPDATE crm_scheduler.task_pool_sending_finished
            SET successfull = False, error = 'Retry Timeout Error: sending_finished task'
            WHERE id = task_id;

        PERFORM remove_sending_using_sending_finished_task(task_id, sending.sending_id, NOW() at time zone 'utc');

    END LOOP;

    RETURN;
END IF;

-- old logic without changes
-- from delete_failed_tasks
-- migration V30__add_zuzer_log_trigger.sql

IF task_type_name = 'crm_policy' THEN
    column_to_update := 'policy_summ_failed';
    column_to_update_message := 'policy_fail_messages';
END IF;

IF task_type_name = 'logs' THEN
    column_to_update := 'logs_failed';
    column_to_update_message := 'logs_fail_messages';
END IF;

IF (SELECT name from crm_scheduler.channels where name = task_type_name) IS NOT NULL THEN
    column_to_update := 'send_to_channel_failed';
    column_to_update_message := 'send_fail_messages';
END IF;

IF column_to_update IS NULL THEN
    RAISE 'delete_failed_tasks: Broken task_type_name: %', task_type_name;
END IF;

FOREACH task_id in ARRAY tasks_ids LOOP
    EXECUTE 'SELECT * FROM crm_scheduler.task_pool_'||task_type_name||'_in_process WHERE id = $1' USING task_id INTO task;
    task_total_size := (WITH X AS(
                            SELECT unnest(task.size) AS VALOR
                        )
                        SELECT SUM(VALOR) FROM X);

    IF task_total_size IS NULL THEN
        task_total_size := 1;
    END IF;

    sending_size := (SELECT crm_scheduler.sendings.size from crm_scheduler.sendings where id = task.sending_id_id);

    INSERT INTO crm_scheduler.sendings_runtime (sending_id_id, size)
    VALUES (task.sending_id_id, sending_size)
        ON CONFLICT(sending_id_id) DO NOTHING;

    PERFORM 1 FROM crm_scheduler.sendings_runtime WHERE crm_scheduler.sendings_runtime.sending_id_id = task.sending_id_id FOR UPDATE;

    EXECUTE 'UPDATE crm_scheduler.sendings_runtime SET '||column_to_update||' = '||column_to_update||' + '||task_total_size
        ||' WHERE sending_id_id = '|| task.sending_id_id;
    EXECUTE 'DELETE FROM crm_scheduler.task_pool_'||task_type_name||'_in_process WHERE id = $1' USING task_id;

    IF array_length(tasks_ids, 1) > 0 THEN
            EXECUTE 'UPDATE crm_scheduler.sendings_runtime SET '||column_to_update_message
                    ||' = array_append('|| column_to_update_message ||', $1) '
                    ||' where sending_id_id = $2' using 'Retry Timout Error'::text, task.sending_id_id;
    END IF;
END LOOP;

END;
$$ language 'plpgsql';

-- last change: V26__make_logs_determined.sql
-- here: little refactoring + ignoring reported tasks for test_sendings
CREATE OR REPLACE FUNCTION check_sending_has_active_tasks(sending_id_id_ integer)
    RETURNS boolean AS $$
DECLARE
task_type_name text;
priority_name text;
task_id bigint;
report_id bigint;
is_test_sending boolean;
BEGIN

FOR task_type_name IN SELECT name FROM crm_scheduler.task_types LOOP
    IF task_type_name = 'sending_finished' THEN
        CONTINUE;
    END IF;

    EXECUTE 'SELECT id FROM crm_scheduler.task_pool_'||task_type_name||' where sending_id_id = $1' using sending_id_id_ into task_id;
    IF task_id IS NOT NULL THEN
        RETURN TRUE;
    END IF;

    EXECUTE 'SELECT id FROM crm_scheduler.task_pool_'||task_type_name||'_in_process where sending_id_id = $1' using sending_id_id_ into task_id;
    IF task_id IS NOT NULL THEN
        RETURN TRUE;
    END IF;

END LOOP;

SELECT test_sending FROM crm_scheduler.sendings WHERE id = sending_id_id_ INTO is_test_sending;

FOR priority_name in SELECT name from crm_scheduler.priorities LOOP
    EXECUTE 'SELECT id FROM crm_scheduler.task_reported_'||priority_name||' where sending_id_id = $1' using sending_id_id_ into report_id;
    IF (NOT is_test_sending) AND (report_id IS NOT NULL) THEN
        RETURN TRUE;
    END IF;
END LOOP;

RETURN FALSE;

END;
$$ language 'plpgsql';
