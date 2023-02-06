from data.lib import Data


class Data1(Data):
    content = """
Traffic policy: PRJ_POL_GE1/0/13, inbound
--------------------------------------------------------------------------------
 Slot: 1
 Item                  Packets                Bytes           pps           bps
 -------------------------------------------------------------------------------
 Matched            5598843073       20665387274628           552       9618864
  Passed            5598843073       20665387274628           552       9618864
  Dropped                    0                    0             0             0
   Filter                    0                    0             0             0
   CAR                       0                    0             0             0
 -------------------------------------------------------------------------------
    """
    cmd = "dis traffic-policy stat interface GE1/0/13"
    host = "sas1-s763"
    version = """
Huawei Versatile Routing Platform Software
VRP (R) software, Version 8.120 (CE5850HI V200R001C00SPC700)
Copyright (C) 2012-2016 Huawei Technologies Co., Ltd.
HUAWEI CE5850-48T4S2Q-HI uptime is 509 days, 18 hours, 46 minutes
Patch Version: V200R001SPH002

CE5850-48T4S2Q-HI(Master) 1 : uptime is  509 days, 18 hours, 45 minutes
        StartupTime 2017/05/06   18:56:26+03:00
Memory    Size    : 2048 M bytes
Flash     Size    : 1024 M bytes
CE5850-48T4S2Q-HI version information                              
1. PCB    Version : CEM48T4S2QP02    VER B
2. MAB    Version : 1
3. Board  Type    : CE5850-48T4S2Q-HI
4. CPLD1  Version : 103
5. BIOS   Version : 365
    """
    result = {"traffic policy": "PRJ_POL_GE1/0/13",
              "Matched": {"Packets": "5598843073", "Bytes": "20665387274628", "pps": "552", "bps": "9618864"},
              "Passed": {"Packets": "5598843073", "Bytes": "20665387274628", "pps": "552", "bps": "9618864"},
              "Dropped": {"Packets": "0", "Bytes": "0", "pps": "0", "bps": "0"},
              "Filter": {"Packets": "0", "Bytes": "0", "pps": "0", "bps": "0"},
              "CAR": {"Packets": "0", "Bytes": "0", "pps": "0", "bps": "0"}}
