INSERT INTO crm_policy.channels (name) VALUES('fullscreen') ON CONFLICT (name) DO NOTHING;
INSERT INTO crm_policy.channels (name) VALUES('push') ON CONFLICT (name) DO NOTHING;
INSERT INTO crm_policy.channels (name) VALUES('sms') ON CONFLICT (name) DO NOTHING;
INSERT INTO crm_policy.channels (name) VALUES('wall') ON CONFLICT (name) DO NOTHING;
INSERT INTO crm_policy.channels (name) VALUES('promo_fs') ON CONFLICT (name) DO NOTHING;
INSERT INTO crm_policy.channels (name) VALUES('promo_card') ON CONFLICT (name) DO NOTHING;
INSERT INTO crm_policy.channels (name) VALUES('promo_notification') ON CONFLICT (name) DO NOTHING;
INSERT INTO crm_policy.channels (name) VALUES('email') ON CONFLICT (name) DO NOTHING;
INSERT INTO crm_policy.round_tables (head) VALUES(0);
