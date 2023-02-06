INSERT INTO eats_tips_withdrawal.sbp_banks VALUES
('100000000001','Газпромбанк', 'Gazprombank', true, 'http://bank.image.ru');

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
  idempotency_key
)
VALUES
(1,'00000000-0000-0000-0000-000000000002',2,'SHORT_FULLNAME_ID',21.00, 0,'2021-06-22 19:10:25','','25','withdrawal1','SBPb2p',false,false,false,false,'100000000001','LONG_PHONE_ID','2021-06-22 19:10:25',22,'precheck created','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwNzlh'),
(2,'00000000-0000-0000-0000-000000000001',1,'SHORT_FULLNAME_ID',21.00, 0,'2021-06-22 19:10:25','','26','withdrawal2','SBPb2p',false,false,false,false,'100000000001','LONG_PHONE_ID','2021-06-22 19:10:25',22,'sent to manual check','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwNzl3'),
(3,'00000000-0000-0000-0000-000000000001',1,'SHORT_FULLNAME_ID',21.00, 0,'2021-06-22 19:10:25','','27','withdrawal3','SBPb2p',false,false,false,false,'100000000001','LONG_PHONE_ID','2021-06-22 19:10:25',22,'manual rejected','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwNzl6'),
(4,'00000000-0000-0000-0000-000000000001',1,'SHORT_FULLNAME_ID',21.00, 0,'2021-06-22 19:10:25','','28','withdrawal4','SBPb2p',false,false,false,false,'100000000001','LONG_PHONE_ID','2021-06-22 19:10:25',22,'successfully sent to B2P','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwNzl7'),
(5,'00000000-0000-0000-0000-000000000001',1,'SHORT_FULLNAME_ID',21.00, 0,'2021-06-22 19:10:25','','29','withdrawal5','SBPb2p',false,false,false,false,'100000000001','LONG_PHONE_ID','2021-06-22 19:10:25',22,'auto approved','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwNz41'),
(6,'00000000-0000-0000-0000-000000000002',1,'SHORT_FULLNAME_ID',21.00, 0,'2021-06-22 19:10:25','','30','withdrawal6','SBPb2p',false,false,false,false,'100000000001','LONG_PHONE_ID','2021-06-22 19:10:25',22,'precheck created','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwNzlq'),
(7,'00000000-0000-0000-0000-000000000002',1,'SHORT_FULLNAME_ID',21.00, 0,'2021-06-22 19:10:25','','31','withdrawal7','SBPb2p',false,false,false,false,'100000000001','LONG_PHONE_ID','2021-06-22 19:10:25',22,'auto approved','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwNzlw'),
(14,'00000000-0000-0000-0000-000000000011',11,'FULLNAME_ID_11',100.00, 0,'2021-06-22 19:10:25','','1617602','withdrawal14','best2pay',false,false,false,false,'100000000001','LONG_PHONE_ID','2021-06-22 19:10:25',22,'error','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwN001'),
(16,'00000000-0000-0000-0000-000000000011',11,'FULLNAME_ID_11',100.00, 0,'2021-06-22 19:10:25','',NULL,'withdrawal16','best2pay',false,false,false,false,'100000000001','LONG_PHONE_ID','2021-06-22 19:10:25',22,'precheck created','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwN003'),
(17,'00000000-0000-0000-0000-000000000011',11,'FULLNAME_ID_11',100.00, 0,'2021-06-22 19:10:25','',NULL,'withdrawal17','best2pay',false,false,false,false,'100000000001','LONG_PHONE_ID','2021-06-22 19:13:25',22,'precheck created','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwN004'),
(18,'00000000-0000-0000-0000-000000000011',11,'FULLNAME_ID_11',100.00, 0,'2021-06-22 19:10:25','','1617603','withdrawal18','best2pay',false,false,false,false,'100000000001','LONG_PHONE_ID','2021-06-22 19:10:25',22,'auto approved','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwN005')
;
