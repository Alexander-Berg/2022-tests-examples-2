INSERT INTO callcenter_stats.call_history
  (id, call_id, queue, agent_id, queued_at, answered_at, completed_at,
   endreason, transfered_to, transfered_to_number, abonent_phone_id,
   called_number, call_guid
   ,direction
  )
VALUES
  ('id1_hash','id1','corp_cc', '111', '2019-09-03 09:00:01.00', null, '2019-09-03 09:20:00.00', 'transfered', 'help', '+74958888888', 'phone_id_2', '+74959999999', '0002030101-0000065536-1585747335-0000937601', 'in'),
  ('id2_hash','id2','corp_cc', null, '2019-09-03 09:00:02.00', '2019-09-03 10:00:00.00', '2019-09-03 11:00:00.00', 'transfered', 'help', '+74958888888', 'phone_id_3', '+74959999999', '0002030101-0000065536-1585747335-0000937602', null),
  ('good_id3_hash','id3','help_cc', '111', '2019-09-03 09:00:03.00', '2019-09-03 10:00:00.00', '2019-09-03 11:00:00.00', 'completed_by_caller' , null, null, 'phone_id_1', '+74959999999', '0002030101-0000065536-1585747335-0000937603', null),
  ('id4_hash','id4','help_cc', '111', '2019-09-03 09:00:04.00', '2019-09-03 09:30:00.00', '2019-09-03 10:00:00.00', 'completed_by_agent' , null, null, 'phone_id_1_extra', '+74959999999', '0002030101-0000065536-1585747335-0000937604', null),
  ('id5_hash','id5','help_cc', '222', '2019-09-03 09:00:05.00', '2019-09-03 10:00:00.00', '2019-09-03 11:00:00.00', 'completed_by_caller' , null, null, 'phone_id_1', '+74959999999', '0002030101-0000065536-1585747335-0000937605', null),
  ('id6_hash','id6','help_cc', '222', '2019-09-03 09:00:06.00', '2019-09-03 09:30:00.00', '2019-09-03 10:00:00.00', 'completed_by_agent' , null, null, 'phone_id_1_extra', '+74959999999', '0002030101-0000065536-1585747335-0000937606', null),
  ('id7_hash','id7','help_cc', '111', '2019-09-03 09:00:07.00', '2019-09-03 09:30:00.00', '2019-09-03 10:00:00.00', 'abandoned', null, null, 'phone_id_1', '+74959999999', '0002030101-0000065536-1585747335-0000937607', null),
  ('id8_hash','id8','help_cc', '222', '2019-09-03 09:00:08.00', '2019-09-03 09:30:00.00', '2019-09-03 10:00:00.00', 'abandoned', null, null, 'phone_id_1', '+74959999999', '0002030101-0000065536-1585747335-0000937608', null),
  ('good_id9_hash','id9','help_cc', null , '2019-09-03 09:20:12.918791', null, '2019-09-03 09:21:12.918791', 'abandoned', null, null, 'phone_id_1', '+74959999999', '0002030101-0000065536-1585747335-0000937609', null),
  ('id10_hash','id10','corp_cc', '222', '2019-09-03 09:25:00.918791', '2019-09-03 09:26:00.918791', '2019-09-03 09:26:01.918791', 'abandoned', null, null, 'phone_id_1', '+74959999999', '0002030101-0000065536-1585747335-0000937610', null)
 ,('id11_hash','id11','corp_cc', '222', '2019-09-03 09:00:11.00', '2019-09-03 09:30:00.00', '2019-09-03 10:00:00.00', 'completed_by_agent', null, null, 'phone_id_1', '+74959999999', '0002030101-0000065536-1585747335-0000937611', 'out')
;