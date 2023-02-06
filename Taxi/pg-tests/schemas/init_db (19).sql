CREATE TABLE menu_statistic
(
    id UUID PRIMARY KEY,
    place_id VARCHAR(255),
    place_group_id VARCHAR(255),
    operation_type VARCHAR(255),
    process_uuid UUID,
    data jsonb,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
);

CREATE TABLE menu_statistic_files
(
    id UUID PRIMARY KEY,
    process_uuid UUID,
    key VARCHAR(255),
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
);

CREATE TABLE collector_synchronization_tasks
(
    id UUID PRIMARY KEY,
    status TEXT,
    type TEXT,
    place_id VARCHAR(255),
    data_file_url VARCHAR(255),
    data_file_version VARCHAR(255),
    message_id VARCHAR(255),
    reason VARCHAR(255),
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
);

CREATE TABLE burger_king_order_statuses
(
    id UUID PRIMARY KEY,
    order_nr VARCHAR(255),
    status VARCHAR(255),
    created_at TIMESTAMPTZ
);

CREATE TABLE courier_arrival_notifications
(
    id UUID PRIMARY KEY,
    order_nr VARCHAR(255),
    status VARCHAR(255),
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
);

CREATE TABLE place_delivery_zone_jobs
(
    id UUID PRIMARY KEY,
    place_id VARCHAR(255),
    status VARCHAR(255),
    errors TEXT,
    last_stamp UUID,
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
);

CREATE TABLE retail_sync_jobs
(
    id UUID PRIMARY KEY,
    place_id VARCHAR(255),
    type VARCHAR(255),
    data_file_url TEXT,
    data_file_version VARCHAR(255),
    status VARCHAR(255),
    attempt int,
    items_processed int,
    consumed_at TIMESTAMPTZ,
    processed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
);
