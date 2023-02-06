#!/usr/bin/env bash
set -e

OS=$(uname -s)
LINUX=$(source /etc/os-release 2>/dev/null; echo $NAME)

if pgrep -F /var/run/nginx.pid nginx > /dev/null 2> /dev/null; then
    echo "Running nginx can break integration tests" >&2
    if [ "$OS" == "Linux" ]; then
        read -p "Stop it now? [Y/n]: " STOP_NGINX
        case "$STOP_NGINX" in
            Y|y|"")
                case "$LINUX" in
                    Ubuntu)
                        sudo service nginx stop
                        ;;
                    Gentoo)
                        sudo rc-service nginx stop
                        ;;
                esac
                ;;
        esac
    fi
fi
