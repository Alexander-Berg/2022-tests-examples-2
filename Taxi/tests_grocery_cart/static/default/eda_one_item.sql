--
-- Data for Name: cart_items; Type: TABLE DATA; Schema: cart; Owner: testsuite
--

INSERT INTO cart.cart_items (cart_id, item_id, price, quantity, currency, updated, created)
VALUES ('8da556be-0971-4f3b-a454-d980130662cc', 'item_id_1', '345', 1, 'RUB',
        '2020-02-03 16:33:54.827958+03', '2020-02-03 16:33:54.827958+03');


--
-- Data for Name: carts; Type: TABLE DATA; Schema: cart; Owner: testsuite
--

INSERT INTO cart.carts (cart_id, cart_version, user_type, user_id, session, bound_sessions, updated, created)
VALUES ('8da556be-0971-4f3b-a454-d980130662cc', 1, 'eats_user_id', '12345', 'eats:123', array['taxi:1234']::TEXT[],
        '2020-02-03 16:33:54.827958+03',
        '2020-02-03 16:33:54.827958+03');


--
-- PostgreSQL database dump complete
--
