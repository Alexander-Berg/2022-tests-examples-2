yav:
  templates:
    /etc/yandex/taxi-secdist/taxi.json:
      template: 'secdist/render_template.tpl'
      owner: 'root:www-data'
      mode: '0644'
      secrets:
        - sec-01ct6bq63kp1kgkrkk9y6003qf->MONGO_SETTINGS
        - sec-01f2vndcx7xkpcqgtxjc0ndqpq->TVM_RENDER_TEMPLATE
