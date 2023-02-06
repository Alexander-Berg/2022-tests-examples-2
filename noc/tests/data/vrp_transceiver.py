from data.lib import Data
from textwrap import dedent


class Data1(Data):
    content = dedent("""
     40GE1/0/2:3 transceiver information:
    -------------------------------------------------------------------
     Common information:
       Transceiver Type                      :40GBASE_CR4
       Connector Type                        :-
       Wavelength (nm)                       :-
       Transfer Distance (m)                 :1(Copper)
       Digital Diagnostic Monitoring         :NO
       Vendor Name                           :OEM
       Vendor Part Number                    :33-4372
       Ordering Name                         :
    -------------------------------------------------------------------
     Manufacture information:
       Manu. Serial Number                   :30700020002
       Manufacturing Date                    :2014-05-14
       Vendor Name                           :OEM
    -------------------------------------------------------------------
     Alarm information:
    -------------------------------------------------------------------
    """)
    cmd = "dis interface 40GE1/0/2:3 transceiver"
    host = "ce7850-test"
    ver = ""
    result = {"40GE1/0/2:3": {
        "common": {"transceiver type": "40GBASE_CR4", "connector type": "-", "wavelength (nm)": "-",
                   "transfer distance (m)": "1(Copper)", "digital diagnostic monitoring": "NO", "vendor name": "OEM",
                   "vendor part number": "33-4372", "ordering name": ""},
        "manufacture": {"manu. serial number": "30700020002", "manufacturing date": "2014-05-14",
                        "vendor name": "OEM"}}}


class Data2(Data):
    content = dedent("""
     40GE1/0/17 transceiver information:
    -------------------------------------------------------------------
     Common information:
       Transceiver Type                      :40GBASE_SR4
       Connector Type                        :MPO
       Wavelength (nm)                       :850
       Transfer Distance (m)                 :100(50um/125um OM3)
                                              150(50um/125um OM4)
       Digital Diagnostic Monitoring         :YES
       Vendor Name                           :FINISAR CORP
       Vendor Part Number                    :FTL410QE3C
       Ordering Name                         :
    -------------------------------------------------------------------
     Manufacture information:
       Manu. Serial Number                   :XWQ0XA8
       Manufacturing Date                    :2017-01-04
       Vendor Name                           :FINISAR CORP
    -------------------------------------------------------------------
     Alarm information:
        LOS Alarm
        Non-Huawei-Ethernet-Switch-Certified Transceiver
    -------------------------------------------------------------------

     40GE1/0/18 transceiver information:
    -------------------------------------------------------------------
     Common information:
       Transceiver Type                      :40GBASE_SR4
       Connector Type                        :MPO
       Wavelength (nm)                       :850
       Transfer Distance (m)                 :100(50um/125um OM3)
                                              150(50um/125um OM4)
       Digital Diagnostic Monitoring         :YES
       Vendor Name                           :FINISAR CORP
       Vendor Part Number                    :FTL410QE3C
       Ordering Name                         :
    -------------------------------------------------------------------
     Manufacture information:
       Manu. Serial Number                   :XWQ0XAD
       Manufacturing Date                    :2017-01-04
       Vendor Name                           :FINISAR CORP
    -------------------------------------------------------------------
     Alarm information:
        LOS Alarm
        Non-Huawei-Ethernet-Switch-Certified Transceiver
    -------------------------------------------------------------------
    """)
    cmd = "dis interface transceiver"  # part
    host = "sas2-9s138"
    ver = ""
    result = {"40GE1/0/17": {
        "common": {"transceiver type": "40GBASE_SR4", "connector type": "MPO", "wavelength (nm)": "850",
                   "transfer distance (m)": "100(50um/125um OM3)\n                                          150(50um/125um OM4)",
                   "digital diagnostic monitoring": "YES", "vendor name": "FINISAR CORP",
                   "vendor part number": "FTL410QE3C", "ordering name": ""},
        "manufacture": {"manu. serial number": "XWQ0XA8", "manufacturing date": "2017-01-04",
                        "vendor name": "FINISAR CORP"}},
        "40GE1/0/18": {
        "common": {"transceiver type": "40GBASE_SR4", "connector type": "MPO", "wavelength (nm)": "850",
                   "transfer distance (m)": "100(50um/125um OM3)\n                                          150(50um/125um OM4)",
                   "digital diagnostic monitoring": "YES", "vendor name": "FINISAR CORP",
                   "vendor part number": "FTL410QE3C", "ordering name": ""},
        "manufacture": {"manu. serial number": "XWQ0XAD", "manufacturing date": "2017-01-04",
                        "vendor name": "FINISAR CORP"}}}


