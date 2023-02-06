CREATE TABLE form_builder.partial_request_queue (
    response_id BIGSERIAL REFERENCES form_builder.responses(id) ON DELETE CASCADE NOT NULL,
    form_code TEXT REFERENCES form_builder.forms(code) ON DELETE CASCADE NOT NULL,
    stage_num INTEGER NOT NULL,
    submit_id TEXT NOT NULL,
    status form_builder.submit_status NOT NULL DEFAULT 'PENDING',
    fail_count INTEGER NOT NULL DEFAULT 0,
    created TIMESTAMPTZ NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
    updated TIMESTAMPTZ NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
    -- submit options values below (state at the creation time of the row)
    method TEXT NOT NULL,
    url TEXT NOT NULL,
    tvm_service_id TEXT,

    UNIQUE (form_code, stage_num, submit_id)
);

CREATE TRIGGER partial_request_queue_set_updated
    BEFORE UPDATE OR INSERT ON form_builder.partial_request_queue
    FOR EACH ROW EXECUTE PROCEDURE set_updated();
