#!/usr/bin/env bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
CREATE DATABASE dborders;

\connect dborders

CREATE TABLE "orders_0" (
    park_id               varchar (32)     not null,
    id                    varchar (32)     not null,
    old_uuid              varchar (48)     null,
    number                int              not null,
    number_group          int              default 0, --порядковый номер заказа по одному телефону

    clid                  bigint           null,
    agg_id                varchar (32)     null,
    agg_name              varchar (128)    null,

    status                int              default 0,

    address_from          varchar (1024)   null,
    address_to            varchar (1024)   null,
    route_points          jsonb            null,

    driver_id             varchar (32)     null,
    driver_name           varchar (128)    null,
    driver_signal         varchar (32)     null,

    car_id                varchar (32)     null,
    car_name              varchar (128)    null,
    car_number            varchar (16)     null,
    car_franchise         bit              default '0',

    phone1                varchar (32)     null,
    phone2                varchar (32)     null,
    phone3                varchar (32)     null,
    phone_addition        bit              default '0',
    phone_show            bit              default '0',

    rule_type_id          varchar (32)     null,
    rule_type_name        varchar (32)     null,
    rule_type_color       varchar (9)      null, --*

    rule_work_id          varchar (32)     null,
    rule_work_name        varchar (64)     null,

    tariff_id             varchar (32)     null,
    tariff_name           varchar (128)    null,
    tariff_discount       varchar (32)     null, --[СкидкаБазовая][Obsolete]
    tariff_type           int              null,

    provider              int              default 0, --*
    kind                  int              default 0,
    categorys             int              default 0,
    requirements          int              default 0,
    payment               int              default 0, --[СпособОплаты]
    chair                 int              default 0, --[ДетскоеКресло]

    date_create           timestamp        not null,
    date_booking          timestamp        not null,

    date_drive            timestamp        null,
    date_waiting          timestamp        null,
    date_calling          timestamp        null,
    date_transporting     timestamp        null,
    date_end              timestamp        null,
    date_last_change      timestamp        null,

    description           varchar (512)    null, --[Примечание]
    description_canceled  varchar (512)    null, --[ПричинаОтказа]
    adv                   varchar (128)    null, --[Источник]

    company_id            varchar (32)     null, --[СсылкаНаЮридическоеЛицо]
    company_name          varchar (128)    null, --[СсылкаНаЮридическоеЛицо.НазваниеОбъекта]
    company_responsible   varchar (128)    null, --[ФИО_Ответственного]
    company_passenger     varchar (128)    null, --[ФИО_Пассажира]
    company_cost_center   varchar (128)    null, --[ЗатратныйЦентр]
    company_subdivision   varchar (128)    null, --[Подразделение]
    company_department    varchar (128)    null, --[Отдел]
    company_comment_trip  varchar (128)    null, --[ЦельПоездки]
    company_comment       varchar (128)    null, --[СлужебнаяИнформация]
    company_slip          varchar (32)     null, --[НомерСлипа]
    company_params        bit              default '0', --[ДополнительныеПараметрыЮрдиц]

    card_paind            bit              default '0', --[CardPaind]

    user_id               varchar (32)     null,
    user_name             varchar (128)    null, --[РедакторРаздела]

    client_id             varchar (32)     null, --[PersonId]
    client_name           varchar (128)    null, --[Имя]
    client_cost_code      varchar (64)     null, --[КостКод]

    cost_pay              numeric (18, 6)  default 0, --[Цена] сумма, которую оплатил клиент
    cost_total            numeric (18, 6)  default 0, --[ЦенаВсего] стоимость зз без учета скидки
    cost_sub              numeric (18, 6)  default 0, --[ЦенаДоп] сумма по компенсациям (устаревшее)
    cost_commission       numeric (18, 6)  default 0, --[ЦенаВКассу] сумма всех комиссий, списанных по зз
    cost_discount         numeric (18, 6)  default 0, --[Скидка] сумма скидки
    cost_cupon            numeric (18, 6)  default 0, --[Купон] Скидка, предоставляемая по купону
    cost_coupon_percent   numeric (10, 5)  null, -- Процентная скидка, предоставляемая по промокоду
    fixed_price           jsonb            null, -- Назначенная фиксированная стоимость поездки

    bill_json             varchar (1024)   null, --[afterCityKm], [afterCityMin], [afterCitySumMin], [afterCitySumKm], [afterSubCitySum]
    bill_total_time       numeric (18, 6)  null, --[МинутыВПути]
    bill_total_distance   numeric (18, 6)  null, --[Километраж]

    important             bit              default '0', --[ВажнаяЗаявка]
    sms                   bit              default '0', --[ОтправитьСмс]
    closed_manually       bit              null,        -- Заказ закрыт диспетчером

    -- данные из CSV комиссий
    csv_commission_cost       numeric (18, 6)  default 0, -- Сумма по которой расчитывалась комиссия - НЕ ЗАПОЛНЯЕТСЯ
    csv_commission_yandex     numeric (18, 6)  default 0, -- Комиссия Яндекса
    csv_commission_agg        numeric (18, 6)  null, -- Комиссия Агрегатора
    csv_commission_park       numeric (18, 6)  null, -- Комиссия Парка

    -- данные из CSV субсидий
    csv_subsidy                 numeric (18, 6)  default 0, -- Субсидии
    csv_subsidy_no_commission   numeric (18, 6)  null,      -- Субсидия без учета комиссии Яндекс.Такси.

    -- данные из CSV купонов
    csv_coupon_paid           numeric (18, 6)  default 0, -- Оплаченый купон

    -- данные из CSV payments
    csv_payments              numeric (18, 6)  default 0, -- Сумма оплаты безналичного заказа
    csv_tips                  numeric (18, 6)  default 0,  -- Сумма чаевых

    price_corrections         json             null,  -- Повышающие коэффициенты/Сурдж
    receipt                   jsonb            null,   --Чек
    home_coord                jsonb            null,   --Координаты дома в Хочу Домой

    cost_full                 numeric (18, 6)  null, -- Сумма заказа с учетом доплат (за скрытую скидку) из CSV комиссий
    subvention                jsonb            null,   --Информация о субсидиях по заказу
    pool                      jsonb            null,  --Информация о вложенных пуловых заказах
    restored_id               varchar (32)     null,   --ID нового заказа, если заказ был восстановлен

    PRIMARY KEY(park_id, id)
);

