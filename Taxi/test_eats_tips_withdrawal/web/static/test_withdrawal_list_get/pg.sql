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
  card_pan
)
VALUES
(1,'19cf3fc9-98e5-4e3d-8459-179a602bd7a2',2,'SHORT_FULLNAME_ID',20.00, 0,'2021-06-22 15:10:20+00:00','','25','withdrawal1','best2pay',false,false,false,false,'','','2021-06-22 16:10:25+00:00',22,'rejected by B2P','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwNzl1', 'some_pan1'),
(2,'19cf3fc9-98e5-4e3d-8459-179a602bd7a2',2,'SHORT_FULLNAME_ID',20.10, 10,'2021-06-22 16:10:23+00:00','','26','withdrawal2','best2pay',false,false,false,false,'','','2021-06-22 16:10:25+00:00',22,'success','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwNzl2', 'some_pan2'),
(3,'19cf3fc9-98e5-4e3d-8459-179a602bd7a2',2,'SHORT_FULLNAME_ID',20.50, 0,'2021-06-22 16:10:24+00:00','','27','withdrawal3','best2pay',false,false,false,false,'','','2021-06-22 16:10:25+00:00',22,'sent to manual check','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwNzl3', 'some_pan3'),
(4,'19cf3fc9-98e5-4e3d-8459-179a602bd7a2',2,'SHORT_FULLNAME_ID',20.20, 0,'2021-06-22 16:10:25+00:00','','28','withdrawal4','best2pay',false,false,false,false,'','','2021-06-22 16:10:25+00:00',22,'successfully sent to B2P','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwNzl4', 'some_pan4'),
(5,'19cf3fc9-98e5-4e3d-8459-179a602bd7a2',2,'SHORT_FULLNAME_ID',20.70, 20,'2021-06-22 16:10:26+00:00','','29','withdrawal5','SBPb2p',false,false,false,false,'','','2021-06-22 16:10:25+00:00',22,'success','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwNzl5', 'some_pan5'),
(6,'19cf3fc9-98e5-4e3d-8459-179a602bd7a2',2,'SHORT_FULLNAME_ID',20.00, 0,'2021-06-22 17:10:30+00:00','','30','withdrawal6','best2pay',false,false,false,false,'','','2021-06-22 16:10:25+00:00',22,'manual rejected','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwNzl6', 'some_pan6'),
(7,'19cf3fc9-98e5-4e3d-8459-179a602bd7a2',2,'SHORT_FULLNAME_ID',20.00, 0,'2021-06-22 17:10:30+00:00','','31','withdrawal6','best2pay',false,false,false,false,'','','2021-06-22 16:10:25+00:00',22,'error','643', 'D12345YyYWUwODk4ZDYwMTNiYTYwNzl7', 'some_pan7')
;
