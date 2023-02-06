DROP SCHEMA IF EXISTS callcenter_queues CASCADE;

CREATE SCHEMA callcenter_queues;

-- distlocks table
CREATE TABLE callcenter_queues.distlocks(
    key TEXT PRIMARY KEY,
    owner TEXT,
    expiration_time TIMESTAMPTZ
);


-- table for storing raw qproc messages
CREATE TYPE callcenter_queues.qproc_event AS (
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

CREATE TABLE callcenter_queues.qproc_events
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
    id                  VARCHAR PRIMARY KEY -- не возрастающий идентификатор сообщения (хэш от поля с data от asterisk)
);

CREATE SEQUENCE callcenter_queues.qproc_events_update_seq;
ALTER TABLE callcenter_queues.qproc_events ADD COLUMN updated_seq BIGINT NOT NULL DEFAULT nextval('callcenter_queues.qproc_events_update_seq');
ALTER SEQUENCE callcenter_queues.qproc_events_update_seq OWNED BY callcenter_queues.qproc_events.updated_seq;

CREATE INDEX qproc_events_updated_seq_idx ON callcenter_queues.qproc_events(updated_seq);
CREATE INDEX qproc_events_created_at_idx ON callcenter_queues.qproc_events(created_at);
CREATE INDEX qproc_events_call_id_idx ON callcenter_queues.qproc_events(CALLID);


-- table for storing operative info for calls of past period (queued/talking/transfered/complated)
CREATE TYPE callcenter_queues.call_v2 AS (
    asterisk_call_id        VARCHAR,
    routing_id              VARCHAR,
    metaqueue               VARCHAR,
    subcluster              VARCHAR,
    status                  VARCHAR,
    last_event_at           TIMESTAMPTZ,
    call_guid               VARCHAR,
    called_number           VARCHAR,
    abonent_phone_id        VARCHAR,
    queued_at               TIMESTAMPTZ,
    answered_at             TIMESTAMPTZ,
    completed_at            TIMESTAMPTZ,
    endreason               VARCHAR,
    transfered_to_number    VARCHAR,
    asterisk_agent_id       VARCHAR
    );

