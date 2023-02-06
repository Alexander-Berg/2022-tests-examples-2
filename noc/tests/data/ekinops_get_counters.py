from data.lib import Data


class Data1(Data):
    content = """

****************************
*    Slot 4                *
*    PM_20002-MR           *
*    Line Counter          *
*    LINE_Number 1         *
****************************

****************************************************************************
*     Counter                   * Value                  * Overload * Err. *
****************************************************************************
*  1. Pre-SD FEC Errors         * 4.24E-03, avg:5.14E-03 * OFF      * OFF  *
*  2. Uncorrected SD FEC Errors * 0.00E+00, avg:1.57E-12 * OFF      * OFF  *
****************************************************************************
    """
    cmd = "get_counters 4 Line"
    host = "dwdm-std-iva"
    version = """
Command-Line Interface, build date Mar 26 2018 15:33:53

   Hardware Version  : 2EK00229
   System  Version   : 3SW06001AAAA
    """
    result = [{'Counter': '1. Pre-SD FEC Errors',
               'Err.': 'OFF',
               'Overload': 'OFF',
               'Value': '4.24E-03, avg:5.14E-03'},
              {'Counter': '2. Uncorrected SD FEC Errors',
               'Err.': 'OFF',
               'Overload': 'OFF',
               'Value': '0.00E+00, avg:1.57E-12'}]
