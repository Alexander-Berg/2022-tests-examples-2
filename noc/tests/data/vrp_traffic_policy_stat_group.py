from data.lib import Data


class Data1(Data):
    content = """
Traffic policy: PRJ_POL_QLOUDNETS, inbound
--------------------------------------------------------------------------------
 Slot: 1
 Item                  Packets                Bytes           pps           bps
 -------------------------------------------------------------------------------
 Matched          359512820925      364955947873835        130535    1031558576
  Passed          359512820925      364955947873835        130535    1031558576
  Dropped                    0                    0             0             0
   Filter                    0                    0             0             0
   CAR                       0                    0             0             0
 -------------------------------------------------------------------------------
    """
    cmd = "dis traffic-policy statistics qos group PRJ_GRP_QLOUDNETS"
    host = "iva1-s14"
    version = """
Huawei Versatile Routing Platform Software
VRP (R) software, Version 8.150 (CE6850EI V200R002C50SPC800)
Copyright (C) 2012-2017 Huawei Technologies Co., Ltd.
HUAWEI CE6850-48S4Q-EI uptime is 448 days, 4 hours, 9 minutes
Patch Version: V200R002SPH010

CE6850-48S4Q-EI(Master) 1 : uptime is  448 days, 4 hours, 7 minutes
        StartupTime 2018/04/03   11:23:44+03:00
Memory    Size    : 2048 M bytes
Flash     Size    : 1024 M bytes
NVRAM     Size    : 512  K bytes
CE6850-48S4Q-EI version information                              
1. PCB    Version : CEM48S4QP01    VER C
2. MAB    Version : 1
3. Board  Type    : CE6850-48S4Q-EI
4. CPLD1  Version : 109
5. CPLD2  Version : 109
6. BIOS   Version : 386
    """
    result = {'traffic policy': 'PRJ_POL_QLOUDNETS',
              'Matched': {'Packets': '359512820925', 'Bytes': '364955947873835', 'pps': '130535', 'bps': '1031558576'},
              'Passed': {'Packets': '359512820925', 'Bytes': '364955947873835', 'pps': '130535', 'bps': '1031558576'},
              'Dropped': {'Packets': '0', 'Bytes': '0', 'pps': '0', 'bps': '0'},
              'Filter': {'Packets': '0', 'Bytes': '0', 'pps': '0', 'bps': '0'},
              'CAR': {'Packets': '0', 'Bytes': '0', 'pps': '0', 'bps': '0'}}
