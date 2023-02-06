-- copied from uservices `services/callcenter-stats/testsuite/schemas/postgresql/callcenter_stats.sql`
DROP SCHEMA IF EXISTS callcenter_stats CASCADE;

CREATE SCHEMA callcenter_stats;
-- table for storing ended call qproc transactions - data moved from call_status when transaction is ended
CREATE TABLE callcenter_stats.call_history
(
    id                  VARCHAR             , -- не возрастающий идентификатор записи (хэш от группы полей)
    created_at          TIMESTAMPTZ         DEFAULT NOW(), -- время создания записи
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
    PRIMARY KEY (id)
);

CREATE INDEX call_history_created_at_idx ON callcenter_stats.call_history(created_at);
-- Индексы для ускорения запросов с фильтрами для ручки /calls/history
CREATE INDEX call_history_agent_id_idx ON callcenter_stats.call_history(agent_id);
CREATE INDEX call_history_abonent_phone_id_idx ON callcenter_stats.call_history(abonent_phone_id);
CREATE INDEX call_history_endreason_idx ON callcenter_stats.call_history(endreason);
CREATE INDEX call_history_queued_at_idx ON callcenter_stats.call_history(queued_at);
CREATE INDEX call_history_completed_at_idx ON callcenter_stats.call_history(completed_at);
