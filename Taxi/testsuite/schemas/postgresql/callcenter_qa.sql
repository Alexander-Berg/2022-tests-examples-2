DROP SCHEMA IF EXISTS callcenter_qa CASCADE;

CREATE SCHEMA callcenter_qa;

-- distlocks table
CREATE TABLE callcenter_qa.distlocks
(
    key             TEXT PRIMARY KEY,
    owner           TEXT,
    expiration_time TIMESTAMPTZ
);

-- table for storing cursor
CREATE TABLE callcenter_qa.cc_stats_cursor
(
    last_cursor BIGINT NOT NULL
);

-- table for storing calls for recognition
CREATE TABLE callcenter_qa.calls
(
    id                  VARCHAR             , -- неупорядоченный идентификатор записи (хэш от группы полей)
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(), -- время создания записи
    stq_started_at      TIMESTAMPTZ         , -- время отправки записи на распознование
    stq_finished_at     TIMESTAMPTZ         , -- время окончания распознования записи
    call_id             VARCHAR NOT NULL    , -- локальный идентификатор звонка
    call_guid           VARCHAR             , -- глобальный идентификатор звонка (из МЕТА)
    duration            INTERVAL NOT NULL   , -- длительность разговора
    in_operation_id     VARCHAR             , -- id операции распознавания канала in
    out_operation_id    VARCHAR             , -- id операции распознавания канала out
    in_text             VARCHAR             , -- распознанный текст канала in
    out_text            VARCHAR             , -- распознанный текст канала out
    in_words            jsonb               , -- список распознанных слов канала in
    out_words           jsonb               , -- список распознанных слов канала out
    PRIMARY KEY (id)
);

CREATE INDEX calls_stq_finished_at_idx ON callcenter_qa.calls(stq_finished_at);

-- table for storing feedbacks
CREATE TABLE callcenter_qa.feedbacks
(
    id                  VARCHAR             , -- уникальный id фидбека
    created_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP, -- время создания записи
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP, -- время последнего обновления записи
    yandex_uid          VARCHAR NOT NULL    , -- uid оператора с прокси
    call_id             VARCHAR             , -- локальный идентификатор звонка
    call_guid           VARCHAR             , -- глобальный идентификатор звонка (из МЕТА)
    commutation_id      VARCHAR             , -- идентификатор коммутации
    type                VARCHAR NOT NULL    , -- тип фидбека
    project             VARCHAR             , -- проект, на котором работает оператор
    binary_data         jsonb               , -- ссылки на файлы, прикрепленные к обращению
    args                jsonb               , -- содержание обращения, заполняется оператором
    extra               jsonb               , -- дополнительная информация об обращении, пришедшая с фронта
    external_info       jsonb               , -- информация полученная из других сервисов. Необходима для
                                              -- создания массовых инцидентов
    enabled_for_aggregation BOOLEAN NOT NULL DEFAULT TRUE, -- нужно ли учитывать фидбек при агрегации
    PRIMARY KEY (id)
);

-- table for storing links between tickets and incidents
CREATE INDEX IF NOT EXISTS feedbacks_created_at_ts ON callcenter_qa.feedbacks(created_at);
CREATE INDEX IF NOT EXISTS feedbacks_updated_at_ts ON callcenter_qa.feedbacks(updated_at);
CREATE INDEX IF NOT EXISTS feedbacks_call_guid ON callcenter_qa.feedbacks(call_guid);
CREATE INDEX IF NOT EXISTS feedbacks_type ON callcenter_qa.feedbacks(type);
CREATE INDEX IF NOT EXISTS feedbacks_commutation_id ON callcenter_qa.feedbacks(commutation_id);

CREATE TABLE callcenter_qa.tickets
(
    ticket_id           VARCHAR             , -- уникальный id тикета
    ticket_name         VARCHAR NOT NULL    , -- название тикета. пример - TAXIBACKEND-1234
    ticket_uri          VARCHAR             , -- полный uri тикета
    created_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP, -- время создания записи
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP, -- время последнего обновления записи
    feedback_id         VARCHAR NOT NULL    , -- id фидбека
    status              VARCHAR DEFAULT 'created', -- статус тикета
    PRIMARY KEY(ticket_id)
);