class Data3(Data):
    content = dedent("""
     100GE1/0/3 transceiver information:
    -------------------------------------------------------------------
     Common information:
       Transceiver Type                      :100GBASE_SR4
       Connector Type                        :MPO
       Wavelength (nm)                       :850
       Transfer Distance (m)                 :100(50um/125um OM3)
                                              100(50um/125um OM4)
       Digital Diagnostic Monitoring         :YES
       Vendor Name                           :Sunfy Tech
       Vendor Part Number                    :SPQSTR-X0
       Ordering Name                         :
    -------------------------------------------------------------------
     Manufacture information:
       Manu. Serial Number                   :S818150002
       Manufacturing Date                    :2018-04-13
       Vendor Name                           :Sunfy Tech
    -------------------------------------------------------------------
     Alarm information:
        LOS Alarm
        Non-Huawei-Ethernet-Switch-Certified Transceiver
    -------------------------------------------------------------------
     Diagnostic information:
       Temperature (Celsius)                 :21.85
       Voltage (V)                           :3.32
       Bias Current (mA)                     :6.47|6.55    (Lane0|Lane1)
                                              6.80|6.51    (Lane2|Lane3)
       Bias High Threshold (mA)              :131.07
       Bias Low Threshold (mA)               :0.00
       Current RX Power (dBm)                :-40.00|-40.00(Lane0|Lane1)
                                              -40.00|-40.00(Lane2|Lane3)
       Default RX Power High Threshold (dBm) :5.40
       Default RX Power Low Threshold (dBm)  :-13.31
       Current TX Power (dBm)                :-40.00|-40.00(Lane0|Lane1)
                                              -40.00|-40.00(Lane2|Lane3)
       Default TX Power High Threshold (dBm) :5.40
       Default TX Power Low Threshold (dBm)  :-11.40
    -------------------------------------------------------------------
    """)
    cmd = "dis int 100GE1/0/3 transceiver verbose"
    host = "CE6870-test"
    ver = ""
    result = {"100GE1/0/3": {
        "common": {"transceiver type": "100GBASE_SR4", "connector type": "MPO", "wavelength (nm)": "850",
                   "transfer distance (m)": "100(50um/125um OM3)\n                                          100(50um/125um OM4)",
                   "digital diagnostic monitoring": "YES", "vendor name": "Sunfy Tech",
                   "vendor part number": "SPQSTR-X0", "ordering name": ""},
        "manufacture": {"manu. serial number": "S818150002", "manufacturing date": "2018-04-13",
                        "vendor name": "Sunfy Tech"},
        "diagnostic": {"temperature (celsius)": "21.85", "voltage (v)": "3.32",
                       "bias current (ma)": {"Lane0": "6.47", "Lane1": "6.55", "Lane2": "6.80", "Lane3": "6.51"},
                       "bias high threshold (ma)": "131.07", "bias low threshold (ma)": "0.00",
                       "current rx power (dbm)": {"Lane0": "-40.00", "Lane1": "-40.00", "Lane2": "-40.00", "Lane3": "-40.00"},
                       "default rx power high threshold (dbm)": "5.40",
                       "default rx power low threshold (dbm)": "-13.31",
                       "current tx power (dbm)": {"Lane0": "-40.00", "Lane1": "-40.00", "Lane2": "-40.00", "Lane3": "-40.00"},
                       "default tx power high threshold (dbm)": "5.40",
                       "default tx power low threshold (dbm)": "-11.40"}}}


class Data4(Data):
    content = dedent("""
     100GE1/0/1 transceiver information:
    -------------------------------------------------------------------
     Common information:
       Transceiver Type                      :100GBASE_SR4
       Connector Type                        :MPO
       Wavelength (nm)                       :850
       Transfer Distance (m)                 :70(50um/125um OM3)
                                              100(50um/125um OM4)
       Digital Diagnostic Monitoring         :YES
       Vendor Name                           :Hisense
       Vendor Part Number                    :LTA8531-PC+
       Ordering Name                         :
    -------------------------------------------------------------------
     Manufacture information:
       Manu. Serial Number                   :T2073003018
       Manufacturing Date                    :2017-03-09
       Vendor Name                           :Hisense
    -------------------------------------------------------------------
     Alarm information:
        LOS Alarm
        Non-Huawei-Ethernet-Switch-Certified Transceiver
    -------------------------------------------------------------------
     Diagnostic information:
       Temperature (Celsius)                 :36.00
       Voltage (V)                           :3.33
       Bias Current (mA)                     :6.13|6.14    (Lane0|Lane1)
                                              6.13|6.14    (Lane2|Lane3)
       Bias High Threshold (mA)              :12.00
       Bias Low Threshold (mA)               :0.00
       Current RX Power (dBm)                :-33.98       (All lanes)
                                              -40.00|-40.00(Lane0|Lane1)
                                              -40.00|-40.00(Lane2|Lane3)
       Default RX Power High Threshold (dBm) :5.40
       Default RX Power Low Threshold (dBm)  :-14.00
       Current TX Power (dBm)                :6.32         (All lanes)
                                              -0.22|0.29   (Lane0|Lane1)
                                              0.81|0.25    (Lane2|Lane3)
       Default TX Power High Threshold (dBm) :5.40
       Default TX Power Low Threshold (dBm)  :-12.10
    -------------------------------------------------------------------
    """)
    cmd = "dis int 100GE1/0/1 transceiver verbose"
    host = "CE6870-test"
    ver = ""
    result = {'100GE1/0/1': {'common': {'transceiver type': '100GBASE_SR4', 'connector type': 'MPO', 'wavelength (nm)': '850',
                                        'transfer distance (m)': '70(50um/125um OM3)\n                                          100(50um/125um OM4)', 'digital diagnostic monitoring': 'YES',
                                        'vendor name': 'Hisense', 'vendor part number': 'LTA8531-PC+', 'ordering name': ''},
                             'manufacture': {'manu. serial number': 'T2073003018', 'manufacturing date': '2017-03-09', 'vendor name': 'Hisense'},
                             'diagnostic': {'temperature (celsius)': '36.00', 'voltage (v)': '3.33',
                                            'bias current (ma)': {'Lane0': '6.13', 'Lane1': '6.14', 'Lane2': '6.13', 'Lane3': '6.14'}, 'bias high threshold (ma)': '12.00',
                                            'bias low threshold (ma)': '0.00',
                                            'current rx power (dbm)': {'All lanes': '-33.98', 'Lane0': '-40.00', 'Lane1': '-40.00', 'Lane2': '-40.00', 'Lane3': '-40.00'},
                                            'default rx power high threshold (dbm)': '5.40', 'default rx power low threshold (dbm)': '-14.00',
                                            'current tx power (dbm)': {'All lanes': '6.32', 'Lane0': '-0.22', 'Lane1': '0.29', 'Lane2': '0.81', 'Lane3': '0.25'},
                                            'default tx power high threshold (dbm)': '5.40', 'default tx power low threshold (dbm)': '-12.10'}}}


