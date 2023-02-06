INSERT INTO alert_manager.notification_options (name, logins, statuses, type, repo_meta)
VALUES ('telegram_option1', ARRAY['d1mbas']::TEXT[], ARRAY[('OK', 'WARN')]::alert_manager.no_status_t[], 'telegram', ('', '', '')::alert_manager.repo_meta_t)
;
