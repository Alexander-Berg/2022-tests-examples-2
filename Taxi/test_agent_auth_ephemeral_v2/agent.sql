INSERT INTO
    callcenter_reg.agent
(yandex_uid, sip_username, reg_node, reg_status, user_socket, supervisor, reg_status_updated_at)
VALUES
 ('1000000000010001', '1000010001', 'node01', 'BadStatus', 'IP1:PORT1', null, now())
,('1000000000010002', '1000010002', null, null, null, null, now())
,('1000000000010003', '1000010003', 'node01', 'Registered', 'IP1:PORT2', null, now())
,('1000000000010004', '1000010004', 'node01', 'Registered', 'IP1:PORT3', '1000020000', now())
,('1000000000010005', '1000010005', 'node01', 'Registered', 'IP1:PORT4', '1000020001', now())
,('1000000000010006', '1000010006', 'node01', 'Registered', 'IP1:PORT5', '1000020002', now())
,('1000000000010007', '1000010007', 'node01', 'Registered', 'IP1:PORT6', '1000020003', now())
,('1000000000010008', '1000010008','node01', 'BadStatus', 'IP1:PORT1',  null, now())
,('1000000000010009', '1000010009', null, null, null, null, now())
,('1000000000010010', '1000010010', 'node01', 'Registered', 'IP1:PORT2',  null, now())
,('1000000000010011', '1000010011', 'node03', 'Registered', 'IP3:PORT2', null, '2021-12-08 12:00:00')
,('1000000000010012', '1000010012', 'node03', 'Unregistered', 'IP4:PORT2', null, now())
,('1000000000010013', '1000010013', 'node03', 'Registered', 'IP5:PORT2', null, now())
,('1000000000010014', '1000010014', 'node03', 'Unregistered', 'IP6:PORT2', null, '2021-12-08 12:00:00')
,('1000000000010015', '1000010015', 'node03', 'Registered', 'IP7:PORT1', null, '2021-12-08 12:00:01')
,('1000000000010016', '1000010016', 'node03', 'Unregistered', 'IP8:PORT1', null, '2021-12-08 12:00:01')
,('1000000000020001', '1000020001', 'node02', 'BadStatus', 'IP1:PORT1', null, now())
,('1000000000020002', '1000020002', null, null, null, null, now())
,('1000000000020003', '1000020003', 'node02', 'Registered', 'IP1:PORT2', null, now())
;
