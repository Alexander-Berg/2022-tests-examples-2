yav:
  templates:
    /etc/redis/include/credentials.conf:
      template: 'redis.tpl'
      owner: 'redis:redis'
      mode: '0600'
      secrets: 'sec-01cs1tr9pmf0qrktcndyjk2y08->REDIS'
    /etc/redis/include/sentinel.conf:
      template: 'sentinel.tpl'
      owner: 'redis:redis'
      mode: '0660'
      secrets: 'sec-01cs1tr9pmf0qrktcndyjk2y08->REDIS'
      vars:
        - START_PORT: 6379
        - END_PORT: 6383

