CREATE TABLE IF NOT EXISTS request_compilations
(
    history_event_id       BIGINT      NOT NULL PRIMARY KEY,
    history_user_id        TEXT        NOT NULL, 
    history_originator_id  TEXT                , 
    history_action         TEXT        NOT NULL, 
    history_timestamp      INTEGER     NOT NULL, 
    history_comment        TEXT                , 
    request_id             TEXT        NOT NULL, 
    data                   TEXT        NOT NULL, 
    employer_code          TEXT        NOT NULL, 
    request_code           TEXT        NOT NULL, 
    request_status         TEXT        NOT NULL, 
    created_at             BIGINT      NOT NULL, 
    delivery_date          BIGINT      NOT NULL, 
    delivery_policy        TEXT        NOT NULL, 
    recipient_phone_pd_id  TEXT                , 
    operator_id            TEXT        NOT NULL
);
