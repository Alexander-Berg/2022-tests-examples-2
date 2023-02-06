create schema yt;
create table yt.operations
(
	id bigserial not null PRIMARY KEY,
	operation_id varchar(255) not null,
	operation_status varchar(255) not null,
	type varchar(255) not null,
	status varchar(255) not null,
	cluster varchar(255) not null,
	created_at timestamptz(0),
	updated_at timestamptz(0),
	date_to timestamptz(0) default now()
);

CREATE TABLE yt.kis_art_summary_report
(
    id                              BIGSERIAL PRIMARY KEY,
    park_id                         TEXT    NOT NULL,
    report_date                     DATE    NOT NULL,
    active_drivers_count            INTEGER NOT NULL,
    drivers_with_permanent_id_count INTEGER NOT NULL,
    drivers_with_temporary_id_count INTEGER NOT NULL,
    drivers_with_requested_id_count INTEGER NOT NULL,
	drivers_with_failed_id_count    INTEGER,
    drivers_without_id_count        INTEGER NOT NULL
);

CREATE UNIQUE INDEX ON yt.kis_art_summary_report USING btree (park_id, report_date);

CREATE TABLE yt.kis_art_detailed_report
(
    id                              BIGSERIAL PRIMARY KEY,
    park_id                         TEXT    NOT NULL,
    report_date                     DATE    NOT NULL,
    driver_profile_id               TEXT    NOT NULL,
	kis_art_status                  TEXT    NOT NULL,
    kis_art_id                      TEXT    NOT NULL,
    driver_full_name                TEXT    NOT NULL
);

CREATE UNIQUE INDEX ON yt.kis_art_detailed_report USING btree (park_id, report_date, driver_profile_id);

CREATE TYPE driver_hire_type AS ENUM
    ('owner', 'rent');

CREATE TABLE yt.commercial_hiring_summary_report
(
    park_id                         TEXT              NOT NULL,
    report_date                     TIMESTAMPTZ       NOT NULL,
    acquisition_type                TEXT              NOT NULL,
    acquisition_source              TEXT              NOT NULL,
    car_profile_id                  TEXT              NOT NULL,
    car_profile_brand_name          TEXT              NOT NULL,
    car_profile_model_name          TEXT              NOT NULL,
    car_number                      TEXT              NOT NULL,
    cnt_orders                      INTEGER           NOT NULL,
    driver_type                     driver_hire_type  NOT NULL,
    driver_profile_id               TEXT              NOT NULL,
    full_name                       TEXT              NOT NULL,
    paid_date_from                  DATE              NOT NULL,
    paid_date_to                    DATE              NOT NULL,
    commercial_hiring_commission           NUMERIC(18, 2)    NOT NULL,
    park_commission                  NUMERIC(18, 2)    NOT NULL,
    rent                            NUMERIC(18, 2)    NOT NULL,
    park_profit                     NUMERIC(18, 2)    NOT NULL
);

CREATE UNIQUE INDEX ON yt.commercial_hiring_summary_report USING btree (park_id, driver_profile_id);

create table yt.report_summary_parks
(
	id bigserial not null PRIMARY KEY,
	park_id varchar(32) not null,
	date_month varchar(32) not null,
	count_active_cars INTEGER,
	count_active_drivers INTEGER,
	count_orders_completed INTEGER,
    count_orders_all INTEGER,
    count_orders_platform INTEGER,
    count_orders_accepted INTEGER,
    count_orders_cancelled_by_driver INTEGER,
    count_orders_cancelled_by_client INTEGER,
	count_new_drivers INTEGER,
	ratio_driver_churn numeric(18,2),
	work_time_seconds BIGINT,
	avg_drivers_work_time_seconds INTEGER,
	avg_cars_work_time_seconds INTEGER,
	price_cash numeric(18,4),
	price_cashless numeric(18,4),
	price_platform_commission numeric(18,4),
	price_park_commission numeric(18,4),
	price_software_commission numeric(18,4),
    price_hiring_services numeric(18,4),
    price_hiring_returned_inc_vat numeric(18,4)
);
CREATE UNIQUE INDEX ON yt.report_summary_parks USING btree (park_id, date_month);
