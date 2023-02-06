CREATE SCHEMA IF NOT EXISTS rent;

CREATE EXTENSION IF NOT EXISTS btree_gist;

CREATE TABLE IF NOT EXISTS rent.affiliations
(
    record_id               TEXT PRIMARY KEY,
    park_id                 TEXT      NOT NULL,
    local_driver_id         TEXT,
    original_driver_park_id TEXT      NOT NULL,
    original_driver_id      TEXT      NOT NULL,
    creator_uid             TEXT      NOT NULL,
    created_at              TIMESTAMP NOT NULL,
    modified_at             TIMESTAMP NOT NULL DEFAULT NOW(), -- replication marker
    state                   TEXT      NOT NULL,
    CONSTRAINT bind UNIQUE (park_id, original_driver_park_id, original_driver_id)
);

CREATE INDEX ON rent.affiliations (record_id, park_id);

CREATE TABLE IF NOT EXISTS rent.records
(
    record_id             TEXT PRIMARY KEY,
    idempotency_token     TEXT      NOT NULL,
    owner_park_id         TEXT      NOT NULL,
    owner_serial_id       BIGINT    NOT NULL,                      -- mostly for representation
    driver_id             TEXT      NOT NULL,
    affiliation_id        TEXT REFERENCES rent.affiliations (record_id),
    title                 TEXT,
    comment               TEXT,
    balance_notify_limit  TEXT,
    begins_at             TIMESTAMP NOT NULL,
    ends_at               TIMESTAMP,
    asset_type            TEXT      NOT NULL,                      -- rented object type
    asset_params          JSONB,                                   -- rented object additional info
    charging_type         TEXT      NOT NULL,
    charging_params       JSONB,
    charging_starts_at    TIMESTAMP NOT NULL,
    creator_uid           TEXT      NOT NULL,
    created_at            TIMESTAMP NOT NULL,
    modified_at           TIMESTAMP NOT NULL DEFAULT NOW(),        -- replication marker
    accepted_at           TIMESTAMP,
    acceptance_reason     TEXT,
    rejected_at           TIMESTAMP,
    rejection_reason      TEXT,
    terminated_at         TIMESTAMP,
    termination_reason    TEXT,
    last_seen_at          TIMESTAMP,
    transfer_order_number TEXT      NOT NULL,
    use_event_queue       BOOLEAN   NOT NULL DEFAULT FALSE,
    use_arbitrary_entries BOOLEAN   NOT NULL DEFAULT FALSE,
    start_clid            TEXT      NULL,
    UNIQUE (owner_park_id, idempotency_token),
    UNIQUE (owner_park_id, owner_serial_id),
    CONSTRAINT check_starts_at_end CHECK ( begins_at <= ends_at ), -- sanity check (allows using tsrange())
    -- rent can't be both accepted and rejected or both rejected and terminated
    CONSTRAINT check_state CHECK (((accepted_at IS NULL AND terminated_at IS NULL) OR rejected_at IS NULL))
);

-- ancillary table to hold serials for each separate owner_park
CREATE TABLE IF NOT EXISTS rent.record_park_counters
(
    owner_park_id    TEXT PRIMARY KEY,
    latest_serial_id BIGINT NOT NULL -- == MAX(records.owner_serial_id)
);

CREATE INDEX ON rent.records (record_id, owner_park_id);


-- TODO: partition by event_at
CREATE TABLE IF NOT EXISTS rent.same_park_transactions_log
(
    id          BIGSERIAL PRIMARY KEY,
    record_id   TEXT      NOT NULL REFERENCES rent.records (record_id) ON DELETE RESTRICT,
    serial_id   BIGINT    NOT NULL,               -- serial transaction id for same record
    category_id TEXT      NOT NULL,
    description TEXT      NOT NULL,
    driver_id   TEXT      NOT NULL,
    park_id     TEXT      NOT NULL,
    event_at    TIMESTAMP NOT NULL,
    amount      DECIMAL   NOT NULL,
    uploaded_at TIMESTAMP,
    modified_at TIMESTAMP NOT NULL DEFAULT NOW(), -- replication marker
    UNIQUE (record_id, serial_id)                 -- transaction creation race protection
);

