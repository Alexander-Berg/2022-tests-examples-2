yav:
  ssl_cert: 'sec-01cxzejqnannx368hvz6rtypjy'
  templates:
    /etc/yandex/octocore/secrets.json:
      template: 'taxi_octocore.tpl'
      owner: 'www-data:www-data'
      mode: '0400'
      secrets:
        - sec-01dg566fnd06xq7hjfpc104c70->PGAAS_SETTINGS
        - sec-01dg4r8a9rkh8vnbb1197yg6nh->OCTONODE_MDS_S3
      vars:
        - S3_BUCKET: 'calls-testing'
