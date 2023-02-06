CREATE TABLE form_builder.partial_submit_options (
    id BIGSERIAL PRIMARY KEY,
    stage_id BIGINT REFERENCES form_builder.stages(id) ON DELETE CASCADE NOT NULL,
    method TEXT NOT NULL,
    url TEXT NOT NULL,
    tvm_service_id TEXT
    -- template body is empty, cause we just build flat dict from submitted stage and push it
);