CREATE TABLE IF NOT EXISTS rent.external_park_transactions_log
(
    id                      BIGSERIAL PRIMARY KEY,
    record_id               TEXT      NOT NULL REFERENCES rent.records (record_id) ON DELETE RESTRICT,
    record_serial_id        BIGINT    NOT NULL,
    serial_id               BIGINT    NOT NULL,               -- serial transaction id for same record
    amount                  DECIMAL   NOT NULL,
    park_id                 TEXT      NOT NULL,
    local_driver_id         TEXT      NOT NULL,
    external_driver_id      TEXT      NOT NULL,
    external_driver_park_id TEXT      NOT NULL,
    timestamp               TIMESTAMP NOT NULL,
    uploaded_at             TIMESTAMP,
    modified_at             TIMESTAMP NOT NULL DEFAULT NOW(), -- replication marker
    UNIQUE (record_id, serial_id)                             -- transaction creation race protection
);

CREATE TABLE IF NOT EXISTS rent.affiliation_notifications
(
    affiliation_id TEXT PRIMARY KEY REFERENCES rent.affiliations (record_id) ON DELETE CASCADE,
    notified_at    TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS rent.rent_notifications
(
    rent_id     TEXT PRIMARY KEY REFERENCES rent.records (record_id) ON DELETE CASCADE,
    notified_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS rent.park_terminate_rent_notifications
(
    rent_id     TEXT PRIMARY KEY REFERENCES rent.records (record_id) ON DELETE CASCADE,
    notified_at TIMESTAMP NOT NULL
);

/**
  Rows created by endpoint
  Filled by STQ, marked as finished by cron
 */
CREATE TABLE IF NOT EXISTS rent.external_debt_cancellations
(
    id              TEXT PRIMARY KEY,
    /* rent id */
    record_id       TEXT        NOT NULL REFERENCES rent.records (record_id) ON DELETE RESTRICT,
    /* ids from billing, filled in stq later */
    payment_doc_ids BIGINT[]    NOT NULL DEFAULT ARRAY []::BIGINT[],
    is_complete     BOOLEAN     NOT NULL DEFAULT FALSE,
    created_by_json JSONB       NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS external_debt_cancellations_created_at_id_btree_idx ON rent.external_debt_cancellations
    USING btree (created_at, id)
    WHERE NOT external_debt_cancellations.is_complete;

CREATE UNIQUE INDEX IF NOT EXISTS external_debt_cancellations_record_id_unique_idx ON rent.external_debt_cancellations (record_id)
    WHERE NOT external_debt_cancellations.is_complete;

CREATE TABLE IF NOT EXISTS rent.park_comm_sync_rent_termination
(
    rent_id    TEXT PRIMARY KEY REFERENCES rent.records (record_id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE rent.event_queue
(
    rent_id      TEXT        NOT NULL REFERENCES rent.records (record_id) ON DELETE CASCADE,
    event_number BIGINT      NOT NULL,
    event_at     TIMESTAMPTZ NOT NULL,
    executed_at  TIMESTAMPTZ,
    modified_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (rent_id, event_number)
);
CREATE INDEX event_queue_unexecuted_idx ON rent.event_queue USING btree(event_at) WHERE executed_at IS NULL;

CREATE TABLE IF NOT EXISTS rent.active_day_start_triggers
(
    rent_id              TEXT REFERENCES rent.records (record_id),
    event_number         BIGINT      NOT NULL,
    park_id              TEXT        NOT NULL,
    driver_id            TEXT        NOT NULL,
    lower_datetime_bound TIMESTAMPTZ NOT NULL,
    upper_datetime_bound TIMESTAMPTZ NULL,
    triggered_at         TIMESTAMPTZ NULL,
    order_id             TEXT        NULL,
    modified_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (rent_id, event_number)
);

CREATE INDEX IF NOT EXISTS order_lookup_idx ON rent.active_day_start_triggers
    USING GIST (driver_id, tstzrange(lower_datetime_bound, upper_datetime_bound)) WHERE triggered_at IS NULL;

CREATE INDEX ON rent.affiliations USING btree(modified_at);
CREATE INDEX ON rent.same_park_transactions_log USING btree(modified_at);
CREATE INDEX ON rent.external_park_transactions_log USING btree(modified_at);
CREATE INDEX ON rent.event_queue USING btree(modified_at);
CREATE INDEX ON rent.active_day_start_triggers USING btree(modified_at);
CREATE INDEX ON rent.external_debt_cancellations USING btree(modified_at);


-- rent.affiliation_notifications
ALTER TABLE rent.affiliation_notifications ADD COLUMN notified_at_tz TIMESTAMPTZ;

CREATE FUNCTION rent.affiliation_notifications_to_tz() RETURNS TRIGGER AS $$
BEGIN
    NEW.notified_at_tz = NEW.notified_at AT TIME ZONE 'UTC';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_to_tz
BEFORE UPDATE OF notified_at ON rent.affiliation_notifications
FOR EACH ROW
EXECUTE PROCEDURE rent.affiliation_notifications_to_tz();

---

CREATE FUNCTION rent.affiliation_notifications_from_tz() RETURNS TRIGGER AS $$
BEGIN
    NEW.notified_at = NEW.notified_at_tz AT TIME ZONE 'UTC';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_from_tz
BEFORE UPDATE OF notified_at_tz ON rent.affiliation_notifications
FOR EACH ROW
EXECUTE PROCEDURE rent.affiliation_notifications_from_tz();

---

CREATE FUNCTION rent.affiliation_notifications_insert() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.notified_at IS NOT NULL THEN
        NEW.notified_at_tz = NEW.notified_at AT TIME ZONE 'UTC';
    ELSEIF NEW.notified_at_tz IS NOT NULL THEN
        NEW.notified_at = NEW.notified_at_tz AT TIME ZONE 'UTC';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER insert_sync BEFORE INSERT ON rent.affiliation_notifications
FOR EACH ROW
EXECUTE PROCEDURE rent.affiliation_notifications_insert();

-- rent.park_terminate_rent_notifications
ALTER TABLE rent.park_terminate_rent_notifications ADD COLUMN notified_at_tz TIMESTAMPTZ;

CREATE FUNCTION rent.park_terminate_rent_notifications_to_tz() RETURNS TRIGGER AS $$
BEGIN
    NEW.notified_at_tz = NEW.notified_at AT TIME ZONE 'UTC';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_to_tz
BEFORE UPDATE OF notified_at ON rent.park_terminate_rent_notifications
FOR EACH ROW
EXECUTE PROCEDURE rent.park_terminate_rent_notifications_to_tz();

---

CREATE FUNCTION rent.park_terminate_rent_notifications_from_tz() RETURNS TRIGGER AS $$
BEGIN
    NEW.notified_at = NEW.notified_at_tz AT TIME ZONE 'UTC';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_from_tz
BEFORE UPDATE OF notified_at_tz ON rent.park_terminate_rent_notifications
FOR EACH ROW
EXECUTE PROCEDURE rent.park_terminate_rent_notifications_from_tz();

---

CREATE FUNCTION rent.park_terminate_rent_notifications_insert() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.notified_at IS NOT NULL THEN
        NEW.notified_at_tz = NEW.notified_at AT TIME ZONE 'UTC';
    ELSEIF NEW.notified_at_tz IS NOT NULL THEN
        NEW.notified_at = NEW.notified_at_tz AT TIME ZONE 'UTC';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER insert_sync BEFORE INSERT ON rent.park_terminate_rent_notifications
FOR EACH ROW
EXECUTE PROCEDURE rent.park_terminate_rent_notifications_insert();

-- rent.rent_notifications
ALTER TABLE rent.rent_notifications ADD COLUMN notified_at_tz TIMESTAMPTZ;

CREATE FUNCTION rent.rent_notifications_to_tz() RETURNS TRIGGER AS $$
BEGIN
    NEW.notified_at_tz = NEW.notified_at AT TIME ZONE 'UTC';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_to_tz
BEFORE UPDATE OF notified_at ON rent.rent_notifications
FOR EACH ROW
EXECUTE PROCEDURE rent.rent_notifications_to_tz();

---

CREATE FUNCTION rent.rent_notifications_from_tz() RETURNS TRIGGER AS $$
BEGIN
    NEW.notified_at = NEW.notified_at_tz AT TIME ZONE 'UTC';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_from_tz
BEFORE UPDATE OF notified_at_tz ON rent.rent_notifications
FOR EACH ROW
EXECUTE PROCEDURE rent.rent_notifications_from_tz();

---

CREATE FUNCTION rent.rent_notifications_insert() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.notified_at IS NOT NULL THEN
        NEW.notified_at_tz = NEW.notified_at AT TIME ZONE 'UTC';
    ELSEIF NEW.notified_at_tz IS NOT NULL THEN
        NEW.notified_at = NEW.notified_at_tz AT TIME ZONE 'UTC';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER insert_sync BEFORE INSERT ON rent.rent_notifications
FOR EACH ROW
EXECUTE PROCEDURE rent.rent_notifications_insert();

--- affiliations

ALTER TABLE rent.affiliations ADD COLUMN created_at_tz TIMESTAMPTZ;
ALTER TABLE rent.affiliations ADD COLUMN modified_at_tz TIMESTAMPTZ DEFAULT NOW() NOT NULL;

CREATE INDEX ON rent.affiliations USING btree(modified_at_tz);

CREATE FUNCTION rent.affiliations_to_tz() RETURNS TRIGGER AS $$
BEGIN
    NEW.created_at_tz = NEW.created_at AT TIME ZONE 'UTC';
    NEW.modified_at_tz = NEW.modified_at AT TIME ZONE 'UTC';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_to_tz
BEFORE UPDATE OF created_at, modified_at ON rent.affiliations
FOR EACH ROW
EXECUTE PROCEDURE rent.affiliations_to_tz();

---

CREATE FUNCTION rent.affiliations_from_tz() RETURNS TRIGGER AS $$
BEGIN
    NEW.created_at = NEW.created_at_tz AT TIME ZONE 'UTC';
    NEW.modified_at = NEW.modified_at_tz AT TIME ZONE 'UTC';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_from_tz
BEFORE UPDATE OF created_at_tz, modified_at_tz ON rent.affiliations
FOR EACH ROW
EXECUTE PROCEDURE rent.affiliations_from_tz();

---

CREATE FUNCTION rent.affiliations_insert() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.created_at IS NOT NULL THEN
        NEW.created_at_tz = NEW.created_at AT TIME ZONE 'UTC';
    ELSEIF NEW.created_at_tz IS NOT NULL THEN
        NEW.created_at = NEW.created_at_tz AT TIME ZONE 'UTC';
    END IF;

    IF NEW.modified_at IS NOT NULL THEN
        NEW.modified_at_tz = NEW.modified_at AT TIME ZONE 'UTC';
    ELSEIF NEW.modified_at_tz IS NOT NULL THEN
        NEW.modified_at = NEW.modified_at_tz AT TIME ZONE 'UTC';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER insert_sync BEFORE INSERT ON rent.affiliations
FOR EACH ROW
EXECUTE PROCEDURE rent.affiliations_insert();

--- external_park_transactions_log

ALTER TABLE rent.external_park_transactions_log ADD COLUMN scheduled_at_tz TIMESTAMPTZ;
ALTER TABLE rent.external_park_transactions_log ADD COLUMN uploaded_at_tz TIMESTAMPTZ;
ALTER TABLE rent.external_park_transactions_log ADD COLUMN modified_at_tz TIMESTAMPTZ DEFAULT NOW() NOT NULL;

CREATE INDEX ON rent.external_park_transactions_log USING btree(modified_at_tz);

CREATE FUNCTION rent.external_park_transactions_log_to_tz() RETURNS TRIGGER AS $$
BEGIN
    NEW.scheduled_at_tz = NEW.timestamp AT TIME ZONE 'UTC';
    NEW.uploaded_at_tz = NEW.uploaded_at AT TIME ZONE 'UTC';
    NEW.modified_at_tz = NEW.modified_at AT TIME ZONE 'UTC';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_to_tz
BEFORE UPDATE OF timestamp, uploaded_at, modified_at ON rent.external_park_transactions_log
FOR EACH ROW
EXECUTE PROCEDURE rent.external_park_transactions_log_to_tz();

---

CREATE FUNCTION rent.external_park_transactions_log_from_tz() RETURNS TRIGGER AS $$
BEGIN
    NEW.timestamp = NEW.scheduled_at_tz AT TIME ZONE 'UTC';
    NEW.uploaded_at = NEW.uploaded_at_tz AT TIME ZONE 'UTC';
    NEW.modified_at = NEW.modified_at_tz AT TIME ZONE 'UTC';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_from_tz
BEFORE UPDATE OF scheduled_at_tz, uploaded_at_tz, modified_at_tz ON rent.external_park_transactions_log
FOR EACH ROW
EXECUTE PROCEDURE rent.external_park_transactions_log_from_tz();

---

CREATE FUNCTION rent.external_park_transactions_log_insert() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.timestamp IS NOT NULL THEN
        NEW.scheduled_at_tz = NEW.timestamp AT TIME ZONE 'UTC';
    ELSEIF NEW.scheduled_at_tz IS NOT NULL THEN
        NEW.timestamp = NEW.scheduled_at_tz AT TIME ZONE 'UTC';
    END IF;

    IF NEW.uploaded_at IS NOT NULL THEN
        NEW.uploaded_at_tz = NEW.uploaded_at AT TIME ZONE 'UTC';
    ELSEIF NEW.uploaded_at_tz IS NOT NULL THEN
        NEW.uploaded_at = NEW.uploaded_at_tz AT TIME ZONE 'UTC';
    END IF;

    IF NEW.modified_at IS NOT NULL THEN
        NEW.modified_at_tz = NEW.modified_at AT TIME ZONE 'UTC';
    ELSEIF NEW.modified_at_tz IS NOT NULL THEN
        NEW.modified_at = NEW.modified_at_tz AT TIME ZONE 'UTC';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER insert_sync BEFORE INSERT ON rent.external_park_transactions_log
FOR EACH ROW
EXECUTE PROCEDURE rent.external_park_transactions_log_insert();

--- records ----------------

ALTER TABLE rent.records ADD COLUMN begins_at_tz TIMESTAMPTZ;
ALTER TABLE rent.records ADD COLUMN ends_at_tz TIMESTAMPTZ;
ALTER TABLE rent.records ADD COLUMN charging_starts_at_tz TIMESTAMPTZ;
ALTER TABLE rent.records ADD COLUMN created_at_tz TIMESTAMPTZ;
ALTER TABLE rent.records ADD COLUMN modified_at_tz TIMESTAMPTZ DEFAULT NOW() NOT NULL;
ALTER TABLE rent.records ADD COLUMN accepted_at_tz TIMESTAMPTZ;
ALTER TABLE rent.records ADD COLUMN rejected_at_tz TIMESTAMPTZ;
ALTER TABLE rent.records ADD COLUMN terminated_at_tz TIMESTAMPTZ;
ALTER TABLE rent.records ADD COLUMN last_seen_at_tz TIMESTAMPTZ;

CREATE INDEX ON rent.records USING btree(modified_at_tz);

CREATE FUNCTION rent.records_to_tz() RETURNS TRIGGER AS $$
BEGIN
    NEW.begins_at_tz = NEW.begins_at AT TIME ZONE 'UTC';
    NEW.ends_at_tz = NEW.ends_at AT TIME ZONE 'UTC';
    NEW.charging_starts_at_tz = NEW.charging_starts_at AT TIME ZONE 'UTC';

    NEW.created_at_tz = NEW.created_at AT TIME ZONE 'UTC';
    NEW.modified_at_tz = NEW.modified_at AT TIME ZONE 'UTC';
    NEW.accepted_at_tz = NEW.accepted_at AT TIME ZONE 'UTC';
    NEW.rejected_at_tz = NEW.rejected_at AT TIME ZONE 'UTC';
    NEW.terminated_at_tz = NEW.terminated_at AT TIME ZONE 'UTC';
    NEW.last_seen_at_tz = NEW.last_seen_at AT TIME ZONE 'UTC';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_to_tz
BEFORE UPDATE OF
    begins_at, ends_at, charging_starts_at,
    created_at, modified_at, accepted_at,
    rejected_at, terminated_at, last_seen_at ON rent.records
FOR EACH ROW
EXECUTE PROCEDURE rent.records_to_tz();

---

CREATE FUNCTION rent.records_from_tz() RETURNS TRIGGER AS $$
BEGIN
    NEW.begins_at = NEW.begins_at_tz AT TIME ZONE 'UTC';
    NEW.ends_at = NEW.ends_at_tz AT TIME ZONE 'UTC';
    NEW.charging_starts_at = NEW.charging_starts_at_tz AT TIME ZONE 'UTC';

    NEW.created_at = NEW.created_at_tz AT TIME ZONE 'UTC';
    NEW.modified_at = NEW.modified_at_tz AT TIME ZONE 'UTC';
    NEW.accepted_at = NEW.accepted_at_tz AT TIME ZONE 'UTC';
    NEW.rejected_at = NEW.rejected_at_tz AT TIME ZONE 'UTC';
    NEW.terminated_at = NEW.terminated_at_tz AT TIME ZONE 'UTC';
    NEW.last_seen_at = NEW.last_seen_at_tz AT TIME ZONE 'UTC';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_from_tz
BEFORE UPDATE OF
    begins_at_tz, ends_at_tz, charging_starts_at_tz,
    created_at_tz, modified_at_tz, accepted_at_tz,
    rejected_at_tz, terminated_at_tz,last_seen_at_tz ON rent.records
FOR EACH ROW
EXECUTE PROCEDURE rent.records_from_tz();

---

CREATE FUNCTION rent.records_insert() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.begins_at IS NOT NULL THEN
        NEW.begins_at_tz = NEW.begins_at AT TIME ZONE 'UTC';
    ELSEIF NEW.begins_at_tz IS NOT NULL THEN
        NEW.begins_at = NEW.begins_at_tz AT TIME ZONE 'UTC';
    END IF;

    IF NEW.ends_at IS NOT NULL THEN
        NEW.ends_at_tz = NEW.ends_at AT TIME ZONE 'UTC';
    ELSEIF NEW.ends_at_tz IS NOT NULL THEN
        NEW.ends_at = NEW.ends_at_tz AT TIME ZONE 'UTC';
    END IF;

    IF NEW.charging_starts_at IS NOT NULL THEN
        NEW.charging_starts_at_tz = NEW.charging_starts_at AT TIME ZONE 'UTC';
    ELSEIF NEW.charging_starts_at_tz IS NOT NULL THEN
        NEW.charging_starts_at = NEW.charging_starts_at_tz AT TIME ZONE 'UTC';
    END IF;

    IF NEW.created_at IS NOT NULL THEN
        NEW.created_at_tz = NEW.created_at AT TIME ZONE 'UTC';
    ELSEIF NEW.created_at_tz IS NOT NULL THEN
        NEW.created_at = NEW.created_at_tz AT TIME ZONE 'UTC';
    END IF;

    IF NEW.modified_at IS NOT NULL THEN
        NEW.modified_at_tz = NEW.modified_at AT TIME ZONE 'UTC';
    ELSEIF NEW.modified_at_tz IS NOT NULL THEN
        NEW.modified_at = NEW.modified_at_tz AT TIME ZONE 'UTC';
    END IF;

    IF NEW.accepted_at IS NOT NULL THEN
        NEW.accepted_at_tz = NEW.accepted_at AT TIME ZONE 'UTC';
    ELSEIF NEW.accepted_at_tz IS NOT NULL THEN
        NEW.accepted_at = NEW.accepted_at_tz AT TIME ZONE 'UTC';
    END IF;

    IF NEW.rejected_at IS NOT NULL THEN
        NEW.rejected_at_tz = NEW.rejected_at AT TIME ZONE 'UTC';
    ELSEIF NEW.rejected_at_tz IS NOT NULL THEN
        NEW.rejected_at = NEW.rejected_at_tz AT TIME ZONE 'UTC';
    END IF;

    IF NEW.terminated_at IS NOT NULL THEN
        NEW.terminated_at_tz = NEW.terminated_at AT TIME ZONE 'UTC';
    ELSEIF NEW.terminated_at_tz IS NOT NULL THEN
        NEW.terminated_at = NEW.terminated_at_tz AT TIME ZONE 'UTC';
    END IF;

    IF NEW.last_seen_at IS NOT NULL THEN
        NEW.last_seen_at_tz = NEW.last_seen_at AT TIME ZONE 'UTC';
    ELSEIF NEW.last_seen_at_tz IS NOT NULL THEN
        NEW.last_seen_at = NEW.last_seen_at_tz AT TIME ZONE 'UTC';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER insert_sync BEFORE INSERT ON rent.records
FOR EACH ROW
EXECUTE PROCEDURE rent.records_insert();

---- same_park_transactions_log -----------

ALTER TABLE rent.same_park_transactions_log ADD COLUMN event_at_tz TIMESTAMPTZ;
ALTER TABLE rent.same_park_transactions_log ADD COLUMN uploaded_at_tz TIMESTAMPTZ;
ALTER TABLE rent.same_park_transactions_log ADD COLUMN modified_at_tz TIMESTAMPTZ DEFAULT NOW() NOT NULL;

CREATE INDEX ON rent.same_park_transactions_log USING btree(modified_at_tz);

CREATE FUNCTION rent.same_park_transactions_log_to_tz() RETURNS TRIGGER AS $$
BEGIN
    NEW.event_at_tz = NEW.event_at AT TIME ZONE 'UTC';
    NEW.uploaded_at_tz = NEW.uploaded_at AT TIME ZONE 'UTC';
    NEW.modified_at_tz = NEW.modified_at AT TIME ZONE 'UTC';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_to_tz
BEFORE UPDATE OF event_at, uploaded_at, modified_at ON rent.same_park_transactions_log
FOR EACH ROW
EXECUTE PROCEDURE rent.same_park_transactions_log_to_tz();

---

CREATE FUNCTION rent.same_park_transactions_log_from_tz() RETURNS TRIGGER AS $$
BEGIN
    NEW.event_at = NEW.event_at_tz AT TIME ZONE 'UTC';
    NEW.uploaded_at = NEW.uploaded_at_tz AT TIME ZONE 'UTC';
    NEW.modified_at = NEW.modified_at_tz AT TIME ZONE 'UTC';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_from_tz
BEFORE UPDATE OF event_at_tz, uploaded_at_tz, modified_at_tz ON rent.same_park_transactions_log
FOR EACH ROW
EXECUTE PROCEDURE rent.same_park_transactions_log_from_tz();

---

CREATE FUNCTION rent.same_park_transactions_log_insert() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.event_at IS NOT NULL THEN
        NEW.event_at_tz = NEW.event_at AT TIME ZONE 'UTC';
    ELSEIF NEW.event_at_tz IS NOT NULL THEN
        NEW.event_at = NEW.event_at_tz AT TIME ZONE 'UTC';
    END IF;

    IF NEW.uploaded_at IS NOT NULL THEN
        NEW.uploaded_at_tz = NEW.uploaded_at AT TIME ZONE 'UTC';
    ELSEIF NEW.uploaded_at_tz IS NOT NULL THEN
        NEW.uploaded_at = NEW.uploaded_at_tz AT TIME ZONE 'UTC';
    END IF;

    IF NEW.modified_at IS NOT NULL THEN
        NEW.modified_at_tz = NEW.modified_at AT TIME ZONE 'UTC';
    ELSEIF NEW.modified_at_tz IS NOT NULL THEN
        NEW.modified_at = NEW.modified_at_tz AT TIME ZONE 'UTC';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER insert_sync BEFORE INSERT ON rent.same_park_transactions_log
FOR EACH ROW
EXECUTE PROCEDURE rent.same_park_transactions_log_insert();

--- adding constraints

ALTER TABLE rent.affiliation_notifications ALTER COLUMN notified_at_tz SET NOT NULL;

ALTER TABLE rent.park_terminate_rent_notifications ALTER COLUMN notified_at_tz SET NOT NULL;

ALTER TABLE rent.rent_notifications ALTER COLUMN notified_at_tz SET NOT NULL;

ALTER TABLE rent.affiliations ALTER COLUMN created_at_tz SET NOT NULL;

ALTER TABLE rent.external_park_transactions_log ALTER COLUMN scheduled_at_tz SET NOT NULL;

ALTER TABLE rent.same_park_transactions_log ALTER COLUMN event_at_tz SET NOT NULL;

ALTER TABLE rent.records ALTER COLUMN begins_at_tz SET NOT NULL;
ALTER TABLE rent.records ALTER COLUMN charging_starts_at_tz SET NOT NULL;
ALTER TABLE rent.records ALTER COLUMN created_at_tz SET NOT NULL;

-- sanity check (allows using tstzrange())
ALTER TABLE rent.records ADD CONSTRAINT check_starts_at_end_tz CHECK ( begins_at_tz <= ends_at_tz );
-- rent can't be both accepted and rejected or both rejected and terminated
ALTER TABLE rent.records ADD CONSTRAINT check_state_tz CHECK (((accepted_at_tz IS NULL AND terminated_at_tz IS NULL) OR rejected_at_tz IS NULL));

--- deleting old

DROP TRIGGER update_to_tz on rent.affiliation_notifications CASCADE;
DROP TRIGGER update_from_tz on rent.affiliation_notifications CASCADE;
DROP TRIGGER insert_sync on rent.affiliation_notifications CASCADE;
DROP FUNCTION rent.affiliation_notifications_to_tz CASCADE;
DROP FUNCTION rent.affiliation_notifications_from_tz CASCADE;
DROP FUNCTION rent.affiliation_notifications_insert CASCADE;
ALTER TABLE rent.affiliation_notifications DROP COLUMN notified_at CASCADE;

DROP TRIGGER update_to_tz on rent.park_terminate_rent_notifications CASCADE;
DROP TRIGGER update_from_tz on rent.park_terminate_rent_notifications CASCADE;
DROP TRIGGER insert_sync on rent.park_terminate_rent_notifications CASCADE;
DROP FUNCTION rent.park_terminate_rent_notifications_to_tz CASCADE;
DROP FUNCTION rent.park_terminate_rent_notifications_from_tz CASCADE;
DROP FUNCTION rent.park_terminate_rent_notifications_insert CASCADE;
ALTER TABLE rent.park_terminate_rent_notifications DROP COLUMN notified_at CASCADE;

DROP TRIGGER update_to_tz on rent.rent_notifications CASCADE;
DROP TRIGGER update_from_tz on rent.rent_notifications CASCADE;
DROP TRIGGER insert_sync on rent.rent_notifications CASCADE;
DROP FUNCTION rent.rent_notifications_to_tz CASCADE;
DROP FUNCTION rent.rent_notifications_from_tz CASCADE;
DROP FUNCTION rent.rent_notifications_insert CASCADE;
ALTER TABLE rent.rent_notifications DROP COLUMN notified_at CASCADE;

DROP TRIGGER update_to_tz on rent.affiliations CASCADE;
DROP TRIGGER update_from_tz on rent.affiliations CASCADE;
DROP TRIGGER insert_sync on rent.affiliations CASCADE;
DROP FUNCTION rent.affiliations_to_tz CASCADE;
DROP FUNCTION rent.affiliations_from_tz CASCADE;
DROP FUNCTION rent.affiliations_insert CASCADE;
ALTER TABLE rent.affiliations DROP COLUMN created_at;
ALTER TABLE rent.affiliations DROP COLUMN modified_at;

DROP TRIGGER update_to_tz on rent.external_park_transactions_log CASCADE;
DROP TRIGGER update_from_tz on rent.external_park_transactions_log CASCADE;
DROP TRIGGER insert_sync on rent.external_park_transactions_log CASCADE;
DROP FUNCTION rent.external_park_transactions_log_to_tz CASCADE;
DROP FUNCTION rent.external_park_transactions_log_from_tz CASCADE;
DROP FUNCTION rent.external_park_transactions_log_insert CASCADE;
ALTER TABLE rent.external_park_transactions_log DROP COLUMN timestamp;
ALTER TABLE rent.external_park_transactions_log DROP COLUMN uploaded_at;
ALTER TABLE rent.external_park_transactions_log DROP COLUMN modified_at;

-- TODO Вернуть, когда на проде и в тестинге удалю
-- DROP TRIGGER update_to_tz on rent.records CASCADE;
-- DROP TRIGGER update_from_tz on rent.records CASCADE;
-- DROP TRIGGER insert_sync on rent.records CASCADE;
-- DROP FUNCTION rent.records_to_tz CASCADE;
-- DROP FUNCTION rent.records_from_tz CASCADE;
-- DROP FUNCTION rent.records_insert CASCADE;
-- ALTER TABLE rent.records DROP COLUMN begins_at;
-- ALTER TABLE rent.records DROP COLUMN ends_at;
-- ALTER TABLE rent.records DROP COLUMN charging_starts_at;
-- ALTER TABLE rent.records DROP COLUMN created_at;
-- ALTER TABLE rent.records DROP COLUMN modified_at;
-- ALTER TABLE rent.records DROP COLUMN accepted_at;
-- ALTER TABLE rent.records DROP COLUMN rejected_at;
-- ALTER TABLE rent.records DROP COLUMN terminated_at;
-- ALTER TABLE rent.records DROP COLUMN last_seen_at;
--
DROP TRIGGER update_to_tz on rent.same_park_transactions_log CASCADE;
DROP TRIGGER update_from_tz on rent.same_park_transactions_log CASCADE;
DROP TRIGGER insert_sync on rent.same_park_transactions_log CASCADE;
DROP FUNCTION rent.same_park_transactions_log_to_tz CASCADE;
DROP FUNCTION rent.same_park_transactions_log_from_tz CASCADE;
DROP FUNCTION rent.same_park_transactions_log_insert CASCADE;
--TODO minchin
--ALTER TABLE rent.records DROP CONSTRAINT check_starts_at_end_tz;
--ALTER TABLE rent.records DROP CONSTRAINT check_state;
ALTER TABLE rent.same_park_transactions_log DROP COLUMN event_at;
ALTER TABLE rent.same_park_transactions_log DROP COLUMN uploaded_at;
ALTER TABLE rent.same_park_transactions_log DROP COLUMN modified_at;

CREATE TABLE rent.rent_history
(
    rent_id               TEXT        NOT NULL,
    version               BIGINT      NOT NULL,
    modification_source   JSONB       NOT NULL,
    owner_park_id         TEXT        NOT NULL,
    owner_serial_id       BIGINT      NOT NULL,
    driver_id             TEXT        NOT NULL,
    affiliation_id        TEXT,
    title                 TEXT,
    comment               TEXT,
    balance_notify_limit  TEXT,
    begins_at             TIMESTAMPTZ NOT NULL,
    ends_at               TIMESTAMPTZ,
    asset_type            TEXT        NOT NULL,
    asset_params          JSONB,
    charging_type         TEXT        NOT NULL,
    charging_params       JSONB,
    charging_starts_at    TIMESTAMPTZ NOT NULL,
    creator_uid           TEXT        NOT NULL,
    created_at            TIMESTAMPTZ NOT NULL,
    modified_at           TIMESTAMPTZ NOT NULL,
    accepted_at           TIMESTAMPTZ,
    acceptance_reason     TEXT,
    rejected_at           TIMESTAMPTZ,
    rejection_reason      TEXT,
    terminated_at         TIMESTAMPTZ,
    termination_reason    TEXT,
    last_seen_at          TIMESTAMPTZ,
    transfer_order_number TEXT        NOT NULL,
    use_event_queue       BOOLEAN     NOT NULL,
    use_arbitrary_entries BOOLEAN     NOT NULL,
    start_clid            TEXT        NULL,
    PRIMARY KEY (rent_id, version)
);
CREATE INDEX ON rent.rent_history USING btree(modified_at);
