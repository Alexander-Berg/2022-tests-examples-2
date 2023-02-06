#!/usr/bin/env bash
set -e

OS=$(uname -s)
LINUX=$(source /etc/os-release 2>/dev/null; echo $NAME)
DOCKER_COMPOSE_MIN_VERSION="1.12.0"

if [ "$USER" == "root" ]; then
    echo "Do not run integration tests as root" 1>&2
    exit 1
fi

while ! docker info > /dev/null; do
    if [ "$OS" != "Linux" ]; then
        echo "Docker does not work :(" 1>&2
        exit 1
    fi

    if ! which dockerd > /dev/null; then
        read -p "Docker is not installed. Try to install it now? [Y/n]: " INSTALL_DOCKER
        case "$INSTALL_DOCKER" in
            Y|y|"")
                case "$LINUX" in
                    Ubuntu)
                        sudo apt-get install docker-ce=17.09.0~ce-0~ubuntu
                        ;;
                    Gentoo)
                        sudo emerge -v app-emulation/docker
                        ;;
                    *)
                        echo "Unsupported operating system, install docker manually"
                        exit 1
                esac
                ;;
            *)
                exit 1
                ;;
        esac

        sleep 1
        continue
    fi

    if ! pgrep dockerd > /dev/null; then
        read -p "Docker is not running. Try to start it now? [Y/n]: " START_DOCKER
        case "$START_DOCKER" in
            Y|y|"")
                case "$LINUX" in
                    Ubuntu)
                        sudo service docker start
                        ;;
                    Gentoo)
                        sudo rc-service docker start
                        ;;
                    *)
                        echo "Unsupported operation system, start docker manually"
                        exit 1
                esac
                ;;
            *)
                exit 1
                ;;
        esac

        sleep 1
        continue
    fi

    if [ ! -r /var/run/docker.sock ]; then
        if [ ! -S /var/run/docker.sock ]; then
            echo "Docker does not work :("
            exit 1
        fi

        read -p "You do not have permissions to docker. Add it now? [Y/n]: " CHMOD_DOCKER
        case "$CHMOD_DOCKER" in
            Y|y|"")
                sudo chmod 666 /var/run/docker.sock
                continue
                ;;
            *)
                exit 1
                ;;
        esac
    fi

    echo "Unknown problem with docker :(" 1>&2
    exit 1
done

if ! which python3.7 > /dev/null; then
    if [ "$OS" != "Linux" ]; then
        echo "Python3.7 is not installed :(" 1>&2
        exit 1
    fi

    read -p "Python3.7 is not installed. Try install it now? [Y/n]: " INSTALL_PYTHON
    case "$INSTALL_PYTHON" in
        Y|y|"")
            case "$LINUX" in
                Ubuntu)
                    sudo apt-get install taxi-deps-py3-2
                    ;;
                Gentoo)
                    sudo emerge -v dev-lang/python:3.7
                    ;;
                *)
                    echo "Unsupported operation system, install python3.7 manually"
                    exit 1
            esac
            ;;
        *)
            exit 1
            ;;
    esac
fi

check_docker_compose () {
    VERSION_REGEXP="[[:digit:]]+\.[[:digit:]]+\.[[:digit:]]+"
    DOCKER_COMPOSE_VERSION=$(docker-compose --version 2>&1 | grep -Eo $VERSION_REGEXP || true)
    if [ -z $DOCKER_COMPOSE_VERSION ]; then
        # docker-compose is absent
        return 1
    fi
    GREATER_VERSION="$(echo -e "$DOCKER_COMPOSE_MIN_VERSION\n$DOCKER_COMPOSE_VERSION" | sort -V | tail -n 1)"
    # check that docker-compose version is correct
    test "$GREATER_VERSION" != "$DOCKER_COMPOSE_MIN_VERSION"
}

if ! check_docker_compose; then
    if ! which docker-compose > /dev/null; then
        DOCKER_COMPOSE_MESSAGE="Docker Compose is not installed"
    else
        DOCKER_COMPOSE_MESSAGE="Docker Compose version is too old"
    fi

    if [ "$OS" != "Linux" ]; then
        echo "$DOCKER_COMPOSE_MESSAGE :(" 1>&2
        exit 1
    fi

    read -p "$DOCKER_COMPOSE_MESSAGE. Try install it now? [Y/n]: " INSTALL_DOCKER_COMPOSE
    case "$INSTALL_DOCKER_COMPOSE" in
        Y|y|"")
            case "$LINUX" in
                Ubuntu)
                    sudo apt-get install taxi-deps-py3-2
                    ;;
                Gentoo)
                    sudo emerge -v app-emulation/docker-compose
                    ;;
                *)
                    echo "Unsupported operation system, install docker-compose manually"
                    exit 1
            esac
            ;;
        *)
            exit 1
            ;;
    esac
fi

./scripts/login.sh
