insert into passenger_profile.profile (
    yandex_uid, brand, rating, first_name)
values
-- should be updated
('1', 'yataxi',4.89, ''),
('2', 'yataxi',4.89, ''),
('3', 'yataxi',4.89, ''),
('4', 'yataxi',4.89, ''),
-- should not be updated because the name is set
('5', 'yataxi',4.89, 'Мишка'),
('6', 'yataxi',4.89, 'Мишка'),
-- should not be updated because the app is different
('1', 'yauber', 4.91, 'Михаил'),
('2', 'yauber', 4.91, 'Михаил'),
('3', 'yauber', 4.91, 'Михаил'),
('4', 'yauber', 4.91, 'Михаил'),
('5', 'yauber', 4.91, 'Михаил'),
('6', 'yauber', 4.91, 'Михаил'),
-- uids 7 and 8 should be inserted as new profiles

-- should not be updated because uids are not bound to 1
('9', 'yataxi', 5.00, 'Алексей'),
('10', 'yataxi', 5.00, 'Алексей')
