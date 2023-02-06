yav:
  templates:
    /etc/yandex/taxi-secdist/taxi.yaml:
      template: 'taxi_analytics_business_models/taxi.yaml.tpl'
      owner: 'robot-taxi-stat:www-data'
      mode: 0444
      secrets:
        - sec-01drc5jcyav6dxq32s0trhbdqx->ROBOT_STFIN
        - sec-01drbf7at070phws40np0jyeh9->GOOGLEDOCS
