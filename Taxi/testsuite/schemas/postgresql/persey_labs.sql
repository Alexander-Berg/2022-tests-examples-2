CREATE SCHEMA persey_labs;

-- table with addresses
CREATE TABLE persey_labs.addresses(
    id SERIAL PRIMARY KEY,
    -- full text with country, city, street, house, buildings, etc...
    full_text TEXT NOT NULL,
    -- coordinates of the org
    lon TEXT NOT NULL,
    lat TEXT NOT NULL,

    locality_id INTEGER NOT NULL,

    title TEXT NOT NULL,
    subtitle TEXT NOT NULL,

    comment TEXT
);

-- table with contacts
CREATE TABLE persey_labs.contacts(
    id SERIAL PRIMARY KEY,
    phone TEXT NOT NULL,
    email TEXT,
    web_site TEXT
);

-- table with billing_infos
CREATE TABLE persey_labs.billing_infos(
    id SERIAL PRIMARY KEY,
    legal_name_short TEXT NOT NULL,
    legal_name_full TEXT NOT NULL,
    OGRN TEXT NOT NULL,
    legal_address TEXT NOT NULL,
    postal_address TEXT NOT NULL,
    web_license_resource TEXT NOT NULL,
    BIK TEXT NOT NULL,
    settlement_account TEXT NOT NULL,
    contract_start_dt TEXT NOT NULL,
    partner_uid TEXT NOT NULL,
    partner_commission TEXT NOT NULL DEFAULT 'n/a',
    --- XXX: try to drop not null
    contract_id TEXT NOT NULL DEFAULT 'n/a'
);

-- table with lab_entities
CREATE TABLE persey_labs.lab_entities(
    id VARCHAR PRIMARY KEY,
    taxi_corp_id TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    -- unstructured contacts information
    contacts TEXT DEFAULT NULL,
    -- DEPRECATED
    test_kind TEXT,
    employee_tests_threshold INTEGER,
    custom_employee_address BOOLEAN NOT NULL DEFAULT FALSE,
    custom_lab_id BOOLEAN NOT NULL DEFAULT FALSE,
    communication_name TEXT NOT NULL,
    contact_id INTEGER NOT NULL REFERENCES persey_labs.contacts (id),
    billing_info_id INTEGER NOT NULL REFERENCES persey_labs.billing_infos (id)
);

-- table with lab_entities tests
CREATE TABLE persey_labs.lab_entity_tests(
    id SERIAL PRIMARY KEY,
    lab_entity_id VARCHAR NOT NULL REFERENCES persey_labs.lab_entities (id) ON DELETE CASCADE,
    -- test_id from config
    test_id TEXT NOT NULL,

    UNIQUE (lab_entity_id, test_id)
);


-- table with person_infos
CREATE TABLE persey_labs.person_infos(
    id SERIAL PRIMARY KEY,
    firstname TEXT NOT NULL,
    middlename TEXT DEFAULT NULL,
    surname TEXT NOT NULL
);

-- table with contact_persons
CREATE TABLE persey_labs.lab_contact_persons(
    id SERIAL PRIMARY KEY,
    "name" TEXT NOT NULL,
    contact_id INTEGER NOT NULL REFERENCES persey_labs.contacts (id)
);

-- table with labs
CREATE TABLE persey_labs.labs(
    id VARCHAR PRIMARY KEY,
    lab_entity_id VARCHAR NOT NULL REFERENCES persey_labs.lab_entities (id),
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    "name" TEXT NOT NULL,
    description TEXT DEFAULT NULL,
    -- aka capacity
    tests_per_day INTEGER NOT NULL DEFAULT 0,
    -- unstructured contacts information
    contacts TEXT DEFAULT NULL,
    contact_id INTEGER NOT NULL REFERENCES persey_labs.contacts (id),
    address_id INTEGER NOT NULL REFERENCES persey_labs.addresses (id),
    contact_person_id INTEGER NOT NULL REFERENCES persey_labs.lab_contact_persons (id)
);

-- table with lab_employees
CREATE TABLE persey_labs.lab_employees(
    id SERIAL PRIMARY KEY,
    lab_id VARCHAR NOT NULL REFERENCES persey_labs.labs (id),
    yandex_login TEXT,
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    contact_id INTEGER REFERENCES persey_labs.contacts (id),
    person_info_id INTEGER REFERENCES persey_labs.person_infos (id),
    address_id INTEGER NOT NULL REFERENCES persey_labs.addresses (id),

    UNIQUE (yandex_login)
);

-- table with lab_employee_shifts
CREATE TABLE persey_labs.lab_employee_shifts(
    id SERIAL PRIMARY KEY,
    lab_employee_id INTEGER NOT NULL REFERENCES persey_labs.lab_employees (id),
    start_time TIMESTAMPTZ NOT NULL,
    finish_time TIMESTAMPTZ NOT NULL,
    taxi_order_id TEXT,
    taxi_order_state TEXT NOT NULL DEFAULT 'planned'
);

-- table with shifts tests
CREATE TABLE persey_labs.shift_tests(
    id SERIAL PRIMARY KEY,
    shift_id INTEGER NOT NULL REFERENCES persey_labs.lab_employee_shifts (id) ON DELETE CASCADE,
    -- test_id from config (consistency with lab entity provided on code level)
    test_id TEXT NOT NULL,

    UNIQUE (shift_id, test_id)
);

-- sequence for generating labs ids
CREATE SEQUENCE labs_ids START 143523;

-- table with employee_state_history
CREATE TABLE persey_labs.employee_state_history(
  id SERIAL UNIQUE PRIMARY KEY,
  employee_id INTEGER NOT NULL REFERENCES persey_labs.lab_employees (id),
  employee_state TEXT NOT NULL,
  change_time TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE persey_labs.lab_employee_shift_history(
  id SERIAL UNIQUE PRIMARY KEY,
  lab_employee_id INTEGER NOT NULL, -- ID из таблицы persey_labs.lab_employees (id)
  shift_id INTEGER NOT NULL, -- ID из таблицы persey_labs.lab_employee_shifts (id)
  action TEXT NOT NULL,
  action_yandex_login_id TEXT NOT NULL,
  action_datetime TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ON persey_labs.employee_state_history (employee_id);
CREATE INDEX ON persey_labs.labs (lab_entity_id);
CREATE INDEX ON persey_labs.addresses (locality_id);
CREATE INDEX ON persey_labs.lab_employee_shifts (lab_employee_id);
CREATE INDEX ON persey_labs.lab_employee_shift_history (lab_employee_id);
CREATE INDEX shifts_time ON persey_labs.lab_employee_shifts (start_time, finish_time DESC);
