#!/bin/bash

# run to setup dev environment
PASSPORT_INFRA_DEV_SECRET=sec-01g004e3v8at2f2kf30md6fkzk
SECRETS_DIR="/etc/fastcgi2/available/blackbox_keys"

function setEnvVar {
    if [[ ! -n "${!1}" ]]; then
        echo "Set env var $1"
        echo "$1=$(yav get version $PASSPORT_INFRA_DEV_SECRET -o $1 --rsa-private-key ~/.ssh/id_rsa --rsa-login $USER)" | sudo tee -a /etc/environment
        source /etc/environment
    else
        echo "Env var $1 was already set"
    fi
}

function putSecretFile {
    if [[ ! -f $SECRETS_DIR/$1 ]]; then
        echo "Put file $SECRETS_DIR/$1"
        yav get version $PASSPORT_INFRA_DEV_SECRET -o $1 > /tmp/$1
        sudo mv /tmp/$1 $SECRETS_DIR/$1
    fi
}

if [[ -z "$(which yav || true)" ]]; then
    sudo apt-get -y update
    sudo apt-get -y install yandex-passport-vault-client
fi

sudo mkdir -p $SECRETS_DIR

setEnvVar "BB_PASSPORTDB_USER_RW"
setEnvVar "BB_PASSPORTDB_PASSWD_RW"

putSecretFile "bb_test_1.secret"
putSecretFile "bb_test_2.secret"
putSecretFile "bb_test_3.secret"
putSecretFile "bb_test_5.secret"
putSecretFile "bb_test_6.secret"
putSecretFile "passport_dev.secret"

sudo usermod -a -G blackbox $USER

echo "OK"