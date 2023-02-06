from data.lib import Data


class Data1(Data):
    content = """
Huawei Versatile Routing Platform Software
VRP (R) software, Version 8.180 (CE6870EI V200R005C00SPC800)
Copyright (C) 2012-2018 Huawei Technologies Co., Ltd.
HUAWEI CE6870-48S6CQ-EI uptime is 9 days, 0 hour, 47 minutes

CE6870-48S6CQ-EI(Master) 1 : uptime is  9 days, 0 hour, 46 minutes
        StartupTime 2019/02/16   10:28:06
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
    cmd = "display version"
    host = "ce6870ei-test"
    version = """
Huawei Versatile Routing Platform Software
VRP (R) software, Version 8.180 (CE6870EI V200R005C00SPC800)
Copyright (C) 2012-2018 Huawei Technologies Co., Ltd.
HUAWEI CE6870-48S6CQ-EI uptime is 9 days, 0 hour, 47 minutes

CE6870-48S6CQ-EI(Master) 1 : uptime is  9 days, 0 hour, 46 minutes
        StartupTime 2019/02/16   10:28:06
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
    result = ('CE6870-48S6CQ-EI', 'V200R005C00SPC800')  # insert parsed result here
