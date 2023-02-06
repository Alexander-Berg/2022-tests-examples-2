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
(40, 2, -21,null,'pending',0,0,0,0,0,0,1624378225,0,0, '',0,0,0,0,1,0,0,0,'',0,'','','',''),
(50, 2, -21,2,'succeeded',0,0,0,1,0,0,1624378225,0,0, '',0,0,0,0,1,0,0,0,'',0,'','','','some_pan2'),
(51, 2, -21,3,'succeeded',0,0,0,1,0,0,1624378225,0,0, '',0,0,0,0,1,0,0,0,'',0,'a_some_migrated_key','','',''),
(53, 2, -21,5,'succeeded',0,0,0,1,0,0,1624378225,0,0, '',0,0,0,0,1,0,0,0,'',0,'','','',''),
(56, 2, -20,4,'succeeded',0,0,0,1,0,0,1624378225,2,1, '',0,0,0,0,1,0,0,0,'',53,'','','',''),
(54, 2, -21,6,'succeeded',0,0,0,1,0,0,1624374085,0,0, '',0,0,0,0,1,0,0,0,'',0,'','','','')

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
(21,1,'test fio',21,1624378225,0,0,40,'best2pay',0,0,'','',0,0,0,0,'','',1624378225,0,'',Null),
(22,1,'test fio',0,1624378225,0,0,41,'best2pay',1,1624378226,'why not','b2p message',0,0,0,0,'','',1624378226,0,'',Null),
(23,1,'test fio',21,1624378225,-1,1624378226,50,'best2pay',0,0,'','',0,0,0,0,'','',1624378226,0,'',Null),
(24,1,'test fio',21,1624378225,-1,1624378226,51,'best2pay',0,0,'','',0,0,0,0,'','',1624378226,0,'','a_some_migrated_key'),
(25,1,'test fio',21,1624378225,2,1624378226,53,'best2pay',0,0,'','',0,0,0,0,'','',1624378226,0,'',Null),
(26,1,'test fio',21,1624374085,0,0,54,'best2pay',0,0,'','',0,0,0,0,'','',1624378226,0,'',Null)
;
