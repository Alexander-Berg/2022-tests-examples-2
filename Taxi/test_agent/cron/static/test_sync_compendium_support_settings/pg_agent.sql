INSERT INTO agent.chatterbox_support_settings
(
    login,
    assigned_lines,
    can_choose_from_assigned_lines,
    can_choose_except_assigned_lines,
    max_chats,
    languages,
    work_off_shift,
    needs_compendium_sync
)
VALUES
('regular_login','{line_1,line_2}',TRUE,TRUE,12,'{ru,en}',TRUE, TRUE),
('login_not_for_sync','{line_1}',FALSE,FALSE,12,'{ru}',TRUE, FALSE),
('login_for_sync','{line_1}',FALSE,FALSE,12,'{ru}',TRUE, TRUE);

INSERT INTO auth_user
(id,username)
VALUES
(1,'regular_login'),
(2,'login_not_for_sync'),
(3,'login_for_sync');

INSERT INTO compendium_customuser
(
    user_ptr_id,
    max_chats_chatterbox,
    dis_tickets_off_shift,
    dismissed
)
VALUES
(1,3,FALSE,FALSE),
(2,3,FALSE,FALSE),
(3,3,TRUE,FALSE);

INSERT INTO compendium_customuser_knows_languages
(customuser_id, users_languages_id)
VALUES
(1,1),
(1,2);

INSERT INTO compendium_users_languages
(id, code)
VALUES
(1,'ru'),
(2,'en');
