tun64:
  firewall_permit_rules:
    - voip.uiscom.ru:
      source: 195.211.120.35
      proto: udp
      ports: 5080,16384:32767
