INSERT INTO booking.slots (id, name, count) VALUES (1000, 'prev_zone/prev_area/prev_tag', 1);
INSERT INTO booking.slots (id, name, count) VALUES (1001, 'prev_work_mode/prev_rule_id', 1);

INSERT INTO booking.slot_reservations (slot_id, issuer) VALUES (1000, 'parkid1_uuid1');
INSERT INTO booking.slot_reservations (slot_id, issuer) VALUES (1001, 'parkid2_uuid2');
INSERT INTO booking.slot_reservations (slot_id, issuer) VALUES (1001, 'parkid3_uuid3');
