yav:
  templates:
    /etc/hw_watcher/conf.d/bot-api-token.conf:
      template: 'hw_watcher/bot-api-token.tpl'
      owner: 'hw-watcher:hw-watcher'
      mode: '0440'
      secrets: 'sec-01ctdfvp30jdmccc3env05mamw->ROBOT'
