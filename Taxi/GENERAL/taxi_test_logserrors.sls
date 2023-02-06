yav:
  templates:
    /etc/yandex/taxi-secdist/taxi.json:
      template: 'secdist/logserrors.tpl'
      owner: 'root:www-data'
      mode: '0640'
      secrets:
        - sec-01cxzcc4ypkbb1kvbcaxyp4d3d->POSTGRESQL_SETTINGS
        - sec-01d4qfywjg815vxxzmahs3efb9->API_ADMIN_SERVICES_TOKENS
        - sec-01ct1ak1amgqnb1kmb8q82th9n->STARTRACK_API_TOKEN
      vars:
        - ST_URL: "https://st-api.test.yandex-team.ru/v2/"
