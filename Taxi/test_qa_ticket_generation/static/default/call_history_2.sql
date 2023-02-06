INSERT INTO callcenter_stats.call_history
  (id, call_id, queue, agent_id, queued_at, answered_at, completed_at,
   endreason, transfered_to, transfered_to_number, abonent_phone_id,
   called_number, call_guid, direction)
VALUES
   ('id1/hash', 'id1' ,'help_cc_on_1', '111', '2020-07-07 08:00:00.00', '2020-07-07 09:00:00.00', '2020-07-07 09:00:01.00', 'completed_by_caller', null, null, 'phone_id_1', '+74959999999', '0002030101+0000065536+1585747335+0000937601', 'in')
  ,('id2/hash', 'id2' ,'help_cc_on_1', '111', '2020-07-07 08:00:00.00', '2020-07-07 09:00:00.00', '2020-07-07 09:00:05.00', 'completed_by_agent', null, null, 'phone_id_1', '+74959999999', '0002030101/0000065536/1585747335/0000937602', null)
  ,('id3/hash', 'id3' ,'help_cc_on_1', '111', '2020-07-07 08:00:00.00', '2020-07-07 09:00:00.00', '2020-07-07 09:00:10.00', 'completed_by_caller', null, null, 'phone_id_2', '+74958888888', '0002030101-0000065536-1585747335-0000937603=', 'in')
  ,('id4/hash', 'id4' ,'help_cc_on_1', '111', '2020-07-07 08:00:00.00', '2020-07-07 09:00:00.00', '2020-07-07 09:00:30.00', 'completed_by_agent', null, null, 'phone_id_1', '+74958888888', '0002030101-0000065536-1585747335-0000937604=', null)
  ,('id5/hash', 'id5' ,'help_cc_on_1', '111', '2020-07-07 08:00:00.00', '2020-07-07 09:00:00.00', '2020-07-07 09:01:30.00', 'completed_by_caller', null, null, 'phone_id_1', '+74959999999', '0002030101=0000065536=1585747335=0000937605', 'in')
  ,('id6/hash', 'id6' ,'help_cc_on_1', '111', '2020-07-07 08:00:00.00', '2020-07-07 09:00:00.00', '2020-07-07 09:02:00.00', 'completed_by_agent', null, null, 'phone_id_2', '+74959999999', '0002030101-0000065536-1585747335-0000937606=', null)
  ,('id7/hash', 'id7' ,'help_cc_on_1', '111', '2020-07-07 08:00:00.00', '2020-07-07 09:00:00.00', '2020-07-07 09:04:00.00', 'completed_by_caller', null, null, 'phone_id_1', '+74958888888', '0002030101-0000065536-1585747335-0000937607=', 'in')
  ,('id8/hash', 'id8' ,'help_cc_on_1', 'unknown_id', '2020-07-07 08:00:00.00', '2020-07-07 09:00:00.00', '2020-07-07 10:00:00.00', 'completed_by_caller', null, null, 'phone_id_1', '+74959999999', '0002030101-0000065536-1585747335-0000937608=', null)
  ,('id9/hash', 'id9' ,'help_cc_on_1', '111', '2020-07-07 08:00:00.00', '2020-07-07 09:00:00.00', '2020-07-07 09:01:30.00', 'completed_by_caller', null, null, 'phone_id_1', '+74959999999', '0002030101=0000065536=1585747335=0000937605', 'out')
  ,('id10/hash', 'id10' ,'help_cc_on_1', '111', '2020-07-07 08:00:00.00', '2020-07-07 09:00:00.00', '2020-07-07 09:02:00.00', 'completed_by_agent', null, null, 'phone_id_2', '+74959999999', '0002030101-0000065536-1585747335-0000937606=', 'out')
;