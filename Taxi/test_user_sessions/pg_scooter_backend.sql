-- https://a.yandex-team.ru/arc/trunk/arcadia/drive/backend/tables/user
CREATE TABLE IF NOT EXISTS "user" (
    first_name character varying(30) NOT NULL,
    last_name character varying(150) NOT NULL,
    address text,
    email character varying(254),
    date_joined timestamp with time zone NOT NULL,
    id uuid PRIMARY KEY,
    uid bigint,
    username character varying(64) NOT NULL,
    patronymic_name character varying(64) NOT NULL,
    phone character varying(128),
    status character varying(16) NOT NULL,
    registered_at timestamp with time zone,
    is_phone_verified boolean,
    is_email_verified boolean,
    passport_names_hash character varying(64),
    passport_number_hash character varying(64),
    driving_license_number_hash character varying(64),
    is_first_riding boolean DEFAULT true,
    driving_license_ds_revision character varying(64),
    passport_ds_revision character varying(64),
    registration_geo character varying(16),
    has_at_mark boolean,
    environment character varying(254)
);

-- https://a.yandex-team.ru/arc/trunk/arcadia/drive/backend/tables/car_tags
CREATE TABLE IF NOT EXISTS car_tags (
    tag_id uuid DEFAULT (uuid_generate_v4()) NOT NULL,
    object_id uuid NOT NULL,
    tag character varying(50),
    data text NOT NULL,
    performer character varying(50),
    priority integer DEFAULT 0,
    snapshot text DEFAULT NULL
);

TRUNCATE public.user;
TRUNCATE car_tags;
