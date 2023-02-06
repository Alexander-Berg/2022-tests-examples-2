-- Представляет из себя одно окружение сервиса, стейбл и престейбл объединяются
-- маппится 1-M на клоунские бранчи, для поддержки multichildren в няне
CREATE TABLE alert_manager.branches (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP DEFAULT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    service_id BIGINT REFERENCES alert_manager.services(id) ON DELETE RESTRICT NOT NULL,
    repo_meta alert_manager.repo_meta_t NOT NULL,

    clown_branch_ids INTEGER[] NOT NULL,
    names TEXT[] NOT NULL
        CONSTRAINT non_empty_names CHECK ( array_length(names, 1) > 0 ),
    namespace TEXT NOT NULL,

    CONSTRAINT deleted_without_delete_time CHECK ( is_deleted <> (deleted_at IS NULL) )
);

CREATE UNIQUE INDEX uniq_non_deleted_branch_idx
    ON alert_manager.branches(((repo_meta).config_project), service_id, names) WHERE NOT is_deleted;

CREATE TRIGGER alert_manager_branches_set_updated
    BEFORE UPDATE
    ON alert_manager.branches
    FOR EACH ROW EXECUTE PROCEDURE alert_manager.set_updated();

CREATE TRIGGER alert_manager_branches_set_deleted
    BEFORE UPDATE
    ON alert_manager.branches
    FOR EACH ROW EXECUTE PROCEDURE alert_manager.set_deleted();
