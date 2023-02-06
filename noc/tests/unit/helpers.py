import json


ns_mappings = json.loads(
    """{
  "items": [
    {
      "addresses": [
        "80.239.201.65",
        "149.5.244.46",
        "2a02:6b8::105"
      ],
      "fqdn": "st.kp.yandex.net.",
      "ns": "ns3+ns4",
      "ns-type": "dynamic",
      "proxy": "cogent+telia",
      "ttl": 600,
      "type": "AAAA",
      "view": "VIEW_UA",
      "zone": "kp.yandex.net",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "149.5.244.202",
        "80.239.201.67",
        "2a02:6b8::2:105"
      ],
      "fqdn": "front.kp.yandex.net.",
      "ns": "ns3+ns4",
      "ns-type": "dynamic",
      "proxy": "cogent+telia",
      "ttl": 600,
      "type": "AAAA",
      "view": "VIEW_UA",
      "zone": "kp.yandex.net",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "149.5.244.2",
        "80.239.201.90"
      ],
      "fqdn": "resize.yandex.net.",
      "ns": "ns3+ns4",
      "ns-type": "dynamic",
      "proxy": "cogent+telia",
      "ttl": 301,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "resize.yandex.net",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.69",
        "149.5.244.171"
      ],
      "fqdn": "mobileproxy-certificate.passport.yandex.ru.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "yandex.ru",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.90",
        "149.5.244.2"
      ],
      "fqdn": "pdd.yandex.ru.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "yandex.ru",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.90",
        "149.5.244.2"
      ],
      "fqdn": "pass.yandex.ru.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "yandex.ru",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "149.5.244.2",
        "80.239.201.90"
      ],
      "fqdn": "report-2.appmetrica.webvisor.com.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "webvisor.com",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.48",
        "149.5.244.44"
      ],
      "fqdn": "d.aws-proxy.disk.yandex.ua.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "yandex.ua",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "149.5.244.73",
        "80.239.201.47"
      ],
      "fqdn": "loft.z5h64q92x9.net.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "z5h64q92x9.net",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "149.5.244.209",
        "80.239.201.50"
      ],
      "fqdn": "disk.yandex.ua.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "yandex.ua",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.90",
        "149.5.244.2",
        "2a02:6b8::32c"
      ],
      "fqdn": "launcher-cache.mobile.yandex.net.",
      "ns": "ns3+ns4",
      "ns-type": "dynamic",
      "proxy": "cogent+telia",
      "ttl": 900,
      "type": "AAAA",
      "view": "VIEW_UA",
      "zone": "mobile.yandex.net",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.121",
        "149.5.244.251"
      ],
      "fqdn": "metrika-inf.com.",
      "ns": "ns3+ns4",
      "ns-type": "dynamic",
      "proxy": "cogent+telia",
      "ttl": 301,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "metrika-inf.com",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.9",
        "154.47.36.189",
        "2001:2030:20::78",
        "2001:978:7401::78"
      ],
      "fqdn": "ns9.z5h64q92x9.net.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "AAAA",
      "view": "VIEW_UA",
      "zone": "z5h64q92x9.net",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.50",
        "149.5.244.209"
      ],
      "fqdn": "m.aws-proxy.disk.yandex.ua.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "yandex.ua",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "149.5.244.246",
        "80.239.201.32"
      ],
      "fqdn": "ads.adfox.ru.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "adfox.ru",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "149.5.244.63",
        "80.239.201.94"
      ],
      "fqdn": "mail.yandex.ru.",
      "ns": "ns3+ns4",
      "ns-type": "dynamic",
      "proxy": "cogent+telia",
      "ttl": 301,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "mail.yandex.ru",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.90",
        "149.5.244.2"
      ],
      "fqdn": "api.browser.yandex.kz.",
      "ns": "ns3+ns4",
      "ns-type": "dynamic",
      "proxy": "cogent+telia",
      "ttl": 301,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "browser.yandex.kz",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.90",
        "149.5.244.2"
      ],
      "fqdn": "passport.yandex.ru.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "yandex.ru",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "149.5.244.2",
        "80.239.201.90"
      ],
      "fqdn": "redirect.appmetrica.webvisor.com.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "webvisor.com",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.90",
        "149.5.244.2"
      ],
      "fqdn": "report-1.appmetrica.webvisor.com.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "webvisor.com",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "149.5.244.2",
        "80.239.201.90"
      ],
      "fqdn": "push.yandex.com.",
      "ns": "ns3+ns4",
      "ns-type": "dynamic",
      "proxy": "cogent+telia",
      "ttl": 301,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "push.yandex.com",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.90",
        "149.5.244.2"
      ],
      "fqdn": "rosenberg.appmetrica.webvisor.com.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "webvisor.com",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.100",
        "149.5.244.98"
      ],
      "fqdn": "predictor.yandex.net.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "yandex.net",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "149.5.244.57",
        "80.239.201.123"
      ],
      "fqdn": "www.yandex.ru.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "yandex.ru",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.94",
        "149.5.244.63"
      ],
      "fqdn": "mail.yandex.fr.",
      "ns": "ns3+ns4",
      "ns-type": "dynamic",
      "proxy": "cogent+telia",
      "ttl": 301,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "mail.yandex.fr",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.90",
        "149.5.244.2"
      ],
      "fqdn": "api.browser.yandex.net.",
      "ns": "ns3+ns4",
      "ns-type": "dynamic",
      "proxy": "cogent+telia",
      "ttl": 301,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "browser.yandex.net",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "149.5.244.2",
        "80.239.201.90"
      ],
      "fqdn": "news.yandex.ru.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "yandex.ru",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.121",
        "149.5.244.251"
      ],
      "fqdn": "ymetrica2.com.",
      "ns": "ns3+ns4",
      "ns-type": "dynamic",
      "proxy": "cogent+telia",
      "ttl": 301,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "ymetrica2.com",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.90",
        "149.5.244.2"
      ],
      "fqdn": "oauth.yandex.ru.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "yandex.ru",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.45",
        "149.5.244.34",
        "2a02:6b8::1:235"
      ],
      "fqdn": "tracking.ott.yandex.ru.",
      "ns": "ns3+ns4",
      "ns-type": "dynamic",
      "proxy": "cogent+telia",
      "ttl": 900,
      "type": "AAAA",
      "view": "VIEW_UA",
      "zone": "ott.yandex.ru",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.74",
        "149.5.244.219"
      ],
      "fqdn": "mobileproxy.mobile.pssp.smilink.ru.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "smilink.ru",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.123",
        "149.5.244.57",
        "2a02:6b8:a::a"
      ],
      "fqdn": "www.yandex.ua.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 120,
      "type": "AAAA",
      "view": "VIEW_UA",
      "zone": "yandex.ua",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.90",
        "149.5.244.2"
      ],
      "fqdn": "report.appmetrica.webvisor.com.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "webvisor.com",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.90",
        "149.5.244.2"
      ],
      "fqdn": "tv.yandex.ua.",
      "ns": "ns3+ns4",
      "ns-type": "dynamic",
      "proxy": "cogent+telia",
      "ttl": 301,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "tv.yandex.ua",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "149.5.244.34",
        "80.239.201.45",
        "2a02:6b8::2:159"
      ],
      "fqdn": "api.ott.yandex.ru.",
      "ns": "ns3+ns4",
      "ns-type": "dynamic",
      "proxy": "cogent+telia",
      "ttl": 900,
      "type": "AAAA",
      "view": "VIEW_UA",
      "zone": "ott.yandex.ru",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "149.5.244.205",
        "80.239.201.10"
      ],
      "fqdn": "webattach-qloud.yandex.net.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "yandex.net",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.7",
        "149.5.244.182",
        "2001:2030:20::66",
        "2001:978:7401::66"
      ],
      "fqdn": "ns7.yandex.ru.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "AAAA",
      "view": "VIEW_UA",
      "zone": "yandex.ru",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.8",
        "149.5.244.40",
        "2001:2030:20::70",
        "2001:978:7401::70"
      ],
      "fqdn": "ns8.yandex.ru.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "AAAA",
      "view": "VIEW_UA",
      "zone": "yandex.ru",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.50",
        "149.5.244.209"
      ],
      "fqdn": "downloader.disk.yandex.ua.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "yandex.ua",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.17",
        "149.5.244.4",
        "2a02:6b8::298"
      ],
      "fqdn": "fenek.market.yandex.ua.",
      "ns": "ns3+ns4",
      "ns-type": "dynamic",
      "proxy": "cogent+telia",
      "ttl": 900,
      "type": "AAAA",
      "view": "VIEW_UA",
      "zone": "market.yandex.ua",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "149.5.244.251",
        "80.239.201.121"
      ],
      "fqdn": "mc.yandex.ru.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "yandex.ru",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.89",
        "149.5.244.83"
      ],
      "fqdn": "test-market.yandex.ua.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "yandex.ua",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.67",
        "149.5.244.202",
        "2a02:6b8::2:105"
      ],
      "fqdn": "smarttv-app.ott.yandex.ru.",
      "ns": "ns3+ns4",
      "ns-type": "dynamic",
      "proxy": "cogent+telia",
      "ttl": 60,
      "type": "AAAA",
      "view": "VIEW_UA",
      "zone": "ott.yandex.ru",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.100",
        "149.5.244.98"
      ],
      "fqdn": "translate.yandex.net.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "yandex.net",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "149.5.244.2",
        "80.239.201.90"
      ],
      "fqdn": "redirect.appmetrica.yandex.com.",
      "ns": "ns3+ns4",
      "ns-type": "dynamic",
      "proxy": "cogent+telia",
      "ttl": 301,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "appmetrica.yandex.com",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "149.5.244.205",
        "80.239.201.10",
        "2a02:6b8::2:147"
      ],
      "fqdn": "webattach.mail.yandex.net.",
      "ns": "ns3+ns4",
      "ns-type": "dynamic",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "AAAA",
      "view": "VIEW_UA",
      "zone": "mail.yandex.net",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "149.5.244.219",
        "80.239.201.74"
      ],
      "fqdn": "mobileproxy.passport.yandex.ru.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "yandex.ru",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "149.5.244.124",
        "80.239.201.82"
      ],
      "fqdn": "market-click2.yandex.ua.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "yandex.ua",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "149.5.244.57",
        "80.239.201.123",
        "2a02:6b8:a::a"
      ],
      "fqdn": "yandex.ua.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 120,
      "type": "AAAA",
      "view": "VIEW_UA",
      "zone": "yandex.ua",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "149.5.244.63",
        "80.239.201.94"
      ],
      "fqdn": "mail.yandex.ua.",
      "ns": "ns3+ns4",
      "ns-type": "dynamic",
      "proxy": "cogent+telia",
      "ttl": 301,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "mail.yandex.ua",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.100",
        "149.5.244.98"
      ],
      "fqdn": "dictionary.yandex.net.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "yandex.net",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.121",
        "149.5.244.251"
      ],
      "fqdn": "ymetrica.com.",
      "ns": "ns3+ns4",
      "ns-type": "dynamic",
      "proxy": "cogent+telia",
      "ttl": 301,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "ymetrica.com",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.123",
        "149.5.244.57",
        "2a02:6b8:a::a"
      ],
      "fqdn": "yandex.fr.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "AAAA",
      "view": "VIEW_UA",
      "zone": "yandex.fr",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "149.5.244.2",
        "80.239.201.90"
      ],
      "fqdn": "dr.z5h64q92x9.net.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "z5h64q92x9.net",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "149.5.244.118",
        "87.250.250.139",
        "77.88.21.142",
        "213.180.204.142",
        "2a02:6b8::4:139"
      ],
      "fqdn": "spdy3.mob.map.yandex.net.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 600,
      "type": "AAAA",
      "view": "VIEW_UA",
      "zone": "yandex.net",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.90",
        "149.5.244.2"
      ],
      "fqdn": "social.yandex.ru.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "yandex.ru",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.90",
        "149.5.244.2"
      ],
      "fqdn": "api.browser.yandex.com.tr.",
      "ns": "ns3+ns4",
      "ns-type": "dynamic",
      "proxy": "cogent+telia",
      "ttl": 301,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "browser.yandex.com.tr",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.11",
        "149.5.244.169"
      ],
      "fqdn": "proxy-mob-maps.yandex.ua.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "yandex.ua",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.47",
        "149.5.244.73",
        "2001:2030:20::2",
        "2001:978:7401::2"
      ],
      "fqdn": "yastatic.net.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "AAAA",
      "view": "VIEW_UA",
      "zone": "yastatic.net",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.90",
        "149.5.244.2"
      ],
      "fqdn": "push.yandex.ru.",
      "ns": "ns3+ns4",
      "ns-type": "dynamic",
      "proxy": "cogent+telia",
      "ttl": 301,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "push.yandex.ru",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.90",
        "149.5.244.2"
      ],
      "fqdn": "passport.yandex.com.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "yandex.com",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.107",
        "149.5.244.183"
      ],
      "fqdn": "an.webvisor.org.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "webvisor.org",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "149.5.244.219",
        "80.239.201.74"
      ],
      "fqdn": "mobileproxy.passport.yandex.net.",
      "ns": "ns3+ns4",
      "ns-type": "dynamic",
      "proxy": "cogent+telia",
      "ttl": 301,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "passport.yandex.net",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.99",
        "149.5.244.157"
      ],
      "fqdn": "dr.yandex.net.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "yandex.net",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.47",
        "149.5.244.73",
        "2001:978:7401::2",
        "2001:2030:20::2"
      ],
      "fqdn": "static.yandex.net.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "AAAA",
      "view": "VIEW_UA",
      "zone": "yandex.net",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.6",
        "149.5.244.26",
        "2001:2030:20::74",
        "2001:978:7401::74"
      ],
      "fqdn": "ns6.yandex.ru.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "AAAA",
      "view": "VIEW_UA",
      "zone": "yandex.ru",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.89",
        "149.5.244.83",
        "2a02:6b8::21b"
      ],
      "fqdn": "market.yandex.ua.",
      "ns": "ns3+ns4",
      "ns-type": "dynamic",
      "proxy": "cogent+telia",
      "ttl": 900,
      "type": "AAAA",
      "view": "VIEW_UA",
      "zone": "market.yandex.ua",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "149.5.244.202",
        "80.239.201.67"
      ],
      "fqdn": "kinopoisk.ru.",
      "ns": "ns3+ns4",
      "ns-type": "dynamic",
      "proxy": "cogent+telia",
      "ttl": 301,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "kinopoisk.ru",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "149.5.244.57",
        "80.239.201.123"
      ],
      "fqdn": "yandex.ru.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "yandex.ru",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.90",
        "149.5.244.2"
      ],
      "fqdn": "api.browser.yandex.ru.",
      "ns": "ns3+ns4",
      "ns-type": "dynamic",
      "proxy": "cogent+telia",
      "ttl": 301,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "browser.yandex.ru",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.100",
        "149.5.244.98"
      ],
      "fqdn": "z5h64q92x9.net.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "z5h64q92x9.net",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "149.5.244.2",
        "80.239.201.90"
      ],
      "fqdn": "tv.yandex.kz.",
      "ns": "ns3+ns4",
      "ns-type": "dynamic",
      "proxy": "cogent+telia",
      "ttl": 301,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "tv.yandex.kz",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.17",
        "149.5.244.4",
        "2a02:6b8::298"
      ],
      "fqdn": "fox.market.yandex.ua.",
      "ns": "ns3+ns4",
      "ns-type": "dynamic",
      "proxy": "cogent+telia",
      "ttl": 900,
      "type": "AAAA",
      "view": "VIEW_UA",
      "zone": "market.yandex.ua",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.47",
        "149.5.244.73"
      ],
      "fqdn": "cellar.z5h64q92x9.net.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "z5h64q92x9.net",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "149.5.244.251",
        "80.239.201.121"
      ],
      "fqdn": "mc.webvisor.com.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "webvisor.com",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.90",
        "149.5.244.2"
      ],
      "fqdn": "ext.captcha.yandex.net.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "yandex.net",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "149.5.244.73",
        "80.239.201.47",
        "2001:2030:20::2",
        "2001:978:7401::2"
      ],
      "fqdn": "yandex.st.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "AAAA",
      "view": "VIEW_UA",
      "zone": "yandex.st",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "149.5.244.63",
        "80.239.201.94"
      ],
      "fqdn": "mail-qloud.yandex.ru.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "yandex.ru",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.90",
        "149.5.244.2"
      ],
      "fqdn": "api.browser.yandex.com.",
      "ns": "ns3+ns4",
      "ns-type": "dynamic",
      "proxy": "cogent+telia",
      "ttl": 301,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "browser.yandex.com",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.121",
        "149.5.244.251"
      ],
      "fqdn": "metrika-informer.com.",
      "ns": "ns3+ns4",
      "ns-type": "dynamic",
      "proxy": "cogent+telia",
      "ttl": 301,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "metrika-informer.com",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "149.5.244.157",
        "80.239.201.99"
      ],
      "fqdn": "dr2.yandex.net.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "yandex.net",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.90",
        "149.5.244.2"
      ],
      "fqdn": "api.browser.yandex.by.",
      "ns": "ns3+ns4",
      "ns-type": "dynamic",
      "proxy": "cogent+telia",
      "ttl": 301,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "browser.yandex.by",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "149.5.244.118",
        "2a02:6b8::4:139"
      ],
      "fqdn": "spdy3-proxy.maps.yandex.net.",
      "ns": "ns3+ns4",
      "ns-type": "dynamic",
      "proxy": "cogent+telia",
      "ttl": 900,
      "type": "AAAA",
      "view": "VIEW_UA",
      "zone": "maps.yandex.net",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "149.5.244.63",
        "80.239.201.94"
      ],
      "fqdn": "mail.yandex.com.",
      "ns": "ns3+ns4",
      "ns-type": "dynamic",
      "proxy": "cogent+telia",
      "ttl": 301,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "mail.yandex.com",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.50",
        "149.5.244.209"
      ],
      "fqdn": "cloud-api.yandex.ua.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "yandex.ua",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.90",
        "149.5.244.2"
      ],
      "fqdn": "push.yandex.ua.",
      "ns": "ns3+ns4",
      "ns-type": "dynamic",
      "proxy": "cogent+telia",
      "ttl": 301,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "push.yandex.ua",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.47",
        "149.5.244.73",
        "2001:2030:20::2",
        "2001:978:7401::2"
      ],
      "fqdn": "static.yandex.sx.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 600,
      "type": "AAAA",
      "view": "VIEW_UA",
      "zone": "yandex.sx",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "149.5.244.2",
        "80.239.201.90"
      ],
      "fqdn": "tv.yandex.by.",
      "ns": "ns3+ns4",
      "ns-type": "dynamic",
      "proxy": "cogent+telia",
      "ttl": 301,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "tv.yandex.by",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "149.5.244.251",
        "80.239.201.121"
      ],
      "fqdn": "informer.yandex.ru.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "yandex.ru",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "149.5.244.2",
        "80.239.201.90"
      ],
      "fqdn": "avatars.mds.yandex.net.",
      "ns": "ns3+ns4",
      "ns-type": "dynamic",
      "proxy": "cogent+telia",
      "ttl": 301,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "mds.yandex.net",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.103",
        "149.5.244.190",
        "2001:2030:20::116",
        "2001:978:7401::116"
      ],
      "fqdn": "yastat.net.",
      "ns": "ns3+ns4",
      "ns-type": "dynamic",
      "proxy": "cogent+telia",
      "ttl": 301,
      "type": "AAAA",
      "view": "VIEW_UA",
      "zone": "yastat.net",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "149.5.244.251",
        "80.239.201.121"
      ],
      "fqdn": "ymetrica1.com.",
      "ns": "ns3+ns4",
      "ns-type": "dynamic",
      "proxy": "cogent+telia",
      "ttl": 301,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "ymetrica1.com",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.90",
        "149.5.244.2"
      ],
      "fqdn": "tv.yandex.ru.",
      "ns": "ns3+ns4",
      "ns-type": "dynamic",
      "proxy": "cogent+telia",
      "ttl": 301,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "tv.yandex.ru",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "149.5.244.219",
        "80.239.201.74"
      ],
      "fqdn": "mobileproxy.mobile.pssp.z5h64q92x9.net.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "z5h64q92x9.net",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "149.5.244.190",
        "80.239.201.103"
      ],
      "fqdn": "test-yastat.yandex.ua.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "yandex.ua",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "149.5.244.251",
        "80.239.201.121"
      ],
      "fqdn": "mc.webvisor.org.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "webvisor.org",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "149.5.244.2",
        "80.239.201.90"
      ],
      "fqdn": "api.browser.yandex.ua.",
      "ns": "ns3+ns4",
      "ns-type": "dynamic",
      "proxy": "cogent+telia",
      "ttl": 301,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "browser.yandex.ua",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "149.5.244.2",
        "80.239.201.90"
      ],
      "fqdn": "favicon.yandex.net.",
      "ns": "ns1+ns2",
      "ns-type": "static",
      "proxy": "cogent+telia",
      "ttl": 300,
      "type": "A",
      "view": "VIEW_UA",
      "zone": "yandex.net",
      "resolve": "resolve+native"
    },
    {
      "addresses": [
        "80.239.201.90",
        "149.5.244.2",
        "2a02:6b8::266"
      ],
      "fqdn": "addappter-api.mobile.yandex.net.",
      "ns": "ns3+ns4",
      "ns-type": "dynamic",
      "proxy": "cogent+telia",
      "ttl": 900,
      "type": "AAAA",
      "view": "VIEW_UA",
      "zone": "mobile.yandex.net",
      "resolve": "resolve+native"
    }
  ]
}"""
)