CREATE TABLE callcenter_queues.calls
(
    asterisk_call_id        VARCHAR PRIMARY KEY , -- локальный идентификатор звонка в qproc
    routing_id              VARCHAR             , -- id коммутации звонка (из routed_calls), генерируется на нашей стороне (прокидываем через МЕТА сообщение)
    metaqueue               VARCHAR NOT NULL    , -- имя метаочереди, в которую попал звонок
    subcluster              VARCHAR NOT NULL    , -- номер сабкластера, на который попал звонок
    status                  VARCHAR NOT NULL    , -- текущий статус звонка (meta/queued/talking/completed)
    last_event_at           TIMESTAMPTZ NOT NULL, -- время последнего event`а по часам телефонии
    call_guid               VARCHAR             , -- глобальный идентификатор звонка (из МЕТА)
    called_number           VARCHAR             , -- номер, на который позвонил абонент (из МЕТА)
    abonent_phone_id        VARCHAR             , -- идентификатор телефона позвонившего абонента (из ENTERQUEUE)
    queued_at               TIMESTAMPTZ NOT NULL, -- время по часам телефонии, когда звонок попал в очередь
    answered_at             TIMESTAMPTZ         , -- время по часам телефонии, когда на звонок ответил оператор, если status = talking
    completed_at            TIMESTAMPTZ         , -- время по часам телефонии, когда звонок был завершен
    endreason               VARCHAR             , -- причина завершения звонка
    transfered_to_number    VARCHAR             , -- номер телефона, на который был переведен звонок, если endreason
    asterisk_agent_id       VARCHAR             , -- идентификатор ответившего оператора в asterisk (очищенный = только цифры)
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW() -- время создания записи в базе
);


CREATE INDEX calls_created_at_idx ON callcenter_queues.calls(created_at);
CREATE INDEX calls_last_event_at_idx ON callcenter_queues.calls(last_event_at);
CREATE INDEX calls_status_idx ON callcenter_queues.calls(status);
CREATE INDEX calls_metaqueue_idx ON callcenter_queues.calls(metaqueue);
CREATE INDEX calls_routing_idx ON callcenter_queues.calls(routing_id);

CREATE SEQUENCE callcenter_queues.calls_update_seq;
ALTER TABLE callcenter_queues.calls ADD COLUMN update_seq BIGINT NOT NULL DEFAULT nextval('callcenter_queues.calls_update_seq');
ALTER SEQUENCE callcenter_queues.calls_update_seq OWNED BY callcenter_queues.calls.update_seq;

CREATE OR REPLACE FUNCTION trigger_inc_calls_update_seq()
    RETURNS TRIGGER AS $$
BEGIN
    NEW.update_seq = nextval('callcenter_queues.calls_update_seq');
RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER operators_queues_inc_calls_update_seq
    BEFORE UPDATE ON callcenter_queues.calls
    FOR EACH ROW
    EXECUTE PROCEDURE trigger_inc_calls_update_seq();

CREATE UNIQUE INDEX IF NOT EXISTS calls_update_seq_uniqueness ON callcenter_queues.calls (update_seq);
ALTER TABLE callcenter_queues.calls ADD CONSTRAINT calls_update_seq_uniqueness UNIQUE USING INDEX calls_update_seq_uniqueness;


-- table for storing routed calls by POST /calls/route handler
CREATE TABLE callcenter_queues.routed_calls
(
    id                  VARCHAR  PRIMARY KEY,  -- id коммутации звонка, генерируем на нашей стороне (хэш от call_guid + metaqueue + idempotency_token)
    asterisk_call_id    VARCHAR,  -- id соответствующего звонка на asterisk (заполняется по факту появления звонка на нашем бэке)
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    call_guid           VARCHAR NOT NULL, -- глобальный идентификатор звонка, у 1 звонка может быть много коммутаций
    metaqueue           VARCHAR NOT NULL,  -- имя метаочереди, в которую распределен звонок
    subcluster          VARCHAR NOT NULL  -- номер сабкластера, на который распределен звонок
);

CREATE INDEX routed_calls_call_guid_idx ON callcenter_queues.routed_calls(call_guid);
CREATE INDEX routed_calls_created_at_idx ON callcenter_queues.routed_calls(created_at);
CREATE INDEX routed_calls_asterisk_call_id_idx ON callcenter_queues.routed_calls(asterisk_call_id);
CREATE INDEX routed_calls_metaqueue_idx ON callcenter_queues.routed_calls(metaqueue);
CREATE INDEX routed_calls_subcluster_idx ON callcenter_queues.routed_calls(subcluster);

-- table for storing statuses on queue
CREATE TYPE callcenter_queues.talking_status_type AS (
    -- статус talking из ЛБ
    sip_username            VARCHAR, -- идентификатор ответившего оператора
    is_talking              BOOLEAN, -- говорит или нет в данный момент
    metaqueue               VARCHAR, -- метаочередь звонка
    subcluster              VARCHAR, -- сабкластер звонка
    updated_at              TIMESTAMPTZ, -- event time, not time of sql update
    tech_postcall_until     TIMESTAMPTZ,  -- момент времени, до которого должен продолжаться технический postcall по таймеру
    asterisk_call_id        VARCHAR
    );

CREATE TABLE callcenter_queues.talking_status
(
    sip_username            VARCHAR PRIMARY KEY, -- идентификатор ответившего оператора (он же old agent_id)
    is_talking              BOOLEAN NOT NULL DEFAULT false,
    metaqueue               VARCHAR, -- метаочередь звонка
    subcluster              VARCHAR, -- сабкластер звонка
    updated_at              TIMESTAMPTZ NOT NULL , -- event time, not time of sql update
    tech_postcall_until     TIMESTAMPTZ,   -- момент времени, до которого должен продолжаться технический postcall (выставляется после завершения последнего звонка)
    asterisk_call_id        VARCHAR
);

CREATE INDEX talking_status_updated_idx ON callcenter_queues.talking_status(updated_at);
CREATE INDEX talking_status_is_talking_idx ON callcenter_queues.talking_status(is_talking);
CREATE INDEX talking_status_tech_postcall_until_idx ON callcenter_queues.talking_status(tech_postcall_until);

-- tel state table
/*
Таблица является кэшом над tel_api и хранит сырые данные.
Таблица находится в постоянном "инкрементальном" обновлении.
1) POST запросы
При успешном смене статуса в tel-api результат сохраняется в таблицу.
При неуспешной смене статуса результат в таблице инвалидируется (is_valid=False).
2) GET запросы
При запросе статуса в tel, вначале мы будем пытаться взять его из таблицы, и лишь не найдя его пойдем в tel-api.
При хождении в tel-api за статусом, он сохраняется локально.
*/
CREATE TABLE IF NOT EXISTS callcenter_queues.tel_state
(
    sip_username VARCHAR PRIMARY KEY,
    is_connected BOOLEAN NOT NULL DEFAULT FALSE,
    is_paused BOOLEAN NOT NULL DEFAULT FALSE,
    metaqueues VARCHAR[] NOT NULL DEFAULT ARRAY[]::VARCHAR[],
    subcluster VARCHAR,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), --  время, когда был получен и сохранен статус
    is_valid BOOLEAN NOT NULL DEFAULT FALSE -- валидность (для невалидных строк мы не знаем точное состояние юзера)
);

CREATE INDEX IF NOT EXISTS idx_is_valid ON callcenter_queues.tel_state (is_valid);
CREATE INDEX IF NOT EXISTS idx_subcluster ON callcenter_queues.tel_state (subcluster);

CREATE SEQUENCE callcenter_queues.tel_state_updated_seq;
ALTER TABLE callcenter_queues.tel_state ADD COLUMN updated_seq BIGINT NOT NULL DEFAULT nextval('callcenter_queues.tel_state_updated_seq');
ALTER SEQUENCE callcenter_queues.tel_state_updated_seq OWNED BY callcenter_queues.tel_state.updated_seq;

CREATE OR REPLACE FUNCTION trigger_inc_tel_state_updated_seq()
    RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_seq = nextval('callcenter_queues.tel_state_updated_seq');
RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tel_state_inc_updated_seq
    BEFORE UPDATE ON callcenter_queues.tel_state
    FOR EACH ROW
    EXECUTE PROCEDURE trigger_inc_tel_state_updated_seq();

CREATE UNIQUE INDEX IF NOT EXISTS tel_state_updated_seq_uniqueness ON callcenter_queues.tel_state (updated_seq);
ALTER TABLE callcenter_queues.tel_state ADD CONSTRAINT tel_state_updated_seq_uniqueness UNIQUE USING INDEX tel_state_updated_seq_uniqueness;

-- <metaqueues and subclusters> linkage table
/*
Наличие записи в таблице равносильно тому, что связка <саб + мета> настроена на стороне НОК.
Можно включать выключать саб относительно нашего бэка(см. ниже).
На включенных сабах мжно проихводить тонкую настроку (вкл/выкл балансировку звонков, автобалансировку операторов).
*/
CREATE TABLE IF NOT EXISTS callcenter_queues.callcenter_system_info
(
    metaqueue VARCHAR NOT NULL,
    subcluster VARCHAR NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT FALSE,
    /*
        включен или нет кластер относительно нашего бэка.
        Отключенный кластер виден только в админке сабкластеров, но не виден в других.
        Включенный кластер начинает быть видимым в разделе управления операторов, подсчете метрик и тд
    */

    enabled_for_call_balancing BOOLEAN NOT NULL DEFAULT FALSE, -- включен или нет кластер для балансировки звонков

    enabled_for_sip_user_autobalancing BOOLEAN NOT NULL DEFAULT FALSE,
    /*
        включен или нет кластер для автобалансировки операторов (при этом ручная force балансировка на него возможна)
    */
    pg_created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    pg_updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (metaqueue, subcluster)
);

-- table for storing target queues info for sip_user
CREATE TABLE IF NOT EXISTS callcenter_queues.target_queues
(
    sip_username VARCHAR PRIMARY KEY,
    metaqueues VARCHAR[] NOT NULL DEFAULT ARRAY[]::VARCHAR[],
    wanted_subcluster VARCHAR,
    pg_created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    pg_updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE SEQUENCE callcenter_queues.target_queues_updated_seq;
ALTER TABLE callcenter_queues.target_queues ADD COLUMN updated_seq BIGINT NOT NULL DEFAULT nextval('callcenter_queues.target_queues_updated_seq');
ALTER SEQUENCE callcenter_queues.target_queues_updated_seq OWNED BY callcenter_queues.target_queues.updated_seq;

CREATE OR REPLACE FUNCTION trigger_inc_target_queues_updated_seq()
    RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_seq = nextval('callcenter_queues.target_queues_updated_seq');
RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER global_inc_target_queues_updated_seq
    BEFORE UPDATE ON callcenter_queues.target_queues
    FOR EACH ROW
    EXECUTE PROCEDURE trigger_inc_target_queues_updated_seq();

CREATE UNIQUE INDEX IF NOT EXISTS target_queues_updated_seq_uniqueness ON callcenter_queues.target_queues (updated_seq);
ALTER TABLE callcenter_queues.target_queues ADD CONSTRAINT target_queues_updated_seq_uniqueness UNIQUE USING INDEX target_queues_updated_seq_uniqueness;

-- table for storing target status for sip_user
CREATE TABLE IF NOT EXISTS callcenter_queues.target_status
(
    sip_username VARCHAR PRIMARY KEY,
    status VARCHAR NOT NULL,
    pg_created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    pg_updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    project VARCHAR NOT NULL,
    updated_seq BIGINT NOT NULL
    );

CREATE UNIQUE INDEX IF NOT EXISTS target_status_updated_seq_uniqueness ON callcenter_queues.target_status (updated_seq);
ALTER TABLE callcenter_queues.target_status ADD CONSTRAINT target_status_updated_seq_uniqueness UNIQUE USING INDEX target_status_updated_seq_uniqueness;

CREATE INDEX IF NOT EXISTS calls_call_guid_idx ON callcenter_queues.calls(call_guid);

-- table for storing last cursors to change status
CREATE TABLE IF NOT EXISTS callcenter_queues.changes_positions
(
    consumer VARCHAR PRIMARY KEY,
    queues_changes_position BIGINT NOT NULL DEFAULT 0,
    queues_position_fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status_changes_position BIGINT NOT NULL DEFAULT 0,
    status_position_fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO callcenter_queues.changes_positions (consumer) VALUES ('status_changer');
