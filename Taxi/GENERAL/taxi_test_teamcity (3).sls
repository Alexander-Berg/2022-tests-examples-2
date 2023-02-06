yav:
  ssl_cert: 'sec-01d4fehfr24041t3c2gfbqqx87'
  templates:
    /etc/tvmtool/tvmtool.conf:
      template: 'tvmtool/teamcity.tpl'
      owner: 'root:root'
      mode: '0644'
      secrets:
        - sec-01d99sdjwkw6rqahgee1mt50th->TVM_teamcity
  files:
    {{ '/home/' + salt.pillar.get('arc:user', 'teamcity') + '/.arc/token' }}:
      owner: "{{ salt.pillar.get('arc:user', 'teamcity') }}:{{ salt.pillar.get('arc:group', 'fired') }}"
      mode: '0400'
      secret: 'sec-01edcr385fy8w8jhssmjhskzpt'
      key: 'value'
