from data.lib import Data


class Data1(Data):
    content = """
	Identifier                                : 0x11 (QSFP28)
	Extended identifier                       : 0x8c
	Extended identifier description           : 2.5W max. Power consumption
	Extended identifier description           : CDR present in TX, CDR present in RX
	Extended identifier description           : High Power Class (> 3.5 W) not enabled
	Connector                                 : 0x0c (MPO Parallel Optic)
	Transceiver codes                         : 0x80 0x00 0x00 0x00 0x00 0x00 0x00 0x00
	Transceiver type                          : 100G Ethernet: 100G Base-SR4 or 25GBase-SR
	Encoding                                  : 0x05 (64B/66B)
	BR, Nominal                               : 25500Mbps
	Rate identifier                           : 0x00
	Length (SMF,km)                           : 0km
	Length (OM3 50um)                         : 70m
	Length (OM2 50um)                         : 0m
	Length (OM1 62.5um)                       : 0m
	Length (Copper or Active cable)           : 50m
	Transmitter technology                    : 0x00 (850 nm VCSEL)
	Laser wavelength                          : 850.000nm
	Laser wavelength tolerance                : 15.000nm
	Vendor name                               : Mellanox
	Vendor OUI                                : 00:02:c9
	Vendor PN                                 : MMA1B00-C100D
	Vendor rev                                : A4
	Vendor SN                                 : MT1708FT01255
	Revision Compliance                       : SFF-8636 Rev 2.5/2.6/2.7
	Module temperature                        : 30.56 degrees C / 87.01 degrees F
	Module voltage                            : 3.2350 V
	Alarm/warning flags implemented           : Yes
	Laser tx bias current (Channel 1)         : 6.750 mA
	Laser tx bias current (Channel 2)         : 6.750 mA
	Laser tx bias current (Channel 3)         : 6.750 mA
	Laser tx bias current (Channel 4)         : 6.750 mA
	Transmit avg optical power (Channel 1)    : 1.3924 mW / 1.44 dBm
	Transmit avg optical power (Channel 2)    : 1.3181 mW / 1.20 dBm
	Transmit avg optical power (Channel 3)    : 1.3378 mW / 1.26 dBm
	Transmit avg optical power (Channel 4)    : 1.3397 mW / 1.27 dBm
	Rcvr signal avg optical power(Channel 1)  : 0.9720 mW / -0.12 dBm
	Rcvr signal avg optical power(Channel 2)  : 0.9798 mW / -0.09 dBm
	Rcvr signal avg optical power(Channel 3)  : 1.1340 mW / 0.55 dBm
	Rcvr signal avg optical power(Channel 4)  : 1.1340 mW / 0.55 dBm
	Laser bias current high alarm   (Chan 1)  : Off
	Laser bias current low alarm    (Chan 1)  : Off
	Laser bias current high warning (Chan 1)  : Off
	Laser bias current low warning  (Chan 1)  : Off
	Laser bias current high alarm   (Chan 2)  : Off
	Laser bias current low alarm    (Chan 2)  : Off
	Laser bias current high warning (Chan 2)  : Off
	Laser bias current low warning  (Chan 2)  : Off
	Laser bias current high alarm   (Chan 3)  : Off
	Laser bias current low alarm    (Chan 3)  : Off
	Laser bias current high warning (Chan 3)  : Off
	Laser bias current low warning  (Chan 3)  : Off
	Laser bias current high alarm   (Chan 4)  : Off
	Laser bias current low alarm    (Chan 4)  : Off
	Laser bias current high warning (Chan 4)  : Off
	Laser bias current low warning  (Chan 4)  : Off
	Module temperature high alarm             : Off
	Module temperature low alarm              : Off
	Module temperature high warning           : Off
	Module temperature low warning            : Off
	Module voltage high alarm                 : Off
	Module voltage low alarm                  : Off
	Module voltage high warning               : Off
	Module voltage low warning                : Off
	Laser tx power high alarm   (Channel 1)   : Off
	Laser tx power low alarm    (Channel 1)   : Off
	Laser tx power high warning (Channel 1)   : Off
	Laser tx power low warning  (Channel 1)   : Off
	Laser tx power high alarm   (Channel 2)   : Off
	Laser tx power low alarm    (Channel 2)   : Off
	Laser tx power high warning (Channel 2)   : Off
	Laser tx power low warning  (Channel 2)   : Off
	Laser tx power high alarm   (Channel 3)   : Off
	Laser tx power low alarm    (Channel 3)   : Off
	Laser tx power high warning (Channel 3)   : Off
	Laser tx power low warning  (Channel 3)   : Off
	Laser tx power high alarm   (Channel 4)   : Off
	Laser tx power low alarm    (Channel 4)   : Off
	Laser tx power high warning (Channel 4)   : Off
	Laser tx power low warning  (Channel 4)   : Off
	Laser rx power high alarm   (Channel 1)   : Off
	Laser rx power low alarm    (Channel 1)   : Off
	Laser rx power high warning (Channel 1)   : Off
	Laser rx power low warning  (Channel 1)   : Off
	Laser rx power high alarm   (Channel 2)   : Off
	Laser rx power low alarm    (Channel 2)   : Off
	Laser rx power high warning (Channel 2)   : Off
	Laser rx power low warning  (Channel 2)   : Off
	Laser rx power high alarm   (Channel 3)   : Off
	Laser rx power low alarm    (Channel 3)   : Off
	Laser rx power high warning (Channel 3)   : Off
	Laser rx power low warning  (Channel 3)   : Off
	Laser rx power high alarm   (Channel 4)   : Off
	Laser rx power low alarm    (Channel 4)   : Off
	Laser rx power high warning (Channel 4)   : Off
	Laser rx power low warning  (Channel 4)   : Off
	Laser bias current high alarm threshold   : 8.500 mA
	Laser bias current low alarm threshold    : 5.492 mA
	Laser bias current high warning threshold : 8.000 mA
	Laser bias current low warning threshold  : 6.000 mA
	Laser output power high alarm threshold   : 3.4673 mW / 5.40 dBm
	Laser output power low alarm threshold    : 0.0724 mW / -11.40 dBm
	Laser output power high warning threshold : 1.7378 mW / 2.40 dBm
	Laser output power low warning threshold  : 0.1445 mW / -8.40 dBm
	Module temperature high alarm threshold   : 80.00 degrees C / 176.00 degrees F
	Module temperature low alarm threshold    : -10.00 degrees C / 14.00 degrees F
	Module temperature high warning threshold : 70.00 degrees C / 158.00 degrees F
	Module temperature low warning threshold  : 0.00 degrees C / 32.00 degrees F
	Module voltage high alarm threshold       : 3.5000 V
	Module voltage low alarm threshold        : 3.1000 V
	Module voltage high warning threshold     : 3.4650 V
	Module voltage low warning threshold      : 3.1350 V
	Laser rx power high alarm threshold       : 3.4673 mW / 5.40 dBm
	Laser rx power low alarm threshold        : 0.0467 mW / -13.31 dBm
	Laser rx power high warning threshold     : 1.7378 mW / 2.40 dBm
	Laser rx power low warning threshold      : 0.0933 mW / -10.30 dBm
    """
    cmd = "sudo ethtool -m swp14"
    host = "sas2-5s50"
    version = """
Linux sas2-5s50.yndx.net 4.1.0-cl-7-amd64 #1 SMP Debian 4.1.33-1+cl3u17 (2018-10-31) x86_64 GNU/Linux
    """
    result = {
        'Alarm/warning flags implemented': 'Yes',
        'BR, Nominal': '25500Mbps',
        'Connector': '0x0c (MPO Parallel Optic)',
        'Encoding': '0x05 (64B/66B)',
        'Extended identifier': '0x8c',
        'Extended identifier description': '2.5W max. Power consumption CDR present in TX, CDR present in RX High Power Class (> 3.5 W) not enabled',
        'Identifier': '0x11 (QSFP28)',
        'Laser bias current high alarm   (Chan 1)': 'Off',
        'Laser bias current high alarm   (Chan 2)': 'Off',
        'Laser bias current high alarm   (Chan 3)': 'Off',
        'Laser bias current high alarm   (Chan 4)': 'Off',
        'Laser bias current high alarm threshold': '8.500',
        'Laser bias current high warning (Chan 1)': 'Off',
        'Laser bias current high warning (Chan 2)': 'Off',
        'Laser bias current high warning (Chan 3)': 'Off',
        'Laser bias current high warning (Chan 4)': 'Off',
        'Laser bias current high warning threshold': '8.000',
        'Laser bias current low alarm    (Chan 1)': 'Off',
        'Laser bias current low alarm    (Chan 2)': 'Off',
        'Laser bias current low alarm    (Chan 3)': 'Off',
        'Laser bias current low alarm    (Chan 4)': 'Off',
        'Laser bias current low alarm threshold': '5.492',
        'Laser bias current low warning  (Chan 1)': 'Off',
        'Laser bias current low warning  (Chan 2)': 'Off',
        'Laser bias current low warning  (Chan 3)': 'Off',
        'Laser bias current low warning  (Chan 4)': 'Off',
        'Laser bias current low warning threshold': '6.000',
        'Laser output power high alarm threshold': '5.40',
        'Laser output power high warning threshold': '2.40',
        'Laser output power low alarm threshold': '-11.40',
        'Laser output power low warning threshold': '-8.40',
        'Laser rx power high alarm   (Channel 1)': 'Off',
        'Laser rx power high alarm   (Channel 2)': 'Off',
        'Laser rx power high alarm   (Channel 3)': 'Off',
        'Laser rx power high alarm   (Channel 4)': 'Off',
        'Laser rx power high alarm threshold': '5.40',
        'Laser rx power high warning (Channel 1)': 'Off',
        'Laser rx power high warning (Channel 2)': 'Off',
        'Laser rx power high warning (Channel 3)': 'Off',
        'Laser rx power high warning (Channel 4)': 'Off',
        'Laser rx power high warning threshold': '2.40',
        'Laser rx power low alarm    (Channel 1)': 'Off',
        'Laser rx power low alarm    (Channel 2)': 'Off',
        'Laser rx power low alarm    (Channel 3)': 'Off',
        'Laser rx power low alarm    (Channel 4)': 'Off',
        'Laser rx power low alarm threshold': '-13.31',
        'Laser rx power low warning  (Channel 1)': 'Off',
        'Laser rx power low warning  (Channel 2)': 'Off',
        'Laser rx power low warning  (Channel 3)': 'Off',
        'Laser rx power low warning  (Channel 4)': 'Off',
        'Laser rx power low warning threshold': '-10.30',
        'Laser tx bias current (Channel 1)': '6.750',
        'Laser tx bias current (Channel 2)': '6.750',
        'Laser tx bias current (Channel 3)': '6.750',
        'Laser tx bias current (Channel 4)': '6.750',
        'Laser tx power high alarm   (Channel 1)': 'Off',
        'Laser tx power high alarm   (Channel 2)': 'Off',
        'Laser tx power high alarm   (Channel 3)': 'Off',
        'Laser tx power high alarm   (Channel 4)': 'Off',
        'Laser tx power high warning (Channel 1)': 'Off',
        'Laser tx power high warning (Channel 2)': 'Off',
        'Laser tx power high warning (Channel 3)': 'Off',
        'Laser tx power high warning (Channel 4)': 'Off',
        'Laser tx power low alarm    (Channel 1)': 'Off',
        'Laser tx power low alarm    (Channel 2)': 'Off',
        'Laser tx power low alarm    (Channel 3)': 'Off',
        'Laser tx power low alarm    (Channel 4)': 'Off',
        'Laser tx power low warning  (Channel 1)': 'Off',
        'Laser tx power low warning  (Channel 2)': 'Off',
        'Laser tx power low warning  (Channel 3)': 'Off',
        'Laser tx power low warning  (Channel 4)': 'Off',
        'Laser wavelength': '850.000nm',
        'Laser wavelength tolerance': '15.000nm',
        'Length (Copper or Active cable)': '50m',
        'Length (OM1 62.5um)': '0m',
        'Length (OM2 50um)': '0m',
        'Length (OM3 50um)': '70m',
        'Length (SMF,km)': '0km',
        'Module temperature': '30.56',
        'Module temperature high alarm': 'Off',
        'Module temperature high alarm threshold': '80.00',
        'Module temperature high warning': 'Off',
        'Module temperature high warning threshold': '70.00',
        'Module temperature low alarm': 'Off',
        'Module temperature low alarm threshold': '-10.00',
        'Module temperature low warning': 'Off',
        'Module temperature low warning threshold': '0.00',
        'Module voltage': '3.2350',
        'Module voltage high alarm': 'Off',
        'Module voltage high alarm threshold': '3.5000',
        'Module voltage high warning': 'Off',
        'Module voltage high warning threshold': '3.4650',
        'Module voltage low alarm': 'Off',
        'Module voltage low alarm threshold': '3.1000',
        'Module voltage low warning': 'Off',
        'Module voltage low warning threshold': '3.1350',
        'Rate identifier': '0x00',
        'Rcvr signal avg optical power(Channel 1)': '-0.12',
        'Rcvr signal avg optical power(Channel 2)': '-0.09',
        'Rcvr signal avg optical power(Channel 3)': '0.55',
        'Rcvr signal avg optical power(Channel 4)': '0.55',
        'Revision Compliance': 'SFF-8636 Rev 2.5/2.6/2.7',
        'Transceiver codes': '0x80 0x00 0x00 0x00 0x00 0x00 0x00 0x00',
        'Transceiver type': '100G Ethernet: 100G Base-SR4 or 25GBase-SR',
        'Transmit avg optical power (Channel 1)': '1.44',
        'Transmit avg optical power (Channel 2)': '1.20',
        'Transmit avg optical power (Channel 3)': '1.26',
        'Transmit avg optical power (Channel 4)': '1.27',
        'Transmitter technology': '0x00 (850 nm VCSEL)',
        'Vendor OUI': '00:02:c9',
        'Vendor PN': 'MMA1B00-C100D',
        'Vendor SN': 'MT1708FT01255',
        'Vendor name': 'Mellanox',
        'Vendor rev': 'A4'
    }


