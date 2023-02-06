yav:
  templates:
    /etc/yandex/taxi-secdist/taxi.json:
      template: 'secdist/driver_referrals.tpl'
      owner: 'root:www-data'
      mode: '0644'
      secrets:
        - sec-01d42z1z14h8g0rmqxyvge6er6->TVM_api_admin
        - sec-01d42z75b3fdda8p0sa9y7zrsk->TVM_driver_referrals
        - sec-01d6gkb0qgrx6mb1f1ryv2swjf->TVM_driver_protocol
        - sec-01d2fpgnr4agcdxmavphpkbsjt->TVM_parks
        - sec-01d9d25mt0m2vwm5ymas4b13qf->TVM_taximeter_core
        - sec-01ct6bq63kp1kgkrkk9y6003qf->MONGO_SETTINGS
        - sec-01d7m22xgvbdgbgx8nkxfcsaa5->PG_SETTINGS
        - sec-01dbnbn7djh9kvksfrp7fw9ear->YT_TOKEN_HAHN
        - sec-01ctjtjjyhzk84406es1810cy4->TERRITORIES_API_TOKEN
        - sec-01dfbkaqypq6rg9amdzrtx7gns->DRIVER_REFERRALS_YQL_TOKEN
        - sec-01d59wtj9d4dymj65j6g1gdjpx->APIKEYS
