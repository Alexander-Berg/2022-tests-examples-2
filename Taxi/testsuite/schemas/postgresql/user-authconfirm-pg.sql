CREATE TABLE auth_data (
    id varchar(32) primary key NOT NULL,
    personal_phone_id varchar(32) NOT NULL,
    code varchar(6) NOT NULL,
    authorized bool NOT NULL DEFAULT false,
    attempts integer NOT NULL DEFAULT 0,
    code_created timestamptz NOT NULL DEFAULT current_timestamp,
    created timestamptz NOT NULL DEFAULT current_timestamp,
    updated timestamptz  NOT NULL DEFAULT current_timestamp
);

CREATE TABLE phone_data (
    personal_phone_id varchar(32) primary key NOT NULL,
    last_sms_sent timestamptz NOT NULL DEFAULT current_timestamp,
    created timestamptz NOT NULL DEFAULT current_timestamp,
    updated timestamptz NOT NULL DEFAULT current_timestamp
);
