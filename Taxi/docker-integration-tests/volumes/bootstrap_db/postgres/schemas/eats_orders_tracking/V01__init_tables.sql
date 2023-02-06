/* V1 */
/* pgmigrate-encoding: utf-8 */

BEGIN;

CREATE SCHEMA IF NOT EXISTS eats_orders_tracking;

-- таблица списка заказов авторизованных итеров
CREATE TABLE IF NOT EXISTS eats_orders_tracking.eater_order_refs
(
    eater_id TEXT NOT NULL,
    order_nr TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY(eater_id, order_nr)
);
CREATE INDEX eater_order_refs_eater_id_idx ON eats_orders_tracking.eater_order_refs (eater_id);

-- таблица списка заказов неавторизованных итеров
CREATE TABLE IF NOT EXISTS eats_orders_tracking.inner_token_order_refs
(
    inner_token TEXT NOT NULL,
    order_nr TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY(inner_token, order_nr)
);
CREATE INDEX inner_token_order_refs_inner_token_idx ON eats_orders_tracking.inner_token_order_refs (inner_token);

-- таблица кэша заказов
CREATE TABLE IF NOT EXISTS eats_orders_tracking.orders
(
    order_nr TEXT NOT NULL,
    payload JSONB NOT NULL, -- пэйлоад с кэшированными данными по заказу,
    -- включая данные КЦ, статус платежа
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (order_nr)
);

-- таблица кэша ресторанов
CREATE TABLE IF NOT EXISTS eats_orders_tracking.places
(
    place_id TEXT NOT NULL,
    payload JSONB NOT NULL, -- пэйлоад с кэшированными данными по ресторану
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (place_id)
);

-- таблица кэша курьеров
CREATE TABLE IF NOT EXISTS eats_orders_tracking.couriers
(
    order_nr TEXT NOT NULL,
    payload JSONB NOT NULL, -- пэйлоад с кэшированными данными по курьеру (кроме eta и координат)
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (order_nr)
);

-- таблица типов экранов
CREATE TABLE IF NOT EXISTS eats_orders_tracking.display_templates
(
    code TEXT NOT NULL,
    title_key TEXT NOT NULL, -- заголовок экрана
    short_title_key TEXT NOT NULL, -- заголовок на шорткате
    description_key TEXT NOT NULL, -- описание экрана
    short_description_key TEXT NOT NULL, -- описание на шорткате
    show_car_info BOOLEAN NOT NULL, -- флаг того отдавать информацию о машине или нет (если она присутствует)
    show_eta BOOLEAN NOT NULL, -- флаг того отдавать ли ETA для легаси-клиентов и шорткатов
    icons JSONB NOT NULL, -- json иконок на экране (статус, uri и payload для каждой иконки)
    buttons JSONB NOT NULL, -- json кнопок на экране (тип, title, payload и actions для каждой кнопки)
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (code)
);

COMMIT;
