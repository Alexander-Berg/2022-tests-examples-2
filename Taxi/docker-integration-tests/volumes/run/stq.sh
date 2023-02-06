#!/usr/bin/env bash
set -e

mkdir -p /etc/yandex/taxi-stq/

if [ -f /taxi/backend/debian/changelog ]; then

    rm -f /etc/yandex/taxi-stq/*
    ln -s /taxi/backend/debian/settings.*.py /etc/yandex/taxi-stq/

    rm -rf /usr/lib/yandex/taxi-stq/*
    mkdir -p /usr/lib/yandex/taxi-stq/taxi_stq/
    cp /taxi/backend/debian/stq_runner.py /usr/lib/yandex/taxi-stq/
    ln -s /taxi/backend/debian/stq_config.py /usr/lib/yandex/taxi-stq/
    ln -s /taxi/backend/debian/twistedconfig.py /usr/lib/yandex/taxi-stq/
    ln -s /taxi/backend/taxi_stq/* /usr/lib/yandex/taxi-stq/taxi_stq/
    rm -f /usr/lib/yandex/taxi-stq/taxi_stq/blocking_setup.py
    rm -f /usr/lib/yandex/taxi-stq/taxi_stq/twisted_setup.py
    cp /taxi/backend/taxi_stq/blocking_setup.py /usr/lib/yandex/taxi-stq/taxi_stq/
    cp /taxi/backend/taxi_stq/twisted_setup.py /usr/lib/yandex/taxi-stq/taxi_stq/
    ln -s /taxi/backend/taxi_tasks /usr/lib/yandex/taxi-stq/
    ln -s /taxi/backend/taxi /usr/lib/yandex/taxi-stq/
    ln -s /etc/yandex/taxi-stq/settings.production.py \
        /usr/lib/yandex/taxi-stq/taxi_settings.py
    if [ -d /taxi/backend/submodules/stq/stq ]; then
        ln -s /taxi/backend/submodules/stq/stq /usr/lib/yandex/taxi-stq/
    fi
fi

echo "adjust
antifraud_proc
antifraud_start_proc
arrival_push
auto_compensation
billing_prepare_order_events
calc_fulfilled_subventions_notify
chat_processing
check_email
create_change_comment
done_personal_subventions_notify
move_from_expired_to_finished
newdriver_request
notify
notify_on_change
order_billing
personal_subventions_notify
process_change
promocodes_generate
promocodes_to_trust
push
send_cancelrequests
send_confirmation_email
send_messages_master
send_messages_slave
send_payment
send_report
send_sms
subventions_to_trust
svo_order_prepare_queue
update_taximeter_balance_changes
update_transactions
user_support_chat_message
zendesk_forms
zendesk_ticket" > "/etc/yandex/taxi-stq/queues_whitelist"

sed -i 's/logging.DEBUG/logging.INFO/g' /usr/lib/yandex/taxi-stq/stq_runner.py
sed -i 's/logging.DEBUG/logging.INFO/g' /usr/lib/yandex/taxi-stq/taxi_stq/blocking_setup.py
sed -i 's/logging.DEBUG/logging.INFO/g' /usr/lib/yandex/taxi-stq/taxi_stq/twisted_setup.py

/taxi/tools/run.py \
    --restart-service 9999 \
    --syslog \
    --wait \
        mongo.taxi.yandex:27017 \
        memcached.taxi.yandex:11211 \
        http://configs.taxi.yandex.net/ping \
    --run /usr/lib/yandex/taxi-py2/bin/python /usr/lib/yandex/taxi-stq/stq_runner.py
