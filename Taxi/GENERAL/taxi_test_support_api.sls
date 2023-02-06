yav:
  ssl_cert: 'sec-01cqvttzc5nh0v5cmmrh860rw4'
  templates:
    /etc/yandex/taxi-secdist/taxi.json:
      template: 'secdist/support_api.tpl'
      owner: 'root:www-data'
      mode: '0640'
      secrets: 
        - sec-01cqybdfghnh6pf2s0ajs292n6->ZENDESK
        - sec-01cqybe94gw8grxfw3bfm7p70z->SUPPORT_MODERATION_SECRET_KEY
        - sec-01cqybgft11fpjxpcmmv3h96pj->DATABASE_SUPPORT_API
        - sec-01enwknd2sqeyt30j8hv64bgna->TVM_TAXI_SUPPORT_MODERATION
    /etc/yandex/taxi-secdist/taxi-ro.json:
      template: 'secdist-ro/support_api.tpl'
      owner: 'root:www-data'
      mode: '0644'
      secrets: 
        - sec-01cqybdfghnh6pf2s0ajs292n6->ZENDESK
        - sec-01cqybgft11fpjxpcmmv3h96pj->DATABASE_SUPPORT_API
