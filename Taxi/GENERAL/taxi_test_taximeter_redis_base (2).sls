yav:
  templates:
    /etc/redis/include/credentials.conf:
      template: 'redis.tpl'
      owner: 'redis:redis'
      mode: '0600'
      secrets: 'sec-01cs1tw485451x1zaz7fgzsnkh->REDIS'
