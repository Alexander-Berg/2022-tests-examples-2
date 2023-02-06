import json


# TODO: remove after TRAFFIC-12138 has complete
RSD = json.loads(
  """{
    "error": {
      "log": "",
      "type": "",
      "level": "",
      "exception": ""
    },
    "status": {
      "MODIFIED": true,
      "LB_APPLIED": false,
      "NS_APPLIED": false,
      "NEW_MAPPINGS": false
    },
    "settings": {
      "stop_rotation": false,
      "mappings_update": {
        "enabled": true,
        "autorotation_minutes": 30,
        "external_ip_cooldown_hours": 0.001
      },
      "lb_update": {
        "enabled": true,
        "lb_update_expected_time_minutes": 1,
        "lb_ignore": [
          "test-lb.yndx.net"
        ]
      },
      "ns_update": {
        "enabled": true,
        "ns_update_expected_time_minutes": 0
      }
    },
    "providers": {
      "test": {
        "networks": [
          "10.0.0.0/24"
        ],
        "settings": {
          "rotate": false,
          "show_to_ns": false
        },
        "lb_apply_actual": [],
        "lb_apply_intention": [
          "test-lb.yndx.net"
        ]
      },
      "telia": {
        "networks": [
          "80.239.201.0/25"
        ],
        "settings": {
          "rotate": true,
          "show_to_ns": true
        },
        "lb_apply_actual": [],
        "lb_apply_intention": [
          "kiv-lb1.yndx.net",
          "rad-lb1.yndx.net"
        ]
      },
      "cogent": {
        "networks": [
          "149.5.244.0/24",
          "154.47.36.0/24"
        ],
        "settings": {
          "rotate": true,
          "show_to_ns": false
        },
        "lb_apply_actual": [],
        "lb_apply_intention": [
          "kiv-lb1.yndx.net",
          "rad-lb1.yndx.net"
        ]
      }
    },
    "version_id": 1597392277716749,
    "rotation_id": 1,
    "instance_id": "test",
    "rotation_state": {
      "test": {
        "domains": [
          "test.yandex.com"
        ],
        "int_ips": {
          "test": [
            "1.1.1.1"
          ]
        },
        "mappings": {
          "current": {
            "test": {
              "1.1.1.1": {
                "ext_ip": "10.0.0.115",
                "timestamp": "2020-07-23 11:09:28.414158"
              }
            }
          },
          "previous": {
            "test": {
              "1.1.1.1": {
                "ext_ip": "10.0.0.116",
                "timestamp": "2020-07-23 11:09:28.414158"
              }
            }
          }
        },
        "settings": {
          "rotate": true
        },
        "lb_current_ext_ips": [
        ],
        "ns_current_ext_ips": []
      },
      "mobileproxy.passport.yandex.net": {
        "domains": [
          "mobileproxy.passport.yandex.net",
          "mobileproxy.passport.yandex.ru",
          "mobileproxy.mobile.pssp.smilink.ru",
          "mobileproxy.mobile.pssp.z5h64q92x9.net"
        ],
        "int_ips": {
          "telia": [
            "5.45.202.36",
            "5.45.202.37"
          ],
          "cogent": [
            "5.45.202.34",
            "5.45.202.35"
          ]
        },
        "mappings": {
          "current": {
            "telia": {
              "5.45.202.36": {
                "ext_ip": "80.239.201.72",
                "timestamp": "2020-10-08 13:00:23.754765"
              }
            },
            "cogent": {
              "5.45.202.34": {
                "ext_ip": "149.5.244.229",
                "timestamp": "2020-10-08 13:00:23.754765"
              }
            }
          },
          "previous": {
            "telia": {
              "5.45.202.37": {
                "ext_ip": "80.239.201.101",
                "timestamp": "2020-10-08 11:56:14.550047"
              }
            },
            "cogent": {
              "5.45.202.35": {
                "ext_ip": "154.47.36.228",
                "timestamp": "2020-10-08 11:56:14.550047"
              }
            }
          }
        },
        "settings": {
          "rotate": true
        },
        "lb_current_ext_ips": [
          "80.239.201.72",
          "149.5.244.229"
        ]
      },
      "yandex.ua": {
        "domains": [
          "yandex.ru",
          "www.yandex.ru",
          "yandex.fr",
          "yandex.ua",
          "www.yandex.ua"
        ],
        "int_ips": {
          "telia": [
            "5.45.202.107",
            "5.45.202.106"
          ],
          "cogent": [
            "5.45.202.59",
            "5.45.202.58"
          ]
        },
        "mappings": {
          "current": {
            "telia": {
              "5.45.202.106": {
                "ext_ip": "80.239.201.94",
                "timestamp": "2020-10-08 13:00:23.754765"
              }
            },
            "cogent": {
              "5.45.202.59": {
                "ext_ip": "149.5.244.86",
                "timestamp": "2020-10-08 13:00:23.754765"
              }
            }
          },
          "previous": {
            "telia": {
              "5.45.202.107": {
                "ext_ip": "80.239.201.114",
                "timestamp": "2020-10-08 11:56:14.550047"
              }
            },
            "cogent": {
              "5.45.202.58": {
                "ext_ip": "154.47.36.223",
                "timestamp": "2020-10-08 11:56:14.550047"
              }
            }
          }
        },
        "settings": {
          "rotate": true
        },
        "lb_current_ext_ips": [
          "80.239.201.94",
          "149.5.244.86"
        ]
      },
      "yastat.net": {
        "domains": [
          "test-yastat.yandex.ua",
          "yastat.net"
        ],
        "int_ips": {
          "telia": [
            "5.45.202.118",
            "5.45.202.119"
          ],
          "cogent": [
            "5.45.202.116",
            "5.45.202.117"
          ]
        },
        "mappings": {
          "current": {
            "telia": {
              "5.45.202.118": {
                "ext_ip": "80.239.201.116",
                "timestamp": "2020-10-08 13:00:23.754765"
              }
            },
            "cogent": {
              "5.45.202.116": {
                "ext_ip": "149.5.244.195",
                "timestamp": "2020-10-08 13:00:23.754765"
              }
            }
          },
          "previous": {
            "telia": {
              "5.45.202.119": {
                "ext_ip": "80.239.201.62",
                "timestamp": "2020-10-08 11:56:14.550047"
              }
            },
            "cogent": {
              "5.45.202.117": {
                "ext_ip": "154.47.36.41",
                "timestamp": "2020-10-08 11:56:14.550047"
              }
            }
          }
        },
        "settings": {
          "rotate": true
        },
        "lb_current_ext_ips": [
          "80.239.201.116",
          "149.5.244.195"
        ]
      },
      "market.yandex.ua": {
        "domains": [
          "test-market.yandex.ua"
        ],
        "int_ips": {
          "telia": [
            "5.45.202.135",
            "5.45.202.134"
          ],
          "cogent": [
            "5.45.202.132",
            "5.45.202.133"
          ]
        },
        "mappings": {
          "current": {
            "telia": {
              "5.45.202.135": {
                "ext_ip": "80.239.201.107",
                "timestamp": "2020-10-08 13:00:23.754765"
              }
            },
            "cogent": {
              "5.45.202.132": {
                "ext_ip": "149.5.244.222",
                "timestamp": "2020-10-08 13:00:23.754765"
              }
            }
          },
          "previous": {
            "telia": {
              "5.45.202.134": {
                "ext_ip": "80.239.201.1",
                "timestamp": "2020-10-08 11:56:14.550047"
              }
            },
            "cogent": {
              "5.45.202.133": {
                "ext_ip": "154.47.36.246",
                "timestamp": "2020-10-08 11:56:14.550047"
              }
            }
          }
        },
        "settings": {
          "rotate": true
        },
        "lb_current_ext_ips": [
          "80.239.201.107",
          "149.5.244.222"
        ]
      },
      "proxy.yandex.ua": {
        "domains": [
          "tv.yandex.kz",
          "pdd.yandex.ru",
          "api.browser.yandex.kz",
          "push.yandex.ua",
          "news.yandex.ru",
          "push.yandex.ru",
          "api.browser.yandex.ru",
          "passport.yandex.ru",
          "updater.mobile.yandex.net",
          "addappter-api.mobile.yandex.net",
          "resize.yandex.net",
          "oauth.yandex.ru",
          "favicon.yandex.net",
          "rosenberg.appmetrica.webvisor.com",
          "tv.yandex.ua",
          "ads.adfox.ru",
          "login.adfox.ru",
          "api.browser.yandex.ua",
          "launcher-cache.mobile.yandex.net",
          "push.yandex.com",
          "tv.yandex.ru",
          "passport.yandex.com",
          "redirect.appmetrica.webvisor.com",
          "redirect.appmetrica.yandex.com",
          "api.browser.yandex.com",
          "report-2.appmetrica.webvisor.com",
          "report-1.appmetrica.webvisor.com",
          "dr.z5h64q92x9.net",
          "api.browser.yandex.com.tr",
          "avatars.mds.yandex.net",
          "social.yandex.ru",
          "tv.yandex.by",
          "report.appmetrica.webvisor.com",
          "api.browser.yandex.by",
          "pass.yandex.ru",
          "api.browser.yandex.net",
          "ext.captcha.yandex.net"
        ],
        "int_ips": {
          "telia": [
            "5.45.202.40",
            "5.45.202.41"
          ],
          "cogent": [
            "5.45.202.38",
            "5.45.202.39"
          ]
        },
        "mappings": {
          "current": {
            "telia": {
              "5.45.202.40": {
                "ext_ip": "80.239.201.47",
                "timestamp": "2020-10-08 13:00:23.754765"
              }
            },
            "cogent": {
              "5.45.202.39": {
                "ext_ip": "149.5.244.206",
                "timestamp": "2020-10-08 13:00:23.754765"
              }
            }
          },
          "previous": {
            "telia": {
              "5.45.202.41": {
                "ext_ip": "80.239.201.85",
                "timestamp": "2020-10-08 11:56:14.550047"
              }
            },
            "cogent": {
              "5.45.202.38": {
                "ext_ip": "154.47.36.16",
                "timestamp": "2020-10-08 11:56:14.550047"
              }
            }
          }
        },
        "settings": {
          "rotate": true
        },
        "lb_current_ext_ips": [
          "80.239.201.47",
          "149.5.244.206"
        ]
      },
      "d.aws-proxy.disk.yandex.ua": {
        "domains": [
          "d.aws-proxy.disk.yandex.ua"
        ],
        "int_ips": {
          "telia": [
            "5.45.202.24",
            "5.45.202.25"
          ],
          "cogent": [
            "5.45.202.22",
            "5.45.202.23"
          ]
        },
        "mappings": {
          "current": {
            "telia": {
              "5.45.202.25": {
                "ext_ip": "80.239.201.83",
                "timestamp": "2020-10-08 13:00:23.754765"
              }
            },
            "cogent": {
              "5.45.202.22": {
                "ext_ip": "149.5.244.95",
                "timestamp": "2020-10-08 13:00:23.754765"
              }
            }
          },
          "previous": {
            "telia": {
              "5.45.202.24": {
                "ext_ip": "80.239.201.99",
                "timestamp": "2020-10-08 11:56:14.550047"
              }
            },
            "cogent": {
              "5.45.202.23": {
                "ext_ip": "154.47.36.112",
                "timestamp": "2020-10-08 11:56:14.550047"
              }
            }
          }
        },
        "settings": {
          "rotate": true
        },
        "lb_current_ext_ips": [
          "80.239.201.83",
          "149.5.244.95"
        ]
      },
      "spdy3-proxy.maps.yandex.net": {
        "domains": [
          "old-spdy3-proxy.maps.yandex.net"
        ],
        "int_ips": {
          "cogent": [
            "5.45.202.43",
            "5.45.202.42"
          ]
        },
        "mappings": {
          "current": {
            "cogent": {
              "5.45.202.43": {
                "ext_ip": "149.5.244.65",
                "timestamp": "2019-04-17 08:00:05.803014"
              }
            }
          },
          "previous": {
            "cogent": {
              "5.45.202.42": {
                "ext_ip": "154.47.36.58",
                "timestamp": "2019-04-17 07:30:07.396740"
              }
            }
          }
        },
        "settings": {
          "rotate": false
        },
        "lb_current_ext_ips": [
          "149.5.244.65"
        ]
      },
      "uniproxy-rnd.alice.yandex.net": {
        "domains": [
          "uaproxy-uniproxy-rnd.alice.yandex.net"
        ],
        "int_ips": {
          "telia": [
            "5.45.202.153",
            "5.45.202.152"
          ],
          "cogent": [
            "5.45.202.150",
            "5.45.202.151"
          ]
        },
        "mappings": {
          "current": {
            "telia": {
              "5.45.202.152": {
                "ext_ip": "80.239.201.30",
                "timestamp": "2020-06-09 11:40:58.367760"
              }
            },
            "cogent": {
              "5.45.202.150": {
                "ext_ip": "154.47.36.7",
                "timestamp": "2020-06-09 11:07:28.033461"
              }
            }
          },
          "previous": {
            "telia": {
              "5.45.202.153": {
                "ext_ip": "80.239.201.28",
                "timestamp": "2020-06-09 10:04:04.021450"
              }
            },
            "cogent": {
              "5.45.202.151": {
                "ext_ip": "154.47.36.10",
                "timestamp": "2020-06-09 10:32:37.208833"
              }
            }
          }
        },
        "settings": {
          "rotate": false
        },
        "lb_current_ext_ips": [
          "80.239.201.30",
          "154.47.36.7"
        ]
      },
      "lalablah.z5h64q92x9.net": {
        "domains": [
          "lalablah.z5h64q92x9.net"
        ],
        "int_ips": {
          "cogent": [
            "5.45.202.13"
          ]
        },
        "mappings": {
          "current": {
            "cogent": {
              "5.45.202.13": {
                "ext_ip": "154.47.36.164",
                "timestamp": "2018-08-29 14:01:32.224217"
              }
            }
          },
          "previous": {
            "cogent": {}
          }
        },
        "settings": {
          "rotate": false
        },
        "lb_current_ext_ips": [
          "154.47.36.164"
        ]
      },
      "mail-qloud.yandex.ru": {
        "domains": [
          "mail-qloud.yandex.ru",
          "mail.yandex.fr",
          "mail.yandex.com",
          "mail.yandex.ua",
          "mail.yandex.ru"
        ],
        "int_ips": {
          "telia": [
            "5.45.202.89",
            "5.45.202.88"
          ],
          "cogent": [
            "5.45.202.87",
            "5.45.202.86"
          ]
        },
        "mappings": {
          "current": {
            "telia": {
              "5.45.202.88": {
                "ext_ip": "80.239.201.79",
                "timestamp": "2020-10-08 13:00:23.754765"
              }
            },
            "cogent": {
              "5.45.202.87": {
                "ext_ip": "149.5.244.149",
                "timestamp": "2020-10-08 13:00:23.754765"
              }
            }
          },
          "previous": {
            "telia": {
              "5.45.202.89": {
                "ext_ip": "80.239.201.46",
                "timestamp": "2020-10-08 11:56:14.550047"
              }
            },
            "cogent": {
              "5.45.202.86": {
                "ext_ip": "154.47.36.24",
                "timestamp": "2020-10-08 11:56:14.550047"
              }
            }
          }
        },
        "settings": {
          "rotate": true
        },
        "lb_current_ext_ips": [
          "80.239.201.79",
          "149.5.244.149"
        ]
      },
      "static.yandex.net": {
        "domains": [
          "yastatic.net",
          "yandex.st",
          "static.yandex.net",
          "static.yandex.sx",
          "loft.z5h64q92x9.net",
          "cellar.z5h64q92x9.net"
        ],
        "int_ips": {
          "telia": [
            "5.45.202.3",
            "5.45.202.4"
          ],
          "cogent": [
            "5.45.202.1",
            "5.45.202.2"
          ]
        },
        "mappings": {
          "current": {
            "telia": {
              "5.45.202.3": {
                "ext_ip": "80.239.201.21",
                "timestamp": "2020-10-08 13:00:23.754765"
              }
            },
            "cogent": {
              "5.45.202.1": {
                "ext_ip": "149.5.244.154",
                "timestamp": "2020-10-08 13:00:23.754765"
              }
            }
          },
          "previous": {
            "telia": {
              "5.45.202.4": {
                "ext_ip": "80.239.201.118",
                "timestamp": "2020-10-08 11:56:14.550047"
              }
            },
            "cogent": {
              "5.45.202.2": {
                "ext_ip": "154.47.36.48",
                "timestamp": "2020-10-08 11:56:14.550047"
              }
            }
          }
        },
        "settings": {
          "rotate": true
        },
        "lb_current_ext_ips": [
          "80.239.201.21",
          "149.5.244.154"
        ]
      },
      "front.kp.yandex.net": {
        "domains": [
          "front.kp.yandex.net",
          "kinopoisk.ru"
        ],
        "int_ips": {
          "telia": [
            "5.45.202.124",
            "5.45.202.125"
          ],
          "cogent": [
            "5.45.202.123",
            "5.45.202.122"
          ]
        },
        "mappings": {
          "current": {
            "telia": {
              "5.45.202.124": {
                "ext_ip": "80.239.201.119",
                "timestamp": "2020-10-08 13:00:23.754765"
              }
            },
            "cogent": {
              "5.45.202.123": {
                "ext_ip": "149.5.244.120",
                "timestamp": "2020-10-08 13:00:23.754765"
              }
            }
          },
          "previous": {
            "telia": {
              "5.45.202.125": {
                "ext_ip": "80.239.201.45",
                "timestamp": "2020-10-08 11:56:14.550047"
              }
            },
            "cogent": {
              "5.45.202.122": {
                "ext_ip": "154.47.36.153",
                "timestamp": "2020-10-08 11:56:14.550047"
              }
            }
          }
        },
        "settings": {
          "rotate": true
        },
        "lb_current_ext_ips": [
          "80.239.201.119",
          "149.5.244.120"
        ]
      },
      "tpx.maps.yandex.net": {
        "domains": [
          "old-tpx.maps.yandex.net"
        ],
        "int_ips": {
          "telia": [
            "5.45.202.50",
            "5.45.202.51"
          ]
        },
        "mappings": {
          "current": {
            "telia": {
              "5.45.202.51": {
                "ext_ip": "80.239.201.51",
                "timestamp": "2019-04-17 19:30:06.322480"
              }
            }
          },
          "previous": {
            "telia": {
              "5.45.202.50": {
                "ext_ip": "80.239.201.39",
                "timestamp": "2019-04-17 19:00:07.243179"
              }
            }
          }
        },
        "settings": {
          "rotate": false
        },
        "lb_current_ext_ips": [
          "80.239.201.51"
        ]
      },
      "aws-proxy.translate.yandex.net": {
        "domains": [
          "dictionary.yandex.net",
          "translate.yandex.net",
          "z5h64q92x9.net",
          "predictor.yandex.net"
        ],
        "int_ips": {
          "telia": [
            "5.45.202.18",
            "5.45.202.17"
          ],
          "cogent": [
            "5.45.202.20",
            "5.45.202.19"
          ]
        },
        "mappings": {
          "current": {
            "telia": {
              "5.45.202.17": {
                "ext_ip": "80.239.201.35",
                "timestamp": "2020-10-08 13:00:23.754765"
              }
            },
            "cogent": {
              "5.45.202.20": {
                "ext_ip": "149.5.244.208",
                "timestamp": "2020-10-08 13:00:23.754765"
              }
            }
          },
          "previous": {
            "telia": {
              "5.45.202.18": {
                "ext_ip": "80.239.201.104",
                "timestamp": "2020-10-08 11:56:14.550047"
              }
            },
            "cogent": {
              "5.45.202.19": {
                "ext_ip": "154.47.36.181",
                "timestamp": "2020-10-08 11:56:14.550047"
              }
            }
          }
        },
        "settings": {
          "rotate": true
        },
        "lb_current_ext_ips": [
          "80.239.201.35",
          "149.5.244.208"
        ]
      },
      "pool.with.static.mapping": {
        "domains": [
          "uaproxy-ns21.yandex.net",
          "ns8.yandex.ru"
        ],
        "int_ips": {
          "telia": [
            "5.45.202.70",
            "5.45.202.253"
          ],
          "cogent": [
            "5.45.202.71",
            "5.45.202.252",
            "::1",
            "::2"
          ]
        },
        "mappings": {
          "static": {
            "telia": {
              "5.45.202.253": {
                "ext_ip": "80.239.201.127",
                "timestamp": ""
              }
            },
            "cogent": {
              "5.45.202.252": {
                "ext_ip": "149.5.244.254",
                "timestamp": ""
              },
              "::1": {
                "ext_ip": "fdf8:f53b:82e4::53",
                "timestamp": "2021-06-03 13:30:39.509797"
              },
              "::2": {
                "ext_ip": "fdf8:f53b:82e4::543",
                "timestamp": "2021-06-03 13:30:39.509797"
              }
            }
          },
          "current": {
            "telia": {
              "5.45.202.70": {
                "ext_ip": "80.239.201.8",
                "timestamp": "2018-08-15 11:44:42.615406"
              }
            },
            "cogent": {
              "5.45.202.71": {
                "ext_ip": "149.5.244.40",
                "timestamp": "2018-08-15 12:01:40.940674"
              }
            }
          },
          "previous": {
            "telia": {},
            "cogent": {}
          }
        },
        "settings": {
          "rotate": false
        },
        "lb_current_ext_ips": [
          "80.239.201.8",
          "149.5.244.40"
        ]
      },
      "pool.with.static.mapping.new": {
        "domains": [
          "test-uaproxy-ns21.yandex.net",
          "test-ns8.yandex.ru"
        ],
        "int_ips": {
          "telia": [
            "5.45.202.72",
            "5.45.202.250"
          ],
          "cogent": [
            "5.45.202.73",
            "5.45.202.251"
          ]
        },
        "mappings": {
          "static": {
            "telia": {
              "5.45.202.250": {
                "ext_ip": "80.239.201.126",
                "timestamp": ""
              }
            },
            "cogent": {
              "5.45.202.251": {
                "ext_ip": "149.5.244.253",
                "timestamp": ""
              }
            }
          }
        },
        "settings": {
          "rotate": true
        },
        "lb_current_ext_ips": [
          "80.239.201.8",
          "149.5.244.40"
        ]
      }
    }
  }"""
)


