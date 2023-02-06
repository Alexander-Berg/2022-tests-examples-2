yav:
  templates:
    /etc/redis/include/credentials.conf:
      template: 'redis.tpl'
      owner: 'redis:redis'
      mode: '0600'
      secrets: 'sec-01cs1tr9pmf0qrktcndyjk2y08->REDIS'
