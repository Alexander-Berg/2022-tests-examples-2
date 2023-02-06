yav:
  templates:
    /etc/haproxy/haproxy.cfg:
      template: 'taximeter_test_haproxy.tpl'
      owner: 'haproxy:haproxy'
      mode: '0660'
      secrets: 'sec-01cs1tw485451x1zaz7fgzsnkh->REDIS'
