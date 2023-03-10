INSERT INTO modx_web_user_attributes (
    id,
    date_reg,
    internalKey,
    fullname,
    name_small,
    photo,
    phone,
    blocked,
    interface,
    trans_guest_block,
    trans_guest,
    pay_page_option,
    pay_page_bw,
    proc1,
    proc2,
    proc3,
    proc4,
    proc_all,
    price1,
    price2,
    price3,
    price4,
    price_all,
    show_name,
    saving_up_for,
    b2p_block_mcc,
    best2pay_card_token
) VALUES
(1,0, 1, 'нормальный', '', 'photo1', '', 0, 'restaurant', 1, 0, 1, 0, 5, 7, 10, 15, 0, 50, 100, 300, 500, 0, 0, 'почку', 0, ''),
(2,0, 2, 'заблоченный', '', '', '', 1, 'restaurant', 1, 0, 2, 0, 5, 7, 10, 15, 0, 50, 100, 300, 500, 0, 0, '', 0, 'some_card_token'),
(3,0, 3, 'кафе', 'админ кафе', 'photo2', '', 0, 'restaurant', 1, 2, 2, 1, 5, 7, 10, 15, 10, 25, 100, 300, 500, 1000, 1, '', 0, ''),
(4,0, 4, '', 'юзер кафе без имени', '', '', 0, 'restaurant', 1, 0, 0, 0, 0, 0, 0, 0, 0, 50, 100, 300, 500, 0, 0, '', 0, ''),
(5, 1633612189, 5, 'заблоченный юзер кафе', '', '', '', 1, 'restaurant', 1, 0, 0, 0, 5, 7, 10, 15, 0, 50, 100, 300, 500, 0, 0, '', 0, 'some_card_token'),
(6,0, 6, '', '', '', 'юзер кафе без имени с телефоном', 0, 'restaurant', 1, 0, 0, 0, 5, 7, 10, 15, 0, 50, 100, 300, 500, 0, 0, '', 0, ''),
(7,0, 7, 'отель', 'админ отеля', '', '', 0, 'hotel', 1, 1, 1, 0, 10, 14, 20, 30, 0, 50, 100, 300, 500, 0, 0, '', 0, ''),
(8,0, 8, 'горничная в отеле', '', '', '', 0, 'hotel', 1, 0, 0, 0, 5, 7, 10, 15, 0, 50, 100, 300, 500, 0, 0, '', 0, ''),
(9,0, 9, 'номер в отеле', '', '', '', 0, 'hotel', 1, 0, 0, 0, 5, 7, 10, 15, 0, 50, 100, 300, 500, 0, 0, '', 0, ''),
(10,0, 10, 'ещё кафе', 'админ второго кафе', '', '', 0, 'restaurant', 1, 0, 0, 0, 5, 7, 10, 15, 0, 50, 100, 300, 500, 0, 0, '', 0, ''),
(11,0, 11, 'официант', 'официант второго кафе', '', '', 0, 'restaurant', 1, 0, 0, 0, 5, 7, 10, 15, 0, 50, 100, 300, 500, 0, 0, '', 0, 'some_card_token'),
(12,0, 12, 'суперадмин кафе', '', '', '', 0, 'restaurant', 1, 0, 0, 0, 5, 7, 10, 15, 0, 50, 100, 300, 500, 0, 0, '', 0, ''),
(13,0, 13, 'кафе без суперадмина', 'админ кафе', '', '', 0, 'restaurant', 1, 0, 1, 1, 5, 7, 10, 15, 5, 50, 100, 300, 500, 0, 1, '', 0, ''),
(14,0, 14, 'ещё официант', 'официант кафе без суперадмина', '', '', 0, 'restaurant', 1, 0, 0, 0, 5, 7, 10, 15, 0, 50, 100, 300, 500, 0, 0, '', 0, ''),
(15,0, 15, 'суперадмин ресторана', '', '', '', 0, 'restaurant', 1, 0, 0, 0, 5, 7, 10, 15, 0, 50, 100, 300, 500, 0, 0, '', 0, ''),
(16,0, 16, 'ресторан', 'админ ресторана', '', '', 0, 'restaurant', 1, 0, 1, 1, 5, 7, 10, 15, 5, 50, 100, 300, 500, 0, 1, '', 0, ''),
(17,0, 17, 'официант', 'официант ресторана', '', '', 0, 'restaurant', 1, 0, 0, 0, 5, 7, 10, 15, 0, 50, 100, 300, 500, 0, 0, '', 0, ''),
(18,0, 18, 'официант', 'официант ресторана и второго кафе', '', '', 0, 'restaurant', 1, 0, 0, 0, 5, 7, 10, 15, 0, 50, 100, 300, 500, 0, 0, '', 0, ''),
(19,0, 19, 'официант', 'скрытый официант кафе', '', '', 0, 'restaurant', 1, 0, 0, 0, 5, 7, 10, 15, 0, 50, 100, 300, 500, 0, 0, '', 0, ''),
(20,0, 20, 'админ системы', 'админ системы', '', '', 0, 'restaurant', 1, 0, 0, 0, 5, 7, 10, 15, 0, 50, 100, 300, 500, 0, 0, '', 0, ''),
(27,0, 27, 'админ системы2', 'админ системы2', '', '', 0, 'restaurant', 1, 0, 0, 0, 5, 7, 10, 15, 0, 50, 100, 300, 500, 0, 0, '', 0, '')
;

