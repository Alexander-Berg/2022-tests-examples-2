#!/usr/bin/env bash

echo -e "\n"
# check_token
yql_token_path="$HOME/.yql/token"
if [[ -f $yql_token_path ]]; then
  echo "yql_token ok"
else
  pushd `pwd`
  cd $HOME
  mkdir -p ~/.yql
  chmod 700 ~/.yql
  echo "yql token needed (get it using instruction https://wiki.yandex-team.ru/market/analytics/stackoverflow-analitiki-marketa/yt/gde-vzjat-token-dlja-yt/)"
  echo "yql token:"
  read yql_token
  echo "$yql_token" > ~/.yql/token
  echo "yql token saved: $HOME/.yql/token"
  chmod 400 ~/.yql/token
  popd
fi

echo "/usr/lib/yandex/taxi-py3-2/bin/python -m sampling.sampling ${@}"
/usr/lib/yandex/taxi-py3-2/bin/python -m sampling.sampling ${@}

exit $?
