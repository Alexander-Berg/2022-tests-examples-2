mcrouter:
  port: 11211
  pools:
    - name: pool1
      hosts: { memcache01h.taxi.tst.yandex.net }
    - name: pool2
      hosts: { memcache01i.taxi.tst.yandex.net }
    - name: pool3
      hosts: { memcache01f.taxi.tst.yandex.net } 
