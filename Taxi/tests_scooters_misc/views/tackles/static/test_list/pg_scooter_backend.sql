INSERT INTO scooters_misc.tackles(
  id,
  kind,
  depot_id,
  performer_id,
  recharge_task_id,
  version
)
VALUES
  ('1', 'recharging_wire', 'depot1', 'performer1', 'recharge_task1', 1),
  ('2', 'recharging_wire', 'depot1', 'performer1', 'recharge_task1', 1),
  ('3', 'recharging_wire', 'depot1', 'performer1', NULL, 1),
  ('4', 'recharging_wire', 'depot2', 'performer2', 'recharge_task2', 2),
  ('5', 'recharging_wire', 'depot2', 'performer2', 'recharge_task3', 2),
  ('6', 'recharging_wire', 'depot2', 'performer3', 'recharge_task4', 1),
  ('7', 'recharging_wire', 'depot1', 'performer4', 'recharge_task5', 1),
  ('8', 'recharging_wire', 'depot1', 'performer5', 'recharge_task6', 1),
  ('9', 'recharging_wire', NULL, 'performer5', 'recharge_task4', 4),
  ('10', 'recharging_wire', 'depot1', NULL, 'recharge_task6', 1),
  ('11', 'recharging_wire', NULL, 'performer5', NULL, 9),
  ('12', 'recharging_wire', 'depot1', NULL, NULL, 3),
  ('13', 'recharging_wire', NULL, NULL, NULL, 2);
