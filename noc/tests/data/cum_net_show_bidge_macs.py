from data.lib import Data


class Data1(Data):
    content = """
VLAN      Master  Interface  MAC                TunnelDest  State      Flags  LastSeen
--------  ------  ---------  -----------------  ----------  ---------  -----  -----------------
333       bridge  bridge     1e:6b:cf:68:96:a8              permanent         32 days, 12:52:15
542       bridge  bridge     1e:6b:cf:68:96:a8              permanent         32 days, 12:52:06
549       bridge  bridge     1e:6b:cf:68:96:a8              permanent         32 days, 12:52:11
549       bridge  swp1s1     c4:54:44:23:c7:1a                                00:00:09
549       bridge  swp1s2     c4:54:44:23:c7:2c                                00:00:09
549       bridge  swp1s3     08:9e:01:d9:43:3e                                00:00:09
549       bridge  swp2s0     c4:54:44:23:c9:68                                00:00:09
549       bridge  swp2s1     c4:54:44:23:c9:4c                                00:00:09
549       bridge  swp2s2     c4:54:44:23:c8:7e                                00:00:09
549       bridge  swp2s3     c4:54:44:23:c9:70                                00:00:09
549       bridge  swp3s0     c4:54:44:23:c7:00                                00:00:09
549       bridge  swp3s1     c4:54:44:23:c7:a4                                00:00:09
549       bridge  swp3s2     c4:54:44:23:c6:d2                                00:00:09
549       bridge  swp3s3     c4:54:44:23:c7:98                                00:00:09
549       bridge  swp4s0     c4:54:44:23:c9:74                                00:00:09
549       bridge  swp4s1     c4:54:44:23:c9:b0                                00:00:09
549       bridge  swp4s2     c4:54:44:23:c9:4e                                00:00:09
549       bridge  swp4s3     c4:54:44:23:c9:46                                00:00:09
549       bridge  swp5s0     08:9e:01:d9:43:1c                                00:00:09
549       bridge  swp5s1     08:9e:01:d9:43:d2                                00:00:09
549       bridge  swp5s2     c4:54:44:23:c7:28                                00:00:09
549       bridge  swp5s3     c4:54:44:23:c7:80                                00:00:09
549       bridge  swp6s0     c4:54:44:23:c6:b8                                00:00:09
549       bridge  swp6s1     08:9e:01:d9:43:4c                                00:00:09
549       bridge  swp6s2     08:9e:01:d9:43:48                                00:00:09
549       bridge  swp6s3     c4:54:44:23:c7:88                                00:00:09
549       bridge  swp7s0     c4:54:44:23:c9:8c                                00:00:09
549       bridge  swp7s1     c4:54:44:23:c8:d6                                00:00:09
549       bridge  swp7s2     c4:54:44:23:c7:86                                00:00:09
549       bridge  swp7s3     c4:54:44:23:c9:3a                                00:00:09
549       bridge  swp8s0     c4:54:44:23:c7:f4                                00:00:09
549       bridge  swp8s1     c4:54:44:23:c8:7a                                00:00:09
549       bridge  swp8s2     c4:54:44:23:c6:dc                                00:00:09
549       bridge  swp8s3     c4:54:44:23:c7:36                                00:00:09
549       bridge  swp9s0     c4:54:44:23:c7:92                                00:00:09
549       bridge  swp9s1     c4:54:44:23:c8:42                                00:00:09
549       bridge  swp9s2     c4:54:44:23:c9:50                                00:00:09
549       bridge  swp9s3     c4:54:44:23:c9:d4                                00:00:09
549       bridge  swp10s0    c4:54:44:23:c7:7c                                00:00:09
549       bridge  swp10s1    c4:54:44:23:c7:06                                00:00:09
549       bridge  swp10s2    c4:54:44:23:c7:3e                                00:00:09
549       bridge  swp10s3    c4:54:44:23:c7:24                                00:00:09
688       bridge  bridge     1e:6b:cf:68:96:a8              permanent         32 days, 12:52:09
688       bridge  swp1s1     c4:54:44:23:c7:1a                                00:02:39
688       bridge  swp1s2     c4:54:44:23:c7:2c                                00:00:39
688       bridge  swp1s3     08:9e:01:d9:43:3e                                00:00:09
688       bridge  swp2s0     c4:54:44:23:c9:68                                00:02:09
688       bridge  swp2s1     c4:54:44:23:c9:4c                                00:02:39
688       bridge  swp2s2     c4:54:44:23:c8:7e                                00:01:39
688       bridge  swp2s3     c4:54:44:23:c9:70                                00:00:39
688       bridge  swp3s0     c4:54:44:23:c7:00                                00:00:09
688       bridge  swp3s1     c4:54:44:23:c7:a4                                00:00:39
688       bridge  swp3s2     c4:54:44:23:c6:d2                                00:00:39
688       bridge  swp3s3     c4:54:44:23:c7:98                                00:01:09
688       bridge  swp4s0     c4:54:44:23:c9:74                                00:00:09
688       bridge  swp4s1     c4:54:44:23:c9:b0                                00:00:09
688       bridge  swp4s2     c4:54:44:23:c9:4e                                00:01:39
688       bridge  swp4s3     c4:54:44:23:c9:46                                00:00:09
688       bridge  swp5s0     08:9e:01:d9:43:1c                                00:00:39
688       bridge  swp5s1     08:9e:01:d9:43:d2                                00:02:09
688       bridge  swp5s2     c4:54:44:23:c7:28                                00:00:09
688       bridge  swp5s3     c4:54:44:23:c7:80                                00:02:09
688       bridge  swp6s0     c4:54:44:23:c6:b8                                00:01:09
688       bridge  swp6s1     08:9e:01:d9:43:4c                                00:00:09
688       bridge  swp6s2     08:9e:01:d9:43:48                                00:00:09
688       bridge  swp6s3     c4:54:44:23:c7:88                                00:01:39
688       bridge  swp7s0     c4:54:44:23:c9:8c                                00:00:39
688       bridge  swp7s1     c4:54:44:23:c8:d6                                00:00:09
688       bridge  swp7s2     c4:54:44:23:c7:86                                00:00:39
688       bridge  swp7s3     c4:54:44:23:c9:3a                                00:00:09
688       bridge  swp8s0     c4:54:44:23:c7:f4                                00:00:09
688       bridge  swp8s1     c4:54:44:23:c8:7a                                00:00:39
688       bridge  swp8s2     c4:54:44:23:c6:dc                                00:01:39
688       bridge  swp8s3     c4:54:44:23:c7:36                                00:00:09
688       bridge  swp9s0     c4:54:44:23:c7:92                                00:01:09
688       bridge  swp9s1     c4:54:44:23:c8:42                                00:00:09
688       bridge  swp9s2     c4:54:44:23:c9:50                                00:01:09
688       bridge  swp9s3     c4:54:44:23:c9:d4                                00:00:09
688       bridge  swp10s0    c4:54:44:23:c7:7c                                00:00:09
688       bridge  swp10s1    c4:54:44:23:c7:06                                00:00:39
688       bridge  swp10s2    c4:54:44:23:c7:3e                                00:02:09
688       bridge  swp10s3    c4:54:44:23:c7:24                                00:01:09
742       bridge  bridge     1e:6b:cf:68:96:a8              permanent         32 days, 12:52:09
742       bridge  swp1s0     c4:54:44:23:c9:b2                                00:00:09
788       bridge  bridge     1e:6b:cf:68:96:a8              permanent         32 days, 12:52:09
788       bridge  swp1s1     c4:54:44:23:c7:1a                                00:01:09
788       bridge  swp1s2     c4:54:44:23:c7:2c                                00:00:09
788       bridge  swp1s3     08:9e:01:d9:43:3e                                00:00:39
788       bridge  swp2s0     c4:54:44:23:c9:68                                00:02:09
788       bridge  swp2s1     c4:54:44:23:c9:4c                                00:00:39
788       bridge  swp2s2     c4:54:44:23:c8:7e                                00:02:58
788       bridge  swp2s3     c4:54:44:23:c9:70                                00:01:09
788       bridge  swp3s0     c4:54:44:23:c7:00                                00:00:09
788       bridge  swp3s1     c4:54:44:23:c7:a4                                00:00:09
788       bridge  swp3s2     c4:54:44:23:c6:d2                                00:02:09
788       bridge  swp3s3     c4:54:44:23:c7:98                                00:00:09
788       bridge  swp4s0     c4:54:44:23:c9:74                                00:00:09
788       bridge  swp4s1     c4:54:44:23:c9:b0                                00:02:39
788       bridge  swp4s2     c4:54:44:23:c9:4e                                00:02:09
788       bridge  swp4s3     c4:54:44:23:c9:46                                00:00:09
788       bridge  swp5s0     08:9e:01:d9:43:1c                                00:01:09
788       bridge  swp5s1     08:9e:01:d9:43:d2                                00:00:09
788       bridge  swp5s2     c4:54:44:23:c7:28                                00:01:09
788       bridge  swp5s3     c4:54:44:23:c7:80                                00:01:09
788       bridge  swp6s0     c4:54:44:23:c6:b8                                00:00:09
788       bridge  swp6s1     08:9e:01:d9:43:4c                                00:00:39
788       bridge  swp6s2     08:9e:01:d9:43:48                                00:01:09
788       bridge  swp6s3     c4:54:44:23:c7:88                                00:02:39
788       bridge  swp7s0     c4:54:44:23:c9:8c                                00:02:58
788       bridge  swp7s1     c4:54:44:23:c8:d6                                00:01:09
788       bridge  swp7s2     c4:54:44:23:c7:86                                00:00:39
788       bridge  swp7s3     c4:54:44:23:c9:3a                                00:01:09
788       bridge  swp8s0     c4:54:44:23:c7:f4                                00:00:39
788       bridge  swp8s1     c4:54:44:23:c8:7a                                00:00:39
788       bridge  swp8s2     c4:54:44:23:c6:dc                                00:02:58
788       bridge  swp8s3     c4:54:44:23:c7:36                                00:01:09
788       bridge  swp9s0     c4:54:44:23:c7:92                                00:00:39
788       bridge  swp9s1     c4:54:44:23:c8:42                                00:00:39
788       bridge  swp9s2     c4:54:44:23:c9:50                                00:01:09
788       bridge  swp9s3     c4:54:44:23:c9:d4                                00:00:09
788       bridge  swp10s0    c4:54:44:23:c7:7c                                00:00:09
788       bridge  swp10s1    c4:54:44:23:c7:06                                00:01:09
788       bridge  swp10s2    c4:54:44:23:c7:3e                                00:01:09
788       bridge  swp10s3    c4:54:44:23:c7:24                                00:02:09
867       bridge  bridge     1e:6b:cf:68:96:a8              permanent         32 days, 12:52:09
867       bridge  swp1s1     c4:54:44:23:c7:1a                                00:00:09
867       bridge  swp1s2     c4:54:44:23:c7:2c                                00:00:09
867       bridge  swp1s3     08:9e:01:d9:43:3e                                00:00:09
867       bridge  swp2s0     c4:54:44:23:c9:68                                00:00:09
867       bridge  swp2s1     c4:54:44:23:c9:4c                                00:00:09
867       bridge  swp2s2     c4:54:44:23:c8:7e                                00:00:09
867       bridge  swp2s3     c4:54:44:23:c9:70                                00:00:09
867       bridge  swp3s0     c4:54:44:23:c7:00                                00:00:09
867       bridge  swp3s1     c4:54:44:23:c7:a4                                00:00:09
867       bridge  swp3s2     c4:54:44:23:c6:d2                                00:00:09
867       bridge  swp3s3     c4:54:44:23:c7:98                                00:00:09
867       bridge  swp4s0     c4:54:44:23:c9:74                                00:00:09
867       bridge  swp4s1     c4:54:44:23:c9:b0                                00:00:09
867       bridge  swp4s2     c4:54:44:23:c9:4e                                00:00:09
867       bridge  swp4s3     c4:54:44:23:c9:46                                00:00:09
867       bridge  swp5s0     08:9e:01:d9:43:1c                                00:00:09
867       bridge  swp5s1     08:9e:01:d9:43:d2                                00:00:09
867       bridge  swp5s2     c4:54:44:23:c7:28                                00:00:09
867       bridge  swp5s3     c4:54:44:23:c7:80                                00:00:09
867       bridge  swp6s0     c4:54:44:23:c6:b8                                00:00:09
867       bridge  swp6s1     08:9e:01:d9:43:4c                                00:00:09
867       bridge  swp6s2     08:9e:01:d9:43:48                                00:00:09
867       bridge  swp6s3     c4:54:44:23:c7:88                                00:00:09
867       bridge  swp7s0     c4:54:44:23:c9:8c                                00:00:09
867       bridge  swp7s1     c4:54:44:23:c8:d6                                00:00:09
867       bridge  swp7s2     c4:54:44:23:c7:86                                00:00:09
867       bridge  swp7s3     c4:54:44:23:c9:3a                                00:00:09
867       bridge  swp8s0     c4:54:44:23:c7:f4                                00:00:09
867       bridge  swp8s1     c4:54:44:23:c8:7a                                00:00:09
867       bridge  swp8s2     c4:54:44:23:c6:dc                                00:00:09
867       bridge  swp8s3     c4:54:44:23:c7:36                                00:00:09
867       bridge  swp9s0     c4:54:44:23:c7:92                                00:00:09
867       bridge  swp9s1     c4:54:44:23:c8:42                                00:00:09
867       bridge  swp9s2     c4:54:44:23:c9:50                                00:00:09
867       bridge  swp9s3     c4:54:44:23:c9:d4                                00:00:09
867       bridge  swp10s0    c4:54:44:23:c7:7c                                00:00:09
867       bridge  swp10s1    c4:54:44:23:c7:06                                00:00:09
867       bridge  swp10s2    c4:54:44:23:c7:3e                                00:00:09
867       bridge  swp10s3    c4:54:44:23:c7:24                                00:00:09
1354      bridge  bridge     1e:6b:cf:68:96:a8              permanent         32 days, 12:52:09
1354      bridge  swp1s0     c4:54:44:23:c9:b2                                00:00:09
untagged  bridge  dummy0     1e:6b:cf:68:96:a8              permanent         32 days, 12:52:15
untagged  bridge  swp1s0     24:8a:07:f5:0a:18              permanent         32 days, 12:52:15
untagged  bridge  swp1s1     24:8a:07:f5:0a:19              permanent         32 days, 12:52:15
untagged  bridge  swp1s2     24:8a:07:f5:0a:1a              permanent         32 days, 12:52:15
untagged  bridge  swp1s3     24:8a:07:f5:0a:1b              permanent         32 days, 12:52:15
untagged  bridge  swp2s0     24:8a:07:f5:0a:1c              permanent         32 days, 12:52:15
untagged  bridge  swp2s1     24:8a:07:f5:0a:1d              permanent         32 days, 12:52:15
untagged  bridge  swp2s2     24:8a:07:f5:0a:1e              permanent         32 days, 12:52:15
untagged  bridge  swp2s3     24:8a:07:f5:0a:1f              permanent         32 days, 12:52:15
untagged  bridge  swp3s0     24:8a:07:f5:0a:10              permanent         32 days, 12:52:15
untagged  bridge  swp3s1     24:8a:07:f5:0a:11              permanent         32 days, 12:52:15
untagged  bridge  swp3s2     24:8a:07:f5:0a:12              permanent         32 days, 12:52:15
untagged  bridge  swp3s3     24:8a:07:f5:0a:13              permanent         32 days, 12:52:15
untagged  bridge  swp4s0     24:8a:07:f5:0a:14              permanent         32 days, 12:52:15
untagged  bridge  swp4s1     24:8a:07:f5:0a:15              permanent         32 days, 12:52:15
untagged  bridge  swp4s2     24:8a:07:f5:0a:16              permanent         32 days, 12:52:15
untagged  bridge  swp4s3     24:8a:07:f5:0a:17              permanent         32 days, 12:52:15
untagged  bridge  swp5s0     24:8a:07:f5:0a:08              permanent         32 days, 12:52:15
untagged  bridge  swp5s1     24:8a:07:f5:0a:09              permanent         32 days, 12:52:15
untagged  bridge  swp5s2     24:8a:07:f5:0a:0a              permanent         32 days, 12:52:15
untagged  bridge  swp5s3     24:8a:07:f5:0a:0b              permanent         32 days, 12:52:15
untagged  bridge  swp6s0     24:8a:07:f5:0a:0c              permanent         32 days, 12:52:15
untagged  bridge  swp6s1     24:8a:07:f5:0a:0d              permanent         32 days, 12:52:15
untagged  bridge  swp6s2     24:8a:07:f5:0a:0e              permanent         32 days, 12:52:15
untagged  bridge  swp6s3     24:8a:07:f5:0a:0f              permanent         32 days, 12:52:15
untagged  bridge  swp7s0     24:8a:07:f5:0a:00              permanent         32 days, 12:52:15
untagged  bridge  swp7s1     24:8a:07:f5:0a:01              permanent         32 days, 12:52:15
untagged  bridge  swp7s2     24:8a:07:f5:0a:02              permanent         32 days, 12:52:15
untagged  bridge  swp7s3     24:8a:07:f5:0a:03              permanent         32 days, 12:52:15
untagged  bridge  swp8s0     24:8a:07:f5:0a:04              permanent         32 days, 12:52:15
untagged  bridge  swp8s1     24:8a:07:f5:0a:05              permanent         32 days, 12:52:15
untagged  bridge  swp8s2     24:8a:07:f5:0a:06              permanent         32 days, 12:52:15
untagged  bridge  swp8s3     24:8a:07:f5:0a:07              permanent         32 days, 12:52:15
untagged  bridge  swp9s0     24:8a:07:f5:0a:24              permanent         32 days, 12:52:15
untagged  bridge  swp9s1     24:8a:07:f5:0a:25              permanent         32 days, 12:52:15
untagged  bridge  swp9s2     24:8a:07:f5:0a:26              permanent         32 days, 12:52:15
untagged  bridge  swp9s3     24:8a:07:f5:0a:27              permanent         32 days, 12:52:15
untagged  bridge  swp10s0    24:8a:07:f5:0a:20              permanent         32 days, 12:52:15
untagged  bridge  swp10s1    24:8a:07:f5:0a:21              permanent         32 days, 12:52:15
untagged  bridge  swp10s2    24:8a:07:f5:0a:22              permanent         32 days, 12:52:15
untagged  bridge  swp10s3    24:8a:07:f5:0a:23              permanent         32 days, 12:52:15
untagged  bridge  swp11s0    24:8a:07:f5:0a:2c              permanent         32 days, 12:52:15
untagged  bridge  swp11s1    24:8a:07:f5:0a:2d              permanent         32 days, 12:52:15
untagged  bridge  swp11s2    24:8a:07:f5:0a:2e              permanent         32 days, 12:52:15
untagged  bridge  swp11s3    24:8a:07:f5:0a:2f              permanent         32 days, 12:52:15
untagged  bridge  swp12s0    24:8a:07:f5:0a:28              permanent         32 days, 12:52:15
untagged  bridge  swp12s1    24:8a:07:f5:0a:29              permanent         32 days, 12:52:15
untagged  bridge  swp12s2    24:8a:07:f5:0a:2a              permanent         32 days, 12:52:15
untagged  bridge  swp12s3    24:8a:07:f5:0a:2b              permanent         32 days, 12:52:15
    """
    cmd = "sudo net show bridge macs"
    host = "sas2-5s76"
    version = """
Linux sas2-5s76.yndx.net 4.1.0-cl-7-amd64 #1 SMP Debian 4.1.33-1+cl3u17 (2018-10-31) x86_64 GNU/Linux
    """
    result = [{'interface': 'bridge', 'mac': '1e:6b:cf:68:96:a8', 'vlan': '333'},
              {'interface': 'bridge', 'mac': '1e:6b:cf:68:96:a8', 'vlan': '542'},
              {'interface': 'bridge', 'mac': '1e:6b:cf:68:96:a8', 'vlan': '549'},
              {'interface': 'swp1s1', 'mac': 'c4:54:44:23:c7:1a', 'vlan': '549'},
              {'interface': 'swp1s2', 'mac': 'c4:54:44:23:c7:2c', 'vlan': '549'},
              {'interface': 'swp1s3', 'mac': '08:9e:01:d9:43:3e', 'vlan': '549'},
              {'interface': 'swp2s0', 'mac': 'c4:54:44:23:c9:68', 'vlan': '549'},
              {'interface': 'swp2s1', 'mac': 'c4:54:44:23:c9:4c', 'vlan': '549'},
              {'interface': 'swp2s2', 'mac': 'c4:54:44:23:c8:7e', 'vlan': '549'},
              {'interface': 'swp2s3', 'mac': 'c4:54:44:23:c9:70', 'vlan': '549'},
              {'interface': 'swp3s0', 'mac': 'c4:54:44:23:c7:00', 'vlan': '549'},
              {'interface': 'swp3s1', 'mac': 'c4:54:44:23:c7:a4', 'vlan': '549'},
              {'interface': 'swp3s2', 'mac': 'c4:54:44:23:c6:d2', 'vlan': '549'},
              {'interface': 'swp3s3', 'mac': 'c4:54:44:23:c7:98', 'vlan': '549'},
              {'interface': 'swp4s0', 'mac': 'c4:54:44:23:c9:74', 'vlan': '549'},
              {'interface': 'swp4s1', 'mac': 'c4:54:44:23:c9:b0', 'vlan': '549'},
              {'interface': 'swp4s2', 'mac': 'c4:54:44:23:c9:4e', 'vlan': '549'},
              {'interface': 'swp4s3', 'mac': 'c4:54:44:23:c9:46', 'vlan': '549'},
              {'interface': 'swp5s0', 'mac': '08:9e:01:d9:43:1c', 'vlan': '549'},
              {'interface': 'swp5s1', 'mac': '08:9e:01:d9:43:d2', 'vlan': '549'},
              {'interface': 'swp5s2', 'mac': 'c4:54:44:23:c7:28', 'vlan': '549'},
              {'interface': 'swp5s3', 'mac': 'c4:54:44:23:c7:80', 'vlan': '549'},
              {'interface': 'swp6s0', 'mac': 'c4:54:44:23:c6:b8', 'vlan': '549'},
              {'interface': 'swp6s1', 'mac': '08:9e:01:d9:43:4c', 'vlan': '549'},
              {'interface': 'swp6s2', 'mac': '08:9e:01:d9:43:48', 'vlan': '549'},
              {'interface': 'swp6s3', 'mac': 'c4:54:44:23:c7:88', 'vlan': '549'},
              {'interface': 'swp7s0', 'mac': 'c4:54:44:23:c9:8c', 'vlan': '549'},
              {'interface': 'swp7s1', 'mac': 'c4:54:44:23:c8:d6', 'vlan': '549'},
              {'interface': 'swp7s2', 'mac': 'c4:54:44:23:c7:86', 'vlan': '549'},
              {'interface': 'swp7s3', 'mac': 'c4:54:44:23:c9:3a', 'vlan': '549'},
              {'interface': 'swp8s0', 'mac': 'c4:54:44:23:c7:f4', 'vlan': '549'},
              {'interface': 'swp8s1', 'mac': 'c4:54:44:23:c8:7a', 'vlan': '549'},
              {'interface': 'swp8s2', 'mac': 'c4:54:44:23:c6:dc', 'vlan': '549'},
              {'interface': 'swp8s3', 'mac': 'c4:54:44:23:c7:36', 'vlan': '549'},
              {'interface': 'swp9s0', 'mac': 'c4:54:44:23:c7:92', 'vlan': '549'},
              {'interface': 'swp9s1', 'mac': 'c4:54:44:23:c8:42', 'vlan': '549'},
              {'interface': 'swp9s2', 'mac': 'c4:54:44:23:c9:50', 'vlan': '549'},
              {'interface': 'swp9s3', 'mac': 'c4:54:44:23:c9:d4', 'vlan': '549'},
              {'interface': 'swp10s0', 'mac': 'c4:54:44:23:c7:7c', 'vlan': '549'},
              {'interface': 'swp10s1', 'mac': 'c4:54:44:23:c7:06', 'vlan': '549'},
              {'interface': 'swp10s2', 'mac': 'c4:54:44:23:c7:3e', 'vlan': '549'},
              {'interface': 'swp10s3', 'mac': 'c4:54:44:23:c7:24', 'vlan': '549'},
              {'interface': 'bridge', 'mac': '1e:6b:cf:68:96:a8', 'vlan': '688'},
              {'interface': 'swp1s1', 'mac': 'c4:54:44:23:c7:1a', 'vlan': '688'},
              {'interface': 'swp1s2', 'mac': 'c4:54:44:23:c7:2c', 'vlan': '688'},
              {'interface': 'swp1s3', 'mac': '08:9e:01:d9:43:3e', 'vlan': '688'},
              {'interface': 'swp2s0', 'mac': 'c4:54:44:23:c9:68', 'vlan': '688'},
              {'interface': 'swp2s1', 'mac': 'c4:54:44:23:c9:4c', 'vlan': '688'},
              {'interface': 'swp2s2', 'mac': 'c4:54:44:23:c8:7e', 'vlan': '688'},
              {'interface': 'swp2s3', 'mac': 'c4:54:44:23:c9:70', 'vlan': '688'},
              {'interface': 'swp3s0', 'mac': 'c4:54:44:23:c7:00', 'vlan': '688'},
              {'interface': 'swp3s1', 'mac': 'c4:54:44:23:c7:a4', 'vlan': '688'},
              {'interface': 'swp3s2', 'mac': 'c4:54:44:23:c6:d2', 'vlan': '688'},
              {'interface': 'swp3s3', 'mac': 'c4:54:44:23:c7:98', 'vlan': '688'},
              {'interface': 'swp4s0', 'mac': 'c4:54:44:23:c9:74', 'vlan': '688'},
              {'interface': 'swp4s1', 'mac': 'c4:54:44:23:c9:b0', 'vlan': '688'},
              {'interface': 'swp4s2', 'mac': 'c4:54:44:23:c9:4e', 'vlan': '688'},
              {'interface': 'swp4s3', 'mac': 'c4:54:44:23:c9:46', 'vlan': '688'},
              {'interface': 'swp5s0', 'mac': '08:9e:01:d9:43:1c', 'vlan': '688'},
              {'interface': 'swp5s1', 'mac': '08:9e:01:d9:43:d2', 'vlan': '688'},
              {'interface': 'swp5s2', 'mac': 'c4:54:44:23:c7:28', 'vlan': '688'},
              {'interface': 'swp5s3', 'mac': 'c4:54:44:23:c7:80', 'vlan': '688'},
              {'interface': 'swp6s0', 'mac': 'c4:54:44:23:c6:b8', 'vlan': '688'},
              {'interface': 'swp6s1', 'mac': '08:9e:01:d9:43:4c', 'vlan': '688'},
              {'interface': 'swp6s2', 'mac': '08:9e:01:d9:43:48', 'vlan': '688'},
              {'interface': 'swp6s3', 'mac': 'c4:54:44:23:c7:88', 'vlan': '688'},
              {'interface': 'swp7s0', 'mac': 'c4:54:44:23:c9:8c', 'vlan': '688'},
              {'interface': 'swp7s1', 'mac': 'c4:54:44:23:c8:d6', 'vlan': '688'},
              {'interface': 'swp7s2', 'mac': 'c4:54:44:23:c7:86', 'vlan': '688'},
              {'interface': 'swp7s3', 'mac': 'c4:54:44:23:c9:3a', 'vlan': '688'},
              {'interface': 'swp8s0', 'mac': 'c4:54:44:23:c7:f4', 'vlan': '688'},
              {'interface': 'swp8s1', 'mac': 'c4:54:44:23:c8:7a', 'vlan': '688'},
              {'interface': 'swp8s2', 'mac': 'c4:54:44:23:c6:dc', 'vlan': '688'},
              {'interface': 'swp8s3', 'mac': 'c4:54:44:23:c7:36', 'vlan': '688'},
              {'interface': 'swp9s0', 'mac': 'c4:54:44:23:c7:92', 'vlan': '688'},
              {'interface': 'swp9s1', 'mac': 'c4:54:44:23:c8:42', 'vlan': '688'},
              {'interface': 'swp9s2', 'mac': 'c4:54:44:23:c9:50', 'vlan': '688'},
              {'interface': 'swp9s3', 'mac': 'c4:54:44:23:c9:d4', 'vlan': '688'},
              {'interface': 'swp10s0', 'mac': 'c4:54:44:23:c7:7c', 'vlan': '688'},
              {'interface': 'swp10s1', 'mac': 'c4:54:44:23:c7:06', 'vlan': '688'},
              {'interface': 'swp10s2', 'mac': 'c4:54:44:23:c7:3e', 'vlan': '688'},
              {'interface': 'swp10s3', 'mac': 'c4:54:44:23:c7:24', 'vlan': '688'},
              {'interface': 'bridge', 'mac': '1e:6b:cf:68:96:a8', 'vlan': '742'},
              {'interface': 'swp1s0', 'mac': 'c4:54:44:23:c9:b2', 'vlan': '742'},
              {'interface': 'bridge', 'mac': '1e:6b:cf:68:96:a8', 'vlan': '788'},
              {'interface': 'swp1s1', 'mac': 'c4:54:44:23:c7:1a', 'vlan': '788'},
              {'interface': 'swp1s2', 'mac': 'c4:54:44:23:c7:2c', 'vlan': '788'},
              {'interface': 'swp1s3', 'mac': '08:9e:01:d9:43:3e', 'vlan': '788'},
              {'interface': 'swp2s0', 'mac': 'c4:54:44:23:c9:68', 'vlan': '788'},
              {'interface': 'swp2s1', 'mac': 'c4:54:44:23:c9:4c', 'vlan': '788'},
              {'interface': 'swp2s2', 'mac': 'c4:54:44:23:c8:7e', 'vlan': '788'},
              {'interface': 'swp2s3', 'mac': 'c4:54:44:23:c9:70', 'vlan': '788'},
              {'interface': 'swp3s0', 'mac': 'c4:54:44:23:c7:00', 'vlan': '788'},
              {'interface': 'swp3s1', 'mac': 'c4:54:44:23:c7:a4', 'vlan': '788'},
              {'interface': 'swp3s2', 'mac': 'c4:54:44:23:c6:d2', 'vlan': '788'},
              {'interface': 'swp3s3', 'mac': 'c4:54:44:23:c7:98', 'vlan': '788'},
              {'interface': 'swp4s0', 'mac': 'c4:54:44:23:c9:74', 'vlan': '788'},
              {'interface': 'swp4s1', 'mac': 'c4:54:44:23:c9:b0', 'vlan': '788'},
              {'interface': 'swp4s2', 'mac': 'c4:54:44:23:c9:4e', 'vlan': '788'},
              {'interface': 'swp4s3', 'mac': 'c4:54:44:23:c9:46', 'vlan': '788'},
              {'interface': 'swp5s0', 'mac': '08:9e:01:d9:43:1c', 'vlan': '788'},
              {'interface': 'swp5s1', 'mac': '08:9e:01:d9:43:d2', 'vlan': '788'},
              {'interface': 'swp5s2', 'mac': 'c4:54:44:23:c7:28', 'vlan': '788'},
              {'interface': 'swp5s3', 'mac': 'c4:54:44:23:c7:80', 'vlan': '788'},
              {'interface': 'swp6s0', 'mac': 'c4:54:44:23:c6:b8', 'vlan': '788'},
              {'interface': 'swp6s1', 'mac': '08:9e:01:d9:43:4c', 'vlan': '788'},
              {'interface': 'swp6s2', 'mac': '08:9e:01:d9:43:48', 'vlan': '788'},
              {'interface': 'swp6s3', 'mac': 'c4:54:44:23:c7:88', 'vlan': '788'},
              {'interface': 'swp7s0', 'mac': 'c4:54:44:23:c9:8c', 'vlan': '788'},
              {'interface': 'swp7s1', 'mac': 'c4:54:44:23:c8:d6', 'vlan': '788'},
              {'interface': 'swp7s2', 'mac': 'c4:54:44:23:c7:86', 'vlan': '788'},
              {'interface': 'swp7s3', 'mac': 'c4:54:44:23:c9:3a', 'vlan': '788'},
              {'interface': 'swp8s0', 'mac': 'c4:54:44:23:c7:f4', 'vlan': '788'},
              {'interface': 'swp8s1', 'mac': 'c4:54:44:23:c8:7a', 'vlan': '788'},
              {'interface': 'swp8s2', 'mac': 'c4:54:44:23:c6:dc', 'vlan': '788'},
              {'interface': 'swp8s3', 'mac': 'c4:54:44:23:c7:36', 'vlan': '788'},
              {'interface': 'swp9s0', 'mac': 'c4:54:44:23:c7:92', 'vlan': '788'},
              {'interface': 'swp9s1', 'mac': 'c4:54:44:23:c8:42', 'vlan': '788'},
              {'interface': 'swp9s2', 'mac': 'c4:54:44:23:c9:50', 'vlan': '788'},
              {'interface': 'swp9s3', 'mac': 'c4:54:44:23:c9:d4', 'vlan': '788'},
              {'interface': 'swp10s0', 'mac': 'c4:54:44:23:c7:7c', 'vlan': '788'},
              {'interface': 'swp10s1', 'mac': 'c4:54:44:23:c7:06', 'vlan': '788'},
              {'interface': 'swp10s2', 'mac': 'c4:54:44:23:c7:3e', 'vlan': '788'},
              {'interface': 'swp10s3', 'mac': 'c4:54:44:23:c7:24', 'vlan': '788'},
              {'interface': 'bridge', 'mac': '1e:6b:cf:68:96:a8', 'vlan': '867'},
              {'interface': 'swp1s1', 'mac': 'c4:54:44:23:c7:1a', 'vlan': '867'},
              {'interface': 'swp1s2', 'mac': 'c4:54:44:23:c7:2c', 'vlan': '867'},
              {'interface': 'swp1s3', 'mac': '08:9e:01:d9:43:3e', 'vlan': '867'},
              {'interface': 'swp2s0', 'mac': 'c4:54:44:23:c9:68', 'vlan': '867'},
              {'interface': 'swp2s1', 'mac': 'c4:54:44:23:c9:4c', 'vlan': '867'},
              {'interface': 'swp2s2', 'mac': 'c4:54:44:23:c8:7e', 'vlan': '867'},
              {'interface': 'swp2s3', 'mac': 'c4:54:44:23:c9:70', 'vlan': '867'},
              {'interface': 'swp3s0', 'mac': 'c4:54:44:23:c7:00', 'vlan': '867'},
              {'interface': 'swp3s1', 'mac': 'c4:54:44:23:c7:a4', 'vlan': '867'},
              {'interface': 'swp3s2', 'mac': 'c4:54:44:23:c6:d2', 'vlan': '867'},
              {'interface': 'swp3s3', 'mac': 'c4:54:44:23:c7:98', 'vlan': '867'},
              {'interface': 'swp4s0', 'mac': 'c4:54:44:23:c9:74', 'vlan': '867'},
              {'interface': 'swp4s1', 'mac': 'c4:54:44:23:c9:b0', 'vlan': '867'},
              {'interface': 'swp4s2', 'mac': 'c4:54:44:23:c9:4e', 'vlan': '867'},
              {'interface': 'swp4s3', 'mac': 'c4:54:44:23:c9:46', 'vlan': '867'},
              {'interface': 'swp5s0', 'mac': '08:9e:01:d9:43:1c', 'vlan': '867'},
              {'interface': 'swp5s1', 'mac': '08:9e:01:d9:43:d2', 'vlan': '867'},
              {'interface': 'swp5s2', 'mac': 'c4:54:44:23:c7:28', 'vlan': '867'},
              {'interface': 'swp5s3', 'mac': 'c4:54:44:23:c7:80', 'vlan': '867'},
              {'interface': 'swp6s0', 'mac': 'c4:54:44:23:c6:b8', 'vlan': '867'},
              {'interface': 'swp6s1', 'mac': '08:9e:01:d9:43:4c', 'vlan': '867'},
              {'interface': 'swp6s2', 'mac': '08:9e:01:d9:43:48', 'vlan': '867'},
              {'interface': 'swp6s3', 'mac': 'c4:54:44:23:c7:88', 'vlan': '867'},
              {'interface': 'swp7s0', 'mac': 'c4:54:44:23:c9:8c', 'vlan': '867'},
              {'interface': 'swp7s1', 'mac': 'c4:54:44:23:c8:d6', 'vlan': '867'},
              {'interface': 'swp7s2', 'mac': 'c4:54:44:23:c7:86', 'vlan': '867'},
              {'interface': 'swp7s3', 'mac': 'c4:54:44:23:c9:3a', 'vlan': '867'},
              {'interface': 'swp8s0', 'mac': 'c4:54:44:23:c7:f4', 'vlan': '867'},
              {'interface': 'swp8s1', 'mac': 'c4:54:44:23:c8:7a', 'vlan': '867'},
              {'interface': 'swp8s2', 'mac': 'c4:54:44:23:c6:dc', 'vlan': '867'},
              {'interface': 'swp8s3', 'mac': 'c4:54:44:23:c7:36', 'vlan': '867'},
              {'interface': 'swp9s0', 'mac': 'c4:54:44:23:c7:92', 'vlan': '867'},
              {'interface': 'swp9s1', 'mac': 'c4:54:44:23:c8:42', 'vlan': '867'},
              {'interface': 'swp9s2', 'mac': 'c4:54:44:23:c9:50', 'vlan': '867'},
              {'interface': 'swp9s3', 'mac': 'c4:54:44:23:c9:d4', 'vlan': '867'},
              {'interface': 'swp10s0', 'mac': 'c4:54:44:23:c7:7c', 'vlan': '867'},
              {'interface': 'swp10s1', 'mac': 'c4:54:44:23:c7:06', 'vlan': '867'},
              {'interface': 'swp10s2', 'mac': 'c4:54:44:23:c7:3e', 'vlan': '867'},
              {'interface': 'swp10s3', 'mac': 'c4:54:44:23:c7:24', 'vlan': '867'},
              {'interface': 'bridge', 'mac': '1e:6b:cf:68:96:a8', 'vlan': '1354'},
              {'interface': 'swp1s0', 'mac': 'c4:54:44:23:c9:b2', 'vlan': '1354'}]
