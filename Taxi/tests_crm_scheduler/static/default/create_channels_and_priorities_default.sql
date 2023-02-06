INSERT INTO crm_scheduler.channels (name) VALUES('push') ON CONFLICT (name) DO NOTHING;
INSERT INTO crm_scheduler.channels (name) VALUES('sms') ON CONFLICT (name) DO NOTHING;
INSERT INTO crm_scheduler.channels (name) VALUES('wall') ON CONFLICT (name) DO NOTHING;
INSERT INTO crm_scheduler.channels (name) VALUES('promo_fs') ON CONFLICT (name) DO NOTHING;
INSERT INTO crm_scheduler.channels (name) VALUES('promo_card') ON CONFLICT (name) DO NOTHING;
INSERT INTO crm_scheduler.channels (name) VALUES('promo_notification') ON CONFLICT (name) DO NOTHING;

INSERT INTO crm_scheduler.channels(name) VALUES('driver_wall');
INSERT INTO crm_scheduler.channels(name) VALUES('driver_push');
INSERT INTO crm_scheduler.channels(name) VALUES('driver_sms');
INSERT INTO crm_scheduler.channels(name) VALUES('user_push');
INSERT INTO crm_scheduler.channels(name) VALUES('user_eda_sms');
INSERT INTO crm_scheduler.channels(name) VALUES('user_tags');
INSERT INTO crm_scheduler.channels(name) VALUES('eda_push');
INSERT INTO crm_scheduler.channels(name) VALUES('z_user_push');
INSERT INTO crm_scheduler.channels(name) VALUES('promo') ON CONFLICT (name) DO NOTHING;

INSERT INTO crm_scheduler.priorities (name) VALUES('low') ON CONFLICT (name) DO NOTHING;
INSERT INTO crm_scheduler.priorities (name) VALUES('default') ON CONFLICT (name) DO NOTHING;
INSERT INTO crm_scheduler.priorities (name) VALUES('high') ON CONFLICT (name) DO NOTHING;
INSERT INTO crm_scheduler.priorities (name) VALUES('very_high') ON CONFLICT (name) DO NOTHING;

INSERT INTO crm_scheduler.task_types(name) VALUES('crm_policy');
INSERT INTO crm_scheduler.task_types(name) VALUES('logs');
INSERT INTO crm_scheduler.task_types(name) VALUES('push');
INSERT INTO crm_scheduler.task_types(name) VALUES('sms');
INSERT INTO crm_scheduler.task_types(name) VALUES('wall');
INSERT INTO crm_scheduler.task_types(name) VALUES('promo_fs');
INSERT INTO crm_scheduler.task_types(name) VALUES('promo_card');
INSERT INTO crm_scheduler.task_types(name) VALUES('promo_notification');
INSERT INTO crm_scheduler.task_types(name) VALUES('sending_finished');

INSERT INTO crm_scheduler.task_types(name) VALUES('driver_wall');
INSERT INTO crm_scheduler.task_types(name) VALUES('driver_push');
INSERT INTO crm_scheduler.task_types(name) VALUES('driver_sms');
INSERT INTO crm_scheduler.task_types(name) VALUES('user_push');
INSERT INTO crm_scheduler.task_types(name) VALUES('user_eda_sms');
INSERT INTO crm_scheduler.task_types(name) VALUES('user_tags');
INSERT INTO crm_scheduler.task_types(name) VALUES('eda_push');
INSERT INTO crm_scheduler.task_types(name) VALUES('z_user_push');
INSERT INTO crm_scheduler.task_types(name) VALUES('promo') ON CONFLICT (name) DO NOTHING;
INSERT INTO crm_scheduler.task_types(name) VALUES('counter_filter') ON CONFLICT (name) DO NOTHING;


INSERT INTO crm_scheduler.runtime_locks(name) VALUES('generate_tasks_lock');

INSERT INTO crm_scheduler.emitter_task_state(lock, last_task_type_id, task_thread_emitted) VALUES(1,0,0);
