#!/usr/bin/env bash
set -e
appname=taxi-atlas-backend-router

touch /taxi/logs/application-$appname.log
chown www-data /taxi/logs/application-$appname.log
chmod 666 /taxi/logs/application-$appname.log

start_atlas=/taxi/atlas/run/start_atlas.sh

# кровь, кишки
#sed -i 's/= True if db.atlas.idm_roles.find_one.*/= True/g' \
#/usr/lib/yandex/taxi-atlas-backend-router/atlas/permissions.py
sed -i 's/return roles\>/return {"superuser": True, "login": "default", "cities": \["Пекин"\], "main": True, "car_map": True}/g' \
/usr/lib/yandex/taxi-atlas-backend-router/atlas/permissions.py
sed -i '/^def get_user_login():/a\
    return "default"' \
/usr/lib/yandex/taxi-atlas-backend-router/atlas/permissions.py
sed -i 's/login\s*=\s*permissions.get_user_login()/login = "default"/' \
/usr/lib/yandex/taxi-atlas-backend-router/atlas/api/v0/atlas_handbook/misc.py
sed -i 's/CH_CREDENTIALS = CLICKHOUSE\[CH_SERVER\]/# CH_CREDENTIALS = CLICKHOUSE\[CH_SERVER\]/' \
/usr/lib/yandex/taxi-atlas-backend-router/atlas/user_deliveries.py
sed -i 's/mongodb:\/\/{user}:{password}@{host}:{port}\/{database}/mongodb:\/\/{host}:{port}\/{database}/' \
/usr/lib/yandex/taxi-atlas-backend-router/connections/mongodb/connect.py

# FIXME - this is awkward, we had to move /etc/nginx/sites-enabled/atlas_nginx.conf
# to /etc/nginx/sites-available because --nginx will create symlink
# from available to enabled. 
mv -f /etc/nginx/sites-enabled/atlas_nginx.conf /etc/nginx/sites-available/atlas_nginx.conf

/taxi/tools/run.py \
    --nginx atlas_nginx.conf \
    --restart-service 9999 \
    --wait mongo.taxi.yandex:27017 \
    --run su www-data -s /bin/bash -c \
     "cd /usr/lib/yandex/taxi-atlas-backend-router/ && $start_atlas"
