mmcd_instance_list: [ memcached ]

memcached:
  slab_page: 50m
  memory: 256
  port: 11211
  iconnect: 1024
  user: nobody
  ip: '"[::1]"'
  logfile: /var/log/memcached.log