RSD_YANDEX_TEST = {
    "error": {
      "log": "",
      "data": "",
      "type": "",
      "level": "",
      "exception": ""
    },
    "status": {
      "MODIFIED": True,
      "LB_APPLIED": True,
      "NS_APPLIED": True,
      "NEW_MAPPINGS": True
    },
    "settings": {
      "lb_update": {
        "enabled": False,
        "lb_ignore": [],
        "lb_update_expected_time_minutes": 0
      },
      "ns_update": {
        "enabled": False,
        "ns_update_expected_time_minutes": 10
      },
      "stop_rotation": False,
      "mappings_update": {
        "enabled": True,
        "autorotation_minutes": 60,
        "external_ip_cooldown_hours": 0.001
      },
       "views": [
        "world"
      ]
    },
    "providers": {
      "pool1": {
        "networks": [
          "5.255.255.5/32",
          "5.255.255.50/32",
          "5.255.255.55/32",
          "5.255.255.60/32",
          "5.255.255.70/32",
          "5.255.255.77/32",
          "5.255.255.80/32",
          "5.255.255.88/32"
        ],
        "settings": {
          "rotate": True,
          "show_to_ns": True
        },
        "lb_apply_actual": [],
        "lb_apply_intention": []
      },
      "pool2": {
        "networks": [
          "77.88.55.50/32",
          "77.88.55.55/32",
          "77.88.55.60/32",
          "77.88.55.66/32",
          "77.88.55.70/32",
          "77.88.55.77/32",
          "77.88.55.80/32",
          "77.88.55.88/32"
        ],
        "settings": {
          "rotate": True,
          "show_to_ns": True
        },
        "lb_apply_actual": [],
        "lb_apply_intention": []
      }
    },
    "version_id": 1614190060094008,
    "instance_id": "yandex_integ_test",
    "rotation_id": 1,
    "rotation_state": {
      "yandex.ru": {
        "views": {
          "world": [
            "yandex.ru"
          ]
        },
        "int_ips": {
          "pool1": [
            "0.0.0.1",
            "0.0.0.2",
            "0.0.0.3",
            "0.0.0.4",
            "::1"
          ],
          "pool2": [
            "0.0.0.5",
            "0.0.0.6",
            "0.0.0.7",
            "0.0.0.8",
            "::2"
          ]
        },
        "mappings": {
          "current": {
            "pool1": {
              "0.0.0.3": {
                "ext_ip": "5.255.255.55",
                "timestamp": "2021-02-24 18:07:40.094008"
              },
              "0.0.0.4": {
                "ext_ip": "5.255.255.88",
                "timestamp": "2021-02-24 18:07:40.094008"
              }
            },
            "pool2": {
              "0.0.0.5": {
                "ext_ip": "77.88.55.55",
                "timestamp": "2021-02-24 18:07:40.094008"
              },
              "0.0.0.6": {
                "ext_ip": "77.88.55.50",
                "timestamp": "2021-02-24 18:07:40.094008"
              }
            }
          },
          "previous": {
            "pool1": {
              "0.0.0.1": {
                "ext_ip": "5.255.255.5",
                "timestamp": "2021-02-24 18:07:38.277717"
              },
              "0.0.0.2": {
                "ext_ip": "5.255.255.50",
                "timestamp": "2021-02-24 18:07:38.277717"
              }
            },
            "pool2": {
              "0.0.0.7": {
                "ext_ip": "77.88.55.66",
                "timestamp": "2021-02-24 18:07:38.277717"
              },
              "0.0.0.8": {
                "ext_ip": "77.88.55.60",
                "timestamp": "2021-02-24 18:07:38.277717"
              }
            }
          },
          "static": {
            "pool1": {
              "::1": {
                "ext_ip": "fdf8:f53b:82e4::53",
                "timestamp": "2021-06-03 13:30:39.509797"
              }
            },
            "pool2": {
              "::2": {
                "ext_ip": "fdf8:f53b:82e4::543",
                "timestamp": "2021-06-03 13:30:39.509797"
              }
            }
          }
        },
        "settings": {
          "rotate": True,
          "ns_tracking": True
        },
        "lb_current_ext_ips": [],
        "ns_current_ext_ips": []
      }
    }
  }


