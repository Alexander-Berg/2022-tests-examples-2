yav:
  templates:
    /etc/mongos/key-billing-buffer-proxy:
      template: 'mongo-secret-key.tpl'
      owner: 'mongodb:root'
      mode: '0600'
      secrets: 'sec-01d45pv7xa5qcpjj063tzwhxep->MONGO'
