include:
  - yav.mongo-backup-s3cmd

yav:
  templates:
    /etc/mongo-monitor.conf:
      template: 'mongo-monitor.tpl'
      secrets: 'sec-01cs2gne7ahcepenyvrbqjj07g->MONGO_MONITOR'
    /etc/mongo-secret-key.conf:
      template: 'mongo-secret-key.tpl'
      owner: 'mongodb:root'
      mode: '0600'
      secrets: 'sec-01cs2gne7ahcepenyvrbqjj07g->MONGO'
    /etc/yandex/genbackup/genbackup.conf:
      template: 'mongo-s3-backup/genbackup.tpl'
      owner: 'root:genbackup'
      mode: '0640'
      secrets:
        - sec-01cs2gne7ahcepenyvrbqjj07g->MONGO
        - sec-01dnsk72ztgsx7q6n141agtw8k->TAXI_MONGO_S3_BACKUP_GPG
      vars:
        - S3_PATH_ROOT: 's3://mongo-backup-testing/taxi_test_db_mongo_companion'
        - BACKUP_RATE_LIMIT: 2M
        - ENVIRONMENT: testing