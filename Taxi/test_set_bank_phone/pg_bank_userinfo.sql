INSERT INTO bank_userinfo.phones (
  phone_id,
  phone
)
VALUES (
  'b97acb1c-7441-4383-9db2-4e40eea48317',
  '+79111111111'
), (
  '5d54349b-2de3-49b3-8f1e-5b2bea8e8766',
  '+79111111112'
), (
  'c36e1046-7a22-4f9f-92cb-49b778b0860a',
  '+79111111113'
), (
  'c34510c3-52b5-4a8c-bbce-0f73e21f45bc',
  '+79111111117'
), (
  '973db1db-2dea-424f-a55f-111111111111',
  '+79111111118'
), (
   '973db1db-2dea-424f-2222-111111111111',
   '+79111111119'
), (
   '973db1db-2dea-424f-3333-111111111111',
   '+79111111120'
);

INSERT INTO bank_userinfo.buids (
  bank_uid,
  yandex_uid,
  phone_id,
  status
)
VALUES (
  '8c9df3f9-1942-4899-bf72-f31663f20733',
  '111111',
  'b97acb1c-7441-4383-9db2-4e40eea48317',
  'NEW'
), (
  'b7fcb9d5-19ee-4c2f-9cb1-67d3aa1f5971',
  '111112',
  '5d54349b-2de3-49b3-8f1e-5b2bea8e8766',
  'FINAL'
), (
  '84e91c04-9279-4a07-a6d9-dd8369c82148',
  '111113',
  'c36e1046-7a22-4f9f-92cb-49b778b0860a',
  'PHONE_CONFIRMED'
), (
  '9abbd664-4195-449d-92d4-087ca97daf30',
  '111114',
  NULL,
  'NEW'
), (
  '6c6f2aca-4507-4733-b3d4-9669fe8a4b23',
  '111115',
  NULL,
  'PHONE_CONFIRMED'
), (
  'a1fed95a-eaf7-4ca3-92b4-5f87655d7255',
  '111116',
  NULL,
  'FINAL'
), (
  'f1a69dcc-9b49-41df-84d2-7df5a64ad270',
  '111117',
  NULL,
  'NEW'
), (
  '41042ac5-8728-4511-8071-ba4b1e19968e',
  '111118',
  NULL,
  'NEW'
),(
  '973db1db-2dea-424f-a55f-228a0c2c8002',
  '111119',
  NULL,
  'NEW'
),
(
  '973db1db-2dea-424f-a55f-111111111111',
  '111120',
  NULL,
  'NEW'
),(
   '8c9df3f9-1942-4899-1111-f31663f20733',
   '111121',
   '973db1db-2dea-424f-2222-111111111111',
   'CHANGING_PHONE'
);
