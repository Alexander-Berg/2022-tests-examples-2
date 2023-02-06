--
-- Data for Name: cart_items; Type: TABLE DATA; Schema: cart; Owner: testsuite
--

INSERT INTO cart.cart_items (cart_id, item_id, price, quantity, currency, updated, created)
VALUES ('8da556be-0971-4f3b-a454-d980130662cc', 'item_id_1:st-pa', '345', 1, 'RUB',
        '2020-02-03 16:33:54.827958+03', '2020-02-03 16:33:54.827958+03');


--
-- Data for Name: carts; Type: TABLE DATA; Schema: cart; Owner: testsuite
--

INSERT INTO cart.carts (cart_id, cart_version, user_type, user_id, session, bound_sessions, updated, created)
VALUES ('8da556be-0971-4f3b-a454-d980130662cc', 1, 'yandex_taxi', '1234', 'taxi:1234', array['eats:123']::TEXT[],
        '2019-12-01 01:01:01.000000+00',
        '2019-12-01 01:01:01.000000+00');


--
-- PostgreSQL database dump complete
--
