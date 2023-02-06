INSERT INTO price_modifications.rules
    (rule_id, name, source_code, policy, author, approvals_id, ast, updated, deleted, previous_version_id)
  VALUES
    (1, 'one', 'return {boarding=ride.price.boarding + 2, metadata=["w":ride.price.waiting]};', 'backend_only', '200ok', 00, 'CR(boarding=B(B(B(1.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(boarding)),distance=B(B(B(1.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(distance)),time=B(B(B(1.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(time)),waiting=B(B(B(1.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(waiting)),requirements=B(B(B(1.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(requirements)),transit_waiting=B(B(B(1.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(transit_waiting)),destination_waiting=B(B(B(1.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(destination_waiting)))', '2010-03-04 06:00:00', true, null),
    (2, 'two', 'return ride.price * 2;', 'backend_only', '200ok', 01, 'CR(boarding=B(B(B(1.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(boarding)),distance=B(B(B(1.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(distance)),time=B(B(B(1.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(time)),waiting=B(B(B(1.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(waiting)),requirements=B(B(B(1.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(requirements)),transit_waiting=B(B(B(1.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(transit_waiting)),destination_waiting=B(B(B(1.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(destination_waiting)))', '2010-03-04 06:00:00', true, null),
    (3, 'three', 'return {boarding=ride.price.boarding + 3, metadata=["r":ride.price.requirements]};', 'backend_only', '200ok', 02, 'CR(boarding=B(B(B(1.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(boarding)),distance=B(B(B(1.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(distance)),time=B(B(B(1.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(time)),waiting=B(B(B(1.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(waiting)),requirements=B(B(B(1.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(requirements)),transit_waiting=B(B(B(1.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(transit_waiting)),destination_waiting=B(B(B(1.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(destination_waiting)))', '2010-03-04 06:00:00', true, null),
    (4, 'four', 'return ride.price * 3;', 'backend_only', '200ok', 03, 'CR(boarding=B(B(B(1.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(boarding)),distance=B(B(B(1.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(distance)),time=B(B(B(1.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(time)),waiting=B(B(B(1.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(waiting)),requirements=B(B(B(1.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(requirements)),transit_waiting=B(B(B(1.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(transit_waiting)),destination_waiting=B(B(B(1.00000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(destination_waiting)))', '2010-03-04 06:00:00', true, null)
;