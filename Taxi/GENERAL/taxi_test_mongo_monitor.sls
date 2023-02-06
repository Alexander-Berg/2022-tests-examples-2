yav:
  templates:
    /etc/mongo-monitor.conf:
      template: 'mongo-monitor.tpl'
      owner: 'mongodb:root'
      mode: '0600'
      secrets: 'sec-01crzqb910h1p2d5acvwf0chpr->MONGO_MONITOR'
