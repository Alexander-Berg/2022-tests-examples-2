INSERT INTO eats_restapp_menu.pictures(
    avatarnica_identity,
    partner_id,
    place_id,
    origin_id,
    menu_revision,
    status,
    updated_at,
    created_at
)
VALUES
('123/1234',1,111,'123-456','1q2w3e','deleted',NOW(),NOW()),
('123/1234',1,112,'123-456','1q2w3e','deleted',NOW()+interval '1 year',NOW()),
('123/1234',1,112,'123-457','1q2w3e','approved',NOW(),NOW()),
('123/1235',1,111,'123-456','1q2w3e','deleted',NOW(),NOW()),
('123/1235',1,112,'123-456','1q2w3e','deleted',NOW(),NOW()),
('123/1235',1,112,'123-457','1q2w3e','approved',NOW(),NOW()),
('123/1236',1,112,'123-458','1q2w3e','approved',NOW(),NOW()),
('123/1236',1,112,'123-459','1q2w3e','approved',NOW(),NOW()),
('123/1237',1,111,'123-456','1q2w3e','deleted',NOW(),NOW()),
('123/1237',1,112,'123-456','1q2w3e','deleted',NOW(),NOW());