class Data2(Data):
    content = """
        Identifier                                : 0x0d (QSFP+)
        Extended identifier                       : 0x10
        Extended identifier description           : 1.5W max. Power consumption
        Extended identifier description           : No CDR in TX, No CDR in RX
        Extended identifier description           : High Power Class (> 3.5 W) not enabled
        Connector                                 : 0x0c (MPO Parallel Optic)
        Transceiver codes                         : 0x04 0x00 0x00 0x00 0x40 0x40 0x02 0x00
        Transceiver type                          : 40G Ethernet: 40G Base-SR4
        Transceiver type                          : FC: short distance (S)
        Transceiver type                          : FC: Shortwave laser w/o OFC (SN)
        Transceiver type                          : FC: Multimode, 50um (OM3)
        Encoding                                  : 0x05 (64B/66B)
        BR, Nominal                               : 10300Mbps
        Rate identifier                           : 0x00
        Length (SMF,km)                           : 0km
        Length (OM3 50um)                         : 100m
        Length (OM2 50um)                         : 0m
        Length (OM1 62.5um)                       : 0m
        Length (Copper or Active cable)           : 0m
        Transmitter technology                    : 0x00 (850 nm VCSEL)
        Laser wavelength                          : 850.000nm
        Laser wavelength tolerance                : 10.000nm
        Vendor name                               : FINISAR CORP
        Vendor OUI                                : 00:90:65
        Vendor PN                                 : FTL410QE2C
        Vendor rev                                : A
        Vendor SN                                 : ESQ014E
        Revision Compliance                       : Revision not specified
        Module temperature                        : 30.93 degrees C / 87.67 degrees F
        Module voltage                            : 3.2981 V
        Alarm/warning flags implemented           : Yes
        Laser tx bias current (Channel 1)         : 0.000 mA
        Laser tx bias current (Channel 2)         : 0.000 mA
        Laser tx bias current (Channel 3)         : 0.000 mA
        Laser tx bias current (Channel 4)         : 0.000 mA
        Transmit avg optical power (Channel 1)    : 0.0000 mW / -inf dBm
        Transmit avg optical power (Channel 2)    : 0.0000 mW / -inf dBm
        Transmit avg optical power (Channel 3)    : 0.0000 mW / -inf dBm
        Transmit avg optical power (Channel 4)    : 0.0000 mW / -inf dBm
        Rcvr signal avg optical power(Channel 1)  : 0.0000 mW / -inf dBm
        Rcvr signal avg optical power(Channel 2)  : 0.0000 mW / -inf dBm
        Rcvr signal avg optical power(Channel 3)  : 0.0000 mW / -inf dBm
        Rcvr signal avg optical power(Channel 4)  : 0.0000 mW / -inf dBm
        Laser bias current high alarm   (Chan 1)  : Off
        Laser bias current low alarm    (Chan 1)  : Off
        Laser bias current high warning (Chan 1)  : Off
        Laser bias current low warning  (Chan 1)  : Off
        Laser bias current high alarm   (Chan 2)  : Off
        Laser bias current low alarm    (Chan 2)  : Off
        Laser bias current high warning (Chan 2)  : Off
        Laser bias current low warning  (Chan 2)  : Off
        Laser bias current high alarm   (Chan 3)  : Off
        Laser bias current low alarm    (Chan 3)  : Off
        Laser bias current high warning (Chan 3)  : Off
        Laser bias current low warning  (Chan 3)  : Off
        Laser bias current high alarm   (Chan 4)  : Off
        Laser bias current low alarm    (Chan 4)  : Off
        Laser bias current high warning (Chan 4)  : Off
        Laser bias current low warning  (Chan 4)  : Off
        Module temperature high alarm             : Off
        Module temperature low alarm              : Off
        Module temperature high warning           : Off
        Module temperature low warning            : Off
        Module voltage high alarm                 : Off
        Module voltage low alarm                  : Off
        Module voltage high warning               : Off
        Module voltage low warning                : Off
        Laser tx power high alarm   (Channel 1)   : Off
        Laser tx power low alarm    (Channel 1)   : Off
        Laser tx power high warning (Channel 1)   : Off
        Laser tx power low warning  (Channel 1)   : Off
        Laser tx power high alarm   (Channel 2)   : Off
        Laser tx power low alarm    (Channel 2)   : Off
        Laser tx power high warning (Channel 2)   : Off
        Laser tx power low warning  (Channel 2)   : Off
        Laser tx power high alarm   (Channel 3)   : Off
        Laser tx power low alarm    (Channel 3)   : Off
        Laser tx power high warning (Channel 3)   : Off
        Laser tx power low warning  (Channel 3)   : Off
        Laser tx power high alarm   (Channel 4)   : Off
        Laser tx power low alarm    (Channel 4)   : Off
        Laser tx power high warning (Channel 4)   : Off
        Laser tx power low warning  (Channel 4)   : Off
        Laser rx power high alarm   (Channel 1)   : Off
        Laser rx power low alarm    (Channel 1)   : Off
        Laser rx power high warning (Channel 1)   : Off
        Laser rx power low warning  (Channel 1)   : Off
        Laser rx power high alarm   (Channel 2)   : Off
        Laser rx power low alarm    (Channel 2)   : Off
        Laser rx power high warning (Channel 2)   : Off
        Laser rx power low warning  (Channel 2)   : Off
        Laser rx power high alarm   (Channel 3)   : Off
        Laser rx power low alarm    (Channel 3)   : Off
        Laser rx power high warning (Channel 3)   : Off
        Laser rx power low warning  (Channel 3)   : Off
        Laser rx power high alarm   (Channel 4)   : Off
        Laser rx power low alarm    (Channel 4)   : Off
        Laser rx power high warning (Channel 4)   : Off
        Laser rx power low warning  (Channel 4)   : Off
        Laser bias current high alarm threshold   : 0.000 mA
        Laser bias current low alarm threshold    : 0.000 mA
        Laser bias current high warning threshold : 0.000 mA
        Laser bias current low warning threshold  : 0.000 mA
        Laser output power high alarm threshold   : 0.0000 mW / -inf dBm
        Laser output power low alarm threshold    : 0.0000 mW / -inf dBm
        Laser output power high warning threshold : 0.0000 mW / -inf dBm
        Laser output power low warning threshold  : 0.0000 mW / -inf dBm
        Module temperature high alarm threshold   : 75.00 degrees C / 167.00 degrees F
        Module temperature low alarm threshold    : -5.00 degrees C / 23.00 degrees F
        Module temperature high warning threshold : 70.00 degrees C / 158.00 degrees F
        Module temperature low warning threshold  : 0.00 degrees C / 32.00 degrees F
        Module voltage high alarm threshold       : 3.8000 V
        Module voltage low alarm threshold        : 2.8400 V
        Module voltage high warning threshold     : 3.4500 V
        Module voltage low warning threshold      : 3.1500 V
        Laser rx power high alarm threshold       : 0.0000 mW / -inf dBm
        Laser rx power low alarm threshold        : 0.0000 mW / -inf dBm
        Laser rx power high warning threshold     : 0.0000 mW / -inf dBm
        Laser rx power low warning threshold      : 0.0000 mW / -inf dBm
    """
    cmd = "sudo ethtool -m swp13"
    host = "man1-4s7"
    version = """Linux man1-4s7.yndx.net 4.1.0-cl-7-amd64 #1 SMP Debian 4.1.33-1+cl3u17 (2018-10-31) x86_64 GNU/Linux"""
    result = {'Identifier': '0x0d (QSFP+)',
              'Extended identifier': '0x10',
               'Extended identifier description': '1.5W max. Power consumption No CDR in TX, '
                                                  'No CDR in RX High Power Class (> 3.5 W) '
                                                  'not enabled',
              'Connector': '0x0c (MPO Parallel Optic)',
              'Transceiver codes': '0x04 0x00 0x00 0x00 0x40 0x40 0x02 0x00',
              'Transceiver type': '40G Ethernet: 40G Base-SR4 FC: short distance (S) FC: '
                                  'Shortwave laser w/o OFC (SN) FC: Multimode, 50um (OM3)',
              'Encoding': '0x05 (64B/66B)',
              'BR, Nominal': '10300Mbps',
              'Rate identifier': '0x00',
              'Length (SMF,km)': '0km',
              'Length (OM3 50um)': '100m',
              'Length (OM2 50um)': '0m',
              'Length (OM1 62.5um)': '0m',
              'Length (Copper or Active cable)': '0m',
              'Transmitter technology': '0x00 (850 nm VCSEL)',
              'Laser wavelength': '850.000nm',
              'Laser wavelength tolerance': '10.000nm',
              'Vendor name': 'FINISAR CORP',
              'Vendor OUI': '00:90:65',
              'Vendor PN': 'FTL410QE2C',
              'Vendor rev': 'A',
              'Vendor SN': 'ESQ014E',
              'Revision Compliance': 'Revision not specified',
              'Module temperature': '30.93',
              'Module voltage': '3.2981',
              'Alarm/warning flags implemented': 'Yes',
              'Laser tx bias current (Channel 1)': '0.000',
              'Laser tx bias current (Channel 2)': '0.000',
              'Laser tx bias current (Channel 3)': '0.000',
              'Laser tx bias current (Channel 4)': '0.000',
              'Transmit avg optical power (Channel 1)': '-inf',
              'Transmit avg optical power (Channel 2)': '-inf',
              'Transmit avg optical power (Channel 3)': '-inf',
              'Transmit avg optical power (Channel 4)': '-inf',
              'Rcvr signal avg optical power(Channel 1)': '-inf',
              'Rcvr signal avg optical power(Channel 2)': '-inf',
              'Rcvr signal avg optical power(Channel 3)': '-inf',
              'Rcvr signal avg optical power(Channel 4)': '-inf',
              'Laser bias current high alarm   (Chan 1)': 'Off',
              'Laser bias current low alarm    (Chan 1)': 'Off',
              'Laser bias current high warning (Chan 1)': 'Off',
              'Laser bias current low warning  (Chan 1)': 'Off',
              'Laser bias current high alarm   (Chan 2)': 'Off',
              'Laser bias current low alarm    (Chan 2)': 'Off',
              'Laser bias current high warning (Chan 2)': 'Off',
              'Laser bias current low warning  (Chan 2)': 'Off',
              'Laser bias current high alarm   (Chan 3)': 'Off',
              'Laser bias current low alarm    (Chan 3)': 'Off',
              'Laser bias current high warning (Chan 3)': 'Off',
              'Laser bias current low warning  (Chan 3)': 'Off',
              'Laser bias current high alarm   (Chan 4)': 'Off',
              'Laser bias current low alarm    (Chan 4)': 'Off',
              'Laser bias current high warning (Chan 4)': 'Off',
              'Laser bias current low warning  (Chan 4)': 'Off',
              'Module temperature high alarm': 'Off',
              'Module temperature low alarm': 'Off',
              'Module temperature high warning': 'Off',
              'Module temperature low warning': 'Off',
              'Module voltage high alarm': 'Off',
              'Module voltage low alarm': 'Off',
              'Module voltage high warning': 'Off',
              'Module voltage low warning': 'Off',
              'Laser tx power high alarm   (Channel 1)': 'Off',
              'Laser tx power low alarm    (Channel 1)': 'Off',
              'Laser tx power high warning (Channel 1)': 'Off',
              'Laser tx power low warning  (Channel 1)': 'Off',
              'Laser tx power high alarm   (Channel 2)': 'Off',
              'Laser tx power low alarm    (Channel 2)': 'Off',
              'Laser tx power high warning (Channel 2)': 'Off',
              'Laser tx power low warning  (Channel 2)': 'Off',
              'Laser tx power high alarm   (Channel 3)': 'Off',
              'Laser tx power low alarm    (Channel 3)': 'Off',
              'Laser tx power high warning (Channel 3)': 'Off',
              'Laser tx power low warning  (Channel 3)': 'Off',
              'Laser tx power high alarm   (Channel 4)': 'Off',
              'Laser tx power low alarm    (Channel 4)': 'Off',
              'Laser tx power high warning (Channel 4)': 'Off',
              'Laser tx power low warning  (Channel 4)': 'Off',
              'Laser rx power high alarm   (Channel 1)': 'Off',
              'Laser rx power low alarm    (Channel 1)': 'Off',
              'Laser rx power high warning (Channel 1)': 'Off',
              'Laser rx power low warning  (Channel 1)': 'Off',
              'Laser rx power high alarm   (Channel 2)': 'Off',
              'Laser rx power low alarm    (Channel 2)': 'Off',
              'Laser rx power high warning (Channel 2)': 'Off',
              'Laser rx power low warning  (Channel 2)': 'Off',
              'Laser rx power high alarm   (Channel 3)': 'Off',
              'Laser rx power low alarm    (Channel 3)': 'Off',
              'Laser rx power high warning (Channel 3)': 'Off',
              'Laser rx power low warning  (Channel 3)': 'Off',
              'Laser rx power high alarm   (Channel 4)': 'Off',
              'Laser rx power low alarm    (Channel 4)': 'Off',
              'Laser rx power high warning (Channel 4)': 'Off',
              'Laser rx power low warning  (Channel 4)': 'Off',
              'Laser bias current high alarm threshold': '0.000',
              'Laser bias current low alarm threshold': '0.000',
              'Laser bias current high warning threshold': '0.000',
              'Laser bias current low warning threshold': '0.000',
              'Laser output power high alarm threshold': '-inf',
              'Laser output power low alarm threshold': '-inf',
              'Laser output power high warning threshold': '-inf',
              'Laser output power low warning threshold': '-inf',
              'Module temperature high alarm threshold': '75.00',
              'Module temperature low alarm threshold': '-5.00',
              'Module temperature high warning threshold': '70.00',
              'Module temperature low warning threshold': '0.00',
              'Module voltage high alarm threshold': '3.8000',
              'Module voltage low alarm threshold': '2.8400',
              'Module voltage high warning threshold': '3.4500',
              'Module voltage low warning threshold': '3.1500',
              'Laser rx power high alarm threshold': '-inf',
              'Laser rx power low alarm threshold': '-inf',
              'Laser rx power high warning threshold': '-inf',
              'Laser rx power low warning threshold': '-inf'}


