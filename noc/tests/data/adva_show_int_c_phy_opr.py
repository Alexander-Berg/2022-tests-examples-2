from data.lib import Data


class Data1(Data):
    content = """
current nint-Power:
  monitored-entity: node 1 interface 1/2/c1 opt-phy-multilane pm
  pm-profile: nint-Power
  interval-size: live
  suspect-status: admin-state-change
  elapsed-time: 11671624 seconds
  pm-data:
    opt-rx-pwr: -33.9 dBm
    opt-tx-pwr: 5.4 dBm
    """
    cmd = "show interface 1/2/c1 optm-phy pm current nint-Power"
    host = "dwdm-iva-m9"
    version = """
release-manifest:
  release-name: 1.3.1
    """
    result = {'opt-rx-pwr': '-33.9', 'opt-tx-pwr': '5.4'}  # insert parsed result here
