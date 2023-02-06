yav:
  templates:
    /etc/yandex/taxi-secdist/taxi.json:
      template: 'secdist/supply_diagnostics.tpl'
      owner: 'root:www-data'
      mode: '0644'
      secrets:
        - sec-01ct6bq63kp1kgkrkk9y6003qf->MONGO_SETTINGS
        - sec-01d2cqn2kcmtj93vyvss2myr7c->S3_SETTINGS_SUPPLY_DIAGNOSTICS
        - sec-01cxzcc4ypkbb1kvbcaxyp4d3d->POSTGRESQL_SETTINGS
        - sec-01dfk1f539rdfcb54z8ng589fa->TVM_TAXI_SUPPLY_DIAGNOSTICS
