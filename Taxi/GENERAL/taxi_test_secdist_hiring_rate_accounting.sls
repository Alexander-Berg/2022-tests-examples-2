yav:
  templates:
    /etc/yandex/taxi-secdist/taxi.json:
      template: 'secdist/hiring_rate_accounting.tpl'
      owner: 'root:www-data'
      mode: '0640'
      secrets:
        - sec-01cxzcc4ypkbb1kvbcaxyp4d3d->POSTGRESQL_SETTINGS
        - sec-01e7172hmxene8vjvp5vms6dbb->TVM_TAXI_HIRING_RATE_ACCOUNTING
