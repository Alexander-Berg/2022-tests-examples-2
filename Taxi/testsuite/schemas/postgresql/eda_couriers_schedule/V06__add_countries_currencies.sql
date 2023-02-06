START TRANSACTION;

CREATE TABLE public.currencies
(
    code           CHAR(3)      NOT NULL,
    name           VARCHAR(128) NOT NULL,
    symbol         VARCHAR(3)   NOT NULL,
    decimal_places INT          NOT NULL,
    created_at     TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    PRIMARY KEY (code)
);
CREATE INDEX idx__currencies__created_at ON currencies (created_at);
CREATE INDEX idx__currencies__updated_at ON currencies (updated_at);
COMMENT ON COLUMN currencies.code IS 'Код валюты';
COMMENT ON COLUMN currencies.name IS 'Название валюты';
COMMENT ON COLUMN currencies.symbol IS 'Символ';
COMMENT ON COLUMN currencies.decimal_places IS 'Количество знаков после запятой';

CREATE TABLE public.countries (
          code CHAR(2) NOT NULL,
          name VARCHAR(255) NOT NULL,
          currency_code CHAR(3) NOT NULL,
          created_at TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
          updated_at TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
          PRIMARY KEY(code)
        );

CREATE INDEX idx__countries__created_at ON countries (created_at);
CREATE INDEX idx__countries__updated_at ON countries (updated_at);
CREATE UNIQUE INDEX uq__countries__name ON countries (name);
COMMENT ON COLUMN countries.code IS 'Код страны ISO 3166-1 alpha-2';
COMMENT ON COLUMN countries.name IS 'Название страны';
COMMENT ON COLUMN countries.currency_code IS 'Код валюты';

COMMIT;
