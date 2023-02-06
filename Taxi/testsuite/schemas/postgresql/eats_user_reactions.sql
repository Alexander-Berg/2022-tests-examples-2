DROP SCHEMA IF EXISTS eats_places_description;

CREATE SCHEMA eats_places_description;

CREATE TABLE eats_places_description.zen_articles(
	id serial PRIMARY KEY,
	brand_id integer NOT NULL,
	place_id integer,
    zen_id varchar(32),
    title TEXT NOT NULL,
	description TEXT NOT NULL,
	author_avatar_url TEXT NOT NULL,
	url TEXT NOT NULL,
	priority integer NOT NULL DEFAULT 0,
	is_deactivated boolean not null DEFAULT false,
	published_at timestamptz NOT NULL DEFAULT NOW(),
	created_at timestamptz NOT NULL DEFAULT NOW(),
	updated_at timestamptz NOT NULL DEFAULT NOW()
);

CREATE INDEX ON eats_places_description.zen_articles(brand_id);

CREATE UNIQUE INDEX ON eats_places_description.zen_articles(zen_id);

COMMIT;

CREATE TYPE eats_places_description.zen_articles_v1 AS (
	id integer,
	brand_id integer,
	place_id integer,
	zen_id varchar(32),
	title text,
	description text,
	author_avatar_url text,
	url text,
	priority integer,
	is_deactivated boolean,
	published_at timestamptz,
	created_at timestamptz,
	updated_at timestamptz);