class Data5(Data):
    content = dedent("""
     100GE8/0/0 transceiver information:
    -------------------------------------------------------------------
     Common information:
       Transceiver Type                      :40GBASE_SR4
       Connector Type                        :MPO
       Wavelength (nm)                       :850
       Transfer Distance (m)                 :100(50um/125um OM3)
                                              150(50um/125um OM4)
       Digital Diagnostic Monitoring         :YES
       Vendor Name                           :FINISAR CORP
       Vendor Part Number                    :FTL410QE2C
       Ordering Name                         :
    -------------------------------------------------------------------
     Manufacture information:
       Manu. Serial Number                   :MR604SS
       Manufacturing Date                    :2014-03-11
       Vendor Name                           :FINISAR CORP
    -------------------------------------------------------------------
     Alarm information:
    -------------------------------------------------------------------
     Diagnostic information: 
       Temperature (Celsius)                 :19.69
       Voltage (V)                           :3.31
       Bias Current (mA)                     :-|-          (Lane0|Lane1)
                                              -|-          (Lane2|Lane3)
       Bias High Threshold (mA)              :-
       Bias Low Threshold (mA)               :-
       Current RX Power (dBm)                :N/A          (All lanes)
                                              -|-          (Lane0|Lane1)
                                              -|-          (Lane2|Lane3)
       Default RX Power High Threshold (dBm) :-
       Default RX Power Low Threshold (dBm)  :-
       Current TX Power (dBm)                :N/A          (All lanes)
                                              -|-          (Lane0|Lane1)
                                              -|-          (Lane2|Lane3)
       Default TX Power High Threshold (dBm) :-
       Default TX Power Low Threshold (dBm)  :-
    -------------------------------------------------------------------
    

    """)
    cmd = "dis int 100GE8/0/0 transceiver verbose"
    host = "myt-e1"
    ver = ""
    result = {'100GE8/0/0': {'common': {'transceiver type': '40GBASE_SR4', 'connector type': 'MPO', 'wavelength (nm)': '850',
                                        'transfer distance (m)': '100(50um/125um OM3)\n                                          150(50um/125um OM4)', 'digital diagnostic monitoring': 'YES',
                                        'vendor name': 'FINISAR CORP', 'vendor part number': 'FTL410QE2C', 'ordering name': ''},
                             'manufacture': {'manu. serial number': 'MR604SS', 'manufacturing date': '2014-03-11', 'vendor name': 'FINISAR CORP'},
                             'diagnostic': {'temperature (celsius)': '19.69', 'voltage (v)': '3.31', 'bias current (ma)': {'Lane0': '-', 'Lane1': '-', 'Lane2': '-', 'Lane3': '-'},
                                            'bias high threshold (ma)': '-', 'bias low threshold (ma)': '-',
                                            'current rx power (dbm)': {'All lanes': 'N/A', 'Lane0': '-', 'Lane1': '-', 'Lane2': '-', 'Lane3': '-'},
                                            'default rx power high threshold (dbm)': '-', 'default rx power low threshold (dbm)': '-',
                                            'current tx power (dbm)': {'All lanes': 'N/A', 'Lane0': '-', 'Lane1': '-', 'Lane2': '-', 'Lane3': '-'},
                                            'default tx power high threshold (dbm)': '-', 'default tx power low threshold (dbm)': '-'}}}


