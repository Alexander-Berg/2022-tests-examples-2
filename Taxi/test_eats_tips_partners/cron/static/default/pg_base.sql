ALTER SEQUENCE alias_sequence RESTART WITH 3000000;

INSERT INTO eats_tips_partners.role (slug, title)
VALUES
('recipient', 'recipient'),
('admin', 'admin'),
('unknown', 'unknown role')
;


INSERT INTO eats_tips_partners.mysql_cursor (slug, cursor)
VALUES
('user_cursor', 0),
('user_role_cursor', 0)
;
