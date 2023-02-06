yav:
  templates:
    /etc/yandex/taxi-secdist/taxi.yaml:
      template: 'taxi_analytics_gpdb/taxi.yaml.tpl'
      owner: 'robot-taxi-tst-gpadm:root'
      mode: '0400'
      secrets:
        - sec-01dhkwvd3hbacsj82shymx7yrs->S3MDS_TAXI_GPDB_BACKUP
        - sec-01djqyh50hwepycm3ny38e8jg8->POSTGRES_TAXI_GP_BACKUP_MANAGER
  files:
    /home/robot-taxi-tst-gpadm/.ssh/id_rsa:
      owner: 'robot-taxi-tst-gpadm:dpt_virtual_robots'
      mode: 0600
      secret: sec-01egg679bmc0a5zcer9dxx0a0d
      key: 'id_rsa_secret'
    /home/robot-taxi-tst-gpadm/.ssh/id_rsa.pub:
      owner: 'robot-taxi-tst-gpadm:dpt_virtual_robots'
      mode: 0644
      secret: sec-01egg679bmc0a5zcer9dxx0a0d
      key: 'id_rsa_public'
