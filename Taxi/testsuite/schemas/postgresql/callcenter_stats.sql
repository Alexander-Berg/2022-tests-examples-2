DROP SCHEMA IF EXISTS callcenter_stats CASCADE;

CREATE SCHEMA callcenter_stats;


-- version table
CREATE TABLE IF NOT EXISTS callcenter_stats.version (
    id SERIAL,
    version VARCHAR NOT NULL,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO callcenter_stats.version (version)
VALUES ('v1'), ('v2'), ('v3'), ('v4'), ('v5'), ('v6'), ('v7'), ('v8'), ('v9'), ('v10'),
       ('v11'), ('v12'), ('v13'), ('v14'), ('v15'), ('v16'), ('v17'), ('v18'), ('v19'), ('v20'),
       ('v21'), ('v22'), ('v23'), ('v24'), ('v25'), ('v26'), ('v27'), ('v28'), ('v29'), ('v30'),
       ('v31'), ('v32'), ('v33'), ('v34'), ('v35'), ('v36'), ('v37'), ('v38'), ('v39'), ('v40'),
       ('v41'), ('v42'), ('v43'), ('v44'), ('v45'), ('v46'), ('v47'), ('v48'), ('v49'), ('v50');


-- distlocks table
CREATE TABLE callcenter_stats.distlocks(
    key TEXT PRIMARY KEY,
    owner TEXT,
    expiration_time TIMESTAMPTZ
);


-- logbroker schema and offsets table
CREATE SCHEMA lb;
CREATE TABLE lb.offsets (
    topic_partition TEXT PRIMARY KEY,
    offsets BIGINT
);


-- table for storing operator actions - order commits and others
CREATE TABLE callcenter_stats.actions
(
    id                  BIGSERIAL      ,
    chain_id            VARCHAR        ,
    created_at          TIMESTAMPTZ    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    offer_id            VARCHAR        ,
    order_id            VARCHAR        ,
    discount_card       VARCHAR        ,
    base_discount       VARCHAR        ,
    cc_discount         VARCHAR        ,
    zone_name           VARCHAR        ,
    agent_id            VARCHAR        ,
    yandex_uid          VARCHAR        ,
    action_type              VARCHAR        ,
    PRIMARY KEY (id)
);

CREATE INDEX created_at_idx ON callcenter_stats.actions(created_at);
-- Индекс для поиска по call_guid
CREATE INDEX actions_chain_id_idx ON callcenter_stats.actions(chain_id);


-- table for storing operator status changes from cc-operators
CREATE TABLE callcenter_stats.operator_history
(
    id                  BIGSERIAL         ,
    agent_id            VARCHAR           NOT NULL,
    login               VARCHAR           NOT NULL,
    queues              VARCHAR[]         NOT NULL          DEFAULT ARRAY[]::VARCHAR[],
    status              VARCHAR           NOT NULL,
    created_at          TIMESTAMPTZ       DEFAULT NOW(),
    sub_status          VARCHAR,
    prev_queues         VARCHAR[],
    prev_status         VARCHAR,
    prev_created_at     TIMESTAMPTZ,
    prev_sub_status     VARCHAR,
    PRIMARY KEY (id)
);

CREATE INDEX operator_history_created_at_idx ON callcenter_stats.operator_history(created_at);


-- table for storing current operator status from cc-operators
CREATE TABLE callcenter_stats.operator_status
(
    agent_id            VARCHAR           NOT NULL,
    updated_at          TIMESTAMPTZ       NOT NULL,
    status              VARCHAR           NOT NULL,
    queues              VARCHAR[]         NOT NULL          DEFAULT ARRAY[]::VARCHAR[],
    login               VARCHAR,
    sub_status          VARCHAR,
    status_updated_at   TIMESTAMPTZ       NOT NULL,
    sub_status_updated_at TIMESTAMPTZ     NOT NULL,
    last_history_at     TIMESTAMPTZ,
    PRIMARY KEY (agent_id)
);

CREATE INDEX operator_status_status_idx ON callcenter_stats.operator_status(status);


-- table for storing current talking status of operator from LB QProc event messages
CREATE TABLE callcenter_stats.operator_talking_status
(
    agent_id            VARCHAR           NOT NULL,
    updated_at          TIMESTAMPTZ       NOT NULL, -- event time, not time of sql update
    is_talking          BOOLEAN           NOT NULL,
    queue               VARCHAR,
    postcall_until      TIMESTAMPTZ,
    PRIMARY KEY (agent_id)
);


-- table for storing current call qproc transaction status (queued/talking)
CREATE TABLE callcenter_stats.call_status
(
    call_id             VARCHAR NOT NULL    , -- локальный идентификатор звонка
    queue               VARCHAR NOT NULL    , -- имя очереди, в которую попал звонок
    status              VARCHAR NOT NULL    , -- текущий статус звонка (meta/queued/talking)
    last_event_at       TIMESTAMPTZ         , -- время последнего event`а по часам телефонии
    call_guid           VARCHAR             , -- глобальный идентификатор звонка (из МЕТА)
    called_number       VARCHAR             , -- номер, на который позвонил абонент (из МЕТА)
    abonent_phone_id    VARCHAR             , -- идентификатор телефона позвонившего абонента (из ENTERQUEUE)
    queued_at           TIMESTAMPTZ NOT NULL, -- время по часам телефонии, когда звонок попал в очередь
    answered_at         TIMESTAMPTZ         , -- время по часам телефонии, когда на звонок ответил оператор, если status = talking
    agent_id            VARCHAR             , -- идентификатор ответившего оператора, если status = talking
    commutation_id      VARCHAR             , -- id коммутации. Выставляется звонку при балансировке на очереди в cc-queues
    PRIMARY KEY (call_id)
);

CREATE INDEX call_status_commutation_id_idx ON callcenter_stats.call_status(commutation_id);

-- table for storing ended call qproc transactions - data moved from call_status when transaction is ended
CREATE TABLE callcenter_stats.call_history
(
    id                  VARCHAR             , -- не возрастающий идентификатор записи (хэш от группы полей)
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(), -- время создания записи
    call_guid           VARCHAR             , -- глобальный идентификатор звонка (из МЕТА)
    call_id             VARCHAR NOT NULL    , -- локальный идентификатор звонка
    queue               VARCHAR NOT NULL    , -- имя очереди, в которую попал звонок
    abonent_phone_id    VARCHAR             , -- идентификатор телефона позвонившего абонента (из ENTERQUEUE)
    agent_id            VARCHAR             , -- идентификатор ответившего оператора, если endreason = {completed, transfered}
    queued_at           TIMESTAMPTZ NOT NULL, -- время по часам телефонии, когда звонок попал в очередь
    answered_at         TIMESTAMPTZ         , -- время по часам телефонии, когда на звонок ответил оператор, если endreason = {completed, transfered}
    completed_at        TIMESTAMPTZ NOT NULL, -- время по часам телефонии, когда звонок был завершен
    endreason           VARCHAR NOT NULL    , -- причина завершения звонка
    transfered_to       VARCHAR             , -- куда звонок был переведен, если звонок был переведен, если endreason = {transfered}
    transfered_to_number VARCHAR            , -- номер телефона, на который был переведен звонок, если endreason = {transfered}
    called_number       VARCHAR             , -- номер, на который позвонил абонент (из МЕТА)
    postcall_until      TIMESTAMPTZ         , -- момент времени, до которого должен продолжаться postcall по таймеру
    created_seq         BIGSERIAL           , -- возрастающий идентификатор записи
    direction           VARCHAR             , -- направление звонка: in - входящий, out - исходящий
    PRIMARY KEY (id)
);

CREATE INDEX call_history_created_at_idx ON callcenter_stats.call_history(created_at);
-- Индексы для ускорения запросов с фильтрами для ручки /calls/history
CREATE INDEX call_history_agent_id_idx ON callcenter_stats.call_history(agent_id);
CREATE INDEX call_history_abonent_phone_id_idx ON callcenter_stats.call_history(abonent_phone_id);
CREATE INDEX call_history_endreason_idx ON callcenter_stats.call_history(endreason);
CREATE INDEX call_history_queued_at_idx ON callcenter_stats.call_history(queued_at);
CREATE INDEX call_history_completed_at_idx ON callcenter_stats.call_history(completed_at);
CREATE INDEX call_history_queue_idx ON callcenter_stats.call_history(queue);
CREATE INDEX call_history_called_number_idx ON callcenter_stats.call_history(called_number);
CREATE INDEX call_history_created_seq_idx ON callcenter_stats.call_history(created_seq);

-- table for storing raw lb messages
CREATE TYPE callcenter_stats.qapp_event AS (
    NODE                VARCHAR,
    PARTITION_          VARCHAR,
    DATE_               INTERVAL,
    CALLID              VARCHAR,
    QUEUENAME           VARCHAR,
    AGENT               VARCHAR,
    ACTION_             VARCHAR,
    DATA1               VARCHAR,
    DATA2               VARCHAR,
    DATA3               VARCHAR,
    DATA4               VARCHAR,
    DATA5               VARCHAR,
    DATA6               VARCHAR,
    DATA7               VARCHAR,
    DATA8               VARCHAR,
    OTHER               VARCHAR,
    id                  VARCHAR
    );

CREATE TABLE callcenter_stats.qapp_events
(
    created_at          TIMESTAMPTZ NOT NULL,
    NODE                VARCHAR,
    PARTITION_          VARCHAR,
    DATE_               INTERVAL NOT NULL,
    CALLID              VARCHAR NOT NULL,
    QUEUENAME           VARCHAR NOT NULL,
    AGENT               VARCHAR,
    ACTION_             VARCHAR NOT NULL,
    DATA1               VARCHAR,
    DATA2               VARCHAR,
    DATA3               VARCHAR,
    DATA4               VARCHAR,
    DATA5               VARCHAR,
    DATA6               VARCHAR,
    DATA7               VARCHAR,
    DATA8               VARCHAR,
    OTHER               VARCHAR,
    id                  VARCHAR, -- не возрастающий идентификатор сообщения (хэш от поля с data от asterisk)
    PRIMARY KEY (id)
);

CREATE SEQUENCE callcenter_stats.qapp_events_update_seq;
ALTER TABLE callcenter_stats.qapp_events ADD COLUMN updated_seq BIGINT NOT NULL DEFAULT nextval('callcenter_stats.qapp_events_update_seq');
ALTER SEQUENCE callcenter_stats.qapp_events_update_seq OWNED BY callcenter_stats.qapp_events.updated_seq;

CREATE INDEX qapp_events_updated_seq_idx ON callcenter_stats.qapp_events(updated_seq);
CREATE INDEX qapp_events_created_at_idx ON callcenter_stats.qapp_events(created_at);
CREATE INDEX qapp_events_call_id_idx ON callcenter_stats.qapp_events(CALLID);

CREATE TABLE IF NOT EXISTS callcenter_stats.general_call_history
(
    call_guid           VARCHAR PRIMARY KEY , -- глобальный идентификатор звонка
    call_external_id    VARCHAR             , -- внешний идентификатор звонка
    project             VARCHAR             , -- идентификатор проекта
    init_event_id       BIGINT NOT NULL     , -- идентификатор инициализируещего звонок события
    initiator_type      VARCHAR NOT NULL    , -- тип инициатора: abonent, operator, personnel, ivr_flow_worker, native_worker, ...
    initiator_id        VARCHAR NOT NULL    , -- идентификатор инициатора (abonent_phone_id, yandex_uid, ivt_flow_id, worker_id, ...)
    initiated_at        TIMESTAMPTZ NOT NULL, -- дата и время начала
    finished_at         TIMESTAMPTZ         , -- дата и время завершения
    context             JSONB                 -- контекст
);

CREATE INDEX general_call_history_call_external_id_idx ON callcenter_stats.general_call_history(call_external_id, init_event_id);
CREATE INDEX general_call_history_project_id_idx ON callcenter_stats.general_call_history(project, init_event_id);
CREATE INDEX general_call_history_initiator_type_idx ON callcenter_stats.general_call_history(initiator_type, init_event_id);
CREATE INDEX general_call_history_initiator_id_idx ON callcenter_stats.general_call_history(initiator_id, init_event_id);
CREATE INDEX general_call_history_initiated_at_idx ON callcenter_stats.general_call_history(initiated_at, init_event_id);
CREATE INDEX general_call_history_duration_idx ON callcenter_stats.general_call_history((finished_at - initiated_at), init_event_id);

CREATE TABLE IF NOT EXISTS callcenter_stats.call_leg_history
(
    leg_id              VARCHAR PRIMARY KEY , -- идентификатор соединения
    call_guid           VARCHAR NOT NULL    , -- глобальный идентификатор звонка
    contact_type        VARCHAR NOT NULL    , -- тип адресата: abonent, operator, personnel, ivr_flow_worker, native_worker, ...
    contact_id          VARCHAR NOT NULL    , -- идентификатор адресата (abonent_phone_id, yandex_uid, ivt_flow_id, worker_id, ...)
    contact_uri         VARCHAR             , -- физический адрес адресата
    init_mode           VARCHAR NOT NULL    , -- способ инициализации соединения: originate, answer, forward, switch
    initiated_at        TIMESTAMPTZ NOT NULL, -- дата и время начала сеанса
    answered_at         TIMESTAMPTZ         , -- дата и время ответа адресата
    finished_at         TIMESTAMPTZ           -- дата и время завершения сеанса
);

CREATE INDEX call_leg_history_guid_idx ON callcenter_stats.call_leg_history(call_guid);
CREATE INDEX call_leg_history_contact_type_idx ON callcenter_stats.call_leg_history(contact_type);
CREATE INDEX call_leg_history_contact_id_idx ON callcenter_stats.call_leg_history(contact_id);

CREATE TABLE IF NOT EXISTS callcenter_stats.call_event_history
(
    event_id            BIGINT PRIMARY KEY  , -- внешний, монотонно возрастающий идентификатор события
    call_guid           VARCHAR NOT NULL    , -- глобальный идентификатор звонка
    leg_id              VARCHAR             , -- идентификатор соединения
    controller_id       VARCHAR             , -- идентификатор диспетчера (ivr_flow_id, worker_id, ...)
    event_type          VARCHAR NOT NULL    , -- тип события
    event_time          TIMESTAMPTZ NOT NULL, -- дата и время события
    params              JSONB                 -- параметры события
);

CREATE INDEX call_event_history_guid_idx ON callcenter_stats.call_event_history(call_guid);
CREATE INDEX call_event_history_leg_idx ON callcenter_stats.call_event_history(leg_id);
CREATE INDEX call_event_history_controller_idx ON callcenter_stats.call_event_history(controller_id);


CREATE TYPE callcenter_stats.talking_agent AS (
    agent_id VARCHAR,
    updated_at TIMESTAMPTZ,
    is_talking BOOLEAN,
    queue VARCHAR,
    postcall_until TIMESTAMPTZ
);

CREATE TYPE callcenter_stats.call_status_raw_v2 AS (
    call_id             VARCHAR,
    queue               VARCHAR,
    status              VARCHAR,
    last_event_at       TIMESTAMPTZ,
    call_guid           VARCHAR,
    called_number       VARCHAR,
    abonent_phone_id    VARCHAR,
    queued_at           TIMESTAMPTZ,
    answered_at         TIMESTAMPTZ,
    agent_id            VARCHAR,
    commutation_id      VARCHAR
);

CREATE TYPE callcenter_stats.call_history_raw_v3 AS (
    id                  VARCHAR,
    created_at          TIMESTAMPTZ,
    call_guid           VARCHAR,
    call_id             VARCHAR,
    queue               VARCHAR,
    abonent_phone_id    VARCHAR,
    agent_id            VARCHAR,
    queued_at           TIMESTAMPTZ,
    answered_at         TIMESTAMPTZ,
    completed_at        TIMESTAMPTZ,
    endreason           VARCHAR,
    transfered_to       VARCHAR,
    transfered_to_number VARCHAR,
    called_number       VARCHAR,
    postcall_until      TIMESTAMPTZ,
    direction           VARCHAR,
    created_seq         BIGINT
);

-- параметры события
CREATE TYPE callcenter_stats.call_event_history_params AS (
    extra JSONB
);
-- контекст
CREATE TYPE callcenter_stats.call_event_history_context AS (
    extra JSONB
);
-- история событий звонка, импортируемая из ivr-dispatcher
CREATE TYPE callcenter_stats.call_event_history_raw AS (
   event_id            BIGINT     , -- монотонно возрастающий идентификатор события
   call_guid           VARCHAR    , -- глобальный идентификатор звонка
   call_external_id    VARCHAR    , -- внешний идентификатор звонка
   leg_id              VARCHAR    , -- идентификатор соединения
   transferee_id       VARCHAR    , -- идентификатор соединения с адресатом перевода звонка
   controller_id       VARCHAR    , -- идентификатор диспетчера (ivr_flow_id, worker_id, ...)
   event_type          VARCHAR    , -- тип события
   event_time          TIMESTAMPTZ, -- дата и время события
   params              callcenter_stats.call_event_history_params,
   initiator_type      VARCHAR    , -- тип инициатора (abonent, operator, personnel, ivr_flow_worker, native_worker, ...)
   initiator_id        VARCHAR    , -- идентификатор инициатора (abonent_phone_id, yandex_uid, ivt_flow_id, worker_id, ...)
   contact_type        VARCHAR    , -- тип адресата: (abonent, operator, personnel, ivr_flow_worker, native_worker, ...), если указан transferee_id, то содержит тип адресата перевода
   contact_id          VARCHAR    , -- идентификатор адресата (abonent_phone_id, yandex_uid, ivt_flow_id, worker_id, ...), если указан transferee_id, то содержит идентификатор адресата перевода
   contact_uri         VARCHAR    , -- физический адрес адресата
   answered            BOOLEAN    , -- признак ответа адресата соединения, если указан transferee_id, то содержит признак ответа адресата перевода
   finished            BOOLEAN    , -- признак завершения соединения, если указан transferee_id, то содержит признак завершения соединения с адресатом перевода
   project             VARCHAR    , -- идентификатор проекта
   context             callcenter_stats.call_event_history_context
);
-- история соединений звонка
CREATE TYPE callcenter_stats.call_leg_history_raw AS (
     leg_id              VARCHAR             , -- идентификатор соединения
     contact_type        VARCHAR             , -- тип адресата: abonent, operator, personnel, ivr_flow_worker, native_worker, ...
     contact_id          VARCHAR             , -- идентификатор адресата (abonent_phone_id, yandex_uid, ivt_flow_id, worker_id, ...)
     contact_uri         VARCHAR             , -- физический адрес адресата
     init_mode           VARCHAR             , -- способ инициализации соединения: originate, answer, forward, switch
     initiated_at        TIMESTAMPTZ         , -- дата и время начала сеанса
     answered_at         TIMESTAMPTZ         , -- дата и время ответа адресата
     finished_at         TIMESTAMPTZ           -- дата и время завершения сеанса
);
-- история событий завершенния звонка
CREATE TYPE callcenter_stats.call_event_time_history_raw AS (
    call_guid           VARCHAR,
    leg_id              VARCHAR,
    event_time          TIMESTAMPTZ
);

-- user target_queues table
CREATE TABLE IF NOT EXISTS callcenter_stats.user_queues
(
    sip_username VARCHAR PRIMARY KEY,
    metaqueues VARCHAR[] NOT NULL DEFAULT ARRAY[]::VARCHAR[],
    updated_seq BIGINT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()  -- real updated_at
);

CREATE TYPE callcenter_stats.user_queues_raw AS (
    sip_username VARCHAR,
    metaqueues VARCHAR[],
    updated_seq BIGINT,
    updated_at TIMESTAMPTZ
);

-- tel_state table
CREATE TABLE IF NOT EXISTS callcenter_stats.tel_state
(
    sip_username VARCHAR PRIMARY KEY,
    is_connected BOOLEAN NOT NULL DEFAULT FALSE,
    is_paused BOOLEAN NOT NULL DEFAULT FALSE,
    metaqueues VARCHAR[] NOT NULL DEFAULT ARRAY[]::VARCHAR[],
    subcluster VARCHAR,
    updated_seq BIGINT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),  -- real updated_at
    is_valid BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX tel_state_is_valid_indx ON callcenter_stats.tel_state(is_valid);

CREATE TYPE callcenter_stats.tel_state_raw_v2 AS (
    sip_username VARCHAR,
    metaqueues VARCHAR[],
    subcluster VARCHAR,
    is_connected BOOLEAN,
    is_paused BOOLEAN,
    is_valid BOOLEAN,
    updated_seq BIGINT,
    updated_at TIMESTAMPTZ
);

-- status table
CREATE TABLE IF NOT EXISTS callcenter_stats.user_status (
    sip_username VARCHAR PRIMARY KEY,
    status  VARCHAR NOT NULL,
    sub_status VARCHAR,
    project VARCHAR NOT NULL,
    updated_seq BIGINT NOT NULL,
    status_updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), -- real updated_at for status
    sub_status_updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW() -- real updated_at for sub_status
);

CREATE INDEX user_status_status_idx ON callcenter_stats.user_status(status);

CREATE TYPE callcenter_stats.user_status_raw AS (
    sip_username VARCHAR,
    status  VARCHAR,
    sub_status VARCHAR,
    project VARCHAR,
    updated_seq BIGINT,
    updated_at TIMESTAMPTZ
);

\ir ./functions/operator_united_status.sql
\ir ./functions/operator_status_times_v2.sql
\ir ./functions/operator_substatus.sql
\ir ./functions/operator_status_intervals.sql
\ir ./functions/user_substatus.sql
\ir ./functions/user_unified_status.sql
