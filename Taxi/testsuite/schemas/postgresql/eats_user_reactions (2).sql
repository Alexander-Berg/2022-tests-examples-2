CREATE SCHEMA eats_user_reactions;

CREATE TABLE eats_user_reactions.favourite_reactions
(
    id                UUID PRIMARY KEY,
    eater_id          TEXT                     NOT NULL,
    subject_namespace TEXT                     NOT NULL,
    subject_id        TEXT                     NOT NULL,
    created_at        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX ux__fr__eater_id__subject_namespace__subject_id on eats_user_reactions.favourite_reactions (eater_id, subject_namespace, subject_id);
CREATE INDEX idx__favourite_reactions__created_at on eats_user_reactions.favourite_reactions (created_at);

CREATE TYPE eats_user_reactions.favourite_reaction_v1 AS
(
    id                UUID,
    eater_id          TEXT,
    subject_namespace TEXT,
    subject_id        TEXT,
    created_at        TIMESTAMP WITH TIME ZONE,
    updated_at        TIMESTAMP WITH TIME ZONE
);

ALTER TABLE eats_user_reactions.favourite_reactions
ADD COLUMN deleted_at TIMESTAMP WITH TIME ZONE;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx__favourite_reactions__updated_at on eats_user_reactions.favourite_reactions (updated_at);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx__favourite_reactions__deleted_at on eats_user_reactions.favourite_reactions (deleted_at);
