--
-- PostgreSQL database dump
--

-- Dumped from database version 10.20 (Debian 10.20-1.pgdg90+1)
-- Dumped by pg_dump version 10.19 (Ubuntu 10.19-0ubuntu0.18.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: draft_spec; Type: TABLE DATA; Schema: fees; Owner: sibilla
--


INSERT INTO fees.draft_spec VALUES (5, 'e4a9bce5ec214f2baf81054225e62616', '2022-01-19 13:43:32.493869+00', '<scripts>', 'maksimzubkov', 'TAXIBILLING-6144', '', NULL);
INSERT INTO fees.draft_spec VALUES (6, '69afddc70def4c2c9b409657977a82b4', '2022-04-15 15:26:12.860333+00', '<scripts>', 'maksimzubkov', 'TAXI', '', NULL);


--
-- Data for Name: base_rule; Type: TABLE DATA; Schema: fees; Owner: sibilla
--

INSERT INTO fees.base_rule VALUES ('1715b67358f9478bb3fc15f828a4e6db', 'samara', NULL, NULL, 'corp', '2019-01-01 00:00:00+00', '2019-05-06 20:00:00+00', 'Europe/Samara', 'fixed_percent', '{"percent": 1200}', 0, 150000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 0, "agp": 0, "hiring": {"extra_percent": 200, "max_age_in_seconds": 15552000, "extra_percent_with_rent": 400}, "taximeter_payment": 10000, "callcenter_commission_percent": 200}', 0, '{"cost": 1500000, "percent": 700}', '[]', 12000, '[]', 6, '2019-04-26 12:24:14.662+00');
INSERT INTO fees.base_rule VALUES ('1b09bdcf8d624156935e46e2023980fc', 'samara', NULL, NULL, 'card', '2018-08-18 07:58:00+00', '2018-09-28 18:01:30+00', 'Europe/Samara', 'fixed_percent', '{"percent": 1200}', 0, 150000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 0, "agp": 0, "hiring": {"extra_percent": 200, "max_age_in_seconds": 15552000, "extra_percent_with_rent": 400}, "taximeter_payment": 10000, "callcenter_commission_percent": 0}', 0, '{"cost": 1500000, "percent": 700}', '[{"value": 300, "marketing_level": ["sticker"]}, {"value": 300, "marketing_level": ["sticker", "lightbox"]}]', 11800, '[]', 6, '2018-09-27 08:31:26.648+00');
INSERT INTO fees.base_rule VALUES ('3216c6de408b46d6bb800aeb5f36ab93', 'samara', NULL, NULL, 'card', '2018-03-22 21:00:00+00', '2018-08-18 07:58:00+00', 'Europe/Samara', 'fixed_percent', '{"percent": 1200}', 0, 150000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 0, "agp": 1, "hiring": {"extra_percent": 200, "max_age_in_seconds": 15552000, "extra_percent_with_rent": 400}, "taximeter_payment": 10000, "callcenter_commission_percent": 0}', 0, '{"cost": 1500000, "percent": 700}', '[{"value": 300, "marketing_level": ["sticker"]}, {"value": 300, "marketing_level": ["sticker", "lightbox"]}]', 11800, '[]', 6, '2018-08-15 14:36:49.862+00');
INSERT INTO fees.base_rule VALUES ('5243704b1fb64ada8128a8a5c459f0be', 'samara', NULL, NULL, 'card', '2019-01-01 00:00:00+00', '2019-05-06 20:00:00+00', 'Europe/Samara', 'fixed_percent', '{"percent": 1200}', 0, 150000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 0, "agp": 0, "hiring": {"extra_percent": 200, "max_age_in_seconds": 15552000, "extra_percent_with_rent": 400}, "taximeter_payment": 10000, "callcenter_commission_percent": 200}', 0, '{"cost": 1500000, "percent": 700}', '[]', 12000, '[]', 6, '2019-04-26 12:24:14.852+00');
INSERT INTO fees.base_rule VALUES ('5c42c71a5fc74305b41b28f10d8087ec', 'samara', NULL, NULL, 'corp', '2018-09-28 18:01:30+00', '2018-09-30 20:00:00+00', 'Europe/Samara', 'fixed_percent', '{"percent": 1200}', 0, 150000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 0, "agp": 0, "hiring": {"extra_percent": 200, "max_age_in_seconds": 15552000, "extra_percent_with_rent": 400}, "taximeter_payment": 10000, "callcenter_commission_percent": 200}', 0, '{"cost": 1500000, "percent": 700}', '[{"value": 300, "marketing_level": ["sticker"]}, {"value": 300, "marketing_level": ["sticker", "lightbox"]}]', 11800, '[]', 6, '2018-09-27 08:31:39.56+00');
INSERT INTO fees.base_rule VALUES ('91d90b31c9f24ddb8a564624e3348ad5', 'samara', NULL, NULL, 'cash', '2018-08-18 07:58:00+00', '2018-09-28 18:01:30+00', 'Europe/Samara', 'fixed_percent', '{"percent": 1200}', 0, 150000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 0, "agp": 0, "hiring": {"extra_percent": 200, "max_age_in_seconds": 15552000, "extra_percent_with_rent": 400}, "taximeter_payment": 10000, "callcenter_commission_percent": 0}', 0, '{"cost": 1500000, "percent": 700}', '[{"value": 300, "marketing_level": ["sticker"]}, {"value": 300, "marketing_level": ["sticker", "lightbox"]}]', 11800, '[]', 6, '2018-09-27 08:31:32.782+00');
INSERT INTO fees.base_rule VALUES ('b41a377abb5c43ac9ec957f877854afb', 'samara', NULL, NULL, 'cash', '2018-01-28 21:00:00+00', '2018-02-04 20:00:00+00', 'Europe/Samara', 'asymptotic_formula', '{"asymp": 113800, "cost_norm": 152000, "numerator": 1686000, "max_commission_percent": 1138}', 0, 150000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 0, "agp": 1, "hiring": {"extra_percent": 0, "max_age_in_seconds": 0, "extra_percent_with_rent": 0}, "taximeter_payment": 10000, "callcenter_commission_percent": 0}', 0, '{"cost": 1500000, "percent": 700}', '[{"value": 500, "marketing_level": ["sticker"]}, {"value": 500, "marketing_level": ["sticker", "lightbox"]}]', 11800, '[]', 6, '2018-08-15 14:36:39.476+00');
INSERT INTO fees.base_rule VALUES ('bcf532a803124b948aa8e6532c709c32', 'samara', NULL, NULL, 'corp', '2018-03-22 21:00:00+00', '2018-08-18 07:58:00+00', 'Europe/Samara', 'fixed_percent', '{"percent": 1200}', 0, 150000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 0, "agp": 1, "hiring": {"extra_percent": 200, "max_age_in_seconds": 15552000, "extra_percent_with_rent": 400}, "taximeter_payment": 10000, "callcenter_commission_percent": 0}', 0, '{"cost": 1500000, "percent": 700}', '[{"value": 300, "marketing_level": ["sticker"]}, {"value": 300, "marketing_level": ["sticker", "lightbox"]}]', 11800, '[]', 6, '2018-08-15 14:36:49.879+00');
INSERT INTO fees.base_rule VALUES ('c12d9fff73d5483fa6c5ca9ae6dc0865', 'samara', NULL, NULL, 'card', '2018-09-28 18:01:30+00', '2018-09-30 20:00:00+00', 'Europe/Samara', 'fixed_percent', '{"percent": 1200}', 0, 150000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 0, "agp": 0, "hiring": {"extra_percent": 200, "max_age_in_seconds": 15552000, "extra_percent_with_rent": 400}, "taximeter_payment": 10000, "callcenter_commission_percent": 200}', 0, '{"cost": 1500000, "percent": 700}', '[{"value": 300, "marketing_level": ["sticker"]}, {"value": 300, "marketing_level": ["sticker", "lightbox"]}]', 11800, '[]', 6, '2018-09-27 08:31:26.648+00');
INSERT INTO fees.base_rule VALUES ('c31e1ef7a00c443c98d79fbafba13b02', 'samara', NULL, NULL, 'cash', '2018-09-28 18:01:30+00', '2018-09-30 20:00:00+00', 'Europe/Samara', 'fixed_percent', '{"percent": 1200}', 0, 150000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 0, "agp": 0, "hiring": {"extra_percent": 200, "max_age_in_seconds": 15552000, "extra_percent_with_rent": 400}, "taximeter_payment": 10000, "callcenter_commission_percent": 200}', 0, '{"cost": 1500000, "percent": 700}', '[{"value": 300, "marketing_level": ["sticker"]}, {"value": 300, "marketing_level": ["sticker", "lightbox"]}]', 11800, '[]', 6, '2018-09-27 08:31:32.782+00');
INSERT INTO fees.base_rule VALUES ('c4db08f1799242688b198759998a3c1a', 'samara', NULL, NULL, 'cash', '2018-03-22 21:00:00+00', '2018-08-18 07:58:00+00', 'Europe/Samara', 'fixed_percent', '{"percent": 1200}', 0, 150000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 0, "agp": 1, "hiring": {"extra_percent": 200, "max_age_in_seconds": 15552000, "extra_percent_with_rent": 400}, "taximeter_payment": 10000, "callcenter_commission_percent": 0}', 0, '{"cost": 1500000, "percent": 700}', '[{"value": 300, "marketing_level": ["sticker"]}, {"value": 300, "marketing_level": ["sticker", "lightbox"]}]', 11800, '[]', 6, '2018-08-15 14:36:49.859+00');
INSERT INTO fees.base_rule VALUES ('de873750a6044b9a8f79e10da9964b24', 'samara', NULL, NULL, 'cash', '2019-01-01 00:00:00+00', '2019-05-06 20:00:00+00', 'Europe/Samara', 'fixed_percent', '{"percent": 1200}', 0, 150000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 0, "agp": 0, "hiring": {"extra_percent": 200, "max_age_in_seconds": 15552000, "extra_percent_with_rent": 400}, "taximeter_payment": 10000, "callcenter_commission_percent": 200}', 0, '{"cost": 1500000, "percent": 700}', '[]', 12000, '[]', 6, '2019-04-26 12:24:15.045+00');
INSERT INTO fees.base_rule VALUES ('e083a5d49fb149f4a19c3156b3d6f53f', 'samara', NULL, NULL, 'card', '2018-01-28 21:00:00+00', '2018-02-04 20:00:00+00', 'Europe/Samara', 'asymptotic_formula', '{"asymp": 113800, "cost_norm": 152000, "numerator": 1686000, "max_commission_percent": 1138}', 0, 150000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 0, "agp": 1, "hiring": {"extra_percent": 0, "max_age_in_seconds": 0, "extra_percent_with_rent": 0}, "taximeter_payment": 10000, "callcenter_commission_percent": 0}', 0, '{"cost": 1500000, "percent": 700}', '[{"value": 500, "marketing_level": ["sticker"]}, {"value": 500, "marketing_level": ["sticker", "lightbox"]}]', 11800, '[]', 6, '2018-08-15 14:36:39.513+00');
INSERT INTO fees.base_rule VALUES ('ead341100a0642b4bc95c50fe49ca4b9', 'samara', NULL, NULL, 'corp', '2018-08-18 07:58:00+00', '2018-09-28 18:01:30+00', 'Europe/Samara', 'fixed_percent', '{"percent": 1200}', 0, 150000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 0, "agp": 0, "hiring": {"extra_percent": 200, "max_age_in_seconds": 15552000, "extra_percent_with_rent": 400}, "taximeter_payment": 10000, "callcenter_commission_percent": 0}', 0, '{"cost": 1500000, "percent": 700}', '[{"value": 300, "marketing_level": ["sticker"]}, {"value": 300, "marketing_level": ["sticker", "lightbox"]}]', 11800, '[]', 6, '2018-09-27 08:31:39.56+00');
INSERT INTO fees.base_rule VALUES ('ee0cc06cf61647dca9e80a6a19f042d8', 'samara', NULL, NULL, 'corp', '2018-01-28 21:00:00+00', '2018-02-04 20:00:00+00', 'Europe/Samara', 'asymptotic_formula', '{"asymp": 113800, "cost_norm": 152000, "numerator": 1686000, "max_commission_percent": 1138}', 0, 150000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 0, "agp": 1, "hiring": {"extra_percent": 0, "max_age_in_seconds": 0, "extra_percent_with_rent": 0}, "taximeter_payment": 10000, "callcenter_commission_percent": 0}', 0, '{"cost": 1500000, "percent": 700}', '[{"value": 500, "marketing_level": ["sticker"]}, {"value": 500, "marketing_level": ["sticker", "lightbox"]}]', 11800, '[]', 6, '2018-08-15 14:36:39.48+00');
INSERT INTO fees.base_rule VALUES ('572cdd05cee4443646c3a12a', 'samara', NULL, NULL, 'cash', '2016-05-06 21:00:00+00', '2016-05-31 21:00:00+00', 'Europe/Samara', 'fixed_percent', '{"percent": 0}', 0, 60000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 200, "agp": 1, "hiring": {"extra_percent": 0, "max_age_in_seconds": 0, "extra_percent_with_rent": 0}, "taximeter_payment": 0, "callcenter_commission_percent": 0}', 0, '{"cost": 8000000, "percent": 0}', '[{"value": 300, "marketing_level": ["lightbox"]}, {"value": 300, "marketing_level": ["lightbox", "sticker"]}]', 11800, '[]', 6, '2018-08-15 14:36:18.772+00');
INSERT INTO fees.base_rule VALUES ('572cdd05cee4443646c3a12b', 'samara', NULL, NULL, 'card', '2016-05-06 21:00:00+00', '2016-05-31 21:00:00+00', 'Europe/Samara', 'fixed_percent', '{"percent": 0}', 0, 60000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 200, "agp": 1, "hiring": {"extra_percent": 0, "max_age_in_seconds": 0, "extra_percent_with_rent": 0}, "taximeter_payment": 0, "callcenter_commission_percent": 0}', 0, '{"cost": 8000000, "percent": 0}', '[{"value": 300, "marketing_level": ["lightbox"]}, {"value": 300, "marketing_level": ["lightbox", "sticker"]}]', 11800, '[]', 6, '2018-08-15 14:36:18.772+00');
INSERT INTO fees.base_rule VALUES ('574d821dcee44418cea0c94d', 'samara', NULL, NULL, 'cash', '2016-05-31 21:00:00+00', '2016-07-11 19:58:13+00', 'Europe/Samara', 'asymptotic_formula', '{"asymp": 81400, "cost_norm": 326000, "numerator": 1336000, "max_commission_percent": 814}', 0, 60000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 200, "agp": 1, "hiring": {"extra_percent": 0, "max_age_in_seconds": 0, "extra_percent_with_rent": 0}, "taximeter_payment": 0, "callcenter_commission_percent": 0}', 1100, '{"cost": 1500000, "percent": 700}', '[]', 11800, '[]', 6, '2018-08-15 14:36:18.795+00');
INSERT INTO fees.base_rule VALUES ('574d821dcee44418cea0c94e', 'samara', NULL, NULL, 'card', '2016-05-31 21:00:00+00', '2016-07-11 19:58:13+00', 'Europe/Samara', 'asymptotic_formula', '{"asymp": 81400, "cost_norm": 326000, "numerator": 1336000, "max_commission_percent": 814}', 0, 60000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 200, "agp": 1, "hiring": {"extra_percent": 0, "max_age_in_seconds": 0, "extra_percent_with_rent": 0}, "taximeter_payment": 0, "callcenter_commission_percent": 0}', 1100, '{"cost": 1500000, "percent": 700}', '[]', 11800, '[]', 6, '2018-08-15 14:36:18.795+00');
INSERT INTO fees.base_rule VALUES ('5783cefa97655a7cb3e8e511', 'samara', NULL, NULL, 'cash', '2016-07-11 19:58:13+00', '2016-08-24 12:00:00+00', 'Europe/Samara', 'asymptotic_formula', '{"asymp": 81400, "cost_norm": 326000, "numerator": 1336000, "max_commission_percent": 814}', 0, 60000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 200, "agp": 1, "hiring": {"extra_percent": 0, "max_age_in_seconds": 0, "extra_percent_with_rent": 0}, "taximeter_payment": 0, "callcenter_commission_percent": 0}', 1100, '{"cost": 1500000, "percent": 700}', '[{"value": 400, "marketing_level": ["sticker"]}, {"value": 400, "marketing_level": ["lightbox", "sticker"]}]', 11800, '[]', 6, '2018-08-15 14:36:18.818+00');
INSERT INTO fees.base_rule VALUES ('5783cefa97655a7cb3e8e512', 'samara', NULL, NULL, 'card', '2016-07-11 19:58:13+00', '2016-08-24 12:00:00+00', 'Europe/Samara', 'asymptotic_formula', '{"asymp": 81400, "cost_norm": 326000, "numerator": 1336000, "max_commission_percent": 814}', 0, 60000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 200, "agp": 1, "hiring": {"extra_percent": 0, "max_age_in_seconds": 0, "extra_percent_with_rent": 0}, "taximeter_payment": 0, "callcenter_commission_percent": 0}', 1100, '{"cost": 1500000, "percent": 700}', '[{"value": 400, "marketing_level": ["sticker"]}, {"value": 400, "marketing_level": ["lightbox", "sticker"]}]', 11800, '[]', 6, '2018-08-15 14:36:18.818+00');
INSERT INTO fees.base_rule VALUES ('57b2f39ecee44413b1df4acc', 'samara', NULL, NULL, 'corp', '2016-07-11 19:58:13+00', '2016-08-24 12:00:00+00', 'Europe/Samara', 'asymptotic_formula', '{"asymp": 81400, "cost_norm": 326000, "numerator": 1336000, "max_commission_percent": 814}', 0, 60000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 200, "agp": 1, "hiring": {"extra_percent": 0, "max_age_in_seconds": 0, "extra_percent_with_rent": 0}, "taximeter_payment": 0, "callcenter_commission_percent": 0}', 1100, '{"cost": 1500000, "percent": 700}', '[{"value": 400, "marketing_level": ["sticker"]}, {"value": 400, "marketing_level": ["lightbox", "sticker"]}]', 11800, '[]', 6, '2018-08-15 14:36:18.839+00');
INSERT INTO fees.base_rule VALUES ('57bd76f0ea43b000287bb1e3', 'samara', NULL, NULL, 'cash', '2016-08-24 12:00:00+00', '2016-10-26 13:45:00+00', 'Europe/Samara', 'asymptotic_formula', '{"asymp": 81400, "cost_norm": 326000, "numerator": 1336000, "max_commission_percent": 814}', 0, 60000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 200, "agp": 1, "hiring": {"extra_percent": 0, "max_age_in_seconds": 0, "extra_percent_with_rent": 0}, "taximeter_payment": 0, "callcenter_commission_percent": 0}', 1100, '{"cost": 1500000, "percent": 700}', '[{"value": 400, "marketing_level": ["co_branding", "lightbox"]}, {"value": 400, "marketing_level": ["sticker"]}, {"value": 400, "marketing_level": ["co_branding"]}, {"value": 400, "marketing_level": ["sticker", "lightbox"]}]', 11800, '[]', 6, '2018-08-15 14:36:23.885+00');
INSERT INTO fees.base_rule VALUES ('57bd76f0ea43b000287bb1e4', 'samara', NULL, NULL, 'card', '2016-08-24 12:00:00+00', '2016-10-26 13:45:00+00', 'Europe/Samara', 'asymptotic_formula', '{"asymp": 81400, "cost_norm": 326000, "numerator": 1336000, "max_commission_percent": 814}', 0, 60000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 200, "agp": 1, "hiring": {"extra_percent": 0, "max_age_in_seconds": 0, "extra_percent_with_rent": 0}, "taximeter_payment": 0, "callcenter_commission_percent": 0}', 1100, '{"cost": 1500000, "percent": 700}', '[{"value": 400, "marketing_level": ["co_branding", "lightbox"]}, {"value": 400, "marketing_level": ["sticker"]}, {"value": 400, "marketing_level": ["co_branding"]}, {"value": 400, "marketing_level": ["sticker", "lightbox"]}]', 11800, '[]', 6, '2018-08-15 14:36:23.885+00');
INSERT INTO fees.base_rule VALUES ('57bd76f1ea43b000287bb27c', 'samara', NULL, NULL, 'corp', '2016-08-24 12:00:00+00', '2016-10-26 13:45:00+00', 'Europe/Samara', 'asymptotic_formula', '{"asymp": 81400, "cost_norm": 326000, "numerator": 1336000, "max_commission_percent": 814}', 0, 60000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 200, "agp": 1, "hiring": {"extra_percent": 0, "max_age_in_seconds": 0, "extra_percent_with_rent": 0}, "taximeter_payment": 0, "callcenter_commission_percent": 0}', 1100, '{"cost": 1500000, "percent": 700}', '[{"value": 400, "marketing_level": ["co_branding", "lightbox"]}, {"value": 400, "marketing_level": ["sticker"]}, {"value": 400, "marketing_level": ["co_branding"]}, {"value": 400, "marketing_level": ["sticker", "lightbox"]}]', 11800, '[]', 6, '2018-08-15 14:36:23.907+00');
INSERT INTO fees.base_rule VALUES ('5810ac5dcee444cbbae6c1b4', 'samara', NULL, NULL, 'cash', '2016-10-26 13:45:00+00', '2017-01-31 20:00:00+00', 'Europe/Samara', 'asymptotic_formula', '{"asymp": 81400, "cost_norm": 326000, "numerator": 1336000, "max_commission_percent": 814}', 0, 60000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 200, "agp": 1, "hiring": {"extra_percent": 0, "max_age_in_seconds": 0, "extra_percent_with_rent": 0}, "taximeter_payment": 0, "callcenter_commission_percent": 0}', 0, '{"cost": 1500000, "percent": 700}', '[{"value": 400, "marketing_level": ["co_branding", "lightbox"]}, {"value": 400, "marketing_level": ["sticker"]}, {"value": 400, "marketing_level": ["co_branding"]}, {"value": 400, "marketing_level": ["sticker", "lightbox"]}]', 11800, '[]', 6, '2018-08-15 14:36:23.948+00');
INSERT INTO fees.base_rule VALUES ('5810ac5dcee444cbbae6c1b5', 'samara', NULL, NULL, 'card', '2016-10-26 13:45:00+00', '2017-01-31 20:00:00+00', 'Europe/Samara', 'asymptotic_formula', '{"asymp": 81400, "cost_norm": 326000, "numerator": 1336000, "max_commission_percent": 814}', 0, 60000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 200, "agp": 1, "hiring": {"extra_percent": 0, "max_age_in_seconds": 0, "extra_percent_with_rent": 0}, "taximeter_payment": 0, "callcenter_commission_percent": 0}', 0, '{"cost": 1500000, "percent": 700}', '[{"value": 400, "marketing_level": ["co_branding", "lightbox"]}, {"value": 400, "marketing_level": ["sticker"]}, {"value": 400, "marketing_level": ["co_branding"]}, {"value": 400, "marketing_level": ["sticker", "lightbox"]}]', 11800, '[]', 6, '2018-08-15 14:36:23.949+00');
INSERT INTO fees.base_rule VALUES ('5810ac5ecee444cbbae6c21e', 'samara', NULL, NULL, 'corp', '2016-10-26 13:45:00+00', '2017-01-31 20:00:00+00', 'Europe/Samara', 'asymptotic_formula', '{"asymp": 81400, "cost_norm": 326000, "numerator": 1336000, "max_commission_percent": 814}', 0, 60000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 200, "agp": 1, "hiring": {"extra_percent": 0, "max_age_in_seconds": 0, "extra_percent_with_rent": 0}, "taximeter_payment": 0, "callcenter_commission_percent": 0}', 0, '{"cost": 1500000, "percent": 700}', '[{"value": 400, "marketing_level": ["co_branding", "lightbox"]}, {"value": 400, "marketing_level": ["sticker"]}, {"value": 400, "marketing_level": ["co_branding"]}, {"value": 400, "marketing_level": ["sticker", "lightbox"]}]', 11800, '[]', 6, '2018-08-15 14:36:23.961+00');
INSERT INTO fees.base_rule VALUES ('58908d14c69b0fba54b80991', 'samara', NULL, NULL, 'corp', '2017-01-31 20:00:00+00', '2017-03-01 20:00:00+00', 'Europe/Samara', 'asymptotic_formula', '{"asymp": 81400, "cost_norm": 326000, "numerator": 1336000, "max_commission_percent": 814}', 0, 60000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 200, "agp": 1, "hiring": {"extra_percent": 0, "max_age_in_seconds": 0, "extra_percent_with_rent": 0}, "taximeter_payment": 4000, "callcenter_commission_percent": 0}', 0, '{"cost": 1500000, "percent": 700}', '[{"value": 400, "marketing_level": ["co_branding", "lightbox"]}, {"value": 400, "marketing_level": ["sticker"]}, {"value": 400, "marketing_level": ["co_branding"]}, {"value": 400, "marketing_level": ["sticker", "lightbox"]}]', 11800, '[]', 6, '2018-08-15 14:36:29.066+00');
INSERT INTO fees.base_rule VALUES ('58908d29c69b0fb1bd590863', 'samara', NULL, NULL, 'cash', '2017-01-31 20:00:00+00', '2017-03-01 20:00:00+00', 'Europe/Samara', 'asymptotic_formula', '{"asymp": 81400, "cost_norm": 326000, "numerator": 1336000, "max_commission_percent": 814}', 0, 60000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 200, "agp": 1, "hiring": {"extra_percent": 0, "max_age_in_seconds": 0, "extra_percent_with_rent": 0}, "taximeter_payment": 4000, "callcenter_commission_percent": 0}', 0, '{"cost": 1500000, "percent": 700}', '[{"value": 400, "marketing_level": ["co_branding", "lightbox"]}, {"value": 400, "marketing_level": ["sticker"]}, {"value": 400, "marketing_level": ["co_branding"]}, {"value": 400, "marketing_level": ["sticker", "lightbox"]}]', 11800, '[]', 6, '2018-08-15 14:36:29.066+00');
INSERT INTO fees.base_rule VALUES ('58908d3cc69b0fb1bd590865', 'samara', NULL, NULL, 'card', '2017-01-31 20:00:00+00', '2017-03-01 20:00:00+00', 'Europe/Samara', 'asymptotic_formula', '{"asymp": 81400, "cost_norm": 326000, "numerator": 1336000, "max_commission_percent": 814}', 0, 60000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 200, "agp": 1, "hiring": {"extra_percent": 0, "max_age_in_seconds": 0, "extra_percent_with_rent": 0}, "taximeter_payment": 4000, "callcenter_commission_percent": 0}', 0, '{"cost": 1500000, "percent": 700}', '[{"value": 400, "marketing_level": ["co_branding", "lightbox"]}, {"value": 400, "marketing_level": ["sticker"]}, {"value": 400, "marketing_level": ["co_branding"]}, {"value": 400, "marketing_level": ["sticker", "lightbox"]}]', 11800, '[]', 6, '2018-08-15 14:36:29.067+00');
INSERT INTO fees.base_rule VALUES ('58b6b7e1c69b0f6c3da6afb8', 'samara', NULL, NULL, 'corp', '2017-03-01 20:00:00+00', '2017-03-15 21:00:00+00', 'Europe/Samara', 'asymptotic_formula', '{"asymp": 113800, "cost_norm": 152000, "numerator": 1686000, "max_commission_percent": 1138}', 0, 60000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 200, "agp": 1, "hiring": {"extra_percent": 0, "max_age_in_seconds": 0, "extra_percent_with_rent": 0}, "taximeter_payment": 4000, "callcenter_commission_percent": 0}', 0, '{"cost": 1500000, "percent": 700}', '[{"value": 400, "marketing_level": ["co_branding", "lightbox"]}, {"value": 400, "marketing_level": ["sticker"]}, {"value": 400, "marketing_level": ["co_branding"]}, {"value": 400, "marketing_level": ["sticker", "lightbox"]}]', 11800, '[]', 6, '2018-08-15 14:36:29.089+00');
INSERT INTO fees.base_rule VALUES ('58b6b800c69b0f4414135323', 'samara', NULL, NULL, 'card', '2017-03-01 20:00:00+00', '2017-03-15 21:00:00+00', 'Europe/Samara', 'asymptotic_formula', '{"asymp": 113800, "cost_norm": 152000, "numerator": 1686000, "max_commission_percent": 1138}', 0, 60000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 200, "agp": 1, "hiring": {"extra_percent": 0, "max_age_in_seconds": 0, "extra_percent_with_rent": 0}, "taximeter_payment": 4000, "callcenter_commission_percent": 0}', 0, '{"cost": 1500000, "percent": 700}', '[{"value": 400, "marketing_level": ["co_branding", "lightbox"]}, {"value": 400, "marketing_level": ["sticker"]}, {"value": 400, "marketing_level": ["co_branding"]}, {"value": 400, "marketing_level": ["sticker", "lightbox"]}]', 11800, '[]', 6, '2018-08-15 14:36:29.089+00');
INSERT INTO fees.base_rule VALUES ('58b6b80ac69b0fb5f6079874', 'samara', NULL, NULL, 'cash', '2017-03-01 20:00:00+00', '2017-03-15 21:00:00+00', 'Europe/Samara', 'asymptotic_formula', '{"asymp": 113800, "cost_norm": 152000, "numerator": 1686000, "max_commission_percent": 1138}', 0, 60000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 200, "agp": 1, "hiring": {"extra_percent": 0, "max_age_in_seconds": 0, "extra_percent_with_rent": 0}, "taximeter_payment": 4000, "callcenter_commission_percent": 0}', 0, '{"cost": 1500000, "percent": 700}', '[{"value": 400, "marketing_level": ["co_branding", "lightbox"]}, {"value": 400, "marketing_level": ["sticker"]}, {"value": 400, "marketing_level": ["co_branding"]}, {"value": 400, "marketing_level": ["sticker", "lightbox"]}]', 11800, '[]', 6, '2018-08-15 14:36:29.09+00');
INSERT INTO fees.base_rule VALUES ('58c9856ab45bfd5fbfe360ec', 'samara', NULL, NULL, 'corp', '2017-03-15 21:00:00+00', '2017-07-02 20:00:00+00', 'Europe/Samara', 'asymptotic_formula', '{"asymp": 113800, "cost_norm": 152000, "numerator": 1686000, "max_commission_percent": 1138}', 0, 60000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 0, "agp": 1, "hiring": {"extra_percent": 0, "max_age_in_seconds": 0, "extra_percent_with_rent": 0}, "taximeter_payment": 4000, "callcenter_commission_percent": 0}', 0, '{"cost": 1500000, "percent": 700}', '[{"value": 400, "marketing_level": ["co_branding", "lightbox"]}, {"value": 400, "marketing_level": ["sticker"]}, {"value": 400, "marketing_level": ["co_branding"]}, {"value": 400, "marketing_level": ["sticker", "lightbox"]}]', 11800, '[]', 6, '2018-08-15 14:36:29.126+00');
INSERT INTO fees.base_rule VALUES ('595cef16c69b0fc56d94062a', 'samara', NULL, NULL, 'corp', '2017-07-05 20:00:00+00', '2017-11-30 20:00:00+00', 'Europe/Samara', 'asymptotic_formula', '{"asymp": 113800, "cost_norm": 152000, "numerator": 1686000, "max_commission_percent": 1138}', 0, 60000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 0, "agp": 1, "hiring": {"extra_percent": 0, "max_age_in_seconds": 0, "extra_percent_with_rent": 0}, "taximeter_payment": 4000, "callcenter_commission_percent": 0}', 0, '{"cost": 1500000, "percent": 700}', '[{"value": 800, "marketing_level": ["sticker"]}, {"value": 800, "marketing_level": ["sticker", "lightbox"]}]', 11800, '[]', 6, '2018-08-15 14:36:34.265+00');
INSERT INTO fees.base_rule VALUES ('58c9856ab45bfd5fbfe360ef', 'samara', NULL, NULL, 'card', '2017-03-15 21:00:00+00', '2017-07-02 20:00:00+00', 'Europe/Samara', 'asymptotic_formula', '{"asymp": 113800, "cost_norm": 152000, "numerator": 1686000, "max_commission_percent": 1138}', 0, 60000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 0, "agp": 1, "hiring": {"extra_percent": 0, "max_age_in_seconds": 0, "extra_percent_with_rent": 0}, "taximeter_payment": 4000, "callcenter_commission_percent": 0}', 0, '{"cost": 1500000, "percent": 700}', '[{"value": 400, "marketing_level": ["co_branding", "lightbox"]}, {"value": 400, "marketing_level": ["sticker"]}, {"value": 400, "marketing_level": ["co_branding"]}, {"value": 400, "marketing_level": ["sticker", "lightbox"]}]', 11800, '[]', 6, '2018-08-15 14:36:29.126+00');
INSERT INTO fees.base_rule VALUES ('58c9856ab45bfd5fbfe360f2', 'samara', NULL, NULL, 'cash', '2017-03-15 21:00:00+00', '2017-07-02 20:00:00+00', 'Europe/Samara', 'asymptotic_formula', '{"asymp": 113800, "cost_norm": 152000, "numerator": 1686000, "max_commission_percent": 1138}', 0, 60000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 0, "agp": 1, "hiring": {"extra_percent": 0, "max_age_in_seconds": 0, "extra_percent_with_rent": 0}, "taximeter_payment": 4000, "callcenter_commission_percent": 0}', 0, '{"cost": 1500000, "percent": 700}', '[{"value": 400, "marketing_level": ["co_branding", "lightbox"]}, {"value": 400, "marketing_level": ["sticker"]}, {"value": 400, "marketing_level": ["co_branding"]}, {"value": 400, "marketing_level": ["sticker", "lightbox"]}]', 11800, '[]', 6, '2018-08-15 14:36:29.126+00');
INSERT INTO fees.base_rule VALUES ('59555d06dac625aa919a03a1', 'samara', NULL, NULL, 'corp', '2017-07-02 20:00:00+00', '2017-07-05 20:00:00+00', 'Europe/Samara', 'asymptotic_formula', '{"asymp": 113800, "cost_norm": 152000, "numerator": 1686000, "max_commission_percent": 1138}', 0, 60000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 0, "agp": 1, "hiring": {"extra_percent": 0, "max_age_in_seconds": 0, "extra_percent_with_rent": 0}, "taximeter_payment": 4000, "callcenter_commission_percent": 0}', 0, '{"cost": 1500000, "percent": 700}', '[{"value": 800, "marketing_level": ["lightbox"]}, {"value": 800, "marketing_level": ["sticker", "lightbox"]}]', 11800, '[]', 6, '2018-08-15 14:36:29.184+00');
INSERT INTO fees.base_rule VALUES ('59555d19dac625204b445b89', 'samara', NULL, NULL, 'cash', '2017-07-02 20:00:00+00', '2017-07-05 20:00:00+00', 'Europe/Samara', 'asymptotic_formula', '{"asymp": 113800, "cost_norm": 152000, "numerator": 1686000, "max_commission_percent": 1138}', 0, 60000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 0, "agp": 1, "hiring": {"extra_percent": 0, "max_age_in_seconds": 0, "extra_percent_with_rent": 0}, "taximeter_payment": 4000, "callcenter_commission_percent": 0}', 0, '{"cost": 1500000, "percent": 700}', '[{"value": 800, "marketing_level": ["lightbox"]}, {"value": 800, "marketing_level": ["sticker", "lightbox"]}]', 11800, '[]', 6, '2018-08-15 14:36:29.184+00');
INSERT INTO fees.base_rule VALUES ('59555d32dac625ebee89686f', 'samara', NULL, NULL, 'card', '2017-07-02 20:00:00+00', '2017-07-05 20:00:00+00', 'Europe/Samara', 'asymptotic_formula', '{"asymp": 113800, "cost_norm": 152000, "numerator": 1686000, "max_commission_percent": 1138}', 0, 60000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 0, "agp": 1, "hiring": {"extra_percent": 0, "max_age_in_seconds": 0, "extra_percent_with_rent": 0}, "taximeter_payment": 4000, "callcenter_commission_percent": 0}', 0, '{"cost": 1500000, "percent": 700}', '[{"value": 800, "marketing_level": ["lightbox"]}, {"value": 800, "marketing_level": ["sticker", "lightbox"]}]', 11800, '[]', 6, '2018-08-15 14:36:29.185+00');
INSERT INTO fees.base_rule VALUES ('59555d55dac62510ed7edd1d', 'samara', NULL, NULL, 'corp', '2017-11-30 20:00:00+00', '2018-01-28 21:00:00+00', 'Europe/Samara', 'asymptotic_formula', '{"asymp": 113800, "cost_norm": 152000, "numerator": 1686000, "max_commission_percent": 1138}', 0, 60000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 0, "agp": 1, "hiring": {"extra_percent": 0, "max_age_in_seconds": 0, "extra_percent_with_rent": 0}, "taximeter_payment": 4000, "callcenter_commission_percent": 0}', 0, '{"cost": 1500000, "percent": 700}', '[{"value": 500, "marketing_level": ["sticker"]}, {"value": 500, "marketing_level": ["sticker", "lightbox"]}]', 11800, '[]', 6, '2018-08-15 14:36:29.185+00');
INSERT INTO fees.base_rule VALUES ('59555d67dac625aa919a03a6', 'samara', NULL, NULL, 'cash', '2017-11-30 20:00:00+00', '2018-01-28 21:00:00+00', 'Europe/Samara', 'asymptotic_formula', '{"asymp": 113800, "cost_norm": 152000, "numerator": 1686000, "max_commission_percent": 1138}', 0, 60000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 0, "agp": 1, "hiring": {"extra_percent": 0, "max_age_in_seconds": 0, "extra_percent_with_rent": 0}, "taximeter_payment": 4000, "callcenter_commission_percent": 0}', 0, '{"cost": 1500000, "percent": 700}', '[{"value": 500, "marketing_level": ["sticker"]}, {"value": 500, "marketing_level": ["sticker", "lightbox"]}]', 11800, '[]', 6, '2018-08-15 14:36:29.185+00');
INSERT INTO fees.base_rule VALUES ('59555d72dac62510ed7edd1f', 'samara', NULL, NULL, 'card', '2017-11-30 20:00:00+00', '2018-01-28 21:00:00+00', 'Europe/Samara', 'asymptotic_formula', '{"asymp": 113800, "cost_norm": 152000, "numerator": 1686000, "max_commission_percent": 1138}', 0, 60000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 0, "agp": 1, "hiring": {"extra_percent": 0, "max_age_in_seconds": 0, "extra_percent_with_rent": 0}, "taximeter_payment": 4000, "callcenter_commission_percent": 0}', 0, '{"cost": 1500000, "percent": 700}', '[{"value": 500, "marketing_level": ["sticker"]}, {"value": 500, "marketing_level": ["sticker", "lightbox"]}]', 11800, '[]', 6, '2018-08-15 14:36:29.185+00');
INSERT INTO fees.base_rule VALUES ('5cc2f2f10c69ff5feec1ff6e', 'samara', NULL, NULL, 'card', '2019-05-06 20:00:00+00', '2999-12-31 21:00:00+00', 'Europe/Samara', 'fixed_percent', '{"percent": 1350}', 0, 150000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 0, "u_min": 0}', '{"acp": 0, "agp": 0, "hiring": {"extra_percent": 200, "max_age_in_seconds": 15552000, "extra_percent_with_rent": 400}, "taximeter_payment": 10000, "callcenter_commission_percent": 200}', 0, '{"cost": 1500000, "percent": 1350}', '[]', 12000, '[]', 6, '2019-04-26 12:00:49.801+00');
INSERT INTO fees.base_rule VALUES ('595cef26c69b0ff11abc4abb', 'samara', NULL, NULL, 'cash', '2017-07-05 20:00:00+00', '2017-11-30 20:00:00+00', 'Europe/Samara', 'asymptotic_formula', '{"asymp": 113800, "cost_norm": 152000, "numerator": 1686000, "max_commission_percent": 1138}', 0, 60000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 0, "agp": 1, "hiring": {"extra_percent": 0, "max_age_in_seconds": 0, "extra_percent_with_rent": 0}, "taximeter_payment": 4000, "callcenter_commission_percent": 0}', 0, '{"cost": 1500000, "percent": 700}', '[{"value": 800, "marketing_level": ["sticker"]}, {"value": 800, "marketing_level": ["sticker", "lightbox"]}]', 11800, '[]', 6, '2018-08-15 14:36:34.265+00');
INSERT INTO fees.base_rule VALUES ('595cef2ec69b0ff11abc4abd', 'samara', NULL, NULL, 'card', '2017-07-05 20:00:00+00', '2017-11-30 20:00:00+00', 'Europe/Samara', 'asymptotic_formula', '{"asymp": 113800, "cost_norm": 152000, "numerator": 1686000, "max_commission_percent": 1138}', 0, 60000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 0, "agp": 1, "hiring": {"extra_percent": 0, "max_age_in_seconds": 0, "extra_percent_with_rent": 0}, "taximeter_payment": 4000, "callcenter_commission_percent": 0}', 0, '{"cost": 1500000, "percent": 700}', '[{"value": 800, "marketing_level": ["sticker"]}, {"value": 800, "marketing_level": ["sticker", "lightbox"]}]', 11800, '[]', 6, '2018-08-15 14:36:34.265+00');
INSERT INTO fees.base_rule VALUES ('5a74448edac625f2c239c635', 'samara', NULL, NULL, 'corp', '2018-02-04 20:00:00+00', '2018-03-22 21:00:00+00', 'Europe/Samara', 'asymptotic_formula', '{"asymp": 113800, "cost_norm": 152000, "numerator": 1686000, "max_commission_percent": 1138}', 0, 150000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 0, "agp": 1, "hiring": {"extra_percent": 200, "max_age_in_seconds": 15552000, "extra_percent_with_rent": 400}, "taximeter_payment": 10000, "callcenter_commission_percent": 0}', 0, '{"cost": 1500000, "percent": 700}', '[{"value": 300, "marketing_level": ["sticker"]}, {"value": 300, "marketing_level": ["sticker", "lightbox"]}]', 11800, '[]', 6, '2018-08-15 14:36:39.541+00');
INSERT INTO fees.base_rule VALUES ('5a7444c2dac625d48521931a', 'samara', NULL, NULL, 'cash', '2018-02-04 20:00:00+00', '2018-03-22 21:00:00+00', 'Europe/Samara', 'asymptotic_formula', '{"asymp": 113800, "cost_norm": 152000, "numerator": 1686000, "max_commission_percent": 1138}', 0, 150000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 0, "agp": 1, "hiring": {"extra_percent": 200, "max_age_in_seconds": 15552000, "extra_percent_with_rent": 400}, "taximeter_payment": 10000, "callcenter_commission_percent": 0}', 0, '{"cost": 1500000, "percent": 700}', '[{"value": 300, "marketing_level": ["sticker"]}, {"value": 300, "marketing_level": ["sticker", "lightbox"]}]', 11800, '[]', 6, '2018-08-15 14:36:39.541+00');
INSERT INTO fees.base_rule VALUES ('5a7444d4dac625dd6f7b6038', 'samara', NULL, NULL, 'card', '2018-02-04 20:00:00+00', '2018-03-22 21:00:00+00', 'Europe/Samara', 'asymptotic_formula', '{"asymp": 113800, "cost_norm": 152000, "numerator": 1686000, "max_commission_percent": 1138}', 0, 150000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 0, "agp": 1, "hiring": {"extra_percent": 200, "max_age_in_seconds": 15552000, "extra_percent_with_rent": 400}, "taximeter_payment": 10000, "callcenter_commission_percent": 0}', 0, '{"cost": 1500000, "percent": 700}', '[{"value": 300, "marketing_level": ["sticker"]}, {"value": 300, "marketing_level": ["sticker", "lightbox"]}]', 11800, '[]', 6, '2018-08-15 14:36:39.541+00');
INSERT INTO fees.base_rule VALUES ('5bac955e8f19ceed7f743df7', 'samara', NULL, NULL, 'card', '2018-09-30 20:00:00+00', '2019-01-01 00:00:00+00', 'Europe/Samara', 'fixed_percent', '{"percent": 1200}', 0, 150000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 0, "agp": 0, "hiring": {"extra_percent": 200, "max_age_in_seconds": 15552000, "extra_percent_with_rent": 400}, "taximeter_payment": 10000, "callcenter_commission_percent": 200}', 0, '{"cost": 1500000, "percent": 700}', '[]', 11800, '[]', 6, '2018-09-27 08:31:26.634+00');
INSERT INTO fees.base_rule VALUES ('5bac95648f19ceed7f743df9', 'samara', NULL, NULL, 'cash', '2018-09-30 20:00:00+00', '2019-01-01 00:00:00+00', 'Europe/Samara', 'fixed_percent', '{"percent": 1200}', 0, 150000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 0, "agp": 0, "hiring": {"extra_percent": 200, "max_age_in_seconds": 15552000, "extra_percent_with_rent": 400}, "taximeter_payment": 10000, "callcenter_commission_percent": 200}', 0, '{"cost": 1500000, "percent": 700}', '[]', 11800, '[]', 6, '2018-09-27 08:31:32.769+00');
INSERT INTO fees.base_rule VALUES ('5bac956b8f19ceed2d713168', 'samara', NULL, NULL, 'corp', '2018-09-30 20:00:00+00', '2019-01-01 00:00:00+00', 'Europe/Samara', 'fixed_percent', '{"percent": 1200}', 0, 150000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 600, "u_min": 120}', '{"acp": 0, "agp": 0, "hiring": {"extra_percent": 200, "max_age_in_seconds": 15552000, "extra_percent_with_rent": 400}, "taximeter_payment": 10000, "callcenter_commission_percent": 200}', 0, '{"cost": 1500000, "percent": 700}', '[]', 11800, '[]', 6, '2018-09-27 08:31:39.412+00');
INSERT INTO fees.base_rule VALUES ('5caf65178f19ce4685c1e6a6', 'moscow', 'econom', NULL, 'card', '2019-04-11 21:00:00+00', '2999-12-31 21:00:00+00', 'Europe/Moscow', 'fixed_percent', '{"percent": 1800}', 0, 150000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 0, "u_min": 0}', '{"acp": 0, "agp": 0, "hiring": {"extra_percent": 200, "max_age_in_seconds": 15552000, "extra_percent_with_rent": 400}, "taximeter_payment": 55000, "callcenter_commission_percent": 100}', NULL, '{"cost": 8000000, "percent": 1100}', '[]', 12000, '[]', 6, '2019-04-11 16:02:31.591+00');
INSERT INTO fees.base_rule VALUES ('5caf65178f19ce4685c1e6a8', 'moscow', 'econom', NULL, 'cash', '2019-04-11 21:00:00+00', '2999-12-31 21:00:00+00', 'Europe/Moscow', 'fixed_percent', '{"percent": 1800}', 0, 150000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 0, "u_min": 0}', '{"acp": 0, "agp": 0, "hiring": {"extra_percent": 200, "max_age_in_seconds": 15552000, "extra_percent_with_rent": 400}, "taximeter_payment": 55000, "callcenter_commission_percent": 100}', NULL, '{"cost": 8000000, "percent": 1100}', '[]', 12000, '[]', 6, '2019-04-11 16:02:31.591+00');
INSERT INTO fees.base_rule VALUES ('5cc2f2f10c69ff5feec1ff6c', 'samara', NULL, NULL, 'corp', '2019-05-06 20:00:00+00', '2999-12-31 21:00:00+00', 'Europe/Samara', 'fixed_percent', '{"percent": 1350}', 0, 150000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 0, "u_min": 0}', '{"acp": 0, "agp": 0, "hiring": {"extra_percent": 200, "max_age_in_seconds": 15552000, "extra_percent_with_rent": 400}, "taximeter_payment": 10000, "callcenter_commission_percent": 200}', 0, '{"cost": 1500000, "percent": 1350}', '[]', 12000, '[]', 6, '2019-04-26 12:00:49.8+00');
INSERT INTO fees.base_rule VALUES ('5cc2f2f10c69ff5feec1ff70', 'samara', NULL, NULL, 'cash', '2019-05-06 20:00:00+00', '2999-12-31 21:00:00+00', 'Europe/Samara', 'fixed_percent', '{"percent": 1350}', 0, 150000000, '{"bcd": 300, "p_max": 600, "p_min": 420, "u_max": 0, "u_min": 0}', '{"acp": 0, "agp": 0, "hiring": {"extra_percent": 200, "max_age_in_seconds": 15552000, "extra_percent_with_rent": 400}, "taximeter_payment": 10000, "callcenter_commission_percent": 200}', 0, '{"cost": 1500000, "percent": 1350}', '[]', 12000, '[]', 6, '2019-04-26 12:00:49.801+00');


--
-- Data for Name: base_rule_draft; Type: TABLE DATA; Schema: fees; Owner: sibilla
--



--
-- Data for Name: category; Type: TABLE DATA; Schema: fees; Owner: sibilla
--



--
-- Data for Name: category_account; Type: TABLE DATA; Schema: fees; Owner: sibilla
--



--
-- Data for Name: draft_category; Type: TABLE DATA; Schema: fees; Owner: sibilla
--



--
-- Data for Name: draft_category_account; Type: TABLE DATA; Schema: fees; Owner: sibilla
--



--
-- Data for Name: draft_rebate_rule; Type: TABLE DATA; Schema: fees; Owner: sibilla
--



--
-- Data for Name: rebate_rule; Type: TABLE DATA; Schema: fees; Owner: sibilla
--



--
-- Data for Name: draft_rebate_rule_to_close; Type: TABLE DATA; Schema: fees; Owner: sibilla
--



--
-- Data for Name: draft_rule; Type: TABLE DATA; Schema: fees; Owner: sibilla
--



--
-- Data for Name: rule; Type: TABLE DATA; Schema: fees; Owner: sibilla
--

INSERT INTO fees.rule VALUES ('39ac60f4-b14d-42c7-9e0f-21739c202931', 'taximeter', 'moscow', 'econom', '2019-04-11 21:00:00+00', '2119-04-11 21:00:00+00', 5, '2022-01-19 13:43:32.493869+00', '{"fee": "5.5"}', '2022-01-19 13:43:32.493869+00');
INSERT INTO fees.rule VALUES ('64784b2e-8499-434c-8016-7b81c93d648e', 'taximeter', 'moscow', 'econom', '2019-04-11 21:00:00+00', '2119-04-11 21:00:00+00', 5, '2022-01-19 13:43:32.493869+00', '{"fee": "5.5"}', '2022-01-19 13:43:32.493869+00');
INSERT INTO fees.rule VALUES ('a83deb7a-b6f4-45ff-bce9-f04d2b80fb75', 'taximeter', 'samara', '', '2019-05-06 20:00:00+00', '2119-05-06 20:00:00+00', 5, '2022-01-19 13:43:32.493869+00', '{"fee": "1.0"}', '2022-01-19 13:43:32.493869+00');
INSERT INTO fees.rule VALUES ('9c5f2519-237e-4db9-9c03-cb761deb15e4', 'taximeter', 'samara', '', '2019-05-06 20:00:00+00', '2119-05-06 20:00:00+00', 5, '2022-01-19 13:43:32.493869+00', '{"fee": "1.0"}', '2022-01-19 13:43:32.493869+00');
INSERT INTO fees.rule VALUES ('6a644cc5-3f6b-4de8-a3c6-7a7337183947', 'taximeter', 'samara', '', '2019-05-06 20:00:00+00', '2119-05-06 20:00:00+00', 5, '2022-01-19 13:43:32.493869+00', '{"fee": "1.0"}', '2022-01-19 13:43:32.493869+00');


--
-- Data for Name: draft_rule_to_close; Type: TABLE DATA; Schema: fees; Owner: sibilla
--



--
-- Data for Name: rebate_rule_change_log; Type: TABLE DATA; Schema: fees; Owner: sibilla
--



--
-- Data for Name: rule_change_log; Type: TABLE DATA; Schema: fees; Owner: sibilla
--

INSERT INTO fees.rule_change_log VALUES (6, '39ac60f4-b14d-42c7-9e0f-21739c202931', '2022-01-19 13:43:32.493869+00', 'maksimzubkov', 'TAXIBILLING-6144', '5', 'Migrate taximeter rules from Mongo', '', '2022-01-19 13:43:32.493869+00');
INSERT INTO fees.rule_change_log VALUES (7, '64784b2e-8499-434c-8016-7b81c93d648e', '2022-01-19 13:43:32.493869+00', 'maksimzubkov', 'TAXIBILLING-6144', '5', 'Migrate taximeter rules from Mongo', '', '2022-01-19 13:43:32.493869+00');
INSERT INTO fees.rule_change_log VALUES (8, 'a83deb7a-b6f4-45ff-bce9-f04d2b80fb75', '2022-01-19 13:43:32.493869+00', 'maksimzubkov', 'TAXIBILLING-6144', '5', 'Migrate taximeter rules from Mongo', '', '2022-01-19 13:43:32.493869+00');
INSERT INTO fees.rule_change_log VALUES (9, '9c5f2519-237e-4db9-9c03-cb761deb15e4', '2022-01-19 13:43:32.493869+00', 'maksimzubkov', 'TAXIBILLING-6144', '5', 'Migrate taximeter rules from Mongo', '', '2022-01-19 13:43:32.493869+00');
INSERT INTO fees.rule_change_log VALUES (10, '6a644cc5-3f6b-4de8-a3c6-7a7337183947', '2022-01-19 13:43:32.493869+00', 'maksimzubkov', 'TAXIBILLING-6144', '5', 'Migrate taximeter rules from Mongo', '', '2022-01-19 13:43:32.493869+00');


--
-- Data for Name: rule_fine_code; Type: TABLE DATA; Schema: fees; Owner: sibilla
--



--
-- Data for Name: rule_hiring_type; Type: TABLE DATA; Schema: fees; Owner: sibilla
--



--
-- Data for Name: rule_min_max_cost; Type: TABLE DATA; Schema: fees; Owner: sibilla
--



--
-- Data for Name: rule_payment_type; Type: TABLE DATA; Schema: fees; Owner: sibilla
--

INSERT INTO fees.rule_payment_type VALUES (6, '39ac60f4-b14d-42c7-9e0f-21739c202931', 'card', '2022-01-19 13:43:32.493869+00');
INSERT INTO fees.rule_payment_type VALUES (7, '64784b2e-8499-434c-8016-7b81c93d648e', 'cash', '2022-01-19 13:43:32.493869+00');
INSERT INTO fees.rule_payment_type VALUES (8, 'a83deb7a-b6f4-45ff-bce9-f04d2b80fb75', 'corp', '2022-01-19 13:43:32.493869+00');
INSERT INTO fees.rule_payment_type VALUES (9, '9c5f2519-237e-4db9-9c03-cb761deb15e4', 'card', '2022-01-19 13:43:32.493869+00');
INSERT INTO fees.rule_payment_type VALUES (10, '6a644cc5-3f6b-4de8-a3c6-7a7337183947', 'cash', '2022-01-19 13:43:32.493869+00');


--
-- Data for Name: rule_tag; Type: TABLE DATA; Schema: fees; Owner: sibilla
--



--
-- Data for Name: withdraw_from_driver_account; Type: TABLE DATA; Schema: fees; Owner: sibilla
--



--
-- Name: category_account_id_seq; Type: SEQUENCE SET; Schema: fees; Owner: sibilla
--

SELECT pg_catalog.setval('fees.category_account_id_seq', 1, false);


--
-- Name: draft_category_account_id_seq; Type: SEQUENCE SET; Schema: fees; Owner: sibilla
--

SELECT pg_catalog.setval('fees.draft_category_account_id_seq', 1, false);


--
-- Name: draft_rebate_rule_to_close_id_seq; Type: SEQUENCE SET; Schema: fees; Owner: sibilla
--

SELECT pg_catalog.setval('fees.draft_rebate_rule_to_close_id_seq', 1, false);


--
-- Name: draft_spec_id_seq; Type: SEQUENCE SET; Schema: fees; Owner: sibilla
--

SELECT pg_catalog.setval('fees.draft_spec_id_seq', 6, true);


--
-- Name: rebate_rule_change_log_id_seq; Type: SEQUENCE SET; Schema: fees; Owner: sibilla
--

SELECT pg_catalog.setval('fees.rebate_rule_change_log_id_seq', 1, false);


--
-- Name: rule_change_log_id_seq; Type: SEQUENCE SET; Schema: fees; Owner: sibilla
--

SELECT pg_catalog.setval('fees.rule_change_log_id_seq', 10, true);


--
-- Name: rule_fine_code_id_seq; Type: SEQUENCE SET; Schema: fees; Owner: sibilla
--

SELECT pg_catalog.setval('fees.rule_fine_code_id_seq', 1, false);


--
-- Name: rule_hiring_type_id_seq; Type: SEQUENCE SET; Schema: fees; Owner: sibilla
--

SELECT pg_catalog.setval('fees.rule_hiring_type_id_seq', 1, false);


--
-- Name: rule_min_max_cost_id_seq; Type: SEQUENCE SET; Schema: fees; Owner: sibilla
--

SELECT pg_catalog.setval('fees.rule_min_max_cost_id_seq', 1, false);


--
-- Name: rule_payment_type_id_seq; Type: SEQUENCE SET; Schema: fees; Owner: sibilla
--

SELECT pg_catalog.setval('fees.rule_payment_type_id_seq', 10, true);


--
-- Name: rule_tag_id_seq; Type: SEQUENCE SET; Schema: fees; Owner: sibilla
--

SELECT pg_catalog.setval('fees.rule_tag_id_seq', 1, false);


--
-- Name: withdraw_from_driver_account_id_seq; Type: SEQUENCE SET; Schema: fees; Owner: sibilla
--

SELECT pg_catalog.setval('fees.withdraw_from_driver_account_id_seq', 1, false);


--
-- PostgreSQL database dump complete
--

