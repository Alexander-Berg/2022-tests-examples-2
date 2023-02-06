/* V1 */
/* pgmigrate-encoding: utf-8 */

BEGIN;

CREATE SCHEMA IF NOT EXISTS driver_status;

CREATE TABLE IF NOT EXISTS driver_status.status_types(
    id text NOT NULL,
    props jsonb,
    PRIMARY KEY (id)
);

COMMENT ON TABLE driver_status.status_types IS 'Driver status allowed values';

CREATE TABLE IF NOT EXISTS driver_status.app_profiles(
    id text NOT NULL,
    props jsonb,
    PRIMARY KEY (id)
);

COMMENT ON TABLE driver_status.app_profiles IS 'Application profile type allowed values';

CREATE TABLE IF NOT EXISTS driver_status.statuses(
  park_id text NOT NULL,
  driver_id text NOT NULL,
  app_profile text NOT NULL REFERENCES driver_status.app_profiles(id),
  status text NOT NULL REFERENCES driver_status.status_types(id),
  updated_ts timestamptz NOT NULL default NOW(),                -- Время последнего обновления всей строки
  status_updated_ts timestamptz NOT NULL default NOW(),         -- Время последнего обновления поля "status"
  next_periodical_update_ts timestamptz NOT NULL default NOW(), -- Время следующего выполнения периодической проверки блокировок
  periodical_update_performed boolean NOT NULL default FALSE,   -- Выполнено ли периодическое обновление после смены статуса водителем
  periodical_update_mode text,
  source text,
  online_start timestamptz,
  blocked_reason text,
  is_only_card boolean NOT NULL default FALSE,
  order_id text,
  order_provider integer NOT NULL default 0,
  comment text,
  driver_providers integer NOT NULL default 0,
  integration_event boolean NOT NULL default FALSE,
  PRIMARY KEY (park_id, driver_id, app_profile)
);

COMMENT ON TABLE driver_status.statuses IS 'Driver statuses with modificators';
COMMENT ON COLUMN driver_status.statuses.park_id IS 'Park ID';
COMMENT ON COLUMN driver_status.statuses.app_profile IS 'Driver application profile type (i.e. application name)';
COMMENT ON COLUMN driver_status.statuses.driver_id IS 'Driver ID in park';
COMMENT ON COLUMN driver_status.statuses.status IS 'Textual representation of driver status';
COMMENT ON COLUMN driver_status.statuses.updated_ts IS 'Record last modified timestamp';
COMMENT ON COLUMN driver_status.statuses.status_updated_ts IS 'Last modified by client timestamp';
COMMENT ON COLUMN driver_status.statuses.next_periodical_update_ts IS 'Timestamp of the next scheduled check for blocks for driver';
COMMENT ON COLUMN driver_status.statuses.periodical_update_performed IS 'True if periodical update was performed after status change';
COMMENT ON COLUMN driver_status.statuses.periodical_update_mode IS 'Periodical updater mode to use for row';
COMMENT ON COLUMN driver_status.statuses.source IS 'Status source (service or client or periodical updater)';
COMMENT ON COLUMN driver_status.statuses.online_start IS 'Driver online (free) status time';
COMMENT ON COLUMN driver_status.statuses.blocked_reason IS 'Reason why driver cannot set free status';
COMMENT ON COLUMN driver_status.statuses.is_only_card IS 'True if driver can get only cashless orders';
COMMENT ON COLUMN driver_status.statuses.order_id IS 'Current order ID for driver';
COMMENT ON COLUMN driver_status.statuses.order_provider IS 'Current order provider for driver';
COMMENT ON COLUMN driver_status.statuses.comment IS 'Status comment, as from client/service';
COMMENT ON COLUMN driver_status.statuses.driver_providers IS 'Providers that should get status updates for this driver';
COMMENT ON COLUMN driver_status.statuses.integration_event IS 'True if status should be sent to integration';

CREATE INDEX IF NOT EXISTS statuses_updated_ts ON driver_status.statuses(updated_ts);
CREATE INDEX IF NOT EXISTS statuses_status_updated_ts ON driver_status.statuses(status_updated_ts);
CREATE INDEX IF NOT EXISTS statuses_next_periodical_updatd_ts ON driver_status.statuses(next_periodical_update_ts);

END;
