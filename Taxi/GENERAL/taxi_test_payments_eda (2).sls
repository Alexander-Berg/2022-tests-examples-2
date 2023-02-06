yav:
  templates:
    /etc/yandex/taxi-secdist/taxi.json:
      template: 'secdist/payments_eda.tpl'
      owner: 'root:www-data'
      mode: '0644'
      secrets:
        - sec-01ct6bq63kp1kgkrkk9y6003qf->MONGO_SETTINGS
        - sec-01d59wtj9d4dymj65j6g1gdjpx->APIKEYS
        - sec-01dch0azpkkf9sww9mkhc7ng8t->TVM_payments_eda
        - sec-01dd3df8t8m09mggaftjc6gq5g->CLIENT_APIKEYS
