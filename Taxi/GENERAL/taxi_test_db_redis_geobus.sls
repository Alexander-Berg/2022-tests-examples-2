yav:
  templates:
    /etc/redis/include/credentials.conf:
      template: 'redis.tpl'
      owner: 'redis:redis'
      mode: '0600'
      secrets: 'sec-01fpjat9725g4c2t87b1kjc629->REDIS'
