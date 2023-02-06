INSERT INTO booking.slots (id, name, count) VALUES (1000, 'next_zone/next_area/next_tag', 1);
INSERT INTO booking.slots (id, name, count) VALUES (1001, 'next_work_mode/next_rule_id', 1);
INSERT INTO booking.slots (id, name, count) VALUES (1002, 'next_work_mode/next_context_zone', 1);

INSERT INTO booking.slot_reservations (slot_id, issuer) VALUES (1000, 'parkid3_uuid3');
INSERT INTO booking.slot_reservations (slot_id, issuer) VALUES (1001, 'parkid4_uuid4');
INSERT INTO booking.slot_reservations (slot_id, issuer) VALUES (1002, 'parkid5_uuid6');
