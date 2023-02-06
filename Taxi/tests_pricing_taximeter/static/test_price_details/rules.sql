INSERT INTO price_modifications.rules
  (rule_id, name, source_code, policy, author, approvals_id, ast)
VALUES
  (1, 'emit components', '', 'both_side', '200ok', 1, '')
;

UPDATE price_modifications.rules
    SET source_code = '
return {metadata=[
    "req:something_important:price": 100.0,
    "req:something_important:per_unit": 25.0,
    "req:something_important:count": 4,

    "srv:something_unusual": 12.34,
    "srv:anything_unusual:price": 34.21

]};',
ast = 'E("req:something_important:price",100.0);E("req:something_important:per_unit",25.0);E("req:something_important:count",4.0);E("srv:something_unusual",12.34);E("srv:anything_unusual:price",34.21);CR(boarding=B(B(ride,.,F(price)),.,F(boarding)),distance=B(B(ride,.,F(price)),.,F(distance)),time=B(B(ride,.,F(price)),.,F(time)),waiting=B(B(ride,.,F(price)),.,F(waiting)),requirements=B(B(ride,.,F(price)),.,F(requirements)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_waiting)),destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)))'
WHERE rule_id = 1;
