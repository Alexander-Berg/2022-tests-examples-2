#!/usr/bin/env bash
set -e

if ! grep --quiet registry.yandex.net ~/.docker/config.json; then
    if [ -n "$YANDEX_LOGIN" -a -n "$YANDEX_TOKEN" ]; then
        docker login -u $YANDEX_LOGIN -p $YANDEX_TOKEN registry.yandex.net
    else
        echo "You must log in to the docker distribution service."
        echo "For this you need to get any OAuth token issued in Yandex."
        echo "You can get token by following the link:"
        echo "https://oauth.yandex-team.ru/authorize?response_type=token&client_id=12225edea41e4add87aaa4c4896431f1"
        echo
        echo "For more information about this, see the wiki:"
        echo "https://wiki.yandex-team.ru/cocaine/docker-registry-distribution/#avtorizacija"
        echo
        echo "To login in registry.yandex.net, please enter your OAuth token (instead of password)"
        echo "Logging in as $USER"
        docker login --username $USER registry.yandex.net
        echo
        read -p "Do you want to automatically update docker images? [Y/n] " UPDATE_IMAGES
        case "$UPDATE_IMAGES" in
            Y|y|"")
                MINUTES=$(( ( RANDOM % 60 )  + 1 ))
                LINE="$MINUTES 7 * * * cd '$(pwd)' && make pull-images docker-cleanup"
                if [ -f /etc/cron.allow ]; then
                    if ! grep -q $USER /etc/cron.allow; then
                        echo "Crontab disabled on your system: /etc/cron.allow found and current user not listed in it."
                        read -p "Do you want to enable it? [Y/n]: " ALLOW_CRONTAB
                        case $ALLOW_CRONTAB in
                        Y|y|"")
                            sudo sh -c "echo $USER >> /etc/cron.allow"
                            echo "Allowed crontab for $USER"
                            ;;
                        *)
                            "Crontab disabled. Exiting"
                            exit 0
                            ;;
                        esac
                    fi
                fi
                NEW_CRONTAB=$(crontab -l 2>/dev/null; echo "$LINE")
                echo "$NEW_CRONTAB" | crontab -
                echo "New crontab line has been added. You can edit it by crontab -e"
                ;;
        esac
    fi
fi
