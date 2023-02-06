yav:
  templates:
    /etc/redis/include/sentinel.conf:
      template: 'sentinel.tpl'
      owner: 'redis:redis'
      mode: '0660'
      secrets: 'sec-01fpjat9725g4c2t87b1kjc629->REDIS'
      vars:
        - START_PORT: 6379
        - END_PORT: 6395