INSERT INTO modx_web_users_org (
    id,
    user_id,
    to_user_id,
    status,
    show_in_menu
) VALUES
(1, 3, 3, 1, 1),
(2, 3, 4, 1, 1),
(3, 3, 5, 1, 1),
(4, 3, 6, 1, 1),
(5, 9, 8, 1, 1),
(6, 10, 11, 1, 1),
(7, 13, 14, 1, 1),
(8, 16, 17, 1, 1),
(9, 16, 18, 1, 1),
(10, 10, 18, 1, 1),
(11, 3, 19, 1, 0)
;

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
-- error
(70, 11, -100,1617604,'succeeded',0,1,0,1,0,0,100,0,0, '',0,0,0,0,1,0,0,0,'',0,'','','',''),
-- precheck only
(71, 11, -100,null,'pending',0,1,0,1,0,0,100,0,0, '',0,0,0,0,1,0,0,0,'',0,'','','',''),
(72, 11, -1,null,'succeeded',100,1,0,1,0,0,100,2,1, '',0,0,0,0,1,0,0,0,'',71,'','','',''),
(73, 3719, 1,null,'succeeded',100,1,0,1,0,0,100,2,0, '',0,0,11,0,1,0,0,0,'',71,'','','',''),
(74, 3719, -1,null,'succeeded',100,1,0,1,0,0,100,2,1, '',0,0,11,0,1,0,0,0,'',71,'','','',''),
-- precheck + order id(registered order) | manual | auto approved
(81, 11, -100,1617603,'pending',0,1,0,1,0,0,100,0,0, '',0,0,0,0,1,0,0,0,'',0,'','','',''),
(82, 11, -1,null,'succeeded',100,1,0,1,0,0,100,2,1, '',0,0,0,0,1,0,0,0,'',81,'','','',''),
(83, 3719, 1,null,'succeeded',100,1,0,1,0,0,100,2,0, '',0,0,11,0,1,0,0,0,'',81,'','','',''),
(84, 3719, -1,null,'succeeded',100,1,0,1,0,0,100,2,1, '',0,0,11,0,1,0,0,0,'',81,'','','',''),
-- success
(91, 11, -100,1,'succeeded',101,1,0,1,0,0,100,0,0, '',0,0,0,0,1,0,0,0,'',0,'','','',''),
(92, 11, -1,null,'succeeded',100,1,0,1,0,0,100,2,1, '',0,0,0,0,1,0,0,0,'',91,'','','',''),
(93, 3719, 1,null,'succeeded',100,1,0,1,0,0,100,2,0, '',0,0,11,0,1,0,0,0,'',91,'','','',''),
(94, 3719, -1,null,'succeeded',100,1,0,1,0,0,100,2,1, '',0,0,11,0,1,0,0,0,'',91,'','','',''),
--
(34, 1, -200,25,'pending',0,1,0,1,0,0,100,0,0, '',0,0,0,0,1,0,0,0,'',0,'','','',''),
(35, 6, 4000,125,'succeeded',1633612189,1,0,1,0,0,100,0,0, '',0,0,0,0,1,0,0,0,'',22,'','','',''),
(36, 5, 4000,126,'succeeded',1633612189,1,0,1,0,0,100,0,0, '',0,0,0,0,1,0,0,0,'',22,'','','','1234567890123456'),
(37, 5, 3,127,'succeeded',1633612189,1,0,1,0,0,100,0,0, '',0,0,0,0,1,0,0,0,'',22,'','','','1234567890123456'),
(38, 5, 3,128,'succeeded',1633612189,1,0,1,0,0,100,0,0, '',0,0,0,0,1,0,0,0,'',22,'','','','1234567890123456'),
(39, 5, 3,129,'succeeded',1633612189,1,0,1,0,0,100,0,0, '',0,0,0,0,1,0,0,0,'',22,'','','','1234567890123456'),
(40, 1, -3,130,'pending',0,1,0,1,0,0,100,0,0, '',0,0,0,0,1,0,0,0,'',22,'','','',''),
(41, 1, 3,131,'pending',0,1,0,1,0,0,100,2,0, '',0,0,0,0,1,0,0,0,'',40,'','','',''),
(52, 1, -3,28,'pending',0,1,0,1,0,0,100,0,0, '',0,0,0,0,1,0,0,0,'',0,'','','',''),
(53, 1, 3,132,'pending',0,1,0,1,0,0,100,2,0, '',0,0,0,0,1,0,0,0,'',52,'','','',''),
(54, 1, -3,29,'pending',0,1,0,1,0,0,100,0,0, '',0,0,0,0,1,0,0,0,'',0,'','','',''),
(55, 1, 3,133,'pending',0,1,0,1,0,0,100,2,0, '',0,0,0,0,1,0,0,0,'',54,'','','',''),
(56, 1, -3,26,'pending',0,1,0,1,0,0,100,0,0, '',0,0,0,0,1,0,0,0,'',0,'','','',''),
(57, 1, 3,134,'pending',0,1,0,1,0,0,100,2,0, '',0,0,0,0,1,0,0,0,'',56,'','','',''),
(58, 1, -3,30,'pending',0,1,0,1,0,0,100,0,0, '',0,0,0,0,1,0,0,0,'',0,'','','',''),
(59, 1, 3,138,'pending',0,1,0,1,0,0,100,2,0, '',0,0,0,0,1,0,0,0,'',58,'','','',''),
(60, 1, -3,31,'pending',0,1,0,1,0,0,100,0,0, '',0,0,0,0,1,0,0,0,'',0,'','','',''),
(61, 1, 3,139,'pending',0,1,0,1,0,0,100,2,0, '',0,0,0,0,1,0,0,0,'',60,'','','',''),
(62, 1, -3,27,'pending',0,1,0,1,0,0,100,0,0, '',0,0,0,0,1,0,0,0,'',0,'','','',''),
(63, 1, 3,140,'pending',0,1,0,1,0,0,100,2,0, '',0,0,0,0,1,0,0,0,'',62,'','','',''),
(64, 1, -3,141,'pending',0,1,0,1,0,0,100,0,0, '',0,0,0,0,1,0,0,0,'',0,'','','',''),
(65, 1, 3,142,'pending',0,1,0,1,0,0,100,2,0, '',0,0,0,0,1,0,0,0,'',64,'','','',''),
(26, 2, 3,143,'pending',0,1,0,1,0,0,100,2,0, '',0,0,0,0,1,0,0,0,'',22,'','','',''),
(25, 3719, -3,144,'pending',0,1,0,1,0,0,100,2,0, '',0,0,0,0,1,0,0,0,'',22,'','','',''),
(24, 3719, -1,145,'pending',0,1,0,1,0,0,100,3,0, '',0,0,0,0,1,0,0,0,'',22,'','','',''),
(23, 3719, 10,146,'pending',0,1,0,1,0,0,100,4,0, '',0,0,0,0,1,0,0,0,'',22,'','','',''),
(22, 2, -100,147,'pending',0,1,0,1,0,0,100,0,0, '',0,0,0,0,1,0,0,0,'',0,'','','',''),
(21, 1, -21000,148,'pending',0,1,0,1,0,0,100,0,0, '',0,0,0,0,1,0,0,0,'',0,'','','',''),
(20, 1, 3,149,'pending',0,1,0,1,0,0,100,2,0, '',0,0,0,0,1,0,0,0,'',21,'','','',''),
(42, 2, -100,150,'pending',0,1,0,1,0,0,100,0,0, '',0,0,0,0,1,0,0,0,'',0,'','','','')
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
(6,11,'FULLNAME_ID_11','100',12345,0,0,81,'best2pay',0,0,'','',0,0,0,0,'','',12345,0,'sent to manual check','D12345YyYWUwODk4ZDYwMTNiYTYwN006'),
(7,11,'FULLNAME_ID_11','100',12345,0,0,81,'best2pay',0,0,'','',0,0,0,0,'','',12345,0,'auto approved','D12345YyYWUwODk4ZDYwMTNiYTYwN005'),
(8,11,'FULLNAME_ID_11','100',12345,0,0,81,'best2pay',0,0,'','',0,0,0,0,'','',12345,0,'precheck created','D12345YyYWUwODk4ZDYwMTNiYTYwN004'),
(9,11,'FULLNAME_ID_11','100',12345,0,0,71,'best2pay',0,0,'','',0,0,0,0,'','',12345,0,'precheck created','D12345YyYWUwODk4ZDYwMTNiYTYwN003'),
(10,11,'FULLNAME_ID_11','100',12345,0,100,91,'best2pay',0,0,'','',0,0,0,0,'','',12345,0,'successfully sent to B2P','D12345YyYWUwODk4ZDYwMTNiYTYwN002'),
(11,11,'FULLNAME_ID_11','100',12345,0,0,70,'best2pay',0,100,'some','',0,0,0,0,'','',12345,0,'error','D12345YyYWUwODk4ZDYwMTNiYTYwN001'),
(12,6,'test fio','10',12345,0,0,40,'SBPb2p',0,0,'','',0,0,0,0,'100000000001','79110000000',12345,21,'auto approved','D12345YyYWUwODk4ZDYwMTNiYTYwNz62'),
(13,6,'test fio','10',12345,0,0,40,'SBPb2p',0,0,'','',0,0,0,0,'100000000001','79110000000',12345,21,'precheck created','D12345YyYWUwODk4ZDYwMTNiYTYwNz61'),
(14,5,'test fio','21000',12345,0,0,21,'SBPb2p',0,0,'','',0,0,0,0,'100000000001','79110000000',12345,21,'precheck created','D12345YyYWUwODk4ZDYwMTNiYTYwNz26'),
(15,4,'test fio','200',12345,0,0,40,'SBPb2p',0,0,'','',0,0,0,0,'100000000001','79110000000',12345,21,'precheck created','D12345YyYWUwODk4ZDYwMTNiYTYwNz25'),
(16,4,'test fio','200',12345,0,0,40,'SBPb2p',0,0,'','',0,0,0,0,'100000000001','79110000000',12345,21,'sent to manual check','D12345YyYWUwODk4ZDYwMTNiYTYwNz24'),
(17,4,'test fio','200',12345,0,0,40,'SBPb2p',0,0,'','',0,0,0,0,'100000000001','79110000000',12345,21,'sent to manual check','D12345YyYWUwODk4ZDYwMTNiYTYwNz23'),
(18,1,'test fio','200',12345,0,0,34,'SBPb2p',0,0,'','',0,0,0,0,'100000000001','79110000000',12345,21,'precheck created','D12345YyYWUwODk4ZDYwMTNiYTYwNz22'),
(19,1,'test fio','21',12345,0,0,40,'SBPb2p',0,0,'','',0,0,0,0,'100000000001','79110000000',12345,21,'precheck created','D12345YyYWUwODk4ZDYwMTNiYTYwNz21'),
(20,1,'test fio','21',12345,0,0,40,'SBPb2p',0,0,'','',0,0,0,0,'100000000001','79110000000',12345,21,'auto approved','D12345YyYWUwODk4ZDYwMTNiYTYwNz41'),
(21,1,'test fio','21',12345,0,0,40,'SBPb2p',0,0,'','',0,0,0,0,'100000000001','79110000000',12345,21,'successfully sent to B2P','D12345YyYWUwODk4ZDYwMTNiYTYwNzl7'),
(22,1,'test fio','21',12345,0,0,40,'SBPb2p',0,0,'','',0,0,0,0,'100000000001','79110000000',12345,21,'manual rejected','D12345YyYWUwODk4ZDYwMTNiYTYwNzl6'),
(23,1,'test fio','21',12345,0,0,40,'SBPb2p',0,0,'','',0,0,0,0,'100000000001','79110000000',12345,21,'sent to manual check','D12345YyYWUwODk4ZDYwMTNiYTYwNzl3'),
(24,1,'test fio','21',12345,0,0,40,'SBPb2p',0,0,'','',0,0,0,0,'100000000001','79110000000',12345,21,'not SBP','D12345YyYWUwODk4ZDYwMTNiYTYwNzl0'),
(25,2,'SHORT_FULLNAME_ID','21',12345,0,0,40,'SBPb2p',0,0,'','',0,0,0,0,'100000000001','LONG_PHONE_ID',12345,22,'precheck created','D12345YyYWUwODk4ZDYwMTNiYTYwNzlh'),
(26,1,'test fio','21',12345,0,0,52,'SBPb2p',0,0,'','',0,0,0,0,'100000000001','79110000000',12345,21,'sent to manual check','D12345YyYWUwODk4ZDYwMTNiYTYwNzc1'),
(27,2,'test fio','21',12345,0,0,54,'SBPb2p',0,0,'','',0,0,0,0,'100000000001','79110000000',12345,22,'precheck created','D12345YyYWUwODk4ZDYwMTNiYTYwNzc2'),
(28,5,'test fio','21',12345,0,0,56,'SBPb2p',0,0,'','',0,0,0,0,'100000000001','79110000000',12345,22,'auto approved','D12345YyYWUwODk4ZDYwMTNiYTYwNzc3'),
(29,2,'test fio','21',12345,-1,0,58,'SBPb2p',0,0,'','',0,0,0,0,'100000000001','79110000000',12345,22,'success','D12345YyYWUwODk4ZDYwMTNiYTYwNzc4'),
(30,2,'test fio','21',12345,20,0,60,'SBPb2p',0,0,'','',0,0,0,0,'100000000001','79110000000',12345,22,'successfully sent to B2P','D12345YyYWUwODk4ZDYwMTNiYTYwNzc5'),
(31,2,'test fio','21',12345,0,0,62,'SBPb2p',-1,0,'','',0,0,0,0,'100000000001','79110000000',12345,22,'rejected by B2P','D12345YyYWUwODk4ZDYwMTNiYTYwNzc6'),
(32,2,'test fio','21',12345,0,0,64,'SBPb2p',99,0,'','',0,0,0,0,'100000000001','79110000000',12345,22,'manual rejected','D12345YyYWUwODk4ZDYwMTNiYTYwNzc7')
;
