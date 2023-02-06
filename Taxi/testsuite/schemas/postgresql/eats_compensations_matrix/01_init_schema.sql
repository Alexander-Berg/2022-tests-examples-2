START TRANSACTION;

CREATE SCHEMA eats_compensations_matrix;

CREATE TABLE eats_compensations_matrix.compensation_matrices
(
    id                  SERIAL PRIMARY KEY,
    version_code        VARCHAR(255)                 NOT NULL UNIQUE,
    parent_version_code VARCHAR(255),
    approved_at         TIMESTAMP WITH TIME ZONE,
    author              VARCHAR(255)                 NOT NULL,
    approve_author      VARCHAR(255),
    created_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx__compensation_matrices__approved_at
    ON eats_compensations_matrix.compensation_matrices (approved_at);

comment on column eats_compensations_matrix.compensation_matrices.version_code is 'Код матрицы, его можно прописывать в эксперимент';
comment on column eats_compensations_matrix.compensation_matrices.parent_version_code is 'Код родительской матрицы, от которой была унаследована эта';
comment on column eats_compensations_matrix.compensation_matrices.approved_at is 'Дата подтверждения, если не заполнена - нельзя редактировать, но можно использовать в экспериментов';
comment on column eats_compensations_matrix.compensation_matrices.author is 'Автор матрицы';
comment on column eats_compensations_matrix.compensation_matrices.approve_author is 'Кто дал аппрув матрице';

CREATE TABLE eats_compensations_matrix.situation_groups
(
    id          SERIAL PRIMARY KEY,
    title       VARCHAR(255)             NOT NULL,
    description VARCHAR(255)             NOT NULL,
    priority    INTEGER                  NOT NULL DEFAULT 0,
    created_at  TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

comment on column eats_compensations_matrix.situation_groups.title is 'Название группы ситуаций';
comment on column eats_compensations_matrix.situation_groups.description is 'Описание группы ситуаций (например, когда применять)';
comment on column eats_compensations_matrix.situation_groups.priority is 'Приоритет в списке у сотрудника КЦ';

CREATE TYPE eats_compensations_matrix.situation_group_v1 AS (
    id          INTEGER,
    title       VARCHAR(255),
    description VARCHAR(255),
    priority    INTEGER
    );

CREATE TABLE eats_compensations_matrix.situations
(
    id                  SERIAL PRIMARY KEY,
    matrix_id           INTEGER REFERENCES eats_compensations_matrix.compensation_matrices(id) ON DELETE CASCADE,
    group_id            INTEGER REFERENCES eats_compensations_matrix.situation_groups(id),
    code                VARCHAR(255)             NOT NULL,
    title               VARCHAR(255)             NOT NULL,
    violation_level     VARCHAR(32)              NOT NULL,
    responsible         VARCHAR(32)              NOT NULL,
    need_confirmation   BOOLEAN                  NOT NULL DEFAULT FALSE,
    priority            INTEGER                  NOT NULL DEFAULT 0,
    is_system           BOOLEAN                  NOT NULL DEFAULT FALSE,
    order_type          INTEGER                  NOT NULL,
    order_delivery_type INTEGER                  NOT NULL,
    created_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx__situations__code
    ON eats_compensations_matrix.situations (code);

comment on column eats_compensations_matrix.situations.matrix_id is 'Идентификатор матрицы ситуаций в compensation_matrices';
comment on column eats_compensations_matrix.situations.group_id is 'Идентификатор группы ситуаций в situation_groups';
comment on column eats_compensations_matrix.situations.code is 'Код ситуации';
comment on column eats_compensations_matrix.situations.title is 'Название ситуации';
comment on column eats_compensations_matrix.situations.violation_level is 'Уровень нарушения';
comment on column eats_compensations_matrix.situations.responsible is 'Ответственная сторона за нарушение';
comment on column eats_compensations_matrix.situations.need_confirmation is 'Нужно ли подтверждение от L2';
comment on column eats_compensations_matrix.situations.priority is 'Приоритет в списке у сотрудника КЦ';
comment on column eats_compensations_matrix.situations.is_system is 'Системная ли ситуация';
comment on column eats_compensations_matrix.situations.order_type is 'Тип заказа, при котором доступна ситуация';
comment on column eats_compensations_matrix.situations.order_delivery_type is 'Тип доставки, при котором доступна ситуация';

CREATE TABLE eats_compensations_matrix.compensation_types
(
    id           SERIAL PRIMARY KEY,
    type         VARCHAR(32) NOT NULL,
    rate         DOUBLE PRECISION,
    description  VARCHAR(255),
    full_refund  BOOLEAN NOT NULL DEFAULT FALSE,
    max_value    INTEGER,
    min_value    INTEGER,
    notification VARCHAR(255) NOT NULL,
    created_at   TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

comment on column eats_compensations_matrix.compensation_types.type is 'Тип компенсации';
comment on column eats_compensations_matrix.compensation_types.rate is 'Рейт действия (количество процентов или денег)';
comment on column eats_compensations_matrix.compensation_types.description is 'Описание действия';
comment on column eats_compensations_matrix.compensation_types.full_refund is 'Полная ли компенсация стоимости заказа';
comment on column eats_compensations_matrix.compensation_types.max_value is 'Максимальная компенсация';
comment on column eats_compensations_matrix.compensation_types.min_value is 'Минимальная компенсация';
comment on column eats_compensations_matrix.compensation_types.notification is 'Код нотификации';

CREATE TABLE eats_compensations_matrix.compensation_packs
(
    id                  SERIAL PRIMARY KEY,
    situation_id        INTEGER REFERENCES eats_compensations_matrix.situations(id) ON DELETE CASCADE,
    available_source    INTEGER                      NOT NULL,
    max_cost            INTEGER,
    min_cost            INTEGER,
    compensations_count INTEGER,
    payment_method_type VARCHAR(32)                  NOT NULL DEFAULT 'all',
    antifraud_score     VARCHAR(32)                  NOT NULL DEFAULT 'all',
    country             VARCHAR(32)                  NOT NULL DEFAULT 'all',
    created_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

comment on column eats_compensations_matrix.compensation_packs.situation_id is 'Идентификатор ситуации в situations';
comment on column eats_compensations_matrix.compensation_packs.available_source is 'То, откуда доступен пак';
comment on column eats_compensations_matrix.compensation_packs.max_cost is 'Максимальная стоимость заказа';
comment on column eats_compensations_matrix.compensation_packs.min_cost is 'Минимальная стоимость заказа';
comment on column eats_compensations_matrix.compensation_packs.compensations_count is 'Количество предшествующих компенсаций, при которых пак доступен';
comment on column eats_compensations_matrix.compensation_packs.payment_method_type is 'Тип оплаты, при котором доступен пак';
comment on column eats_compensations_matrix.compensation_packs.antifraud_score is 'Рейтинг антифрода';
comment on column eats_compensations_matrix.compensation_packs.country is 'Страна, для которой доступен пак';

CREATE TABLE eats_compensations_matrix.compensation_packs_to_types
(
    id      SERIAL PRIMARY KEY,
    type_id INTEGER REFERENCES eats_compensations_matrix.compensation_types(id),
    pack_id INTEGER REFERENCES eats_compensations_matrix.compensation_packs(id) ON DELETE CASCADE,
    UNIQUE(type_id, pack_id)
);

comment on column eats_compensations_matrix.compensation_packs_to_types.type_id is 'Идентификатор действия в compensation_types';
comment on column eats_compensations_matrix.compensation_packs_to_types.pack_id is 'Идентификатор пака компенсаций в compensation_packs';

-- cancelling

CREATE TABLE eats_compensations_matrix.order_cancel_matrices
(
    id                  SERIAL PRIMARY KEY,
    version_code        VARCHAR(255)             NOT NULL UNIQUE,
    parent_version_code VARCHAR(255),
    approved_at         TIMESTAMP WITH TIME ZONE,
    author              VARCHAR(255)             NOT NULL,
    approve_author      VARCHAR(255),
    activated_author    VARCHAR(255),
    created_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx__order_cancel_matrices__approved_at
    ON eats_compensations_matrix.order_cancel_matrices (approved_at);

comment on column eats_compensations_matrix.order_cancel_matrices.version_code is 'Код матрицы, его можно прописывать в эксперимент';
comment on column eats_compensations_matrix.order_cancel_matrices.parent_version_code is 'Код родительской матрицы, от которой была унаследована эта';
comment on column eats_compensations_matrix.order_cancel_matrices.approved_at is 'Дата подтверждения, если не заполнена - нельзя редактировать, но можно использовать в экспериментов';
comment on column eats_compensations_matrix.order_cancel_matrices.author is 'Автор матрицы';
comment on column eats_compensations_matrix.order_cancel_matrices.approve_author is 'Кто дал аппрув матрице';

CREATE TABLE eats_compensations_matrix.order_cancel_reason_groups
(
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(255)             NOT NULL,
    code       VARCHAR(255)             NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

comment on column eats_compensations_matrix.order_cancel_reason_groups.name is 'Название группы причин отмены заказа';
comment on column eats_compensations_matrix.order_cancel_reason_groups.code is 'Код группы причин отмены заказа';

CREATE TABLE eats_compensations_matrix.order_cancel_reasons
(
    id                  SERIAL PRIMARY KEY,
    matrix_id           INTEGER REFERENCES eats_compensations_matrix.order_cancel_matrices(id) ON DELETE CASCADE,
    group_id            INTEGER REFERENCES eats_compensations_matrix.order_cancel_reason_groups(id),
    name                VARCHAR(255)             NOT NULL,
    code                VARCHAR(255)             NOT NULL,
    priority            INTEGER                  NOT NULL,
    type                VARCHAR(32)              NOT NULL,
    is_system           BOOLEAN                  NOT NULL DEFAULT FALSE,
    order_type          INTEGER                  NOT NULL,
    order_delivery_type INTEGER                  NOT NULL,
    created_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx__order_cancel_reasons__code
    ON eats_compensations_matrix.order_cancel_reasons (code);

comment on column eats_compensations_matrix.order_cancel_reasons.matrix_id is 'Идентификатор матрицы отмен в order_cancel_matrices';
comment on column eats_compensations_matrix.order_cancel_reasons.group_id is 'Идентификатор группы причины отмены в order_cancel_reason_groups';
comment on column eats_compensations_matrix.order_cancel_reasons.name is 'Название причины отмены заказа';
comment on column eats_compensations_matrix.order_cancel_reasons.code is 'Код причины отмены заказа';
comment on column eats_compensations_matrix.order_cancel_reasons.priority is 'Приоритет в списке';
comment on column eats_compensations_matrix.order_cancel_reasons.type is 'Тип причины';
comment on column eats_compensations_matrix.order_cancel_reasons.is_system is 'Системная ли причина отмены';
comment on column eats_compensations_matrix.order_cancel_reasons.order_type is 'Тип заказа, при котором доступна причина';
comment on column eats_compensations_matrix.order_cancel_reasons.order_delivery_type is 'Тип доставки, при котором доступна причина';

CREATE TABLE eats_compensations_matrix.order_cancel_reactions
(
    id                  SERIAL PRIMARY KEY,
    reason_id           INTEGER REFERENCES eats_compensations_matrix.order_cancel_reasons(id) ON DELETE CASCADE,
    name                VARCHAR(255)             NOT NULL,
    type                VARCHAR(255)             NOT NULL,
    payload             TEXT                     NOT NULL,
    is_transferred      BOOLEAN,
    auto                BOOLEAN                  NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

comment on column eats_compensations_matrix.order_cancel_reactions.reason_id is 'Идентификатор причины';
comment on column eats_compensations_matrix.order_cancel_reactions.type is 'Группа реакции';
comment on column eats_compensations_matrix.order_cancel_reactions.payload is 'Строка с json для нужд обработки отмены';
comment on column eats_compensations_matrix.order_cancel_reactions.is_transferred is 'Заказ в статусе вендорка/до подтверждения рестораном или интеграция/до отправки';
comment on column eats_compensations_matrix.order_cancel_reactions.auto is 'Автоматически применяется реакция или нет';

CREATE TABLE eats_compensations_matrix.order_cancel_compensation_packs
(
    id                  SERIAL PRIMARY KEY,
    reaction_id         INTEGER REFERENCES eats_compensations_matrix.order_cancel_reactions(id) ON DELETE CASCADE,
    max_cost            INTEGER,
    min_cost            INTEGER,
    compensations_count INTEGER,
    antifraud_score     VARCHAR(32)              NOT NULL DEFAULT 'all',
    country             VARCHAR(32)              NOT NULL DEFAULT 'all',
    payment_method_type VARCHAR(32)              NOT NULL,
    created_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

comment on column eats_compensations_matrix.order_cancel_compensation_packs.reaction_id is 'Идентификатор ситуации в reactions';
comment on column eats_compensations_matrix.order_cancel_compensation_packs.max_cost is 'Максимальная стоимость заказа';
comment on column eats_compensations_matrix.order_cancel_compensation_packs.min_cost is 'Минимальная стоимость заказа';
comment on column eats_compensations_matrix.order_cancel_compensation_packs.compensations_count is 'Количество предшествующих компенсаций, при которых пак доступен';
comment on column eats_compensations_matrix.order_cancel_compensation_packs.antifraud_score is 'Рейтинг антифрода';
comment on column eats_compensations_matrix.order_cancel_compensation_packs.country is 'Страна, для которой доступен пак';
comment on column eats_compensations_matrix.order_cancel_compensation_packs.payment_method_type is 'Тип оплаты, при котором доступна реакция';

CREATE TABLE eats_compensations_matrix.order_cancel_compensation_packs_to_types
(
    id      SERIAL PRIMARY KEY,
    type_id INTEGER REFERENCES eats_compensations_matrix.compensation_types(id),
    pack_id INTEGER REFERENCES eats_compensations_matrix.order_cancel_compensation_packs(id) ON DELETE CASCADE,
    UNIQUE(type_id, pack_id)
);

comment on column eats_compensations_matrix.order_cancel_compensation_packs_to_types.type_id is 'Идентификатор действия в compensation_types';
comment on column eats_compensations_matrix.order_cancel_compensation_packs_to_types.pack_id is 'Идентификатор пака компенсаций отмен в order_cancel_compensation_packs';

COMMIT;
