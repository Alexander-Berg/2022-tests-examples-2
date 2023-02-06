CREATE SCHEMA cardstorage;

CREATE TABLE cardstorage.fallback
(
  request_name    TEXT           NOT NULL,
  timestamp       TIMESTAMPTZ    NOT NULL,
  failures        INTEGER        NOT NULL,
  total           INTEGER        NOT NULL,
  PRIMARY KEY (request_name, timestamp)
);

CREATE INDEX timestamp_index ON cardstorage.fallback (timestamp);
