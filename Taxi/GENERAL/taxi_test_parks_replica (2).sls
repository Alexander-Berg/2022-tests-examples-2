yav:
  templates:
    /etc/yandex/taxi-secdist/taxi.json:
      template: 'secdist/parks_replica.tpl'
      owner: 'root:www-data'
      mode: '0644'
      secrets:
        - sec-01ct6bq63kp1kgkrkk9y6003qf->MONGO_SETTINGS
        - sec-01dd2zb6tqemr6vgg9zgdsf039->TVM_parks_replica
