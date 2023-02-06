yav:
  templates:
    /etc/yandex/taxi-secdist/taxi.json:
      template: 'secdist/hiring_taxiparks_gambling.tpl'
      owner: 'root:www-data'
      mode: '0640'
      secrets:
        - sec-01cxzcc4ypkbb1kvbcaxyp4d3d->POSTGRESQL_SETTINGS
        - sec-01d59wtj9d4dymj65j6g1gdjpx->APIKEYS
        - sec-01dhrqx2434k436dwdb6npkfwn->TVM_HIRING_TAXIPARKS_GAMBLING
