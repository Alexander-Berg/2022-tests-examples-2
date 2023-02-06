INSERT INTO modx_web_users_pays (
  id,
  to_user_id,
  amount,
  transaction_id,
  transaction_status,
  transaction_pay_date,
  is_b2p_fail,
  is_apple,
  is_google,
  is_samsung,
  is_yandex,
  date_created,
  procent,
  type,
  language,
  test,
  is_blago,
  who,
  is_ecommpay,
  is_best2pay,
  best2pay_fee,
  code,
  room_id,
  comment,
  parent_id,
  idempotenceKey,
  message,
  email,
  pan
)
VALUES
(42, 2, 100,1,'pending',0,1,0,1,0,0,100,0,0, '',0,0,0,0,1,0,0,0,'',0,'','','',''),
(43, 1, 100,null,'pending',0,0,0,0,0,0,200,0,0, '',0,0,0,0,1,0,0,0,'',0,'','','',''),
(44, 2, 100,2,'pending',0,0,0,0,0,0,201,0,0, '',0,0,0,0,1,0,0,0,'',0,'','','',''),
(45, 2, 100,3,'succeeded',100,0,0,0,0,0,202,0,0, '',0,0,0,0,1,0,0,0,'',0,'','','',''),
(46, 2, 100,4,'pending',0,1,0,0,0,0,203,0,0, '',0,0,0,0,1,0,0,0,'',0,'','','',''),

(47, 2, 100,null,'pending',0,0,1,0,0,0,200,0,0, '',0,0,0,0,1,0,0,0,'',0,'','','',''),
(48, 2, 100,null,'pending',0,0,1,0,0,0,201,0,0, '',0,0,0,0,1,0,0,0,'',0,'','','',''),
(49, 2, 100,5,'succeeded',100,0,1,0,0,0,202,0,0, '',0,0,0,0,1,0,0,0,'',0,'','','',''),
(50, 2, 100,6,'pending',0,1,1,0,0,0,203,0,0, '',0,0,0,0,1,0,0,0,'',0,'','','',''),

(51, 2, 100,7,'pending',0,0,0,1,0,0,200,0,0, '',0,0,0,0,1,0,0,0,'',0,'','','',''),
(52, 2, 100,8,'pending',0,0,0,1,0,0,201,0,0, '',0,0,0,0,1,0,0,0,'',0,'','','',''),
(53, 2, 100,9,'succeeded',100,0,0,1,0,0,202,0,0, '',0,0,0,0,1,0,0,0,'',0,'','','',''),
(54, 2, 100,10,'pending',0,1,0,1,0,0,203,0,0, '',0,0,0,0,1,0,0,0,'',0,'','','',''),
(55, 2, 100,11,'pending',0,1,0,1,0,0,204,0,0, '',0,0,0,0,1,0,0,0,'',0,'','','','')
;

INSERT INTO modx_web_users_withdrawal (
  `id`,
  `user_id`,
  `fullname`,
  `sum`,
  `date_time`,
  `admin_id`,
  `transaction_date`,
  `pay_id`,
  `pay_method`,
  `cancel_admin_id`,
  `cancel_date`,
  `cancel_reason`,
  `cancel_reason_description`,
  `is_blacklist`,
  `is_one_card`,
  `is_not_from_russian`,
  `is_from_3k_pay`,
  `bank_id`,
  `target_phone_id`,
  `last_update_time`,
  `precheck_id`,
  `status`,
  `idempotency_key`
)
VALUES
(23,1,'test fio','21',12345,0,0,40,'SBPb2p',0,0,'','',0,0,0,0,'100000000001','79110000000',12345,21,'sent to manual check','D12345YyYWUwODk4ZDYwMTNiYTYwNzl3'),
(26,1,'test fio','21',12345,0,0,52,'SBPb2p',0,0,'','',0,0,0,0,'100000000001','79110000000',22345,21,'sent to manual check','D12345YyYWUwODk4ZDYwMTNiYTYwNzc1')
;
