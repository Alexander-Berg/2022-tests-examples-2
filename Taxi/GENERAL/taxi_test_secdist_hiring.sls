yav:
  templates:
    /etc/yandex/taxi-secdist/taxi.json:
      template: 'secdist/hiring.tpl'
      owner: 'root:www-data'
      mode: '0644'
      secrets:
        - sec-01cxzcc4ypkbb1kvbcaxyp4d3d->POSTGRESQL_SETTINGS
