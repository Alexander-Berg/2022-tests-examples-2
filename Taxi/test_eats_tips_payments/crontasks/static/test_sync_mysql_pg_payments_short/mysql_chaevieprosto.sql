INSERT INTO modx_web_users_pays (
  id,
  to_user_id,
  amount,
  amount_trans,
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
  pan,
  transaction_status_date
)
VALUES
(1, 2, 102.75, 2.75,1,'succeeded',0,0,0,1,0,0,2588600,0,0, '',0,0,0,0,1,0,0,0,'',0,'','','','',0),
(2, 2, 102.75, 2.75,2,'pending',0,1,0,1,0,0,2592240,0,0, '',0,0,0,0,1,0,0,0,'',0,'','','','',0),
(3, 2, 102.75, 0,3,'succeeded',0,0,0,1,0,0,2592240,0,0, '',0,0,0,0,1,0,0,0,'',0,'','','','',0),
(4, 2, 2.75, 0,NULL,'succeeded',0,0,0,1,0,0,2592240,4,0, '',0,0,0,0,1,0,0,0,'',3,'','','','',0),
(5, 2, 102.75, 2.75,4,'succeeded',0,0,1,0,0,0,2592240,0,0, '',0,0,0,0,1,0,0,0,'some comment',0,'','some message','','',0),
(6, 2, 102.75, 2.75,5,'succeeded',2592241,0,0,0,0,1,2592240,0,0, '',0,0,0,0,1,0,0,0,'some comment',0,'','some message','','',0),
(7, 2, 102.75, 2.75,6,'succeeded',2592241,0,0,0,0,1,2592240,0,0, '',0,0,0,0,1,0,0,0,'some comment',0,'','some message','','',0),
(8, 2, 102.75, 2.75,7,'succeeded',2592241,0,0,0,0,0,2592240,0,0, '',0,0,0,0,1,0,0,0,'some comment',0,'','some message','','some pan',2592242),
(9, 2, 0, 0,8,'succeeded',0,0,0,1,0,0,2592240,0,0, '',0,0,0,0,1,0,0,0,'some comment 2',0,'','some message 2','','',0),
(100, 2, 102.5, 2.5,9,'succeeded',0,0,0,1,0,0,2592240,0,0, '',0,0,0,0,1,0,0,0,'some comment 3',0,'','some message 3','','',0)
;

INSERT INTO modx_web_users_reviews (
  id,
  user_id,
  user_sub_id,
  star,
  review,
  photo,
  is_send_phone,
  service,
  quality,
  clean,
  atmosphere,
  speed,
  good_atmosphere,
  delicious_food,
  delightful_service,
  good_speed,
  master_gold_hand,
  pay_page_type,
  date_time,
  order_id
) VALUES
(101,2,0,5,'Текст отзыва','',0,0,0,0,0,0,0,0,0,0,0,0,2592240,null),
(102,2,0,5,'Текст отзыва','',0,0,0,0,0,0,0,0,0,0,0,0,2592240,null),
(103,2,0,5,'Текст отзыва','',0,0,0,0,0,0,0,0,0,0,0,0,2592240,null),
(104,2,0,5,'Текст отзыва','',0,0,0,0,0,0,0,0,0,0,0,0,2592240,null),
(105,2,0,5,'Текст отзыва','',0,0,0,0,0,0,0,0,0,0,0,0,2592240,null),
(106,2,0,5,'Текст отзыва','',0,0,0,0,0,0,0,0,0,0,0,0,2592240,null),
(107,2,0,5,'Текст отзыва','',0,0,0,0,0,0,0,0,0,0,0,0,2592240,null);
