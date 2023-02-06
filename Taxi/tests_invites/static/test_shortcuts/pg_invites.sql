DO $$
DECLARE
    -- clubs
    club_go_id          UUID := '00000000-11111111-00000000-00000000';
    club_fight_id       UUID := '00000000-22222222-00000000-00000000';
    -- members
    club_go_ivan_id     UUID := '00000000-11111111-11111111-00000000';
    club_go_anna_id     UUID := '00000000-11111111-22222222-00000000';
    club_go_karl_id     UUID := '00000000-11111111-33333333-00000000';
    club_go_lora_id     UUID := '00000000-11111111-44444444-00000000';
    club_go_mark_id     UUID := '00000000-11111111-55555555-00000000';
    club_fight_ivan_id  UUID := '00000000-22222222-11111111-00000000';
BEGIN

    INSERT INTO invites.clubs (id, name, is_active) VALUES
    (club_go_id,    'yandex_go',    true),
    (club_fight_id, 'fight_club',   false);

    INSERT INTO invites.members (id, club_id, phone_id) VALUES 
    (club_go_ivan_id,       club_go_id,     'phone_id_ivan'),
    (club_go_anna_id,       club_go_id,     'phone_id_anna'),
    (club_go_karl_id,       club_go_id,     'phone_id_karl'),
    (club_go_lora_id,       club_go_id,     'phone_id_lora'),
    (club_go_mark_id,       club_go_id,     'phone_id_mark'),
    (club_fight_ivan_id,    club_fight_id,  'phone_id_ivan');

    INSERT INTO invites.codes (id, code, creator_id, consumer_id) VALUES 
    -- go: ivan codes
    ('00000000-11111111-11111111-00000000', 'code_go_for_ivan_1', club_go_ivan_id, null),
    ('00000000-11111111-11111111-11111111', 'code_go_for_ivan_2', club_go_ivan_id, club_go_anna_id),
    ('00000000-11111111-11111111-22222222', 'code_go_for_ivan_3', club_go_ivan_id, null),
    ('00000000-11111111-11111111-33333333', 'code_go_for_ivan_4', club_go_ivan_id, null),
    ('00000000-11111111-11111111-44444444', 'code_go_for_ivan_5', club_go_ivan_id, null),
    -- go: anna codes
    ('00000000-11111111-22222222-00000000', 'code_go_for_anna_1', club_go_anna_id, club_go_karl_id),
    ('00000000-11111111-22222222-11111111', 'code_go_for_anna_2', club_go_anna_id, club_go_lora_id),
    ('00000000-11111111-22222222-22222222', 'code_go_for_anna_3', club_go_anna_id, club_go_mark_id),
    -- fight: ivan codes
    ('00000000-22222222-11111111-00000000', 'code_fight_for_ivan_1', club_fight_ivan_id, null),
    ('00000000-22222222-11111111-11111111', 'code_fight_for_ivan_2', club_fight_ivan_id, null),
    ('00000000-22222222-11111111-22222222', 'code_fight_for_ivan_3', club_fight_ivan_id, null);

END $$;
