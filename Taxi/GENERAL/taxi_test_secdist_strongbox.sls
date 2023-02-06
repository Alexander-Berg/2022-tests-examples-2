yav:
  ssl_cert: 'sec-01d9mdh7ptgr4jrwz2js4hxt11'
  templates:
    /etc/yandex/taxi-secdist/taxi.json:
      template: 'secdist/strongbox.tpl'
      owner: 'root:www-data'
      mode: '0640'
      secrets:
        - sec-01esrgv5p1kggm0vjadwgb0w3n->STRONGBOX_TVM
        - sec-01d8147m1zb7yx94a94c6keh4x->STRONGBOX_PG_SETTINGS
        - sec-01d816c5d6q4m6107a5djp21tc->STRONGBOX_SALT
        - sec-01d94vp2f627d2nrey1yknm6ak->STRONGBOX_YAV_ROBOT
        - sec-01dbfpnr5kbd8npbfj7ypvh1rw->STRONGBOX_API_TOKEN
        - sec-01dbfpxtf0xq5h25kkf8y996hc->STRONGBOX_CONF
        - sec-01dq529ke0ng10t1wpxjx7nab8->API_TOKEN_TAXI_STRONGBOX_GITHUB_OAUTH
        - sec-01fzx12fangqs7pvgvjthdtxjf->API_TOKEN_TAXI_DEVOPS_STRONGBOX_ARC