class Data6(Data):
    content = """
Port GigabitEthernet0/0/1 :Valid only on optical interface.

Port GigabitEthernet0/0/2 :Valid only on optical interface.

Port GigabitEthernet0/0/3 :Valid only on optical interface.

Port GigabitEthernet0/0/4 :Valid only on optical interface.

Port GigabitEthernet0/0/5 :Valid only on optical interface.

Port GigabitEthernet0/0/6 :Valid only on optical interface.

Port GigabitEthernet0/0/7 :Valid only on optical interface.

Port GigabitEthernet0/0/8 :Valid only on optical interface.

Port GigabitEthernet0/0/9 :Valid only on optical interface.

Port GigabitEthernet0/0/10 :Valid only on optical interface.

Port GigabitEthernet0/0/11 :Valid only on optical interface.

Port GigabitEthernet0/0/12 :Valid only on optical interface.

Port GigabitEthernet0/0/13 :Valid only on optical interface.

Port GigabitEthernet0/0/14 :Valid only on optical interface.

Port GigabitEthernet0/0/15 :Valid only on optical interface.

Port GigabitEthernet0/0/16 :Valid only on optical interface.

Port GigabitEthernet0/0/17 :Valid only on optical interface.

Port GigabitEthernet0/0/18 :Valid only on optical interface.

Port GigabitEthernet0/0/19 :Valid only on optical interface.

Port GigabitEthernet0/0/20 :Valid only on optical interface.

Port GigabitEthernet0/0/21 :Valid only on optical interface.

Port GigabitEthernet0/0/22 :Valid only on optical interface.


GigabitEthernet0/0/23 transceiver information:
-------------------------------------------------------------
Common information:
  Transceiver Type               :1000_BASE_LX_SFP
  Connector Type                 :LC
  Wavelength(nm)                 :1550
  Transfer Distance(m)           :160000(9um)
  Digital Diagnostic Monitoring  :YES
  Vendor Name                    :strela->       
  Vendor Part Number             :S>SFPC160C55LD 
  Ordering Name                  :
-------------------------------------------------------------
Manufacture information:
  Manu. Serial Number            :CI31180509020  
  Manufacturing Date             :2018-05-30
  Vendor Name                    :strela->       
-------------------------------------------------------------
Diagnostic information:
  Temperature(��C)              :45.78
  Temp High Threshold(��C)      :90.00
  Temp Low  Threshold(��C)      :-45.00
  Voltage(V)                    :3.31
  Volt High Threshold(V)        :3.80
  Volt Low  Threshold(V)        :2.70
  Bias Current(mA)              :40.96
  Bias High Threshold(mA)       :100.00
  Bias Low  Threshold(mA)       :0.00
  RX Power(dBM)                 :-21.43
  RX Power High Threshold(dBM)  :-5.99
  RX Power Low  Threshold(dBM)  :-36.98
  TX Power(dBM)                 :4.04
  TX Power High Threshold(dBM)  :6.00
  TX Power Low  Threshold(dBM)  :-1.00
-------------------------------------------------------------

GigabitEthernet0/0/24 transceiver information:
-------------------------------------------------------------
Common information:
  Transceiver Type               :1000_BASE_LX_SFP
  Connector Type                 :LC
  Wavelength(nm)                 :1550
  Transfer Distance(m)           :160000(9um)
  Digital Diagnostic Monitoring  :YES
  Vendor Name                    :strela->       
  Vendor Part Number             :S>SFPC160C55LD 
  Ordering Name                  :
-------------------------------------------------------------
Manufacture information:
  Manu. Serial Number            :CI31180509012  
  Manufacturing Date             :2018-05-30
  Vendor Name                    :strela->       
-------------------------------------------------------------
Diagnostic information:
  Temperature(��C)              :45.78
  Temp High Threshold(��C)      :90.00
  Temp Low  Threshold(��C)      :-45.00
  Voltage(V)                    :3.31
  Volt High Threshold(V)        :3.80
  Volt Low  Threshold(V)        :2.70
  Bias Current(mA)              :38.29
  Bias High Threshold(mA)       :100.00
  Bias Low  Threshold(mA)       :0.00
  RX Power(dBM)                 :-23.77
  RX Power High Threshold(dBM)  :-5.99
  RX Power Low  Threshold(dBM)  :-36.98
  TX Power(dBM)                 :3.69
  TX Power High Threshold(dBM)  :6.00
  TX Power Low  Threshold(dBM)  :-1.00
-------------------------------------------------------------
Port XGigabitEthernet0/1/1 :Transceiver is absent.

Port XGigabitEthernet0/1/2 :Transceiver is absent.
    """
    cmd = "display transceiver verbose"
    host = "kol-wdm-s1"
    version = """
Huawei Versatile Routing Platform Software
VRP (R) software, Version 5.150 (S5300 V200R005C00SPC500)
Copyright (C) 2000-2015 HUAWEI TECH CO., LTD
Quidway S5328C-SI Routing Switch uptime is 45 weeks, 6 days, 4 hours, 8 minutes

CX22EFGEC 0(Master) : uptime is 45 weeks, 6 days, 4 hours, 7 minutes
256M bytes DDR Memory
32M bytes FLASH
Pcb      Version :  VER.B
Basic  BOOTROM  Version :  246 Compiled at Jul  2 2015, 16:58:12
CPLD   Version : 6
Software Version : VRP (R) Software, Version 5.150 (V200R005C00SPC500)
FORECARD information
Pcb      Version : CX22E2XY VER.B
FANCARD I information
Pcb      Version : FAN VER.B
PWRCARD I information
Pcb      Version : PWR VER.A
PWRCARD II information
Pcb      Version : PWR VER.A
    """
    result = {
        'GigabitEthernet0/0/23': {
            'common': {'transceiver type': '1000_BASE_LX_SFP', 'connector type': 'LC', 'wavelength(nm)': '1550', 'transfer distance(m)': '160000(9um)', 'digital diagnostic monitoring': 'YES',
                       'vendor name': 'strela->', 'vendor part number': 'S>SFPC160C55LD', 'ordering name': ''},
            'manufacture': {'manu. serial number': 'CI31180509020', 'manufacturing date': '2018-05-30', 'vendor name': 'strela->'},
            'diagnostic': {'temperature(��c)': '45.78', 'temp high threshold(��c)': '90.00', 'temp low  threshold(��c)': '-45.00', 'voltage(v)': '3.31', 'volt high threshold(v)': '3.80',
                           'volt low  threshold(v)': '2.70', 'bias current(ma)': '40.96', 'bias high threshold(ma)': '100.00', 'bias low  threshold(ma)': '0.00', 'rx power(dbm)': '-21.43',
                           'rx power high threshold(dbm)': '-5.99', 'rx power low  threshold(dbm)': '-36.98', 'tx power(dbm)': '4.04', 'tx power high threshold(dbm)': '6.00',
                           'tx power low  threshold(dbm)': '-1.00'}},
        'GigabitEthernet0/0/24': {
            'common': {'transceiver type': '1000_BASE_LX_SFP', 'connector type': 'LC', 'wavelength(nm)': '1550', 'transfer distance(m)': '160000(9um)', 'digital diagnostic monitoring': 'YES',
                       'vendor name': 'strela->', 'vendor part number': 'S>SFPC160C55LD', 'ordering name': ''},
            'manufacture': {'manu. serial number': 'CI31180509012', 'manufacturing date': '2018-05-30', 'vendor name': 'strela->'},
            'diagnostic': {'temperature(��c)': '45.78', 'temp high threshold(��c)': '90.00', 'temp low  threshold(��c)': '-45.00', 'voltage(v)': '3.31', 'volt high threshold(v)': '3.80',
                           'volt low  threshold(v)': '2.70', 'bias current(ma)': '38.29', 'bias high threshold(ma)': '100.00', 'bias low  threshold(ma)': '0.00', 'rx power(dbm)': '-23.77',
                           'rx power high threshold(dbm)': '-5.99', 'rx power low  threshold(dbm)': '-36.98', 'tx power(dbm)': '3.69', 'tx power high threshold(dbm)': '6.00',
                           'tx power low  threshold(dbm)': '-1.00'}}}


