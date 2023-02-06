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

