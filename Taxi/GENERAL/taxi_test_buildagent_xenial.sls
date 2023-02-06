yav:
  templates:
    /home/buildfarm/.docker/config.json:
      template: 'taxi_test_buildagent_xenial_registry.tpl'
      owner: 'buildfarm:root'
      mode: '0640'
      secrets: 'sec-01deve4jkzsmakr2rkje7gygwh->REGISTRY'