class Data7(Data):
    content = """
 100GE1/0/20:2 transceiver information:
-------------------------------------------------------------------
 Common information:
   Transceiver Type                      :100GBASE_CR4
   Connector Type                        :-
   Wavelength (nm)                       :-
   Transfer Distance (m)                 :2(Copper)
   Digital Diagnostic Monitoring         :NO
   Vendor Name                           :Mellanox
   Vendor Part Number                    :MCP7H00-G002R30N
   Ordering Name                         :
-------------------------------------------------------------------
 Manufacture information:
   Manu. Serial Number                   :MT2027VS02652
   Manufacturing Date                    :2020-6-28
   Vendor Name                           :Mellanox
-------------------------------------------------------------------
 Alarm information:
-------------------------------------------------------------------
 Warning information:
-------------------------------------------------------------------

 100GE1/0/25 transceiver information:
-------------------------------------------------------------------
 Common information:
   Transceiver Type                      :100GBASE_SR4
   Connector Type                        :MPO
   Wavelength (nm)                       :850
   Transfer Distance (m)                 :100(50um/125um OM3)
                                          100(50um/125um OM4)
   Digital Diagnostic Monitoring         :YES
   Vendor Name                           :Netwell - OEM
   Vendor Part Number                    :NW-QSFP28-SR4
   Ordering Name                         :
-------------------------------------------------------------------
 Manufacture information:
   Manu. Serial Number                   :G201901280434
   Manufacturing Date                    :2019-2-13
   Vendor Name                           :Netwell - OEM
-------------------------------------------------------------------
 Alarm information:
    Non-Huawei-certified transceiver
-------------------------------------------------------------------
 Warning information:
-------------------------------------------------------------------
 Diagnostic information:
   Temperature (Celsius)                 :22.96
   Voltage (V)                           :3.31
   Bias Current (mA)                     :6.49|5.85    (Lane0|Lane1)
                                          6.04|6.04    (Lane2|Lane3)
   Bias High Threshold (mA)              :15.00
   Bias Low Threshold (mA)               :1.00
   Current RX Power (dBm)                :-0.27|-0.62  (Lane0|Lane1)
                                          -0.39|-0.81  (Lane2|Lane3)
   Default RX Power High Threshold (dBm) :4.00
   Default RX Power Low Threshold (dBm)  :-11.00
   Current TX Power (dBm)                :1.03|0.84    (Lane0|Lane1)
                                          0.43|0.66    (Lane2|Lane3)
   Default TX Power High Threshold (dBm) :4.00
   Default TX Power Low Threshold (dBm)  :-6.00
-------------------------------------------------------------------
    """
    cmd = "dis int transceiver verbose"
    host = "vla2-7s95.yndx.net"
    version = """
Huawei Versatile Routing Platform Software
VRP (R) software, Version 8.20.0.1 (CE8800 V300R020C00SPC200)
Copyright (C) 2012-2020 Huawei Technologies Co., Ltd.
HUAWEI CE8851-32CQ8DQ-P uptime is 83 days, 0 hour, 56 minutes
Patch Version: V300R020SPH001

CE8851-32CQ8DQ-P(Master) 1 : uptime is  83 days, 0 hour, 56 minutes
        StartupTime 2020/11/26   17:41:59
Memory    Size    : 8192 M bytes
Flash     Size    : 4096 M bytes
CE8851-32CQ8DQ-P version information
1. PCB    Version : CEM32CQ8DQP01 VER B
2. MAB    Version : 0
3. Board  Type    : CE8851-32CQ8DQ-P
4. CPLD1  Version : 257
5. CPLD2  Version : 257
6. BIOS   Version : 1276
    """
    result = {
        '100GE1/0/20:2': {
            'common': {
                'transceiver type': '100GBASE_CR4',
                'connector type': '-',
                'wavelength (nm)': '-',
                'transfer distance (m)': '2(Copper)',
                'digital diagnostic monitoring': 'NO',
                'vendor name': 'Mellanox',
                'vendor part number': 'MCP7H00-G002R30N',
                'ordering name': ''},
            'manufacture': {
                'manu. serial number': 'MT2027VS02652',
                'manufacturing date': '2020-6-28',
                'vendor name': 'Mellanox'}},
        '100GE1/0/25': {
            'common': {
                'transceiver type': '100GBASE_SR4',
                'connector type': 'MPO',
                'wavelength (nm)': '850',
                'transfer distance (m)': '100(50um/125um OM3)\n                                          100(50um/125um OM4)',
                'digital diagnostic monitoring': 'YES',
                'vendor name': 'Netwell - OEM',
                'vendor part number': 'NW-QSFP28-SR4',
                'ordering name': ''},
            'diagnostic': {'bias current (ma)': {'Lane0': '6.49',
                                                 'Lane1': '5.85',
                                                 'Lane2': '6.04',
                                                 'Lane3': '6.04'},
                           'bias high threshold (ma)': '15.00',
                           'bias low threshold (ma)': '1.00',
                           'current rx power (dbm)': {'Lane0': '-0.27',
                                                      'Lane1': '-0.62',
                                                      'Lane2': '-0.39',
                                                      'Lane3': '-0.81'},
                           'current tx power (dbm)': {'Lane0': '1.03',
                                                      'Lane1': '0.84',
                                                      'Lane2': '0.43',
                                                      'Lane3': '0.66'},
                           'default rx power high threshold (dbm)': '4.00',
                           'default rx power low threshold (dbm)': '-11.00',
                           'default tx power high threshold (dbm)': '4.00',
                           'default tx power low threshold (dbm)': '-6.00',
                           'temperature (celsius)': '22.96',
                           'voltage (v)': '3.31'},
            'manufacture': {
                'manu. serial number': 'G201901280434',
                'manufacturing date': '2019-2-13',
                'vendor name': 'Netwell - OEM'}}}


