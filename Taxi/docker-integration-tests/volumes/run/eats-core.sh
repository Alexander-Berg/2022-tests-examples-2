#!/usr/bin/env bash

timestamp() {
    date +"%T" # current time
}

handle_return_code() {
    if [ $1 -ne 0 ];
    then
        exit 1
    fi
}

if [ -f /var/www/RELEASE ]; then
    echo "core version: "
    cat /var/www/RELEASE
fi

echo "====== copy and remove cron configs"
timestamp
echo "Remove useless j2 templates"
rm -f /var/www/docker-files/rtc/templates/etc/php/7.2/mods-available/newrelic.ini.j2
rm -f /var/www/docker-files/rtc/templates/etc/haproxy/haproxy.cfg.j2
rm -f /var/www/docker-files/rtc/templates/etc/nginx/sites-enabled/eda-solomon-metrics-proxy.conf.j2
cp /etc/syslog-ng/conf-enabled/syslog-ng.conf /etc/syslog-ng/syslog-ng.conf
echo "Copy custom rabbitmq consumers settings"
cp -f /supervisor/conf.d/core.conf.j2 /var/www/docker-files/rtc/templates/etc/supervisor/conf.d/core.conf.j2
echo "Copy custom cron configs"
cp -f /cron/cron.d/backend-crons.j2 /var/www/docker-files/rtc/templates/etc/cron.d/backend-crons.j2
echo "Copy custom stq configs"
cp -Rf /stq-runner/* /etc/yandex/taxi/stq-runner/

echo "====== generate ssl certs for core"
timestamp
(printf 'subjectAltName = @alt_names\n\
\n\
[alt_names]\n\
DNS.1 =  eda.yandex') > /tmp/v3.ext
cp /taxi/tools/rootCA.crt /tmp/rootCA.crt
cp /taxi/tools/rootCA.key /tmp/rootCA.key
cd /tmp && \
openssl req -new -newkey rsa:1024 -keyout /etc/ssl/private/server.key -out server.csr -nodes -subj /CN=Server && \
openssl x509 -req -sha256 -days 7000 -in server.csr -extfile /tmp/v3.ext -CA /tmp/rootCA.crt -CAkey /tmp/rootCA.key -CAcreateserial -out /etc/ssl/certs/server.crt
cp /taxi/tools/rootCA.crt /usr/local/share/ca-certificates/rootCA.crt
cat /usr/local/share/ca-certificates/rootCA.crt >> /etc/ssl/certs/ca-certificates.crt

echo "====== set syslog config, env, ulimit"
timestamp
/usr/bin/syslog-ng-inc > /etc/syslog-ng/syslog-ng.conf
/usr/bin/printenv | sed 's/^\(.*\)\=\(.*\)$/export \1\="\2"/g' > /env.sh
chmod +x /env.sh
ulimit -n 250000


echo "====== substitute .jinja templates"
timestamp
for f in $(find /var/www/docker-files/rtc/templates -type f -name '*.j2'); do
  dest=$(echo ${f%.j2} | sed 's/\/var\/www\/docker-files\/rtc\/templates//g')
  echo -e "Evaluating template\n\tSource: $f\n\tDest: ${dest}"
  j2 ${f} > ${dest}
  if [ "$(dirname ${dest})" = "/etc/supervisor/conf.d" ]; then
    echo -e "\tChecking supervisor config: ${dest}"
    if ! supervisor_config_validator_py.py --config-path ${dest}; then
      echo "Invalid config found, stopping the start process. Please investigate manually"
      exit 1
    fi
  elif [ "$(dirname ${dest})" = "/etc/cron.d" ]; then
    echo -e "\tChecking cron config: ${dest}"
    if ! chkcrontab ${dest}; then
      echo "Invalid config found, stopping the start process. Please investigate manually"
      exit 1
    fi
  fi
done

echo "===== Apply db data scripts"
timestamp
sleep 30
set +e
for f in /initdb/db_data/*; do
  echo "$f >..."
  mysql -uroot -Dbigfood -ppassword -hmysql.yandex.net < "$f"
  handle_return_code $?
done

echo "===== Removing and relinking logs, prepare dirs"
timestamp
SERVICE=backend
rm -rf /var/www/var/logs
rm -rf /var/log/${SERVICE}/* || true
ln -s /var/log/${SERVICE} /var/www/var/logs
cat /etc/yandex/statbox-push-client/custom/*|grep name | awk '{print $3}' | xargs -n1 touch
mkdir -p /var/www/web/private/jwt-keys
mkdir -p /var/www/web/private/payture-keys
mkdir /var/cache/nginx
mkdir -p /var/cache/yandex/eda_core && chown -R www-data:www-data /var/cache/yandex/eda_core

echo "====== Remove jobs (consumers & crons)"
timestamp
rm -f /etc/supervisor/conf.d/core.prod.conf
rm -f /etc/cron.d/backend-common-crons
rm -f /etc/cron.d/backend-consumers-restart

echo "====== Add jwt keys"
timestamp
if [ -f "$HOME/jwt/private.pem" ] && [ -f "$HOME/jwt/public.pem" ]; then
  echo "Copying jwt keys"
  cp "$HOME/jwt/private.pem" "$HOME/jwt/public.pem" /var/www/web/private/jwt-keys/
fi

echo "====== Push-client setup"
timestamp
custom_dir="/etc/yandex/statbox-push-client/custom"
if [ -d $custom_dir ]; then
  DAEMON_CONF="$(ls $custom_dir/*.yaml 2>/dev/null | xargs)"
  for conf in $DAEMON_CONF; do
    DAEMON_OPTS="$DAEMON_OPTS -c $conf "; \
  done
cat > /etc/supervisor/conf.d/push-client.conf <<EOL
[program:push-client]
command = /usr/bin/push-client -f -w $DAEMON_OPTS
stdout_logfile_maxbytes = 5MB
stderr_logfile_maxbytes = 5MB
stdout_logfile_backups = 2
stderr_logfile_backups = 2
autorestart = true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
EOL
fi

chmod 644 /etc/cron.d/*

echo "====== Generate STQ configs"
timestamp
export STQ_CONFIG_DIR=/etc/yandex/taxi/stq-runner
/usr/bin/php /var/www/bin/console --env=${SYMFONY_ENV} stq:config-create --output-dir ${STQ_CONFIG_DIR} \
&& grep "name: " ${STQ_CONFIG_DIR}/worker_config.yaml >> ${STQ_CONFIG_DIR}/stq_config.yaml
handle_return_code $?

echo "Update STQ config"
sed -i 's/^service_name: .*$/service_name: core_stq-runner/g' ${STQ_CONFIG_DIR}/config_vars.yaml \
&& sed -i 's/^stq_tvm_service_name: .*$/stq_tvm_service_name: eda_core/g' ${STQ_CONFIG_DIR}/config_vars.yaml \
&& sed -i 's/^tvm_service_name: .*$/tvm_service_name: eda_core/g' ${STQ_CONFIG_DIR}/config_vars.yaml \
&& sed -i 's~^stq_config_path: .*$~stq_config_path: '${STQ_CONFIG_DIR}'/stq_config.yaml~g' ${STQ_CONFIG_DIR}/config_vars.yaml \
&& sed -i 's~^stq_service_source_dir: .*$~stq_service_source_dir: /var/www~g' ${STQ_CONFIG_DIR}/config_vars.yaml \
&& sed -i 's/^tvm_service_name: .*$/tvm_service_name: eda_core/g' ${STQ_CONFIG_DIR}/stq_config.yaml \
&& echo "Update STQ config complete"

echo "====== remove tvmtool cron"
rm -f /etc/supervisor/conf.d/tvmtool.conf

echo "====== taxi-config:update"
timestamp
php /var/www/bin/console taxi-config:update --full -v
echo "Update taxi config exit code: ${?}"
handle_return_code $?

echo "====== settings:cache:update"
timestamp
php /var/www/bin/console -v settings:cache:update
echo "Update settings cache exit code: ${?}"
handle_return_code $?

echo "====== run core base migrations"
timestamp
cd /var/www && php /var/www/bin/console doctrine:migrations:migrate -n --env=migration
echo "doctrine:migrations exit code: ${?}"
handle_return_code $?

echo "====== create database payment system"
timestamp
php /var/www/bin/console doctrine:database:create --connection=payment_system --if-not-exists
echo "Create payment system database exit code: ${?}"
handle_return_code $?

echo "====== run payment system db migrations"
timestamp
cd /var/www && php /var/www/bin/console doctrine:migrations:migrate -v --em=payment_system --no-interaction --configuration=app/config/migrations_payment_system.yml
echo "payment system doctrine:migrations exit code: ${?}"
handle_return_code $?

echo "====== start rabbitmq queues"
timestamp
php /var/www/bin/console -v rabbitmq:setup-fabric
echo "Start rabbitmq queues exit code: ${?}"
handle_return_code $?

echo "====== run supervisor"
timestamp
/usr/bin/supervisord -c /etc/supervisor/supervisord.conf