class Data3(Data):
    content = """
        Identifier                                : 0x0d (QSFP+)
        Extended identifier                       : 0x00
        Extended identifier description           : 1.5W max. Power consumption
        Extended identifier description           : No CDR in TX, No CDR in RX
        Extended identifier description           : High Power Class (> 3.5 W) not enabled
        Connector                                 : 0x23 (No separable connector)
        Transceiver codes                         : 0x88 0x00 0x00 0x00 0x00 0x00 0x00 0x00
        Transceiver type                          : 40G Ethernet: 40G Base-CR4
        Transceiver type                          : 100G Ethernet: 100G Base-CR4 or 25G Base-CR CA-L
        Encoding                                  : 0x00 (unspecified)
        BR, Nominal                               : 25500Mbps
        Rate identifier                           : 0x00
        Length (SMF,km)                           : 0km
        Length (OM3 50um)                         : 0m
        Length (OM2 50um)                         : 0m
        Length (OM1 62.5um)                       : 0m
        Length (Copper or Active cable)           : 1m
        Transmitter technology                    : 0xa0 (Copper cable unequalized)
        Attenuation at 2.5GHz                     : 2db
        Attenuation at 5.0GHz                     : 3db
        Attenuation at 7.0GHz                     : 4db
        Attenuation at 12.9GHz                    : 7db
        Vendor name                               : Mellanox
        Vendor OUI                                : 00:02:c9
        Vendor PN                                 : MCP1600-E00A
        Vendor rev                                : A2
        Vendor SN                                 : MT1526VS05742
        Revision Compliance                       : SFF-8636 Rev 1.5
        Module temperature                        : 0.00 degrees C / 32.00 degrees F
        Module voltage                            : 0.0000 V
    """
    cmd = "sudo ethtool -m swp13"
    host = "mellanox doc"
    version = """Linux sn2100-test 5.8.0-rc3-mlx-5.8-rc3 #1 SMP Thu Jul 2 16:32:17 UTC 2020 x86_64 x86_64 x86_64 GNU/Linux"""
    result = {'Attenuation at 12.9GHz': '7db',
              'Attenuation at 2.5GHz': '2db',
              'Attenuation at 5.0GHz': '3db',
              'Attenuation at 7.0GHz': '4db',
              'BR, Nominal': '25500Mbps',
              'Connector': '0x23 (No separable connector)',
              'Encoding': '0x00 (unspecified)',
              'Extended identifier': '0x00',
              'Extended identifier description': '1.5W max. Power consumption No CDR in TX, '
                                                 'No CDR in RX High Power Class (> 3.5 W) '
                                                 'not enabled',
              'Identifier': '0x0d (QSFP+)',
              'Length (Copper or Active cable)': '1m',
              'Length (OM1 62.5um)': '0m',
              'Length (OM2 50um)': '0m',
              'Length (OM3 50um)': '0m',
              'Length (SMF,km)': '0km',
              'Module temperature': '0.00',
              'Module voltage': '0.0000',
              'Rate identifier': '0x00',
              'Revision Compliance': 'SFF-8636 Rev 1.5',
              'Transceiver codes': '0x88 0x00 0x00 0x00 0x00 0x00 0x00 0x00',
              'Transceiver type': '40G Ethernet: 40G Base-CR4 100G Ethernet: 100G Base-CR4 '
                                  'or 25G Base-CR CA-L',
              'Transmitter technology': '0xa0 (Copper cable unequalized)',
              'Vendor OUI': '00:02:c9',
              'Vendor PN': 'MCP1600-E00A',
              'Vendor SN': 'MT1526VS05742',
              'Vendor name': 'Mellanox',
              'Vendor rev': 'A2'}