RSD_VIEWS_TEST = json.loads("""{
    "error": {
        "log": "",
        "type": "",
        "level": "",
        "exception": ""
    },
    "status": {
        "MODIFIED": true,
        "LB_APPLIED": false,
        "NS_APPLIED": false,
        "NEW_MAPPINGS": false
    },
    "settings": {
        "stop_rotation": false,
        "mappings_update": {
            "enabled": true,
            "autorotation_minutes": 30,
            "external_ip_cooldown_hours": 0.001
        },
        "lb_update": {
            "enabled": true,
            "lb_update_expected_time_minutes": 1,
            "lb_ignore": [
                "test-lb.yndx.net"
            ]
        },
        "ns_update": {
            "enabled": true,
            "ns_update_expected_time_minutes": 0
        },
        "views": [
            "ua",
            "world"
        ]
    },
    "providers": {
        "test": {
            "networks": [
                "10.0.0.0/24"
            ],
            "settings": {
                "rotate": false,
                "show_to_ns": false
            },
            "lb_apply_actual": [],
            "lb_apply_intention": [
                "test-lb.yndx.net"
            ]
        },
        "telia": {
            "networks": [
                "80.239.201.0/25"
            ],
            "settings": {
                "rotate": true,
                "show_to_ns": true
            },
            "lb_apply_actual": [],
            "lb_apply_intention": [
                "kiv-lb1.yndx.net",
                "rad-lb1.yndx.net"
            ]
        },
        "cogent": {
            "networks": [
                "149.5.244.0/24",
                "154.47.36.0/24"
            ],
            "settings": {
                "rotate": true,
                "show_to_ns": false
            },
            "lb_apply_actual": [],
            "lb_apply_intention": [
                "kiv-lb1.yndx.net",
                "rad-lb1.yndx.net"
            ]
        }
    },
    "version_id": 1597392277716749,
    "rotation_id": 1,
    "instance_id": "test",
    "rotation_state": {
        "test": {
            "int_ips": {
                "test": [
                    "1.1.1.1"
                ]
            },
            "mappings": {
                "current": {
                    "test": {
                        "1.1.1.1": {
                            "ext_ip": "10.0.0.115",
                            "timestamp": "2020-07-23 11:09:28.414158"
                        }
                    }
                },
                "previous": {
                    "test": {
                        "1.1.1.1": {
                            "ext_ip": "10.0.0.116",
                            "timestamp": "2020-07-23 11:09:28.414158"
                        }
                    }
                }
            },
            "settings": {
                "rotate": true
            },
            "lb_current_ext_ips": [],
            "ns_current_ext_ips": [],
            "views": {
                "ua": [
                    "test.yandex.com"
                ]
            }
        },
        "mobileproxy.passport.yandex.net": {
            "int_ips": {
                "telia": [
                    "5.45.202.36",
                    "5.45.202.37"
                ],
                "cogent": [
                    "5.45.202.34",
                    "5.45.202.35"
                ]
            },
            "mappings": {
                "current": {
                    "telia": {
                        "5.45.202.36": {
                            "ext_ip": "80.239.201.72",
                            "timestamp": "2020-10-08 13:00:23.754765"
                        }
                    },
                    "cogent": {
                        "5.45.202.34": {
                            "ext_ip": "149.5.244.229",
                            "timestamp": "2020-10-08 13:00:23.754765"
                        }
                    }
                },
                "previous": {
                    "telia": {
                        "5.45.202.37": {
                            "ext_ip": "80.239.201.101",
                            "timestamp": "2020-10-08 11:56:14.550047"
                        }
                    },
                    "cogent": {
                        "5.45.202.35": {
                            "ext_ip": "154.47.36.228",
                            "timestamp": "2020-10-08 11:56:14.550047"
                        }
                    }
                }
            },
            "settings": {
                "rotate": true
            },
            "lb_current_ext_ips": [
                "80.239.201.72",
                "149.5.244.229"
            ],
            "views": {
                "ua": [
                    "mobileproxy.passport.yandex.net",
                    "mobileproxy.passport.yandex.ru",
                    "mobileproxy.mobile.pssp.smilink.ru",
                    "mobileproxy.mobile.pssp.z5h64q92x9.net"
                ],
                "world": [
                    "mobileproxy.passport.yandex.net",
                    "mobileproxy.mobile.pssp.smilink.ru",
                    "mobileproxy.mobile.pssp.z5h64q92x9.net"
                ]
            }
        },
        "yandex.ua": {
            "int_ips": {
                "telia": [
                    "5.45.202.107",
                    "5.45.202.106"
                ],
                "cogent": [
                    "5.45.202.59",
                    "5.45.202.58"
                ]
            },
            "mappings": {
                "current": {
                    "telia": {
                        "5.45.202.106": {
                            "ext_ip": "80.239.201.94",
                            "timestamp": "2020-10-08 13:00:23.754765"
                        }
                    },
                    "cogent": {
                        "5.45.202.59": {
                            "ext_ip": "149.5.244.86",
                            "timestamp": "2020-10-08 13:00:23.754765"
                        }
                    }
                },
                "previous": {
                    "telia": {
                        "5.45.202.107": {
                            "ext_ip": "80.239.201.114",
                            "timestamp": "2020-10-08 11:56:14.550047"
                        }
                    },
                    "cogent": {
                        "5.45.202.58": {
                            "ext_ip": "154.47.36.223",
                            "timestamp": "2020-10-08 11:56:14.550047"
                        }
                    }
                }
            },
            "settings": {
                "rotate": true
            },
            "lb_current_ext_ips": [
                "80.239.201.94",
                "149.5.244.86"
            ],
            "views": {
                "ua": [
                    "yandex.ru",
                    "www.yandex.ru",
                    "yandex.fr",
                    "yandex.ua",
                    "www.yandex.ua"
                ],
                "world": [
                    "yandex.ua",
                    "www.yandex.ua"
                ]
            }
        },
        "yastat.net": {
            "int_ips": {
                "telia": [
                    "5.45.202.118",
                    "5.45.202.119"
                ],
                "cogent": [
                    "5.45.202.116",
                    "5.45.202.117"
                ]
            },
            "mappings": {
                "current": {
                    "telia": {
                        "5.45.202.118": {
                            "ext_ip": "80.239.201.116",
                            "timestamp": "2020-10-08 13:00:23.754765"
                        }
                    },
                    "cogent": {
                        "5.45.202.116": {
                            "ext_ip": "149.5.244.195",
                            "timestamp": "2020-10-08 13:00:23.754765"
                        }
                    }
                },
                "previous": {
                    "telia": {
                        "5.45.202.119": {
                            "ext_ip": "80.239.201.62",
                            "timestamp": "2020-10-08 11:56:14.550047"
                        }
                    },
                    "cogent": {
                        "5.45.202.117": {
                            "ext_ip": "154.47.36.41",
                            "timestamp": "2020-10-08 11:56:14.550047"
                        }
                    }
                }
            },
            "settings": {
                "rotate": true
            },
            "lb_current_ext_ips": [
                "80.239.201.116",
                "149.5.244.195"
            ],
            "views": {
                "ua": [
                    "test-yastat.yandex.ua",
                    "yastat.net"
                ],
                "world": [
                    "test-yastat.yandex.ua",
                    "yastat.net"
                ]
            }
        },
        "market.yandex.ua": {
            "int_ips": {
                "telia": [
                    "5.45.202.135",
                    "5.45.202.134"
                ],
                "cogent": [
                    "5.45.202.132",
                    "5.45.202.133"
                ]
            },
            "mappings": {
                "current": {
                    "telia": {
                        "5.45.202.135": {
                            "ext_ip": "80.239.201.107",
                            "timestamp": "2020-10-08 13:00:23.754765"
                        }
                    },
                    "cogent": {
                        "5.45.202.132": {
                            "ext_ip": "149.5.244.222",
                            "timestamp": "2020-10-08 13:00:23.754765"
                        }
                    }
                },
                "previous": {
                    "telia": {
                        "5.45.202.134": {
                            "ext_ip": "80.239.201.1",
                            "timestamp": "2020-10-08 11:56:14.550047"
                        }
                    },
                    "cogent": {
                        "5.45.202.133": {
                            "ext_ip": "154.47.36.246",
                            "timestamp": "2020-10-08 11:56:14.550047"
                        }
                    }
                }
            },
            "settings": {
                "rotate": true
            },
            "lb_current_ext_ips": [
                "80.239.201.107",
                "149.5.244.222"
            ],
            "views": {
                "ua": [
                    "test-market.yandex.ua"
                ]
            }
        },
        "proxy.yandex.ua": {
            "int_ips": {
                "telia": [
                    "5.45.202.40",
                    "5.45.202.41"
                ],
                "cogent": [
                    "5.45.202.38",
                    "5.45.202.39"
                ]
            },
            "mappings": {
                "current": {
                    "telia": {
                        "5.45.202.40": {
                            "ext_ip": "80.239.201.47",
                            "timestamp": "2020-10-08 13:00:23.754765"
                        }
                    },
                    "cogent": {
                        "5.45.202.39": {
                            "ext_ip": "149.5.244.206",
                            "timestamp": "2020-10-08 13:00:23.754765"
                        }
                    }
                },
                "previous": {
                    "telia": {
                        "5.45.202.41": {
                            "ext_ip": "80.239.201.85",
                            "timestamp": "2020-10-08 11:56:14.550047"
                        }
                    },
                    "cogent": {
                        "5.45.202.38": {
                            "ext_ip": "154.47.36.16",
                            "timestamp": "2020-10-08 11:56:14.550047"
                        }
                    }
                }
            },
            "settings": {
                "rotate": true
            },
            "lb_current_ext_ips": [
                "80.239.201.47",
                "149.5.244.206"
            ],
            "views": {
                "ua": [
                    "tv.yandex.kz",
                    "pdd.yandex.ru",
                    "api.browser.yandex.kz",
                    "push.yandex.ua",
                    "news.yandex.ru",
                    "push.yandex.ru",
                    "api.browser.yandex.ru",
                    "passport.yandex.ru",
                    "updater.mobile.yandex.net",
                    "addappter-api.mobile.yandex.net",
                    "resize.yandex.net",
                    "oauth.yandex.ru",
                    "favicon.yandex.net",
                    "rosenberg.appmetrica.webvisor.com",
                    "tv.yandex.ua",
                    "ads.adfox.ru",
                    "login.adfox.ru",
                    "api.browser.yandex.ua",
                    "launcher-cache.mobile.yandex.net",
                    "push.yandex.com",
                    "tv.yandex.ru",
                    "passport.yandex.com",
                    "redirect.appmetrica.webvisor.com",
                    "redirect.appmetrica.yandex.com",
                    "api.browser.yandex.com",
                    "report-2.appmetrica.webvisor.com",
                    "report-1.appmetrica.webvisor.com",
                    "dr.z5h64q92x9.net",
                    "api.browser.yandex.com.tr",
                    "avatars.mds.yandex.net",
                    "social.yandex.ru",
                    "tv.yandex.by",
                    "report.appmetrica.webvisor.com",
                    "api.browser.yandex.by",
                    "pass.yandex.ru",
                    "api.browser.yandex.net",
                    "ext.captcha.yandex.net"
                ],
                "world": [
                    "tv.yandex.kz",
                    "push.yandex.ua",
                    "news.yandex.ru",
                    "push.yandex.ru",
                    "api.browser.yandex.ru",
                    "passport.yandex.ru",
                    "updater.mobile.yandex.net",
                    "addappter-api.mobile.yandex.net",
                    "rosenberg.appmetrica.webvisor.com",
                    "launcher-cache.mobile.yandex.net",
                    "redirect.appmetrica.yandex.com",
                    "api.browser.yandex.com",
                    "report-2.appmetrica.webvisor.com",
                    "report-1.appmetrica.webvisor.com",
                    "dr.z5h64q92x9.net",
                    "avatars.mds.yandex.net",
                    "social.yandex.ru",
                    "tv.yandex.by"
                ]
            }
        },
        "d.aws-proxy.disk.yandex.ua": {
            "int_ips": {
                "telia": [
                    "5.45.202.24",
                    "5.45.202.25"
                ],
                "cogent": [
                    "5.45.202.22",
                    "5.45.202.23"
                ]
            },
            "mappings": {
                "current": {
                    "telia": {
                        "5.45.202.25": {
                            "ext_ip": "80.239.201.83",
                            "timestamp": "2020-10-08 13:00:23.754765"
                        }
                    },
                    "cogent": {
                        "5.45.202.22": {
                            "ext_ip": "149.5.244.95",
                            "timestamp": "2020-10-08 13:00:23.754765"
                        }
                    }
                },
                "previous": {
                    "telia": {
                        "5.45.202.24": {
                            "ext_ip": "80.239.201.99",
                            "timestamp": "2020-10-08 11:56:14.550047"
                        }
                    },
                    "cogent": {
                        "5.45.202.23": {
                            "ext_ip": "154.47.36.112",
                            "timestamp": "2020-10-08 11:56:14.550047"
                        }
                    }
                }
            },
            "settings": {
                "rotate": true
            },
            "lb_current_ext_ips": [
                "80.239.201.83",
                "149.5.244.95"
            ],
            "views": {
                "ua": [
                    "d.aws-proxy.disk.yandex.ua"
                ]
            }
        },
        "spdy3-proxy.maps.yandex.net": {
            "int_ips": {
                "cogent": [
                    "5.45.202.43",
                    "5.45.202.42"
                ]
            },
            "mappings": {
                "current": {
                    "cogent": {
                        "5.45.202.43": {
                            "ext_ip": "149.5.244.65",
                            "timestamp": "2019-04-17 08:00:05.803014"
                        }
                    }
                },
                "previous": {
                    "cogent": {
                        "5.45.202.42": {
                            "ext_ip": "154.47.36.58",
                            "timestamp": "2019-04-17 07:30:07.396740"
                        }
                    }
                }
            },
            "settings": {
                "rotate": false
            },
            "lb_current_ext_ips": [
                "149.5.244.65"
            ],
            "views": {
                "ua": [
                    "old-spdy3-proxy.maps.yandex.net"
                ]
            }
        },
        "uniproxy-rnd.alice.yandex.net": {
            "int_ips": {
                "telia": [
                    "5.45.202.153",
                    "5.45.202.152"
                ],
                "cogent": [
                    "5.45.202.150",
                    "5.45.202.151"
                ]
            },
            "mappings": {
                "current": {
                    "telia": {
                        "5.45.202.152": {
                            "ext_ip": "80.239.201.30",
                            "timestamp": "2020-06-09 11:40:58.367760"
                        }
                    },
                    "cogent": {
                        "5.45.202.150": {
                            "ext_ip": "154.47.36.7",
                            "timestamp": "2020-06-09 11:07:28.033461"
                        }
                    }
                },
                "previous": {
                    "telia": {
                        "5.45.202.153": {
                            "ext_ip": "80.239.201.28",
                            "timestamp": "2020-06-09 10:04:04.021450"
                        }
                    },
                    "cogent": {
                        "5.45.202.151": {
                            "ext_ip": "154.47.36.10",
                            "timestamp": "2020-06-09 10:32:37.208833"
                        }
                    }
                }
            },
            "settings": {
                "rotate": false
            },
            "lb_current_ext_ips": [
                "80.239.201.30",
                "154.47.36.7"
            ],
            "views": {
                "ua": [
                    "uaproxy-uniproxy-rnd.alice.yandex.net"
                ],
                "world": [
                    "uaproxy-uniproxy-rnd.alice.yandex.net"
                ]
            }
        },
        "lalablah.z5h64q92x9.net": {
            "int_ips": {
                "cogent": [
                    "5.45.202.13"
                ]
            },
            "mappings": {
                "current": {
                    "cogent": {
                        "5.45.202.13": {
                            "ext_ip": "154.47.36.164",
                            "timestamp": "2018-08-29 14:01:32.224217"
                        }
                    }
                },
                "previous": {
                    "cogent": {}
                }
            },
            "settings": {
                "rotate": false
            },
            "lb_current_ext_ips": [
                "154.47.36.164"
            ],
            "views": {
                "ua": [
                    "lalablah.z5h64q92x9.net"
                ],
                "world": [
                    "lalablah.z5h64q92x9.net"
                ]
            }
        },
        "mail-qloud.yandex.ru": {
            "int_ips": {
                "telia": [
                    "5.45.202.89",
                    "5.45.202.88"
                ],
                "cogent": [
                    "5.45.202.87",
                    "5.45.202.86"
                ]
            },
            "mappings": {
                "current": {
                    "telia": {
                        "5.45.202.88": {
                            "ext_ip": "80.239.201.79",
                            "timestamp": "2020-10-08 13:00:23.754765"
                        }
                    },
                    "cogent": {
                        "5.45.202.87": {
                            "ext_ip": "149.5.244.149",
                            "timestamp": "2020-10-08 13:00:23.754765"
                        }
                    }
                },
                "previous": {
                    "telia": {
                        "5.45.202.89": {
                            "ext_ip": "80.239.201.46",
                            "timestamp": "2020-10-08 11:56:14.550047"
                        }
                    },
                    "cogent": {
                        "5.45.202.86": {
                            "ext_ip": "154.47.36.24",
                            "timestamp": "2020-10-08 11:56:14.550047"
                        }
                    }
                }
            },
            "settings": {
                "rotate": true
            },
            "lb_current_ext_ips": [
                "80.239.201.79",
                "149.5.244.149"
            ],
            "views": {
                "ua": [
                    "mail-qloud.yandex.ru",
                    "mail.yandex.fr",
                    "mail.yandex.com",
                    "mail.yandex.ua",
                    "mail.yandex.ru"
                ],
                "world": [
                    "mail-qloud.yandex.ru",
                    "mail.yandex.ru"
                ]
            }
        },
        "static.yandex.net": {
            "int_ips": {
                "telia": [
                    "5.45.202.3",
                    "5.45.202.4"
                ],
                "cogent": [
                    "5.45.202.1",
                    "5.45.202.2"
                ]
            },
            "mappings": {
                "current": {
                    "telia": {
                        "5.45.202.3": {
                            "ext_ip": "80.239.201.21",
                            "timestamp": "2020-10-08 13:00:23.754765"
                        }
                    },
                    "cogent": {
                        "5.45.202.1": {
                            "ext_ip": "149.5.244.154",
                            "timestamp": "2020-10-08 13:00:23.754765"
                        }
                    }
                },
                "previous": {
                    "telia": {
                        "5.45.202.4": {
                            "ext_ip": "80.239.201.118",
                            "timestamp": "2020-10-08 11:56:14.550047"
                        }
                    },
                    "cogent": {
                        "5.45.202.2": {
                            "ext_ip": "154.47.36.48",
                            "timestamp": "2020-10-08 11:56:14.550047"
                        }
                    }
                }
            },
            "settings": {
                "rotate": true
            },
            "lb_current_ext_ips": [
                "80.239.201.21",
                "149.5.244.154"
            ],
            "views": {
                "ua": [
                    "yastatic.net",
                    "yandex.st",
                    "static.yandex.net",
                    "static.yandex.sx",
                    "loft.z5h64q92x9.net",
                    "cellar.z5h64q92x9.net"
                ],
                "world": [
                    "yastatic.net",
                    "yandex.st",
                    "cellar.z5h64q92x9.net"
                ]
            }
        },
        "front.kp.yandex.net": {
            "int_ips": {
                "telia": [
                    "5.45.202.124",
                    "5.45.202.125"
                ],
                "cogent": [
                    "5.45.202.123",
                    "5.45.202.122"
                ]
            },
            "mappings": {
                "current": {
                    "telia": {
                        "5.45.202.124": {
                            "ext_ip": "80.239.201.119",
                            "timestamp": "2020-10-08 13:00:23.754765"
                        }
                    },
                    "cogent": {
                        "5.45.202.123": {
                            "ext_ip": "149.5.244.120",
                            "timestamp": "2020-10-08 13:00:23.754765"
                        }
                    }
                },
                "previous": {
                    "telia": {
                        "5.45.202.125": {
                            "ext_ip": "80.239.201.45",
                            "timestamp": "2020-10-08 11:56:14.550047"
                        }
                    },
                    "cogent": {
                        "5.45.202.122": {
                            "ext_ip": "154.47.36.153",
                            "timestamp": "2020-10-08 11:56:14.550047"
                        }
                    }
                }
            },
            "settings": {
                "rotate": true
            },
            "lb_current_ext_ips": [
                "80.239.201.119",
                "149.5.244.120"
            ],
            "views": {
                "ua": [
                    "front.kp.yandex.net",
                    "kinopoisk.ru"
                ]
            }
        },
        "tpx.maps.yandex.net": {
            "int_ips": {
                "telia": [
                    "5.45.202.50",
                    "5.45.202.51"
                ]
            },
            "mappings": {
                "current": {
                    "telia": {
                        "5.45.202.51": {
                            "ext_ip": "80.239.201.51",
                            "timestamp": "2019-04-17 19:30:06.322480"
                        }
                    }
                },
                "previous": {
                    "telia": {
                        "5.45.202.50": {
                            "ext_ip": "80.239.201.39",
                            "timestamp": "2019-04-17 19:00:07.243179"
                        }
                    }
                }
            },
            "settings": {
                "rotate": false
            },
            "lb_current_ext_ips": [
                "80.239.201.51"
            ],
            "views": {
                "ua": [
                    "old-tpx.maps.yandex.net"
                ]
            }
        },
        "aws-proxy.translate.yandex.net": {
            "int_ips": {
                "telia": [
                    "5.45.202.18",
                    "5.45.202.17"
                ],
                "cogent": [
                    "5.45.202.20",
                    "5.45.202.19"
                ]
            },
            "mappings": {
                "current": {
                    "telia": {
                        "5.45.202.17": {
                            "ext_ip": "80.239.201.35",
                            "timestamp": "2020-10-08 13:00:23.754765"
                        }
                    },
                    "cogent": {
                        "5.45.202.20": {
                            "ext_ip": "149.5.244.208",
                            "timestamp": "2020-10-08 13:00:23.754765"
                        }
                    }
                },
                "previous": {
                    "telia": {
                        "5.45.202.18": {
                            "ext_ip": "80.239.201.104",
                            "timestamp": "2020-10-08 11:56:14.550047"
                        }
                    },
                    "cogent": {
                        "5.45.202.19": {
                            "ext_ip": "154.47.36.181",
                            "timestamp": "2020-10-08 11:56:14.550047"
                        }
                    }
                }
            },
            "settings": {
                "rotate": true
            },
            "lb_current_ext_ips": [
                "80.239.201.35",
                "149.5.244.208"
            ],
            "views": {
                "ua": [
                    "dictionary.yandex.net",
                    "translate.yandex.net",
                    "z5h64q92x9.net",
                    "predictor.yandex.net"
                ],
                "world": [
                    "translate.yandex.net"
                ]
            }
        },
        "pool.with.static.mapping": {
            "int_ips": {
                "telia": [
                    "5.45.202.70",
                    "5.45.202.253"
                ],
                "cogent": [
                    "5.45.202.71",
                    "5.45.202.252",
                    "::1",
                    "::2"
                ]
            },
            "mappings": {
                "static": {
                    "telia": {
                        "5.45.202.253": {
                            "ext_ip": "80.239.201.127",
                            "timestamp": ""
                        }
                    },
                    "cogent": {
                        "5.45.202.252": {
                            "ext_ip": "149.5.244.254",
                            "timestamp": ""
                        },
                        "::1": {
                            "ext_ip": "fdf8:f53b:82e4::53",
                            "timestamp": "2021-06-03 13:30:39.509797"
                        },
                        "::2": {
                            "ext_ip": "fdf8:f53b:82e4::543",
                            "timestamp": "2021-06-03 13:30:39.509797"
                        }
                    }
                },
                "current": {
                    "telia": {
                        "5.45.202.70": {
                            "ext_ip": "80.239.201.8",
                            "timestamp": "2018-08-15 11:44:42.615406"
                        }
                    },
                    "cogent": {
                        "5.45.202.71": {
                            "ext_ip": "149.5.244.40",
                            "timestamp": "2018-08-15 12:01:40.940674"
                        }
                    }
                },
                "previous": {
                    "telia": {},
                    "cogent": {}
                }
            },
            "settings": {
                "rotate": false
            },
            "lb_current_ext_ips": [
                "80.239.201.8",
                "149.5.244.40"
            ],
            "views": {
                "ua": [
                    "uaproxy-ns21.yandex.net",
                    "ns8.yandex.ru"
                ],
                "world": [
                    "uaproxy-ns21.yandex.net"
                ]
            }
        },
        "pool.with.static.mapping.new": {
            "int_ips": {
                "telia": [
                    "5.45.202.72",
                    "5.45.202.250"
                ],
                "cogent": [
                    "5.45.202.73",
                    "5.45.202.251"
                ]
            },
            "mappings": {
                "static": {
                    "telia": {
                        "5.45.202.250": {
                            "ext_ip": "80.239.201.126",
                            "timestamp": ""
                        }
                    },
                    "cogent": {
                        "5.45.202.251": {
                            "ext_ip": "149.5.244.253",
                            "timestamp": ""
                        }
                    }
                }
            },
            "settings": {
                "rotate": true
            },
            "lb_current_ext_ips": [
                "80.239.201.8",
                "149.5.244.40"
            ],
            "views": {
                "ua": [
                    "test-uaproxy-ns21.yandex.net",
                    "test-ns8.yandex.ru"
                ]
            }
        }
    }
}
""")
