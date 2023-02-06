yav:
  templates:
    /etc/yandex/taxi-secdist/taxi.json:
      template: 'secdist/cardstorage.tpl'
      owner: 'root:www-data'
      mode: '0644'
      secrets:
        - sec-01ct6bq63kp1kgkrkk9y6003qf->MONGO_SETTINGS
        - sec-01dcktxxavakmt8719vrmgvatp->BILLINGS_uber
        - sec-01dcktxvbsxb23rc64m5f7fdye->BILLINGS_uber_roaming
        - sec-01dcktxzjwhzhr012y57c97jx8->BILLINGS_card
        - sec-01dckwtzjt5r5ts5513yrgn10b->TVM_cardstorage
        - sec-01cxzcc4ypkbb1kvbcaxyp4d3d->POSTGRESQL_SETTINGS