class Data4(Data):
    content = """
	Identifier                                : 0x11 (QSFP28)
	Extended identifier                       : 0x4c
	Extended identifier description           : 2.0W max. Power consumption
	Extended identifier description           : CDR present in TX, CDR present in RX
	Extended identifier description           : High Power Class (> 3.5 W) not enabled
	Connector                                 : 0x0c (MPO Parallel Optic)
	Transceiver codes                         : 0x80 0x00 0x00 0x00 0x40 0x40 0x02 0x08
	Transceiver type                          : 100G Ethernet: 100G Base-SR4 or 25GBase-SR
	Transceiver type                          : FC: short distance (S)
	Transceiver type                          : FC: Shortwave laser w/o OFC (SN)
	Transceiver type                          : FC: Multimode, 50um (OM3)
	Encoding                                  : 0x05 (64B/66B)
	BR, Nominal                               : 25500Mbps
	Rate identifier                           : 0x00
	Length (SMF,km)                           : 0km
	Length (OM3 50um)                         : 70m
	Length (OM2 50um)                         : 0m
	Length (OM1 62.5um)                       : 0m
	Length (Copper or Active cable)           : 50m
	Transmitter technology                    : 0x00 (850 nm VCSEL)
	Laser wavelength                          : 850.000nm
	Laser wavelength tolerance                : 10.000nm
	Vendor name                               : Hisense
	Vendor OUI                                : 00:00:00
	Vendor PN                                 : LTA8531-PC+
	Vendor rev                                : 01
	Vendor SN                                 : T2073001289
	Revision Compliance                       : SFF-8636 Rev 2.5/2.6/2.7
	Module temperature                        : 25.70 degrees C / 78.25 degrees F
	Module voltage                            : 3.2717 V
	Alarm/warning flags implemented           : Yes
	Laser tx bias current (Channel 1)         : 6.032 mA
	Laser tx bias current (Channel 2)         : 6.040 mA
	Laser tx bias current (Channel 3)         : 6.034 mA
	Laser tx bias current (Channel 4)         : 6.042 mA
	Transmit avg optical power (Channel 1)    : 0.9072 mW / -0.42 dBm
	Transmit avg optical power (Channel 2)    : 0.8831 mW / -0.54 dBm
	Transmit avg optical power (Channel 3)    : 0.9306 mW / -0.31 dBm
	Transmit avg optical power (Channel 4)    : 0.8221 mW / -0.85 dBm
	Rcvr signal avg optical power(Channel 1)  : 0.9748 mW / -0.11 dBm
	Rcvr signal avg optical power(Channel 2)  : 1.0403 mW / 0.17 dBm
	Rcvr signal avg optical power(Channel 3)  : 0.9751 mW / -0.11 dBm
	Rcvr signal avg optical power(Channel 4)  : 1.0195 mW / 0.08 dBm
	Laser bias current high alarm   (Chan 1)  : Off
	Laser bias current low alarm    (Chan 1)  : Off
	Laser bias current high warning (Chan 1)  : Off
	Laser bias current low warning  (Chan 1)  : Off
	Laser bias current high alarm   (Chan 2)  : Off
	Laser bias current low alarm    (Chan 2)  : Off
	Laser bias current high warning (Chan 2)  : Off
	Laser bias current low warning  (Chan 2)  : Off
	Laser bias current high alarm   (Chan 3)  : Off
	Laser bias current low alarm    (Chan 3)  : Off
	Laser bias current high warning (Chan 3)  : Off
	Laser bias current low warning  (Chan 3)  : Off
	Laser bias current high alarm   (Chan 4)  : Off
	Laser bias current low alarm    (Chan 4)  : Off
	Laser bias current high warning (Chan 4)  : Off
	Laser bias current low warning  (Chan 4)  : Off
	Module temperature high alarm             : Off
	Module temperature low alarm              : Off
	Module temperature high warning           : Off
	Module temperature low warning            : Off
	Module voltage high alarm                 : Off
	Module voltage low alarm                  : Off
	Module voltage high warning               : Off
	Module voltage low warning                : Off
	Laser tx power high alarm   (Channel 1)   : Off
	Laser tx power low alarm    (Channel 1)   : Off
	Laser tx power high warning (Channel 1)   : Off
	Laser tx power low warning  (Channel 1)   : Off
	Laser tx power high alarm   (Channel 2)   : Off
	Laser tx power low alarm    (Channel 2)   : Off
	Laser tx power high warning (Channel 2)   : Off
	Laser tx power low warning  (Channel 2)   : Off
	Laser tx power high alarm   (Channel 3)   : Off
	Laser tx power low alarm    (Channel 3)   : Off
	Laser tx power high warning (Channel 3)   : Off
	Laser tx power low warning  (Channel 3)   : Off
	Laser tx power high alarm   (Channel 4)   : Off
	Laser tx power low alarm    (Channel 4)   : Off
	Laser tx power high warning (Channel 4)   : Off
	Laser tx power low warning  (Channel 4)   : Off
	Laser rx power high alarm   (Channel 1)   : Off
	Laser rx power low alarm    (Channel 1)   : Off
	Laser rx power high warning (Channel 1)   : Off
	Laser rx power low warning  (Channel 1)   : Off
	Laser rx power high alarm   (Channel 2)   : Off
	Laser rx power low alarm    (Channel 2)   : Off
	Laser rx power high warning (Channel 2)   : Off
	Laser rx power low warning  (Channel 2)   : Off
	Laser rx power high alarm   (Channel 3)   : Off
	Laser rx power low alarm    (Channel 3)   : Off
	Laser rx power high warning (Channel 3)   : Off
	Laser rx power low warning  (Channel 3)   : Off
	Laser rx power high alarm   (Channel 4)   : Off
	Laser rx power low alarm    (Channel 4)   : Off
	Laser rx power high warning (Channel 4)   : Off
	Laser rx power low warning  (Channel 4)   : Off
	Laser bias current high alarm threshold   : 12.000 mA
	Laser bias current low alarm threshold    : 0.000 mA
	Laser bias current high warning threshold : 10.000 mA
	Laser bias current low warning threshold  : 0.000 mA
	Laser output power high alarm threshold   : 3.4674 mW / 5.40 dBm
	Laser output power low alarm threshold    : 0.0617 mW / -12.10 dBm
	Laser output power high warning threshold : 1.7378 mW / 2.40 dBm
	Laser output power low warning threshold  : 0.1230 mW / -9.10 dBm
	Module temperature high alarm threshold   : 80.00 degrees C / 176.00 degrees F
	Module temperature low alarm threshold    : -10.00 degrees C / 14.00 degrees F
	Module temperature high warning threshold : 75.00 degrees C / 167.00 degrees F
	Module temperature low warning threshold  : -5.00 degrees C / 23.00 degrees F
	Module voltage high alarm threshold       : 3.6000 V
	Module voltage low alarm threshold        : 3.0000 V
	Module voltage high warning threshold     : 3.5000 V
	Module voltage low warning threshold      : 3.1000 V
	Laser rx power high alarm threshold       : 3.4674 mW / 5.40 dBm
	Laser rx power low alarm threshold        : 0.0398 mW / -14.00 dBm
	Laser rx power high warning threshold     : 1.7378 mW / 2.40 dBm
	Laser rx power low warning threshold      : 0.0794 mW / -11.00 dBm
    """
    cmd = "sudo ethtool -m swp4"
    host = "sn2100-test"
    version = """Linux sn2100-test 5.8.0-rc3-mlx-5.8-rc3 #1 SMP Thu Jul 2 16:32:17 UTC 2020 x86_64 x86_64 x86_64 GNU/Linux"""
    result = {'Alarm/warning flags implemented': 'Yes',
              'BR, Nominal': '25500Mbps',
              'Connector': '0x0c (MPO Parallel Optic)',
              'Encoding': '0x05 (64B/66B)',
              'Extended identifier': '0x4c',
              'Extended identifier description': '2.0W max. Power consumption CDR present '
                                                 'in TX, CDR present in RX High Power Class '
                                                 '(> 3.5 W) not enabled',
              'Identifier': '0x11 (QSFP28)',
              'Laser bias current high alarm   (Chan 1)': 'Off',
              'Laser bias current high alarm   (Chan 2)': 'Off',
              'Laser bias current high alarm   (Chan 3)': 'Off',
              'Laser bias current high alarm   (Chan 4)': 'Off',
              'Laser bias current high alarm threshold': '12.000',
              'Laser bias current high warning (Chan 1)': 'Off',
              'Laser bias current high warning (Chan 2)': 'Off',
              'Laser bias current high warning (Chan 3)': 'Off',
              'Laser bias current high warning (Chan 4)': 'Off',
              'Laser bias current high warning threshold': '10.000',
              'Laser bias current low alarm    (Chan 1)': 'Off',
              'Laser bias current low alarm    (Chan 2)': 'Off',
              'Laser bias current low alarm    (Chan 3)': 'Off',
              'Laser bias current low alarm    (Chan 4)': 'Off',
              'Laser bias current low alarm threshold': '0.000',
              'Laser bias current low warning  (Chan 1)': 'Off',
              'Laser bias current low warning  (Chan 2)': 'Off',
              'Laser bias current low warning  (Chan 3)': 'Off',
              'Laser bias current low warning  (Chan 4)': 'Off',
              'Laser bias current low warning threshold': '0.000',
              'Laser output power high alarm threshold': '5.40',
              'Laser output power high warning threshold': '2.40',
              'Laser output power low alarm threshold': '-12.10',
              'Laser output power low warning threshold': '-9.10',
              'Laser rx power high alarm   (Channel 1)': 'Off',
              'Laser rx power high alarm   (Channel 2)': 'Off',
              'Laser rx power high alarm   (Channel 3)': 'Off',
              'Laser rx power high alarm   (Channel 4)': 'Off',
              'Laser rx power high alarm threshold': '5.40',
              'Laser rx power high warning (Channel 1)': 'Off',
              'Laser rx power high warning (Channel 2)': 'Off',
              'Laser rx power high warning (Channel 3)': 'Off',
              'Laser rx power high warning (Channel 4)': 'Off',
              'Laser rx power high warning threshold': '2.40',
              'Laser rx power low alarm    (Channel 1)': 'Off',
              'Laser rx power low alarm    (Channel 2)': 'Off',
              'Laser rx power low alarm    (Channel 3)': 'Off',
              'Laser rx power low alarm    (Channel 4)': 'Off',
              'Laser rx power low alarm threshold': '-14.00',
              'Laser rx power low warning  (Channel 1)': 'Off',
              'Laser rx power low warning  (Channel 2)': 'Off',
              'Laser rx power low warning  (Channel 3)': 'Off',
              'Laser rx power low warning  (Channel 4)': 'Off',
              'Laser rx power low warning threshold': '-11.00',
              'Laser tx bias current (Channel 1)': '6.032',
              'Laser tx bias current (Channel 2)': '6.040',
              'Laser tx bias current (Channel 3)': '6.034',
              'Laser tx bias current (Channel 4)': '6.042',
              'Laser tx power high alarm   (Channel 1)': 'Off',
              'Laser tx power high alarm   (Channel 2)': 'Off',
              'Laser tx power high alarm   (Channel 3)': 'Off',
              'Laser tx power high alarm   (Channel 4)': 'Off',
              'Laser tx power high warning (Channel 1)': 'Off',
              'Laser tx power high warning (Channel 2)': 'Off',
              'Laser tx power high warning (Channel 3)': 'Off',
              'Laser tx power high warning (Channel 4)': 'Off',
              'Laser tx power low alarm    (Channel 1)': 'Off',
              'Laser tx power low alarm    (Channel 2)': 'Off',
              'Laser tx power low alarm    (Channel 3)': 'Off',
              'Laser tx power low alarm    (Channel 4)': 'Off',
              'Laser tx power low warning  (Channel 1)': 'Off',
              'Laser tx power low warning  (Channel 2)': 'Off',
              'Laser tx power low warning  (Channel 3)': 'Off',
              'Laser tx power low warning  (Channel 4)': 'Off',
              'Laser wavelength': '850.000nm',
              'Laser wavelength tolerance': '10.000nm',
              'Length (Copper or Active cable)': '50m',
              'Length (OM1 62.5um)': '0m',
              'Length (OM2 50um)': '0m',
              'Length (OM3 50um)': '70m',
              'Length (SMF,km)': '0km',
              'Module temperature': '25.70',
              'Module temperature high alarm': 'Off',
              'Module temperature high alarm threshold': '80.00',
              'Module temperature high warning': 'Off',
              'Module temperature high warning threshold': '75.00',
              'Module temperature low alarm': 'Off',
              'Module temperature low alarm threshold': '-10.00',
              'Module temperature low warning': 'Off',
              'Module temperature low warning threshold': '-5.00',
              'Module voltage': '3.2717',
              'Module voltage high alarm': 'Off',
              'Module voltage high alarm threshold': '3.6000',
              'Module voltage high warning': 'Off',
              'Module voltage high warning threshold': '3.5000',
              'Module voltage low alarm': 'Off',
              'Module voltage low alarm threshold': '3.0000',
              'Module voltage low warning': 'Off',
              'Module voltage low warning threshold': '3.1000',
              'Rate identifier': '0x00',
              'Rcvr signal avg optical power(Channel 1)': '-0.11',
              'Rcvr signal avg optical power(Channel 2)': '0.17',
              'Rcvr signal avg optical power(Channel 3)': '-0.11',
              'Rcvr signal avg optical power(Channel 4)': '0.08',
              'Revision Compliance': 'SFF-8636 Rev 2.5/2.6/2.7',
              'Transceiver codes': '0x80 0x00 0x00 0x00 0x40 0x40 0x02 0x08',
              'Transceiver type': '100G Ethernet: 100G Base-SR4 or 25GBase-SR FC: short '
                                  'distance (S) FC: Shortwave laser w/o OFC (SN) FC: '
                                  'Multimode, 50um (OM3)',
              'Transmit avg optical power (Channel 1)': '-0.42',
              'Transmit avg optical power (Channel 2)': '-0.54',
              'Transmit avg optical power (Channel 3)': '-0.31',
              'Transmit avg optical power (Channel 4)': '-0.85',
              'Transmitter technology': '0x00 (850 nm VCSEL)',
              'Vendor OUI': '00:00:00',
              'Vendor PN': 'LTA8531-PC+',
              'Vendor SN': 'T2073001289',
              'Vendor name': 'Hisense',
              'Vendor rev': '01'}
