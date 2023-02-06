INSERT INTO eats_tips_withdrawal.withdrawals (
  id,
  partner_id,
  b2p_user_id,
  fullname_id,
  amount,
  fee,
  create_date,
  finish_date,
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
  legacy,
  card_pan
)
VALUES
(1,'00000000-0000-0000-0000-000000000002',2,'SHORT_FULLNAME_ID',21.00, 0,'2021-06-22 19:10:25', Null,'','25','withdrawal1','best2pay',false,false,false,false,'','','2021-06-22 19:10:25', null,'precheck created','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwNzlh', false, 'some_pan'),
(3,'00000000-0000-0000-0000-000000000001',1,'SHORT_FULLNAME_ID',21.00, 0,'2021-06-22 19:10:25', '2021-06-22 19:10:26','1','26','withdrawal3','best2pay',false,false,false,false,'','','2021-06-22 19:10:26', null,'manual rejected','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwNzl6', false, 'some_pan'),
(4,'00000000-0000-0000-0000-000000000001',1,'SHORT_FULLNAME_ID',21.00, 20,'2021-06-22 19:10:25','2021-06-22 19:10:26','-1','27','withdrawal4','best2pay',false,false,false,false,'','','2021-06-22 19:10:26', null,'successfully sent to B2P','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwNzl7', false, 'some_pan'),
(5,'00000000-0000-0000-0000-000000000001',1,'SHORT_FULLNAME_ID',21.00, 0,'2021-06-22 19:10:25','2021-06-22 19:10:26','-1','3','withdrawal5','best2pay',false,false,false,false,'','','2021-06-22 19:10:26', null,'success','643', 'a_some_migrated_key', false, 'some_pan'),
(7,'00000000-0000-0000-0000-000000000001',1,'SHORT_FULLNAME_ID',21.00, 20,'2021-06-22 19:10:25','2021-06-22 19:10:26','2','5','53','best2pay',false,false,false,false,'','','2021-06-22 19:10:26', null,'success','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwNzl9', true, ''),
(6,'00000000-0000-0000-0000-000000000001',1,'SHORT_FULLNAME_ID',21.00, 0,'2021-06-22 18:00:25','2021-06-22 19:10:26','3','30','withdrawal6','SBPb2p',false,false,false,false,'100000000001','LONG_PHONE_ID','2021-06-22 19:10:26',22,'success','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwNzl8', false, '')

;
