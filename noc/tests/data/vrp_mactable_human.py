from data.lib import Data


class Data1(Data):
    content = """
Flags: * - Backup 
       # - forwarding logical interface, operations cannot be performed based
           on the interface.
BD   : bridge-domain   Age : dynamic MAC learned time in seconds
-------------------------------------------------------------------------------
MAC Address    VLAN/VSI/BD   Learned-From        Type                Age
-------------------------------------------------------------------------------
506b-4b16-3f24 333/-/-       10GE1/0/21          dynamic         3798236
506b-4b16-44c8 333/-/-       10GE1/0/33          dynamic         3798238
506b-4b22-5cfa 333/-/-       10GE1/0/27          dynamic         3798236
506b-4b22-5d02 333/-/-       10GE1/0/18          dynamic         3798237
506b-4b22-5d0a 333/-/-       10GE1/0/30          dynamic         3798237
506b-4b22-5d0e 333/-/-       10GE1/0/36          dynamic         3798238
506b-4b22-5d16 333/-/-       10GE1/0/26          dynamic         3798237
506b-4b22-5d1a 333/-/-       10GE1/0/22          dynamic         3798236
506b-4b22-5d22 333/-/-       10GE1/0/24          dynamic         3798236
506b-4b22-5d32 333/-/-       10GE1/0/28          dynamic         3798236
506b-4b22-5d3e 333/-/-       10GE1/0/32          dynamic         3798237
506b-4b22-5dca 333/-/-       10GE1/0/25          dynamic         3798237
506b-4b22-5dce 333/-/-       10GE1/0/35          dynamic         3798238
506b-4b22-5dea 333/-/-       10GE1/0/31          dynamic         3798237
506b-4b22-5dee 333/-/-       10GE1/0/29          dynamic         3798237
506b-4b22-5f8e 333/-/-       10GE1/0/20          dynamic         3798236
506b-4b22-5f92 333/-/-       10GE1/0/34          dynamic         3798238
506b-4b22-600a 333/-/-       10GE1/0/6           dynamic         3798235
506b-4b22-63b6 333/-/-       10GE1/0/11          dynamic         3798235
506b-4b22-63ba 333/-/-       10GE1/0/15          dynamic         3798217
506b-4b22-63be 333/-/-       10GE1/0/1           dynamic         3798235
506b-4b22-63c6 333/-/-       10GE1/0/9           dynamic         3798235
506b-4b22-63ca 333/-/-       10GE1/0/5           dynamic         3798235
506b-4b22-6aba 333/-/-       10GE1/0/12          dynamic         3798235
506b-4b22-6ac2 333/-/-       10GE1/0/10          dynamic         3798235
506b-4b22-6aca 333/-/-       10GE1/0/8           dynamic         3798235
506b-4b22-6ace 333/-/-       10GE1/0/2           dynamic         3798235
506b-4b22-6ad2 333/-/-       10GE1/0/14          dynamic         3798236
506b-4b22-6d52 333/-/-       10GE1/0/4           dynamic         3798235
506b-4b22-70be 333/-/-       10GE1/0/3           dynamic         3798235
506b-4b22-726e 333/-/-       10GE1/0/23          dynamic         3798236
506b-4b22-7276 333/-/-       10GE1/0/7           dynamic         3798235
506b-4b22-728a 333/-/-       10GE1/0/13          dynamic         3798236
506b-4b22-79b6 333/-/-       10GE1/0/17          dynamic         3798237
506b-4b22-7a9a 333/-/-       10GE1/0/19          dynamic         3798236
506b-4b16-3f24 688/-/-       10GE1/0/21          dynamic         3798236
506b-4b16-44c8 688/-/-       10GE1/0/33          dynamic         3798237
506b-4b22-5cfa 688/-/-       10GE1/0/27          dynamic         3798194
506b-4b22-5d02 688/-/-       10GE1/0/18          dynamic         3798236
506b-4b22-5d0a 688/-/-       10GE1/0/30          dynamic         3798236
506b-4b22-5d0e 688/-/-       10GE1/0/36          dynamic         3798214
506b-4b22-5d16 688/-/-       10GE1/0/26          dynamic         3798236
506b-4b22-5d1a 688/-/-       10GE1/0/22          dynamic         3798236
506b-4b22-5d22 688/-/-       10GE1/0/24          dynamic         3798236
506b-4b22-5d32 688/-/-       10GE1/0/28          dynamic         3798236
506b-4b22-5d3e 688/-/-       10GE1/0/32          dynamic         3798237
506b-4b22-5dca 688/-/-       10GE1/0/25          dynamic         3798236
506b-4b22-5dce 688/-/-       10GE1/0/35          dynamic         3798238
506b-4b22-5dea 688/-/-       10GE1/0/31          dynamic         3798236
506b-4b22-5dee 688/-/-       10GE1/0/29          dynamic         3798236
506b-4b22-5f8e 688/-/-       10GE1/0/20          dynamic         3798236
506b-4b22-5f92 688/-/-       10GE1/0/34          dynamic         3798222
506b-4b22-600a 688/-/-       10GE1/0/6           dynamic         3798234
506b-4b22-63b6 688/-/-       10GE1/0/11          dynamic         3798235
506b-4b22-63ba 688/-/-       10GE1/0/15          dynamic         3798235
506b-4b22-63be 688/-/-       10GE1/0/1           dynamic         3798235
506b-4b22-63c6 688/-/-       10GE1/0/9           dynamic         3798235
506b-4b22-63ca 688/-/-       10GE1/0/5           dynamic         3798235
506b-4b22-6aba 688/-/-       10GE1/0/12          dynamic         3798235
506b-4b22-6ac2 688/-/-       10GE1/0/10          dynamic         3798234
506b-4b22-6aca 688/-/-       10GE1/0/8           dynamic         3798235
506b-4b22-6ace 688/-/-       10GE1/0/2           dynamic         3798235
506b-4b22-6ad2 688/-/-       10GE1/0/14          dynamic         3798235
506b-4b22-6d52 688/-/-       10GE1/0/4           dynamic         3798235
506b-4b22-70be 688/-/-       10GE1/0/3           dynamic         3798232
506b-4b22-726e 688/-/-       10GE1/0/23          dynamic         3798235
506b-4b22-7276 688/-/-       10GE1/0/7           dynamic         3798235
506b-4b22-728a 688/-/-       10GE1/0/13          dynamic         3798235
506b-4b22-79b6 688/-/-       10GE1/0/17          dynamic         3798237
506b-4b22-7a9a 688/-/-       10GE1/0/19          dynamic         3798236
506b-4b16-3f24 700/-/-       10GE1/0/21          dynamic         3798236
506b-4b16-44c8 700/-/-       10GE1/0/33          dynamic         3798238
506b-4b22-5cfa 700/-/-       10GE1/0/27          dynamic         3798226
506b-4b22-5d02 700/-/-       10GE1/0/18          dynamic         3798226
506b-4b22-5d0a 700/-/-       10GE1/0/30          dynamic         3798226
506b-4b22-5d0e 700/-/-       10GE1/0/36          dynamic         3798226
506b-4b22-5d16 700/-/-       10GE1/0/26          dynamic         3798223
506b-4b22-5d1a 700/-/-       10GE1/0/22          dynamic         3798225
506b-4b22-5d22 700/-/-       10GE1/0/24          dynamic         3798236
506b-4b22-5d32 700/-/-       10GE1/0/28          dynamic         3798225
506b-4b22-5d3e 700/-/-       10GE1/0/32          dynamic         3798227
506b-4b22-5dca 700/-/-       10GE1/0/25          dynamic         3798226
506b-4b22-5dce 700/-/-       10GE1/0/35          dynamic         3798227
506b-4b22-5dea 700/-/-       10GE1/0/31          dynamic         3798226
506b-4b22-5dee 700/-/-       10GE1/0/29          dynamic         3798226
506b-4b22-5f8e 700/-/-       10GE1/0/20          dynamic         3798225
506b-4b22-5f92 700/-/-       10GE1/0/34          dynamic         3798238
506b-4b22-600a 700/-/-       10GE1/0/6           dynamic         3798226
506b-4b22-63b6 700/-/-       10GE1/0/11          dynamic         3798227
506b-4b22-63ba 700/-/-       10GE1/0/15          dynamic         3798227
506b-4b22-63be 700/-/-       10GE1/0/1           dynamic         3798226
506b-4b22-63c6 700/-/-       10GE1/0/9           dynamic         3798226
506b-4b22-63ca 700/-/-       10GE1/0/5           dynamic         3798226
506b-4b22-6aba 700/-/-       10GE1/0/12          dynamic         3798226
506b-4b22-6ac2 700/-/-       10GE1/0/10          dynamic         3798226
506b-4b22-6aca 700/-/-       10GE1/0/8           dynamic         3798225
506b-4b22-6ace 700/-/-       10GE1/0/2           dynamic         3798226
506b-4b22-6ad2 700/-/-       10GE1/0/14          dynamic         3798226
506b-4b22-6d52 700/-/-       10GE1/0/4           dynamic         3798227
506b-4b22-70be 700/-/-       10GE1/0/3           dynamic         3798227
506b-4b22-726e 700/-/-       10GE1/0/23          dynamic         3798227
506b-4b22-7276 700/-/-       10GE1/0/7           dynamic         3798226
506b-4b22-728a 700/-/-       10GE1/0/13          dynamic         3798227
506b-4b22-79b6 700/-/-       10GE1/0/17          dynamic         3798227
506b-4b22-7a9a 700/-/-       10GE1/0/19          dynamic         3798227
506b-4b16-3f24 788/-/-       10GE1/0/21          dynamic         3798224
506b-4b16-44c8 788/-/-       10GE1/0/33          dynamic         3798238
506b-4b22-5cfa 788/-/-       10GE1/0/27          dynamic         3798194
506b-4b22-5d02 788/-/-       10GE1/0/18          dynamic         3798217
506b-4b22-5d0a 788/-/-       10GE1/0/30          dynamic         3798216
506b-4b22-5d0e 788/-/-       10GE1/0/36          dynamic         3798211
506b-4b22-5d16 788/-/-       10GE1/0/26          dynamic         3798199
506b-4b22-5d1a 788/-/-       10GE1/0/22          dynamic         3798215
506b-4b22-5d22 788/-/-       10GE1/0/24          dynamic         3798181
506b-4b22-5d32 788/-/-       10GE1/0/28          dynamic         3798178
506b-4b22-5d3e 788/-/-       10GE1/0/32          dynamic         3798224
506b-4b22-5dca 788/-/-       10GE1/0/25          dynamic         3798199
506b-4b22-5dce 788/-/-       10GE1/0/35          dynamic         3798206
506b-4b22-5dea 788/-/-       10GE1/0/31          dynamic         3798175
506b-4b22-5dee 788/-/-       10GE1/0/29          dynamic         3798207
506b-4b22-5f8e 788/-/-       10GE1/0/20          dynamic         3798219
506b-4b22-5f92 788/-/-       10GE1/0/34          dynamic         3798177
506b-4b22-600a 788/-/-       10GE1/0/6           dynamic         3798218
506b-4b22-63b6 788/-/-       10GE1/0/11          dynamic         3798216
506b-4b22-63ba 788/-/-       10GE1/0/15          dynamic         3798226
506b-4b22-63be 788/-/-       10GE1/0/1           dynamic         3798224
506b-4b22-63c6 788/-/-       10GE1/0/9           dynamic         3798212
506b-4b22-63ca 788/-/-       10GE1/0/5           dynamic         3798163
506b-4b22-6aba 788/-/-       10GE1/0/12          dynamic         3798206
506b-4b22-6ac2 788/-/-       10GE1/0/10          dynamic         3798224
506b-4b22-6aca 788/-/-       10GE1/0/8           dynamic         3798134
506b-4b22-6ace 788/-/-       10GE1/0/2           dynamic         3798214
506b-4b22-6ad2 788/-/-       10GE1/0/14          dynamic         3798215
506b-4b22-6d52 788/-/-       10GE1/0/4           dynamic         3798176
506b-4b22-70be 788/-/-       10GE1/0/3           dynamic         3798223
506b-4b22-726e 788/-/-       10GE1/0/23          dynamic         3798222
506b-4b22-7276 788/-/-       10GE1/0/7           dynamic         3798213
506b-4b22-728a 788/-/-       10GE1/0/13          dynamic         3798189
506b-4b22-79b6 788/-/-       10GE1/0/17          dynamic         3798222
506b-4b22-7a9a 788/-/-       10GE1/0/19          dynamic         3798112
-------------------------------------------------------------------------------
Total items: 140
    """
    cmd = "display mac-address"
    host = "vla1-1s80"
    version = """
Huawei Versatile Routing Platform Software
VRP (R) software, Version 8.180 (CE6870EI V200R005C00SPC800)
Copyright (C) 2012-2018 Huawei Technologies Co., Ltd.
HUAWEI CE6870-48S6CQ-EI uptime is 43 days, 23 hours, 7 minutes

CE6870-48S6CQ-EI(Master) 1 : uptime is  43 days, 23 hours, 6 minutes
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
    result = [{'interface': '10GE1/0/21', 'mac': '506b-4b16-3f24', 'vlan': '333'},
              {'interface': '10GE1/0/33', 'mac': '506b-4b16-44c8', 'vlan': '333'},
              {'interface': '10GE1/0/27', 'mac': '506b-4b22-5cfa', 'vlan': '333'},
              {'interface': '10GE1/0/18', 'mac': '506b-4b22-5d02', 'vlan': '333'},
              {'interface': '10GE1/0/30', 'mac': '506b-4b22-5d0a', 'vlan': '333'},
              {'interface': '10GE1/0/36', 'mac': '506b-4b22-5d0e', 'vlan': '333'},
              {'interface': '10GE1/0/26', 'mac': '506b-4b22-5d16', 'vlan': '333'},
              {'interface': '10GE1/0/22', 'mac': '506b-4b22-5d1a', 'vlan': '333'},
              {'interface': '10GE1/0/24', 'mac': '506b-4b22-5d22', 'vlan': '333'},
              {'interface': '10GE1/0/28', 'mac': '506b-4b22-5d32', 'vlan': '333'},
              {'interface': '10GE1/0/32', 'mac': '506b-4b22-5d3e', 'vlan': '333'},
              {'interface': '10GE1/0/25', 'mac': '506b-4b22-5dca', 'vlan': '333'},
              {'interface': '10GE1/0/35', 'mac': '506b-4b22-5dce', 'vlan': '333'},
              {'interface': '10GE1/0/31', 'mac': '506b-4b22-5dea', 'vlan': '333'},
              {'interface': '10GE1/0/29', 'mac': '506b-4b22-5dee', 'vlan': '333'},
              {'interface': '10GE1/0/20', 'mac': '506b-4b22-5f8e', 'vlan': '333'},
              {'interface': '10GE1/0/34', 'mac': '506b-4b22-5f92', 'vlan': '333'},
              {'interface': '10GE1/0/6', 'mac': '506b-4b22-600a', 'vlan': '333'},
              {'interface': '10GE1/0/11', 'mac': '506b-4b22-63b6', 'vlan': '333'},
              {'interface': '10GE1/0/15', 'mac': '506b-4b22-63ba', 'vlan': '333'},
              {'interface': '10GE1/0/1', 'mac': '506b-4b22-63be', 'vlan': '333'},
              {'interface': '10GE1/0/9', 'mac': '506b-4b22-63c6', 'vlan': '333'},
              {'interface': '10GE1/0/5', 'mac': '506b-4b22-63ca', 'vlan': '333'},
              {'interface': '10GE1/0/12', 'mac': '506b-4b22-6aba', 'vlan': '333'},
              {'interface': '10GE1/0/10', 'mac': '506b-4b22-6ac2', 'vlan': '333'},
              {'interface': '10GE1/0/8', 'mac': '506b-4b22-6aca', 'vlan': '333'},
              {'interface': '10GE1/0/2', 'mac': '506b-4b22-6ace', 'vlan': '333'},
              {'interface': '10GE1/0/14', 'mac': '506b-4b22-6ad2', 'vlan': '333'},
              {'interface': '10GE1/0/4', 'mac': '506b-4b22-6d52', 'vlan': '333'},
              {'interface': '10GE1/0/3', 'mac': '506b-4b22-70be', 'vlan': '333'},
              {'interface': '10GE1/0/23', 'mac': '506b-4b22-726e', 'vlan': '333'},
              {'interface': '10GE1/0/7', 'mac': '506b-4b22-7276', 'vlan': '333'},
              {'interface': '10GE1/0/13', 'mac': '506b-4b22-728a', 'vlan': '333'},
              {'interface': '10GE1/0/17', 'mac': '506b-4b22-79b6', 'vlan': '333'},
              {'interface': '10GE1/0/19', 'mac': '506b-4b22-7a9a', 'vlan': '333'},
              {'interface': '10GE1/0/21', 'mac': '506b-4b16-3f24', 'vlan': '688'},
              {'interface': '10GE1/0/33', 'mac': '506b-4b16-44c8', 'vlan': '688'},
              {'interface': '10GE1/0/27', 'mac': '506b-4b22-5cfa', 'vlan': '688'},
              {'interface': '10GE1/0/18', 'mac': '506b-4b22-5d02', 'vlan': '688'},
              {'interface': '10GE1/0/30', 'mac': '506b-4b22-5d0a', 'vlan': '688'},
              {'interface': '10GE1/0/36', 'mac': '506b-4b22-5d0e', 'vlan': '688'},
              {'interface': '10GE1/0/26', 'mac': '506b-4b22-5d16', 'vlan': '688'},
              {'interface': '10GE1/0/22', 'mac': '506b-4b22-5d1a', 'vlan': '688'},
              {'interface': '10GE1/0/24', 'mac': '506b-4b22-5d22', 'vlan': '688'},
              {'interface': '10GE1/0/28', 'mac': '506b-4b22-5d32', 'vlan': '688'},
              {'interface': '10GE1/0/32', 'mac': '506b-4b22-5d3e', 'vlan': '688'},
              {'interface': '10GE1/0/25', 'mac': '506b-4b22-5dca', 'vlan': '688'},
              {'interface': '10GE1/0/35', 'mac': '506b-4b22-5dce', 'vlan': '688'},
              {'interface': '10GE1/0/31', 'mac': '506b-4b22-5dea', 'vlan': '688'},
              {'interface': '10GE1/0/29', 'mac': '506b-4b22-5dee', 'vlan': '688'},
              {'interface': '10GE1/0/20', 'mac': '506b-4b22-5f8e', 'vlan': '688'},
              {'interface': '10GE1/0/34', 'mac': '506b-4b22-5f92', 'vlan': '688'},
              {'interface': '10GE1/0/6', 'mac': '506b-4b22-600a', 'vlan': '688'},
              {'interface': '10GE1/0/11', 'mac': '506b-4b22-63b6', 'vlan': '688'},
              {'interface': '10GE1/0/15', 'mac': '506b-4b22-63ba', 'vlan': '688'},
              {'interface': '10GE1/0/1', 'mac': '506b-4b22-63be', 'vlan': '688'},
              {'interface': '10GE1/0/9', 'mac': '506b-4b22-63c6', 'vlan': '688'},
              {'interface': '10GE1/0/5', 'mac': '506b-4b22-63ca', 'vlan': '688'},
              {'interface': '10GE1/0/12', 'mac': '506b-4b22-6aba', 'vlan': '688'},
              {'interface': '10GE1/0/10', 'mac': '506b-4b22-6ac2', 'vlan': '688'},
              {'interface': '10GE1/0/8', 'mac': '506b-4b22-6aca', 'vlan': '688'},
              {'interface': '10GE1/0/2', 'mac': '506b-4b22-6ace', 'vlan': '688'},
              {'interface': '10GE1/0/14', 'mac': '506b-4b22-6ad2', 'vlan': '688'},
              {'interface': '10GE1/0/4', 'mac': '506b-4b22-6d52', 'vlan': '688'},
              {'interface': '10GE1/0/3', 'mac': '506b-4b22-70be', 'vlan': '688'},
              {'interface': '10GE1/0/23', 'mac': '506b-4b22-726e', 'vlan': '688'},
              {'interface': '10GE1/0/7', 'mac': '506b-4b22-7276', 'vlan': '688'},
              {'interface': '10GE1/0/13', 'mac': '506b-4b22-728a', 'vlan': '688'},
              {'interface': '10GE1/0/17', 'mac': '506b-4b22-79b6', 'vlan': '688'},
              {'interface': '10GE1/0/19', 'mac': '506b-4b22-7a9a', 'vlan': '688'},
              {'interface': '10GE1/0/21', 'mac': '506b-4b16-3f24', 'vlan': '700'},
              {'interface': '10GE1/0/33', 'mac': '506b-4b16-44c8', 'vlan': '700'},
              {'interface': '10GE1/0/27', 'mac': '506b-4b22-5cfa', 'vlan': '700'},
              {'interface': '10GE1/0/18', 'mac': '506b-4b22-5d02', 'vlan': '700'},
              {'interface': '10GE1/0/30', 'mac': '506b-4b22-5d0a', 'vlan': '700'},
              {'interface': '10GE1/0/36', 'mac': '506b-4b22-5d0e', 'vlan': '700'},
              {'interface': '10GE1/0/26', 'mac': '506b-4b22-5d16', 'vlan': '700'},
              {'interface': '10GE1/0/22', 'mac': '506b-4b22-5d1a', 'vlan': '700'},
              {'interface': '10GE1/0/24', 'mac': '506b-4b22-5d22', 'vlan': '700'},
              {'interface': '10GE1/0/28', 'mac': '506b-4b22-5d32', 'vlan': '700'},
              {'interface': '10GE1/0/32', 'mac': '506b-4b22-5d3e', 'vlan': '700'},
              {'interface': '10GE1/0/25', 'mac': '506b-4b22-5dca', 'vlan': '700'},
              {'interface': '10GE1/0/35', 'mac': '506b-4b22-5dce', 'vlan': '700'},
              {'interface': '10GE1/0/31', 'mac': '506b-4b22-5dea', 'vlan': '700'},
              {'interface': '10GE1/0/29', 'mac': '506b-4b22-5dee', 'vlan': '700'},
              {'interface': '10GE1/0/20', 'mac': '506b-4b22-5f8e', 'vlan': '700'},
              {'interface': '10GE1/0/34', 'mac': '506b-4b22-5f92', 'vlan': '700'},
              {'interface': '10GE1/0/6', 'mac': '506b-4b22-600a', 'vlan': '700'},
              {'interface': '10GE1/0/11', 'mac': '506b-4b22-63b6', 'vlan': '700'},
              {'interface': '10GE1/0/15', 'mac': '506b-4b22-63ba', 'vlan': '700'},
              {'interface': '10GE1/0/1', 'mac': '506b-4b22-63be', 'vlan': '700'},
              {'interface': '10GE1/0/9', 'mac': '506b-4b22-63c6', 'vlan': '700'},
              {'interface': '10GE1/0/5', 'mac': '506b-4b22-63ca', 'vlan': '700'},
              {'interface': '10GE1/0/12', 'mac': '506b-4b22-6aba', 'vlan': '700'},
              {'interface': '10GE1/0/10', 'mac': '506b-4b22-6ac2', 'vlan': '700'},
              {'interface': '10GE1/0/8', 'mac': '506b-4b22-6aca', 'vlan': '700'},
              {'interface': '10GE1/0/2', 'mac': '506b-4b22-6ace', 'vlan': '700'},
              {'interface': '10GE1/0/14', 'mac': '506b-4b22-6ad2', 'vlan': '700'},
              {'interface': '10GE1/0/4', 'mac': '506b-4b22-6d52', 'vlan': '700'},
              {'interface': '10GE1/0/3', 'mac': '506b-4b22-70be', 'vlan': '700'},
              {'interface': '10GE1/0/23', 'mac': '506b-4b22-726e', 'vlan': '700'},
              {'interface': '10GE1/0/7', 'mac': '506b-4b22-7276', 'vlan': '700'},
              {'interface': '10GE1/0/13', 'mac': '506b-4b22-728a', 'vlan': '700'},
              {'interface': '10GE1/0/17', 'mac': '506b-4b22-79b6', 'vlan': '700'},
              {'interface': '10GE1/0/19', 'mac': '506b-4b22-7a9a', 'vlan': '700'},
              {'interface': '10GE1/0/21', 'mac': '506b-4b16-3f24', 'vlan': '788'},
              {'interface': '10GE1/0/33', 'mac': '506b-4b16-44c8', 'vlan': '788'},
              {'interface': '10GE1/0/27', 'mac': '506b-4b22-5cfa', 'vlan': '788'},
              {'interface': '10GE1/0/18', 'mac': '506b-4b22-5d02', 'vlan': '788'},
              {'interface': '10GE1/0/30', 'mac': '506b-4b22-5d0a', 'vlan': '788'},
              {'interface': '10GE1/0/36', 'mac': '506b-4b22-5d0e', 'vlan': '788'},
              {'interface': '10GE1/0/26', 'mac': '506b-4b22-5d16', 'vlan': '788'},
              {'interface': '10GE1/0/22', 'mac': '506b-4b22-5d1a', 'vlan': '788'},
              {'interface': '10GE1/0/24', 'mac': '506b-4b22-5d22', 'vlan': '788'},
              {'interface': '10GE1/0/28', 'mac': '506b-4b22-5d32', 'vlan': '788'},
              {'interface': '10GE1/0/32', 'mac': '506b-4b22-5d3e', 'vlan': '788'},
              {'interface': '10GE1/0/25', 'mac': '506b-4b22-5dca', 'vlan': '788'},
              {'interface': '10GE1/0/35', 'mac': '506b-4b22-5dce', 'vlan': '788'},
              {'interface': '10GE1/0/31', 'mac': '506b-4b22-5dea', 'vlan': '788'},
              {'interface': '10GE1/0/29', 'mac': '506b-4b22-5dee', 'vlan': '788'},
              {'interface': '10GE1/0/20', 'mac': '506b-4b22-5f8e', 'vlan': '788'},
              {'interface': '10GE1/0/34', 'mac': '506b-4b22-5f92', 'vlan': '788'},
              {'interface': '10GE1/0/6', 'mac': '506b-4b22-600a', 'vlan': '788'},
              {'interface': '10GE1/0/11', 'mac': '506b-4b22-63b6', 'vlan': '788'},
              {'interface': '10GE1/0/15', 'mac': '506b-4b22-63ba', 'vlan': '788'},
              {'interface': '10GE1/0/1', 'mac': '506b-4b22-63be', 'vlan': '788'},
              {'interface': '10GE1/0/9', 'mac': '506b-4b22-63c6', 'vlan': '788'},
              {'interface': '10GE1/0/5', 'mac': '506b-4b22-63ca', 'vlan': '788'},
              {'interface': '10GE1/0/12', 'mac': '506b-4b22-6aba', 'vlan': '788'},
              {'interface': '10GE1/0/10', 'mac': '506b-4b22-6ac2', 'vlan': '788'},
              {'interface': '10GE1/0/8', 'mac': '506b-4b22-6aca', 'vlan': '788'},
              {'interface': '10GE1/0/2', 'mac': '506b-4b22-6ace', 'vlan': '788'},
              {'interface': '10GE1/0/14', 'mac': '506b-4b22-6ad2', 'vlan': '788'},
              {'interface': '10GE1/0/4', 'mac': '506b-4b22-6d52', 'vlan': '788'},
              {'interface': '10GE1/0/3', 'mac': '506b-4b22-70be', 'vlan': '788'},
              {'interface': '10GE1/0/23', 'mac': '506b-4b22-726e', 'vlan': '788'},
              {'interface': '10GE1/0/7', 'mac': '506b-4b22-7276', 'vlan': '788'},
              {'interface': '10GE1/0/13', 'mac': '506b-4b22-728a', 'vlan': '788'},
              {'interface': '10GE1/0/17', 'mac': '506b-4b22-79b6', 'vlan': '788'},
              {'interface': '10GE1/0/19', 'mac': '506b-4b22-7a9a', 'vlan': '788'}]
