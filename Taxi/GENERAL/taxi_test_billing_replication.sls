yav:
  templates:
    /etc/yandex/taxi-secdist/taxi.json:
      template: 'secdist/billing_replication.tpl'
      owner: 'root:www-data'
      mode: '0644'
      secrets:
        - sec-01ct6bq63kp1kgkrkk9y6003qf->MONGO_SETTINGS
        - sec-01cxzcc4ypkbb1kvbcaxyp4d3d->POSTGRESQL_SETTINGS
        - sec-01d2fpdmqfayvk5xb1vr7bt09p->TVM_admin
        - sec-01d2fpgnr4agcdxmavphpkbsjt->TVM_parks
        - sec-01d2fpjhe08h09k9pd6dm8797f->TVM_billing_replication
        - sec-01d4qq2xnma1k5xwx8ckgehcp2->TVM_yb_trust_payments
        - sec-01d86csaxjn1y0fk8242xjp5e9->TVM_corp_integration_api
        - sec-01d8tj4vtt2ww18fs2cm9d0hfs->TVM_receipt_fetching
        - sec-01d40tjb6g6sg88a4243rmq57s->ADMIN_SCRIPT_LOGS_MDS_S3
        - sec-01d59wtj9d4dymj65j6g1gdjpx->APIKEYS
