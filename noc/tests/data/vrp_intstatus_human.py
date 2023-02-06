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
100GE1/0/1                 up       down     14.58% 19.47%          0          0
100GE1/0/1.3000            up       down         0%     0%          0          0
100GE1/0/2                 up       down     22.31% 21.78%          0          0
100GE1/0/2.3000            up       down         0%     0%          0          0
100GE1/0/3                 up       down     21.71% 20.07%          0          0
100GE1/0/3.3000            up       down         0%     0%          0          0
100GE1/0/4                 up       down     21.64% 20.14%          0          0
100GE1/0/4.3000            up       down         0%     0%          0          0
100GE1/0/5                 down     down         0%     0%          0          0
100GE1/0/6                 down     down         0%     0%          0          0
10GE1/0/1                  up       up       25.84% 19.42%          0          0
10GE1/0/2                  up       up       26.61% 26.90%          0          0
10GE1/0/3                  up       up       28.52% 28.56%          0          0
10GE1/0/4                  up       up       29.97% 27.51%          0          0
10GE1/0/5                  up       up       26.00% 29.08%          0          0
10GE1/0/6                  up       up       24.29% 17.73%          0          0
10GE1/0/7                  up       up       25.81% 25.36%          0          0
10GE1/0/8                  up       up       27.65% 19.21%          0          0
10GE1/0/9                  up       up       26.22% 21.38%          0          0
10GE1/0/10                 up       up       14.91% 29.69%          0          0
10GE1/0/11                 up       up       23.38% 19.11%          0          0
10GE1/0/12                 up       up       25.86% 25.27%          0          0
10GE1/0/13                 up       up       29.97% 18.71%          0          0
10GE1/0/14                 up       up       24.08% 20.45%          0          0
10GE1/0/15                 up       up       26.65% 23.34%          0          0
10GE1/0/16                 up       up           0%  0.01%          0          0
10GE1/0/17                 up       up       26.81% 27.05%          0          0
10GE1/0/18                 up       up       27.46% 28.39%          0          0
10GE1/0/19                 up       up       27.47% 25.69%          0          0
10GE1/0/20                 up       up       26.74% 27.80%          0          0
10GE1/0/21                 up       up       26.95% 26.89%          0          0
10GE1/0/22                 up       up       24.47% 30.18%          0          0
10GE1/0/23                 up       up       23.81% 23.38%          0          0
10GE1/0/24                 up       up       25.44% 28.83%          0          0
10GE1/0/25                 up       up       25.21% 24.64%          0          0
10GE1/0/26                 up       up       25.43% 26.52%          0          0
10GE1/0/27                 up       up        0.07%  0.06%          0          0
10GE1/0/28                 up       up       27.05% 28.38%          0          0
10GE1/0/29                 up       up       29.14% 30.16%          0          0
10GE1/0/30                 up       up       29.18% 28.89%          0          0
10GE1/0/31                 up       up       14.71% 26.71%          0          0
10GE1/0/32                 up       up       37.81% 30.72%          0          0
10GE1/0/33                 up       up       33.46% 38.90%          0          0
10GE1/0/34                 up       up        0.06%  0.06%          0          0
10GE1/0/35                 up       up        1.74%  1.60%          0          0
10GE1/0/36                 up       up        0.06%  0.07%          0          0
10GE1/0/37                 down     down         0%     0%          0          0
10GE1/0/38                 down     down         0%     0%          0          0
10GE1/0/39                 down     down         0%     0%          0          0
10GE1/0/40                 down     down         0%     0%          0          0
10GE1/0/41                 down     down         0%     0%          0          0
10GE1/0/42                 down     down         0%     0%          0          0
10GE1/0/43                 down     down         0%     0%          0          0
10GE1/0/44                 down     down         0%     0%          0          0
10GE1/0/45                 down     down         0%     0%          0          0
10GE1/0/46                 down     down         0%     0%          0          0
10GE1/0/47                 down     down         0%     0%          0          0
10GE1/0/48                 down     down         0%     0%          0          0
MEth0/0/0                  up       up        0.01%  0.01%          0          0
NULL0                      up       up(s)        0%     0%          0          0
Vlanif333                  up       down         --     --          0          0
Vlanif688                  up       down         --     --          0          0
Vlanif700                  up       down         --     --          0          0
Vlanif788                  up       down         --     --          0          0
    """
    cmd = "display interface brief"
    host = "vla1-1s80"
    version = """