create index idx_orders_0_park_id_driver_id_date_booking on "orders_0" (park_id, driver_id, date_booking desc);
create index idx_orders_0_date_booking_park_id on "orders_0" (date_booking desc, park_id);
create index idx_orders_0_date_create on "orders_0" (date_create desc);
create index idx_orders_0_date_end on "orders_0" (date_end desc);
create index idx_orders_0_date_last_change on "orders_0" (date_last_change desc) WHERE date_last_change IS NOT NULL;
create index idx_orders_0_phone1 on "orders_0" (phone1) where phone1 is not null;
create index idx_orders_0_phone2 on "orders_0" (phone2) where phone2 is not null;
create index idx_orders_0_phone3 on "orders_0" (phone3) where phone3 is not null;
create index idx_orders_0_old_uuid on "orders_0" (old_uuid) where old_uuid is not null;
create index idx_orders_0_number on "orders_0" (number desc);
create index idx_orders_0_driver_signal on "orders_0" (driver_signal nulls last);
create index idx_orders_0_payment on "orders_0" (payment asc);
create index idx_orders_0_rule_work_id on "orders_0" (rule_work_id) where rule_work_id is not null;
create index idx_orders_0_rule_type_id on "orders_0" (rule_type_id nulls last);
create index idx_orders_0_provider on "orders_0" (provider asc);
EOSQL