CREATE INDEX IF NOT EXISTS tickets_created_at_ts ON callcenter_qa.tickets(created_at);
CREATE INDEX IF NOT EXISTS tickets_updated_at_ts ON callcenter_qa.tickets(updated_at);
CREATE INDEX IF NOT EXISTS tickets_status ON callcenter_qa.tickets(status);
CREATE INDEX IF NOT EXISTS tickets_feedback_id ON callcenter_qa.tickets USING HASH(feedback_id);

-- table for created mass incidents;
CREATE TABLE callcenter_qa.mass_incidents
(
    id                  VARCHAR             , -- уникальный id тикета
    name                VARCHAR NOT NULL    , -- название тикета. пример - TAXIBACKEND-1234
    uri                 VARCHAR             , -- полный uri тикета
    created_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP, -- время создания записи
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP, -- время последнего обновления записи
    status              VARCHAR DEFAULT 'created', -- статус тикета
    PRIMARY KEY(id)
);

CREATE INDEX IF NOT EXISTS mass_incidents_created_at_ts ON callcenter_qa.mass_incidents(created_at);
CREATE INDEX IF NOT EXISTS mass_incidents_updated_at_ts ON callcenter_qa.mass_incidents(updated_at);
CREATE INDEX IF NOT EXISTS mass_incidents_status ON callcenter_qa.mass_incidents(status);

-- table for links between mass incidents and feedbacks
CREATE TABLE callcenter_qa.mass_incident_links
(
    ticket_id           VARCHAR             , -- уникальный id тикета
    feedback_id         VARCHAR NOT NULL    , -- идентификатор фидбека
    created_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP, -- время создания записи
    PRIMARY KEY(ticket_id, feedback_id)
);

CREATE INDEX IF NOT EXISTS mass_incident_links_feedback_id
    ON callcenter_qa.mass_incident_links USING HASH(feedback_id);
CREATE INDEX IF NOT EXISTS mass_incident_links_created_at_ts ON callcenter_qa.mass_incident_links(created_at);

-- table for numbers in tags
CREATE TABLE callcenter_qa.tags
(
    uuid                VARCHAR             , -- уникальный идентификатор записи
    personal_phone_id   VARCHAR NOT NULL    , -- personal_phone_id клиента
    created_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP, -- время создания записи
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP, -- время последнего обновления записи
    project             VARCHAR NOT NULL    , -- проект, на котором произошел бан
    extra               jsonb               , -- дополнительные аргументы для бана
    reason              VARCHAR NOT NULL    , -- причина, по которой пользователь попал в черный список
    blocked_until       TIMESTAMPTZ NOT NULL, -- время, до которого пользователь находится в бане
    PRIMARY KEY(uuid)
);

CREATE INDEX IF NOT EXISTS tags_created_at_ts ON callcenter_qa.tags(created_at);
CREATE INDEX IF NOT EXISTS tags_updated_at_ts ON callcenter_qa.tags(updated_at);
CREATE INDEX IF NOT EXISTS tags_blocked_until_ts ON callcenter_qa.tags(blocked_until);
CREATE INDEX IF NOT EXISTS tags_abonent_phone_id ON callcenter_qa.tags(personal_phone_id);
CREATE INDEX IF NOT EXISTS tags_project ON callcenter_qa.tags(project);

CREATE TYPE callcenter_qa.tag_type_v1 AS
(
    uuid VARCHAR,
    personal_phone_id VARCHAR,
    project VARCHAR,
    extra jsonb,
    reason VARCHAR,
    feedback_ids VARCHAR[]
);

-- table for links between tags and feedbacks
CREATE TABLE callcenter_qa.tag_links
(
    tag_uuid            VARCHAR             , -- uuid записи в tags
    feedback_id         VARCHAR             , -- идентификатор фидбека
    created_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP, -- время создания записи
    PRIMARY KEY(tag_uuid, feedback_id)
);

CREATE INDEX IF NOT EXISTS tag_links_feedback_id ON callcenter_qa.tag_links(feedback_id);
CREATE INDEX IF NOT EXISTS tag_links_tag_uuid ON callcenter_qa.tag_links(tag_uuid);
CREATE INDEX IF NOT EXISTS tag_links_created_at_ts ON callcenter_qa.tag_links(created_at);

-- table for storing support ratings from csat
CREATE TABLE callcenter_qa.support_ratings
(
    created_at TIMESTAMPTZ DEFAULT NOW() , -- время записи
    rating VARCHAR , -- оценка от пользователя
    call_guid VARCHAR , -- идентификатор звонка
    PRIMARY KEY (call_guid)
);
