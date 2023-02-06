CREATE TYPE alert_manager.flap_settings_t AS (
    flap_time INTEGER,
    stable_time INTEGER,
    critical_time INTEGER
);

CREATE TYPE alert_manager.alarm_settings_t AS (
    count_threshold INTEGER,
    percent_threshold INTEGER
);

CREATE TYPE alert_manager.weak_day_e AS ENUM (
    'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'
);

CREATE TYPE alert_manager.time_settings_t AS (
    -- Период применения действия. Представляет собой трехбуквенные коды дней недели
    -- через дефис: `{day_start}-{day_end}`.
    days alert_manager.weak_day_e[2],
    -- Период применения действия. Представляет собой числовой интервал в часах.
    -- 0-23. min 0, max 23 (including).
    time INTEGER[2],
    warn alert_manager.alarm_settings_t,
    crit alert_manager.alarm_settings_t
);

CREATE TYPE alert_manager.escalation_method_e AS ENUM (
    'phone_escalation'
);

CREATE TYPE alert_manager.alert_state_e AS ENUM (
    'OK',
    'WARN',
    'CRIT'
);

CREATE TYPE alert_manager.startrek_settings_t AS (
    queue TEXT,
    delay INTEGER,
    status alert_manager.alert_state_e[]
);

CREATE TYPE alert_manager.unreach_mode_e AS ENUM ('force_ok', 'skip');

CREATE TYPE alert_manager.unreach_settings_t AS (
    mode alert_manager.unreach_mode_e,
    related_checks TEXT[]
);

CREATE TYPE alert_manager.overridable_settings_t AS (
    children_event TEXT,
    children TEXT[],
    refresh_time INTEGER,
    ttl INTEGER,
    escalation_method alert_manager.escalation_method_e,
    ignore_nodata BOOLEAN,
    flaps alert_manager.flap_settings_t,
    times alert_manager.time_settings_t[],
    startrek alert_manager.startrek_settings_t,
    responsibles TEXT[],
    unreach alert_manager.unreach_settings_t,
    active TEXT,
    active_kwargs JSONB
);