class Data8(Data):
    content = """
GigabitEthernet0/0/1 transceiver information:
-------------------------------------------------------------
Common information:
  Transceiver Type               :1000_BASE_T_SFP
  Connector Type                 :-
  Wavelength(nm)                 :-
  Transfer Distance(m)           :100(copper)
  Digital Diagnostic Monitoring  :NO
  Vendor Name                    :Modultech      
  Vendor Part Number             :MT-E-GB-P1RC   
  Ordering Name                  :
-------------------------------------------------------------
Manufacture information:
  Manu. Serial Number            :E1206291365    
  Manufacturing Date             :2012-07-17
  Vendor Name                    :Modultech      
-------------------------------------------------------------
Diagnostic information:
  Transceiver does not support.
-------------------------------------------------------------
Port GigabitEthernet0/0/2 :Transceiver is absent.

Port GigabitEthernet0/0/3 :Transceiver is absent.

Port GigabitEthernet0/0/4 :Transceiver is absent.

Port GigabitEthernet0/0/5 :Transceiver is absent.

Port GigabitEthernet0/0/6 :Transceiver is absent.

Port GigabitEthernet0/0/7 :Transceiver is absent.

Port GigabitEthernet0/0/8 :Transceiver is absent.

Port GigabitEthernet0/0/9 :Transceiver is absent.

Port GigabitEthernet0/0/10 :Transceiver is absent.

Port GigabitEthernet0/0/11 :Transceiver is absent.

Port GigabitEthernet0/0/12 :Transceiver is absent.

Port GigabitEthernet0/0/13 :Transceiver is absent.

Port GigabitEthernet0/0/14 :Transceiver is absent.

Port GigabitEthernet0/0/15 :Transceiver is absent.

Port GigabitEthernet0/0/16 :Transceiver is absent.

Port GigabitEthernet0/0/17 :Transceiver is absent.

Port GigabitEthernet0/0/18 :Transceiver is absent.

Port GigabitEthernet0/0/19 :Transceiver is absent.


GigabitEthernet0/0/20 transceiver information:
-------------------------------------------------------------
Common information:
  Transceiver Type               :1000_BASE_T_SFP
  Connector Type                 :-
  Wavelength(nm)                 :-
  Transfer Distance(m)           :100(copper)
  Digital Diagnostic Monitoring  :NO
  Vendor Name                    :Modultech      
  Vendor Part Number             :MT-E-GB-P1RC   
  Ordering Name                  :
-------------------------------------------------------------
Manufacture information:
  Manu. Serial Number            :E1211191695    
  Manufacturing Date             :2012-12-11
  Vendor Name                    :Modultech      
-------------------------------------------------------------
Diagnostic information:
  Transceiver does not support.
-------------------------------------------------------------
Port GigabitEthernet0/0/21 :Valid only on optical interface.

Port GigabitEthernet0/0/22 :Valid only on optical interface.

Port GigabitEthernet0/0/23 :Valid only on optical interface.

Port GigabitEthernet0/0/24 :Valid only on optical interface.

Port XGigabitEthernet0/1/1 :Transceiver is absent.

Port XGigabitEthernet0/1/2 :Transceiver is absent.

Port XGigabitEthernet0/1/3 :Transceiver is absent.


XGigabitEthernet0/1/4 transceiver information:
-------------------------------------------------------------
Common information:
  Transceiver Type               :10GBBASE_LR_SFP
  Connector Type                 :LC
  Wavelength(nm)                 :1310
  Transfer Distance(m)           :10000(9um)
  Digital Diagnostic Monitoring  :YES
  Vendor Name                    :FINISAR CORP.  
  Vendor Part Number             :FTLX1471D3BCL  
  Ordering Name                  :
-------------------------------------------------------------
Manufacture information:
  Manu. Serial Number            :AT60CZ8        
  Manufacturing Date             :2015-04-21
  Vendor Name                    :FINISAR CORP.  
-------------------------------------------------------------
Diagnostic information:
  Temperature(��C)              :36.80
  Temp High Threshold(��C)      :78.00
  Temp Low  Threshold(��C)      :-13.00
  Voltage(V)                    :3.30
  Volt High Threshold(V)        :3.70
  Volt Low  Threshold(V)        :2.90
  Bias Current(mA)              :42.54
  Bias High Threshold(mA)       :85.00
  Bias Low  Threshold(mA)       :15.00
  RX Power(dBM)                 :-2.81
  RX Power High Threshold(dBM)  :2.50
  RX Power Low  Threshold(dBM)  :-20.00
  TX Power(dBM)                 :-1.75
  TX Power High Threshold(dBM)  :2.00
  TX Power Low  Threshold(dBM)  :-7.99
-------------------------------------------------------------
    """
    cmd = "dis transceiver verbose"
    host = "kiv-s1.yndx.net"
    version = """
Huawei Versatile Routing Platform Software
VRP (R) software, Version 5.130 (S5700 V200R003C00SPC300)
Copyright (C) 2000-2013 HUAWEI TECH CO., LTD
Quidway S5700-28C-EI-24S Routing Switch uptime is 14 weeks, 4 days, 18 hours, 20 minutes

CX22EFGF 0(Master) : uptime is 14 weeks, 4 days, 18 hours, 19 minutes
256M bytes DDR Memory
32M bytes FLASH
Pcb      Version :  VER B
Basic  BOOTROM  Version :  181 Compiled at Jun 29 2013, 10:18:52
CPLD   Version : 74
Software Version : VRP (R) Software, Version 5.130 (V200R003C00SPC300)
FORECARD information
Pcb      Version : ES510X4S VER B
HINDCARD information
Pcb      Version : CX22ETPB VER C
FANCARD I information
Pcb      Version : FAN VER B
PWRCARD I information
Pcb      Version : PWR VER B
PWRCARD II information
Pcb      Version : PWR VER B
    """
    result = {
        'GigabitEthernet0/0/1': {
            'common': {
                'transceiver type': '1000_BASE_T_SFP',
                'connector type': '-', 'wavelength(nm)': '-',
                'transfer distance(m)': '100(copper)',
                'digital diagnostic monitoring': 'NO',
                'vendor name': 'Modultech',
                'vendor part number': 'MT-E-GB-P1RC',
                'ordering name': ''},
            'manufacture': {
                'manu. serial number': 'E1206291365',
                'manufacturing date': '2012-07-17',
                'vendor name': 'Modultech'}},
        'GigabitEthernet0/0/20': {
            'common': {
                'transceiver type': '1000_BASE_T_SFP',
                'connector type': '-',
                'wavelength(nm)': '-',
                'transfer distance(m)': '100(copper)',
                'digital diagnostic monitoring': 'NO',
                'vendor name': 'Modultech',
                'vendor part number': 'MT-E-GB-P1RC',
                'ordering name': ''},
            'manufacture': {
                'manu. serial number': 'E1211191695',
                'manufacturing date': '2012-12-11',
                'vendor name': 'Modultech'}},
        'XGigabitEthernet0/1/4': {
            'common': {
                'transceiver type': '10GBBASE_LR_SFP',
                'connector type': 'LC',
                'wavelength(nm)': '1310',
                'transfer distance(m)': '10000(9um)',
                'digital diagnostic monitoring': 'YES',
                'vendor name': 'FINISAR CORP.',
                'vendor part number': 'FTLX1471D3BCL',
                'ordering name': ''},
            'manufacture': {
                'manu. serial number': 'AT60CZ8',
                'manufacturing date': '2015-04-21',
                'vendor name': 'FINISAR CORP.'},
            'diagnostic': {
                'temperature(��c)': '36.80',
                'temp high threshold(��c)': '78.00',
                'temp low  threshold(��c)': '-13.00',
                'voltage(v)': '3.30',
                'volt high threshold(v)': '3.70',
                'volt low  threshold(v)': '2.90',
                'bias current(ma)': '42.54',
                'bias high threshold(ma)': '85.00',
                'bias low  threshold(ma)': '15.00',
                'rx power(dbm)': '-2.81',
                'rx power high threshold(dbm)': '2.50',
                'rx power low  threshold(dbm)': '-20.00',
                'tx power(dbm)': '-1.75',
                'tx power high threshold(dbm)': '2.00',
                'tx power low  threshold(dbm)': '-7.99'
            }}}


