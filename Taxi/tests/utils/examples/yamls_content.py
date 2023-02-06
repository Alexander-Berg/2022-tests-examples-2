ADJUST_CONFIG_YAML_CONTENT = (
    """
default:
  __default__: false
  child_tariff_events_enabled: false
  enabled: true
  vip_events_enabled: false
description: new_adjust.com
tags: ['new tag']
validators:
- $dictionary_of:
    required_keys:
    - __default__
    - disabled
""".lstrip()
)
DB_SETTINGS_YAML_CONTENT = (
    """
adjust_stats:
  settings:
    collection: adjust_stats
    connection: stats
    database: dbstats
geofences:
  indexes:
  - key:
    - name: updated
      type: descending
  settings:
    collection: geofences
    connection: gprstimings
    database: gprstimings
""".lstrip()
)
ZENDESK_VERIFY_CERT_YAML_CONTENT = (
    """
default: false
description: zendesk
tags: ['corrupting tag']
validators:
- $boolean
""".lstrip()
)
DEBTS_API_YAML_CONTENT = (
    """
swagger: '2.0'
info:
  description: Yandex Taxi Debts Protocol
  title: Yandex Taxi Debts Protocol
  version: 'v1'
""".lstrip()
)
DEBTS_CLIENT_YAML_CONTENT = (
    """
host:
  production: debts.taxi.yandex.net
  testing: debts.taxi.tst.yandex.net
  unstable: debts.taxi.dev.yandex.net
middlewares:
  tvm: debts
""".lstrip()
)