Huawei Versatile Routing Platform Software
VRP (R) software, Version 8.180 (CE6870EI V200R005C00SPC800)
Copyright (C) 2012-2018 Huawei Technologies Co., Ltd.
HUAWEI CE6870-48S6CQ-EI uptime is 43 days, 22 hours, 49 minutes

CE6870-48S6CQ-EI(Master) 1 : uptime is  43 days, 22 hours, 48 minutes
        StartupTime 2018/11/30   14:06:01+03:00
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
    result = [{'interface': '100GE1/0/1', 'state': 'up'},
              {'interface': '100GE1/0/1.3000', 'state': 'up'},
              {'interface': '100GE1/0/2', 'state': 'up'},
              {'interface': '100GE1/0/2.3000', 'state': 'up'},
              {'interface': '100GE1/0/3', 'state': 'up'},
              {'interface': '100GE1/0/3.3000', 'state': 'up'},
              {'interface': '100GE1/0/4', 'state': 'up'},
              {'interface': '100GE1/0/4.3000', 'state': 'up'},
              {'interface': '100GE1/0/5', 'state': 'down'},
              {'interface': '100GE1/0/6', 'state': 'down'},
              {'interface': '10GE1/0/1', 'state': 'up'},
              {'interface': '10GE1/0/2', 'state': 'up'},
              {'interface': '10GE1/0/3', 'state': 'up'},
              {'interface': '10GE1/0/4', 'state': 'up'},
              {'interface': '10GE1/0/5', 'state': 'up'},
              {'interface': '10GE1/0/6', 'state': 'up'},
              {'interface': '10GE1/0/7', 'state': 'up'},
              {'interface': '10GE1/0/8', 'state': 'up'},
              {'interface': '10GE1/0/9', 'state': 'up'},
              {'interface': '10GE1/0/10', 'state': 'up'},
              {'interface': '10GE1/0/11', 'state': 'up'},
              {'interface': '10GE1/0/12', 'state': 'up'},
              {'interface': '10GE1/0/13', 'state': 'up'},
              {'interface': '10GE1/0/14', 'state': 'up'},
              {'interface': '10GE1/0/15', 'state': 'up'},
              {'interface': '10GE1/0/16', 'state': 'up'},
              {'interface': '10GE1/0/17', 'state': 'up'},
              {'interface': '10GE1/0/18', 'state': 'up'},
              {'interface': '10GE1/0/19', 'state': 'up'},
              {'interface': '10GE1/0/20', 'state': 'up'},
              {'interface': '10GE1/0/21', 'state': 'up'},
              {'interface': '10GE1/0/22', 'state': 'up'},
              {'interface': '10GE1/0/23', 'state': 'up'},
              {'interface': '10GE1/0/24', 'state': 'up'},
              {'interface': '10GE1/0/25', 'state': 'up'},
              {'interface': '10GE1/0/26', 'state': 'up'},
              {'interface': '10GE1/0/27', 'state': 'up'},
              {'interface': '10GE1/0/28', 'state': 'up'},
              {'interface': '10GE1/0/29', 'state': 'up'},
              {'interface': '10GE1/0/30', 'state': 'up'},
              {'interface': '10GE1/0/31', 'state': 'up'},
              {'interface': '10GE1/0/32', 'state': 'up'},
              {'interface': '10GE1/0/33', 'state': 'up'},
              {'interface': '10GE1/0/34', 'state': 'up'},
              {'interface': '10GE1/0/35', 'state': 'up'},
              {'interface': '10GE1/0/36', 'state': 'up'},
              {'interface': '10GE1/0/37', 'state': 'down'},
              {'interface': '10GE1/0/38', 'state': 'down'},
              {'interface': '10GE1/0/39', 'state': 'down'},
              {'interface': '10GE1/0/40', 'state': 'down'},
              {'interface': '10GE1/0/41', 'state': 'down'},
              {'interface': '10GE1/0/42', 'state': 'down'},
              {'interface': '10GE1/0/43', 'state': 'down'},
              {'interface': '10GE1/0/44', 'state': 'down'},
              {'interface': '10GE1/0/45', 'state': 'down'},
              {'interface': '10GE1/0/46', 'state': 'down'},
              {'interface': '10GE1/0/47', 'state': 'down'},
              {'interface': '10GE1/0/48', 'state': 'down'},
              {'interface': 'MEth0/0/0', 'state': 'up'},
              {'interface': 'NULL0', 'state': 'up'},
              {'interface': 'Vlanif333', 'state': 'up'},
              {'interface': 'Vlanif688', 'state': 'up'},
              {'interface': 'Vlanif700', 'state': 'up'},
              {'interface': 'Vlanif788', 'state': 'up'}]
