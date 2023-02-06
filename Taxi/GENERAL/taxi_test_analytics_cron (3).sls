yav:
  templates:
    /home/robot-taxi-business/mylib_config.json:
      template: 'taxi_test_analytics_cron/mylib_config.json.tpl'
      owner: 'robot-taxi-business:dpt_virtual_robots_9257'
      mode: '0400'
      secrets:
        - sec-01e4b77wcnpgnk6hq09xf3v60z->ROBOT_TAXI_BUSINESS_MYLIB_CONFIG
        - sec-01ex4jeddnczf9vesaqtrdgtbj->DRYUKALEX_GEO_METRICS_BOT
