from data.lib import Data


class Data1(Data):
    content = """
**************************************************************
*     Name          * Slot * Lines [Label] * Clients [Label] *
**************************************************************
*     Empty         *  1   * --            * --              *
*     Empty         *  2   * --            * --              *
*     PMOABP-HC     *  3   *  2 [line]     *  2 [client]     *
*     PM_20002-MR   *  4   *  1 [line]     *  2 [client]     *
*     Empty         *  5   * --            * --              *
*     Empty         *  6   * --            * --              *
*     PM_FAN_C200HC *  7   *  0 [line]     *  0 [client]     *
*     PSB_C200HC-AC *  8   *  0 []         *  0 []           *
*     PSB_C200HC-AC *  9   *  0 []         *  0 []           *
**************************************************************
    """
    cmd = "hwlist"
    host = "dwdm-std-iva"
    version = """
Command-Line Interface, build date Mar 26 2018 15:33:53

   Hardware Version  : 2EK00229
   System  Version   : 3SW06001AAAA
    """
    result = [
        {'Name': 'Empty',
         'Slot': '1',
         'Lines [Label]': '--',
         'Clients [Label]': '--'},
        {'Name': 'Empty',
         'Slot': '2',
         'Lines [Label]': '--',
         'Clients [Label]': '--'},
        {'Name': 'PMOABP-HC',
         'Slot': '3',
         'Lines [Label]': '2 [line]',
         'Clients [Label]': '2 [client]'},
        {'Name': 'PM_20002-MR',
         'Slot': '4',
         'Lines [Label]': '1 [line]',
         'Clients [Label]': '2 [client]'},
        {'Name': 'Empty',
         'Slot': '5',
         'Lines [Label]': '--',
         'Clients [Label]': '--'},
        {'Name': 'Empty',
         'Slot': '6',
         'Lines [Label]': '--',
         'Clients [Label]': '--'},
        {'Name': 'PM_FAN_C200HC',
         'Slot': '7',
         'Lines [Label]': '0 [line]',
         'Clients [Label]': '0 [client]'},
        {'Name': 'PSB_C200HC-AC',
         'Slot': '8',
         'Lines [Label]': '0 []',
         'Clients [Label]': '0 []'},
        {'Name': 'PSB_C200HC-AC',
         'Slot': '9',
         'Lines [Label]': '0 []',
         'Clients [Label]': '0 []'}
    ]

