from data.lib import Data


class Data1(Data):
    content = """
PHY: Physical
*down: administratively down
^down: standby
(l): loopback
(s): spoofing
(b): BFD down
(e): ETHOAM down
(d): Dampening Suppressed
(p): port alarm down
(dl): DLDP down
(c): CFM down
InUti/OutUti: input utility rate/output utility rate
Interface                  PHY      Protocol  InUti OutUti   inErrors  outErrors
100GE1/0/1                 up       up           0%  0.01%          0          0
100GE1/0/2                 up       up        0.01%  0.01%          0          0
100GE1/0/3                 *down    down         0%     0%          0          0
100GE1/0/4                 up       up        0.01%  0.01%          0          0
10GE1/0/1                  up       up        0.01%  5.19%          0          0
10GE1/0/2                  down     down         0%     0%          0          0
10GE1/0/11                 down     down         0%     0%          0          0
10GE1/0/12                 up       up        0.01%  0.01%          0          0
10GE1/0/13                 down     down         0%     0%          0          0
10GE1/0/14                 down     down         0%     0%          0          0
10GE1/0/15                 down     down         0%     0%          0          0
10GE1/0/16                 down     down         0%     0%          0          0
10GE1/0/17                 up       up           0%  0.01%          0          0
10GE1/0/41                 up       up        0.01%  0.01%          0          0
10GE1/0/46                 up       up        0.01%  0.01%          0          0
10GE1/0/48.124             down     down         0%     0%          0          0
Eth-Trunk1                 down     down         0%     0%          0          0
LoopBack1                  up       up(s)        0%     0%          0          0
MEth0/0/0                  up       up        0.01%  0.01%          0          0
NULL0                      up       up(s)        0%     0%          0          0
Nve1                       up       up           --     --          0          0
Vlanif500                  *down    down         --     --          0          0
Vlanif802                  up       up           --     --          0          0
Vlanif1002                 down     down         --     --          0          0
    """
    cmd = "display interface brief"
    host = "ce6870ei-test"
    version = """
Huawei Versatile Routing Platform Software
VRP (R) software, Version 8.180 (CE6870EI V200R005C00SPC800)
Copyright (C) 2012-2018 Huawei Technologies Co., Ltd.
HUAWEI CE6870-48S6CQ-EI uptime is 44 days, 0 hour, 49 minutes

CE6870-48S6CQ-EI(Master) 1 : uptime is  44 days, 0 hour, 48 minutes
        StartupTime 2018/11/26   12:45:50
Memory    Size    : 4096 M bytes
Flash     Size    : 1024 M bytes
CE6870-48S6CQ-EI version information                              
1. PCB    Version : CEM48S6CQP01    VER B
2. MAB    Version : 1
3. Board  Type    : CE6870-48S6CQ-EI
4. CPLD1  Version : 102
5. CPLD2  Version : 102
6. BIOS   Version : 432
    """
    result = {'100GE1/0/1': {'PHY': 'up', 'Protocol': 'up', 'InUti': '0%', 'OutUti': '0.01%', 'inErrors': '0', 'outErrors': '0'},
              '100GE1/0/2': {'PHY': 'up', 'Protocol': 'up', 'InUti': '0.01%', 'OutUti': '0.01%', 'inErrors': '0', 'outErrors': '0'},
              '100GE1/0/3': {'PHY': '*down', 'Protocol': 'down', 'InUti': '0%', 'OutUti': '0%', 'inErrors': '0', 'outErrors': '0'},
              '100GE1/0/4': {'PHY': 'up', 'Protocol': 'up', 'InUti': '0.01%', 'OutUti': '0.01%', 'inErrors': '0', 'outErrors': '0'},
              '10GE1/0/1': {'PHY': 'up', 'Protocol': 'up', 'InUti': '0.01%', 'OutUti': '5.19%', 'inErrors': '0', 'outErrors': '0'},
              '10GE1/0/2': {'PHY': 'down', 'Protocol': 'down', 'InUti': '0%', 'OutUti': '0%', 'inErrors': '0', 'outErrors': '0'},
              '10GE1/0/11': {'PHY': 'down', 'Protocol': 'down', 'InUti': '0%', 'OutUti': '0%', 'inErrors': '0', 'outErrors': '0'},
              '10GE1/0/12': {'PHY': 'up', 'Protocol': 'up', 'InUti': '0.01%', 'OutUti': '0.01%', 'inErrors': '0', 'outErrors': '0'},
              '10GE1/0/13': {'PHY': 'down', 'Protocol': 'down', 'InUti': '0%', 'OutUti': '0%', 'inErrors': '0', 'outErrors': '0'},
              '10GE1/0/14': {'PHY': 'down', 'Protocol': 'down', 'InUti': '0%', 'OutUti': '0%', 'inErrors': '0', 'outErrors': '0'},
              '10GE1/0/15': {'PHY': 'down', 'Protocol': 'down', 'InUti': '0%', 'OutUti': '0%', 'inErrors': '0', 'outErrors': '0'},
              '10GE1/0/16': {'PHY': 'down', 'Protocol': 'down', 'InUti': '0%', 'OutUti': '0%', 'inErrors': '0', 'outErrors': '0'},
              '10GE1/0/17': {'PHY': 'up', 'Protocol': 'up', 'InUti': '0%', 'OutUti': '0.01%', 'inErrors': '0', 'outErrors': '0'},
              '10GE1/0/41': {'PHY': 'up', 'Protocol': 'up', 'InUti': '0.01%', 'OutUti': '0.01%', 'inErrors': '0', 'outErrors': '0'},
              '10GE1/0/46': {'PHY': 'up', 'Protocol': 'up', 'InUti': '0.01%', 'OutUti': '0.01%', 'inErrors': '0', 'outErrors': '0'},
              '10GE1/0/48.124': {'PHY': 'down', 'Protocol': 'down', 'InUti': '0%', 'OutUti': '0%', 'inErrors': '0', 'outErrors': '0'},
              'Eth-Trunk1': {'PHY': 'down', 'Protocol': 'down', 'InUti': '0%', 'OutUti': '0%', 'inErrors': '0', 'outErrors': '0'},
              'LoopBack1': {'PHY': 'up', 'Protocol': 'up(s)', 'InUti': '0%', 'OutUti': '0%', 'inErrors': '0', 'outErrors': '0'},
              'MEth0/0/0': {'PHY': 'up', 'Protocol': 'up', 'InUti': '0.01%', 'OutUti': '0.01%', 'inErrors': '0', 'outErrors': '0'},
              'NULL0': {'PHY': 'up', 'Protocol': 'up(s)', 'InUti': '0%', 'OutUti': '0%', 'inErrors': '0', 'outErrors': '0'},
              'Nve1': {'PHY': 'up', 'Protocol': 'up', 'InUti': '--', 'OutUti': '--', 'inErrors': '0', 'outErrors': '0'},
              'Vlanif500': {'PHY': '*down', 'Protocol': 'down', 'InUti': '--', 'OutUti': '--', 'inErrors': '0', 'outErrors': '0'},
              'Vlanif802': {'PHY': 'up', 'Protocol': 'up', 'InUti': '--', 'OutUti': '--', 'inErrors': '0', 'outErrors': '0'},
              'Vlanif1002': {'PHY': 'down', 'Protocol': 'down', 'InUti': '--', 'OutUti': '--', 'inErrors': '0', 'outErrors': '0'}}
