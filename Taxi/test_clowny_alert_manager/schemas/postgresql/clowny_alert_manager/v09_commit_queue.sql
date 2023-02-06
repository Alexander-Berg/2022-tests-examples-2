CREATE TYPE alert_manager.queue_status_e AS ENUM (
    'failed',
    'applied',
    'applying',
    'pending'
);

CREATE FUNCTION alert_manager.set_applied() RETURNS TRIGGER AS $set_applied$
    BEGIN
        IF NEW.status = 'applied' THEN NEW.applied_at = NOW(); END IF;
        RETURN NEW;
    END;
$set_applied$ LANGUAGE plpgsql;

CREATE TABLE alert_manager.configs_queue (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    applied_at TIMESTAMP,

    branch_id BIGINT REFERENCES alert_manager.branches(id) ON DELETE RESTRICT NOT NULL,
    data jsonb NOT NULL,
    status alert_manager.queue_status_e NOT NULL DEFAULT 'pending',
    job_id BIGINT,

    CONSTRAINT applied_status_with_time CHECK ( (status = 'applied') = (applied_at IS NOT NULL) ),
    CONSTRAINT attached_job_not_for_pending CHECK ( (status = 'pending') <> (job_id IS NOT NULL) )
);

CREATE UNIQUE INDEX uniq_pending_configs
    ON alert_manager.configs_queue(branch_id) WHERE status = 'pending';
CREATE UNIQUE INDEX uniq_applying_configs
    ON alert_manager.configs_queue(branch_id) WHERE status = 'applying';

CREATE TRIGGER alert_manager_configs_queue_set_updated
    BEFORE UPDATE
    ON alert_manager.configs_queue
    FOR EACH ROW EXECUTE PROCEDURE alert_manager.set_updated();
CREATE TRIGGER alert_manager_configs_queue_set_applied
    BEFORE UPDATE
    ON alert_manager.configs_queue
    FOR EACH ROW EXECUTE PROCEDURE alert_manager.set_applied();
