yav:
  templates:
    /etc/yandex/taxi-secdist/taxi.json:
      template: 'secdist/hiring_st.tpl'
      owner: 'root:www-data'
      mode: '0640'
      secrets:
        - sec-01cxzcc4ypkbb1kvbcaxyp4d3d->POSTGRESQL_SETTINGS
        - sec-01dhrqdsf348xwd0a9tvbp0zvf->TVM_HIRING_ST
