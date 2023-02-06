INSERT INTO eats_tips_withdrawal.withdrawals (
  id,
  partner_id,
  b2p_user_id,
  fullname_id,
  amount,
  fee,
  create_date,
  admin,
  bp2_order_id,
  bp2_order_reference,
  withdrawal_method,
  is_blacklist,
  is_one_card,
  is_not_from_russian,
  is_from_3k_pay,
  bank_id,
  target_phone_id,
  last_update,
  precheck_id,
  status,
  currency,
  idempotency_key,
  comment,
  card_pan
)
VALUES
(1,'00000000-0000-0000-0000-000000000002',2,'SHORT_FULLNAME_ID',21.00, 0,'2021-06-22 19:10:25','','26','withdrawal1','SBPb2p',false,false,false,false,'100000000001','LONG_PHONE_ID','2021-06-22 19:10:25',22,'precheck created','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwNzlh', null, ''),
(2,'00000000-0000-0000-0000-000000000001',1,'SHORT_FULLNAME_ID',21.00, 0,'2021-06-22 19:10:25','','27','withdrawal2','SBPb2p',false,false,false,false,'100000000001','LONG_PHONE_ID','2021-06-22 19:10:25',22,'sent to manual check','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwNzl3', null, ''),
(3,'00000000-0000-0000-0000-000000000001',1,'SHORT_FULLNAME_ID',21.00, 0,'2021-06-22 19:10:25','99','31','withdrawal3','SBPb2p',false,false,false,false,'100000000001','LONG_PHONE_ID','2021-06-22 19:10:25',22,'manual rejected','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwNzl6', 'some comment', ''),
(4,'00000000-0000-0000-0000-000000000001',1,'SHORT_FULLNAME_ID',21.00, 0,'2021-06-22 19:10:25','20','28','withdrawal4','SBPb2p',false,false,false,false,'100000000001','LONG_PHONE_ID','2021-06-22 19:10:25',22,'successfully sent to B2P','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwNzl7', '', ''),
(5,'00000000-0000-0000-0000-000000000001',1,'SHORT_FULLNAME_ID',21.00, 0,'2021-06-22 19:10:25','','30','withdrawal5','SBPb2p',false,false,false,false,'100000000001','LONG_PHONE_ID','2021-06-22 19:10:25',22,'auto approved','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwNz41', 'some error', ''),
(6,'00000000-0000-0000-0000-000000000001',1,'SHORT_FULLNAME_ID',21.00, 0,'2021-06-22 19:10:25','','25','withdrawal6','SBPb2p',false,false,false,false,'100000000001','LONG_PHONE_ID','2021-06-22 19:10:25',22,'precheck created','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwNz21', '', ''),
(7,'00000000-0000-0000-0000-000000000001',1,'SHORT_FULLNAME_ID',210.00, 0,'2021-06-22 19:10:25','','15','withdrawal7','SBPb2p',false,false,false,false,'100000000001','LONG_PHONE_ID','2021-06-22 19:10:25',22,'precheck created','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwNz22', '', ''),
(8,'00000000-0000-0000-0000-000000000004',4,'SHORT_FULLNAME_ID',210.00, 0,'2021-06-22 19:10:25','','16','withdrawal8','SBPb2p',false,false,false,false,'100000000001','LONG_PHONE_ID','2021-06-22 19:10:25',22,'precheck created','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwNz25', '', ''),
(9,'00000000-0000-0000-0000-000000000004',4,'SHORT_FULLNAME_ID',210.00, 0,'2021-06-22 19:10:25','','17','withdrawal9','SBPb2p',false,false,false,false,'100000000001','LONG_PHONE_ID','2021-06-22 19:10:25',22,'sent to manual check','643', '012345YyYWUwODk4ZDYwMTNiYTYwNz25', '', ''),
(10,'00000000-0000-0000-0000-000000000004',4,'SHORT_FULLNAME_ID',210.00, 0,'2021-06-22 19:10:25','','18','withdrawal10','SBPb2p',false,false,false,false,'100000000001','LONG_PHONE_ID','2021-06-22 19:10:25',22,'sent to manual check','643', '112345YyYWUwODk4ZDYwMTNiYTYwNz25', '', ''),
(11,'00000000-0000-0000-0000-000000000005',5,'SHORT_FULLNAME_ID',21000.00, 0,'2021-06-22 19:10:25','','19','withdrawal11','SBPb2p',false,false,false,false,'100000000001','LONG_PHONE_ID','2021-06-22 19:10:25',22,'precheck created','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwNz26', '', ''),
(12,'00000000-0000-0000-0000-000000000006',5,'SHORT_FULLNAME_ID',21.00, 0,'2021-06-22 19:10:25','','20','withdrawal12','SBPb2p',false,false,false,false,'100000000001','LONG_PHONE_ID','2021-06-22 19:10:25',22,'precheck created','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwNz61', '', ''),
(13,'00000000-0000-0000-0000-000000000006',6,'SHORT_FULLNAME_ID',21.00, 0,'2021-06-22 19:10:25','','21','withdrawal13','SBPb2p',false,false,false,false,'100000000001','LONG_PHONE_ID','2021-06-22 19:10:25',22,'auto approved','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwNz62', '', ''),
(14,'00000000-0000-0000-0000-000000000011',11,'FULLNAME_ID_11',100.00, 0,'2021-06-22 19:10:25','','1617600','withdrawal14','best2pay',false,false,false,false,'100000000001','LONG_PHONE_ID','2021-06-22 19:10:25',22,'error','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwN001', '', ''),
(15,'00000000-0000-0000-0000-000000000011',11,'FULLNAME_ID_11',100.00, 0,'2021-06-22 19:10:25','','1617601','withdrawal15','best2pay',false,false,false,false,'100000000001','LONG_PHONE_ID','2021-06-22 19:10:25',22,'successfully sent to B2P','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwN002', '', ''),
(16,'00000000-0000-0000-0000-000000000011',11,'FULLNAME_ID_11',100.00, 0,'2021-06-22 19:10:25','',NULL,'withdrawal16','best2pay',false,false,false,false,'100000000001','LONG_PHONE_ID','2021-06-22 19:10:25',22,'precheck created','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwN003', '', ''),
(17,'00000000-0000-0000-0000-000000000011',11,'FULLNAME_ID_11',100.00, 0,'2021-06-22 19:10:25','','1617602','withdrawal17','best2pay',false,false,false,false,'100000000001','LONG_PHONE_ID','2021-06-22 19:10:25',22,'precheck created','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwN004', '', ''),
(18,'00000000-0000-0000-0000-000000000011',11,'FULLNAME_ID_11',100.00, 0,'2021-06-22 19:10:25','','1617603','withdrawal18','best2pay',false,false,false,false,'100000000001','LONG_PHONE_ID','2021-06-22 19:10:25',22,'auto approved','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwN005', '', ''),
(19,'00000000-0000-0000-0000-000000000011',11,'FULLNAME_ID_11',100.00, 0,'2021-06-22 19:10:25','','1617604','withdrawal19','best2pay',false,false,false,false,'100000000001','LONG_PHONE_ID','2021-06-22 19:10:25',22,'sent to manual check','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwN006', '', ''),
(20,'00000000-0000-0000-0000-000000000001',1,'SHORT_FULLNAME_ID',21.00, 0,'2021-06-22 19:10:25','-1','29','withdrawal20','best2pay',false,false,false,false,'100000000001','LONG_PHONE_ID','2021-06-22 19:10:25',22,'successfully sent to B2P','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwNz24', '', ''),
(21,'00000000-0000-0000-0000-000000000001',1,'SHORT_FULLNAME_ID',21.00, 0,'2021-06-22 19:10:25','-1','32','withdrawal3','SBPb2p',false,false,false,false,'100000000001','LONG_PHONE_ID','2021-06-22 19:10:25',22,'rejected by B2P','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwNz31', 'some comment 2', ''),
(22,'00000000-0000-0000-0000-000000000002',2,'FULLNAME_ID_11',100.00, 0,'2021-06-22 19:10:24','','100','withdrawal22','best2pay',false,false,false,false,'100000000001','LONG_PHONE_ID','2021-06-22 19:10:25',22,'error','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwN101', '', 'some_pan'),
(23,'00000000-0000-0000-0000-000000000001',1,'FULLNAME_ID_11',100.00, 0,'2021-06-22 19:10:24','','101','withdrawal23','best2pay',false,false,false,false,'100000000001','LONG_PHONE_ID','2021-06-22 19:10:25',22,'error','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwN102', '', 'some_pan'),
(24,'00000000-0000-0000-0000-000000000011',11,'FULLNAME_ID_11',100.00, 0,'2021-06-22 19:10:24','','102','withdrawal24','best2pay',false,false,false,false,'100000000001','LONG_PHONE_ID','2021-06-22 19:10:25',22,'error','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwN103', '', 'some_pan')
;

ALTER SEQUENCE eats_tips_withdrawal.withdrawals_id_seq RESTART WITH 10000000;

INSERT INTO eats_tips_withdrawal.sbp_banks VALUES
('100000000001','Газпромбанк', 'Gazprombank', true, 'http://bank.image.ru'),
('100000000002','РНКО Платежный центр', 'RNKO Payment Center', false, NULL)
;