rtnmgr_mappings = json.loads(
    """
{
    "data": {
        "rotation_id": 224,
        "mappings": {
            "yandex.ru": [
              "80.239.201.123",
              "149.5.244.57"
            ],
            "www.yandex.ru": [
              "80.239.201.123",
              "149.5.244.57"
            ],
            "yandex.fr": [
              "80.239.201.123",
              "149.5.244.57"
            ],
            "yandex.ua": [
              "80.239.201.123",
              "149.5.244.57"
            ],
            "www.yandex.ua": [
              "80.239.201.123",
              "149.5.244.57"
            ],
            "test-yastat.yandex.ua": [
              "80.239.201.103",
              "149.5.244.190"
            ],
            "yastat.net": [
              "80.239.201.103",
              "149.5.244.190",
              "2001:2030:20::116",
              "2001:978:7401::116"
            ],
            "mc.webvisor.org": [
              "80.239.201.121",
              "149.5.244.251"
            ],
            "mc.yandex.ru": [
              "80.239.201.121",
              "149.5.244.251"
            ],
            "ymetrica.com": [
              "80.239.201.121",
              "149.5.244.251"
            ],
            "metrika-inf.com": [
              "80.239.201.121",
              "149.5.244.251"
            ],
            "informer.yandex.ru": [
              "80.239.201.121",
              "149.5.244.251"
            ],
            "mc.webvisor.com": [
              "80.239.201.121",
              "149.5.244.251"
            ],
            "metrika-informer.com": [
              "80.239.201.121",
              "149.5.244.251"
            ],
            "ymetrica2.com": [
              "80.239.201.121",
              "149.5.244.251"
            ],
            "ymetrica1.com": [
              "80.239.201.121",
              "149.5.244.251"
            ],
            "dr2.yandex.net": [
              "80.239.201.99",
              "149.5.244.157"
            ],
            "dr.yandex.net": [
              "80.239.201.99",
              "149.5.244.157"
            ],
            "an.webvisor.org": [
              "80.239.201.107",
              "149.5.244.183"
            ],
            "tv.yandex.kz": [
              "80.239.201.90",
              "149.5.244.2"
            ],
            "pdd.yandex.ru": [
              "80.239.201.90",
              "149.5.244.2"
            ],
            "api.browser.yandex.kz": [
              "80.239.201.90",
              "149.5.244.2"
            ],
            "push.yandex.ua": [
              "80.239.201.90",
              "149.5.244.2"
            ],
            "news.yandex.ru": [
              "80.239.201.90",
              "149.5.244.2"
            ],
            "push.yandex.ru": [
              "80.239.201.90",
              "149.5.244.2"
            ],
            "api.browser.yandex.ru": [
              "80.239.201.90",
              "149.5.244.2"
            ],
            "passport.yandex.ru": [
              "80.239.201.90",
              "149.5.244.2"
            ],
            "addappter-api.mobile.yandex.net": [
              "80.239.201.90",
              "149.5.244.2"
            ],
            "resize.yandex.net": [
              "80.239.201.90",
              "149.5.244.2"
            ],
            "oauth.yandex.ru": [
              "80.239.201.90",
              "149.5.244.2"
            ],
            "favicon.yandex.net": [
              "80.239.201.90",
              "149.5.244.2"
            ],
            "rosenberg.appmetrica.webvisor.com": [
              "80.239.201.90",
              "149.5.244.2"
            ],
            "tv.yandex.ua": [
              "80.239.201.90",
              "149.5.244.2"
            ],
            "api.browser.yandex.ua": [
              "80.239.201.90",
              "149.5.244.2"
            ],
            "launcher-cache.mobile.yandex.net": [
              "80.239.201.90",
              "149.5.244.2"
            ],
            "push.yandex.com": [
              "80.239.201.90",
              "149.5.244.2"
            ],
            "tv.yandex.ru": [
              "80.239.201.90",
              "149.5.244.2"
            ],
            "passport.yandex.com": [
              "80.239.201.90",
              "149.5.244.2"
            ],
            "redirect.appmetrica.webvisor.com": [
              "80.239.201.90",
              "149.5.244.2"
            ],
            "redirect.appmetrica.yandex.com": [
              "80.239.201.90",
              "149.5.244.2"
            ],
            "api.browser.yandex.com": [
              "80.239.201.90",
              "149.5.244.2"
            ],
            "report-2.appmetrica.webvisor.com": [
              "80.239.201.90",
              "149.5.244.2"
            ],
            "report-1.appmetrica.webvisor.com": [
              "80.239.201.90",
              "149.5.244.2"
            ],
            "dr.z5h64q92x9.net": [
              "80.239.201.90",
              "149.5.244.2"
            ],
            "api.browser.yandex.com.tr": [
              "80.239.201.90",
              "149.5.244.2"
            ],
            "avatars.mds.yandex.net": [
              "80.239.201.90",
              "149.5.244.2"
            ],
            "social.yandex.ru": [
              "80.239.201.90",
              "149.5.244.2"
            ],
            "tv.yandex.by": [
              "80.239.201.90",
              "149.5.244.2"
            ],
            "report.appmetrica.webvisor.com": [
              "80.239.201.90",
              "149.5.244.2"
            ],
            "api.browser.yandex.by": [
              "80.239.201.90",
              "149.5.244.2"
            ],
            "pass.yandex.ru": [
              "80.239.201.90",
              "149.5.244.2"
            ],
            "api.browser.yandex.net": [
              "80.239.201.90",
              "149.5.244.2"
            ],
            "ext.captcha.yandex.net": [
              "80.239.201.90",
              "149.5.244.2"
            ],
            "test-market.yandex.ua": [
              "80.239.201.89",
              "149.5.244.83"
            ],
            "market.yandex.ua": [
              "80.239.201.89",
              "149.5.244.83"
            ],
            "st.kp.yandex.net": [
              "80.239.201.65",
              "149.5.244.46"
            ],
            "yastatic.net": [
              "80.239.201.47",
              "149.5.244.73"
            ],
            "yandex.st": [
              "80.239.201.47",
              "149.5.244.73"
            ],
            "static.yandex.net": [
              "80.239.201.47",
              "149.5.244.73"
            ],
            "static.yandex.sx": [
              "80.239.201.47",
              "149.5.244.73"
            ],
            "loft.z5h64q92x9.net": [
              "80.239.201.47",
              "149.5.244.73"
            ],
            "cellar.z5h64q92x9.net": [
              "80.239.201.47",
              "149.5.244.73"
            ],
            "front.kp.yandex.net": [
              "80.239.201.67",
              "149.5.244.202"
            ],
            "kinopoisk.ru": [
              "80.239.201.67",
              "149.5.244.202"
            ],
            "smarttv-app.ott.yandex.ru": [
              "80.239.201.67",
              "149.5.244.202"
            ],
            "mail-qloud.yandex.ru": [
              "80.239.201.94",
              "149.5.244.63"
            ],
            "mail.yandex.fr": [
              "80.239.201.94",
              "149.5.244.63"
            ],
            "mail.yandex.com": [
              "80.239.201.94",
              "149.5.244.63"
            ],
            "mail.yandex.ua": [
              "80.239.201.94",
              "149.5.244.63"
            ],
            "mail.yandex.ru": [
              "80.239.201.94",
              "149.5.244.63"
            ],
            "ns6.yandex.ru": [
              "80.239.201.6",
              "149.5.244.26"
            ],
            "ns9.z5h64q92x9.net": [
              "80.239.201.9",
              "154.47.36.189"
            ],
            "ns7.yandex.ru": [
              "80.239.201.7",
              "149.5.244.182"
            ],
            "ns8.yandex.ru": [
              "80.239.201.8",
              "149.5.244.40"
            ],
            "proxy-mob-maps.yandex.ua": [
              "80.239.201.11",
              "149.5.244.169"
            ],
            "spdy3-proxy.maps.yandex.net": [
              "149.5.244.118"
            ],
            "spdy3.mob.map.yandex.net": [
              "149.5.244.118"
            ],
            "d.aws-proxy.disk.yandex.ua": [
              "80.239.201.48",
              "149.5.244.44"
            ],
            "m.aws-proxy.disk.yandex.ua": [
              "80.239.201.50",
              "149.5.244.209"
            ],
            "downloader.disk.yandex.ua": [
              "80.239.201.50",
              "149.5.244.209"
            ],
            "disk.yandex.ua": [
              "80.239.201.50",
              "149.5.244.209"
            ],
            "cloud-api.yandex.ua": [
              "80.239.201.50",
              "149.5.244.209"
            ],
            "z5h64q92x9.net": [
              "80.239.201.100",
              "149.5.244.98"
            ],
            "predictor.yandex.net": [
              "80.239.201.100",
              "149.5.244.98"
            ],
            "dictionary.yandex.net": [
              "80.239.201.100",
              "149.5.244.98"
            ],
            "translate.yandex.net": [
              "80.239.201.100",
              "149.5.244.98"
            ],
            "webattach-qloud.yandex.net": [
              "80.239.201.10",
              "149.5.244.205"
            ],
            "webattach.mail.yandex.net": [
              "80.239.201.10",
              "149.5.244.205"
            ],
            "mobileproxy.passport.yandex.net": [
              "80.239.201.74",
              "149.5.244.219"
            ],
            "mobileproxy.passport.yandex.ru": [
              "80.239.201.74",
              "149.5.244.219"
            ],
            "mobileproxy.mobile.pssp.smilink.ru": [
              "80.239.201.74",
              "149.5.244.219"
            ],
            "mobileproxy.mobile.pssp.z5h64q92x9.net": [
              "80.239.201.74",
              "149.5.244.219"
            ],
            "tracking.ott.yandex.ru": [
              "80.239.201.45",
              "149.5.244.34"
            ],
            "api.ott.yandex.ru": [
              "80.239.201.45",
              "149.5.244.34"
            ],
            "fenek.market.yandex.ua": [
              "80.239.201.17",
              "149.5.244.4"
            ],
            "fox.market.yandex.ua": [
              "80.239.201.17",
              "149.5.244.4"
            ],
            "market-click2.yandex.ua": [
              "80.239.201.82",
              "149.5.244.124"
            ],
            "mobileproxy-certificate.passport.yandex.ru": [
              "80.239.201.69",
              "149.5.244.171"
            ],
            "ads.adfox.ru": [
              "80.239.201.32",
              "149.5.244.246"
            ]
        },
        "ns_update_expected_time_minutes": 100,
        "expected_networks": [
            "80.239.201.0/25",
            "149.5.244.0/24",
            "154.47.36.0/24"
        ]
    },
    "code": 200,
    "status": "success",
    "error_message": null
}
"""
)