class Data9(Data):
    content = """
 40GE1/0/1 transceiver information:
-------------------------------------------------------------------
 Common information:
   Transceiver Type                      :40GBASE_CR4
   Connector Type                        :-
   Wavelength (nm)                       :-
   Transfer Distance (m)                 :2(Copper)
   Digital Diagnostic Monitoring         :NO
   Vendor Name                           :Mellanox
   Vendor Part Number                    :MCP1600-C002E30N
   Ordering Name                         :
-------------------------------------------------------------------
 Manufacture information:
   Manu. Serial Number                   :MT2028VB02770
   Manufacturing Date                    :2020-6-30+03:00
   Vendor Name                           :Mellanox
-------------------------------------------------------------------
 Alarm information:
-------------------------------------------------------------------
    """
    cmd = "dis int transceiver verbose"
    host = "sas1-s102.yndx.net"
    version = """
Huawei Versatile Routing Platform Software
VRP (R) software, Version 8.180 (CE5850HI V200R005C10SPC800)
Copyright (C) 2012-2018 Huawei Technologies Co., Ltd.
HUAWEI CE5850-48T4S2Q-HI uptime is 211 days, 12 hours, 0 minute
Patch Version: V200R005SPH020

CE5850-48T4S2Q-HI(Master) 1 : uptime is  211 days, 11 hours, 59 minutes
        StartupTime 2020/07/21   13:21:07+03:00
Memory    Size    : 2048 M bytes
Flash     Size    : 1024 M bytes
CE5850-48T4S2Q-HI version information                              
1. PCB    Version : CEM48T4S2QP02    VER B
2. MAB    Version : 1
3. Board  Type    : CE5850-48T4S2Q-HI
4. CPLD1  Version : 104
5. BIOS   Version : 433
    """
    result = {
        '40GE1/0/1': {
            'common': {
                'connector type': '-',
                'digital diagnostic monitoring': 'NO',
                'ordering name': '',
                'transceiver type': '40GBASE_CR4',
                'transfer distance (m)': '2(Copper)',
                'vendor name': 'Mellanox',
                'vendor part number': 'MCP1600-C002E30N',
                'wavelength (nm)': '-'},
            'manufacture': {
                'manu. serial number': 'MT2028VB02770',
                'manufacturing date': '2020-6-30+03:00',
                'vendor name': 'Mellanox',
            }}}
