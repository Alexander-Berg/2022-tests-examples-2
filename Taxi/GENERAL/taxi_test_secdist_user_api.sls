yav:
  templates:
    /etc/yandex/taxi-secdist/taxi.json:
      template: 'secdist/user_api.tpl'
      owner: 'root:www-data'
      mode: '0644'
      secrets:
        - sec-01ct6bq63kp1kgkrkk9y6003qf->MONGO_SETTINGS
        - sec-01ct3zpqf30w7gkwaq47n45sx2->PERSONAL_APIKEY
        - sec-01d59wtj9d4dymj65j6g1gdjpx->APIKEYS
        - sec-01d6w89dmrz3zyn3sc1wqjjm7c->USER_PHONES_HASH_SALT
        - sec-01defcncvwjznteaxd4rd10aap->TVM_user_api
