from data.lib import Data


class Data1(Data):
    content = """
****************************
*    Slot 4                *
*    PM_20002-MR           *
*    Line Measurement      *
*    LINE_Number 1         *
****************************

******************************************************************
*     Measurement                             * Value    * Unit  *
******************************************************************
*  1. Current Line Trscv Tx Power             * -3.0     * dBm   *
*  2. Min Line Trscv Tx Power                 * -26.8    * dBm   *
*  3. Max Line Trscv Tx Power                 * -3.0     * dBm   *
*  4. Current Line Trscv Tx Laser Temperature * 49.99    * �C    *
*  5. Min Line Trscv Tx Laser Temperature     * 49.99    * �C    *
*  6. Max Line Trscv Tx Laser Temperature     * 50.01    * �C    *
*  7. Current Line Trscv Rx Power             * -13.1    * dBm   *
*  8. Min Line Trscv Rx Power                 * -35.6    * dBm   *
*  9. Max Line Trscv Rx Power                 * -12.8    * dBm   *
* 10. Current Residual Chromatic Dispersion   * -1074.0  * ps/nm *
* 11. Min Residual Chromatic Dispersion       * 37858.0  * ps/nm *
* 12. Max Residual Chromatic Dispersion       * -37854.0 * ps/nm *
* 13. Current Differential Group Delay        * 51.0     * ps    *
* 14. Min Differential Group Delay            * 0.0      * ps    *
* 15. Max Differential Group Delay            * 56.0     * ps    *
******************************************************************
    """
    cmd = "get_measurements 4 Line"
    host = "dwdm-std-iva"
    version = """
Command-Line Interface, build date Mar 26 2018 15:33:53

   Hardware Version  : 2EK00229
   System  Version   : 3SW06001AAAA
    """
    result = [
        {'Measurement': '1. Current Line Trscv Tx Power',
         'Value': '-3.0',
         'Unit': 'dBm'},
        {'Measurement': '2. Min Line Trscv Tx Power',
         'Value': '-26.8',
         'Unit': 'dBm'},
        {'Measurement': '3. Max Line Trscv Tx Power', 'Value': '-3.0', 'Unit': 'dBm'},
        {'Measurement': '4. Current Line Trscv Tx Laser Temperature',
         'Value': '49.99',
         'Unit': '�C'},
        {'Measurement': '5. Min Line Trscv Tx Laser Temperature',
         'Value': '49.99',
         'Unit': '�C'},
        {'Measurement': '6. Max Line Trscv Tx Laser Temperature',
         'Value': '50.01',
         'Unit': '�C'},
        {'Measurement': '7. Current Line Trscv Rx Power',
         'Value': '-13.1',
         'Unit': 'dBm'},
        {'Measurement': '8. Min Line Trscv Rx Power',
         'Value': '-35.6',
         'Unit': 'dBm'},
        {'Measurement': '9. Max Line Trscv Rx Power',
         'Value': '-12.8',
         'Unit': 'dBm'},
        {'Measurement': '10. Current Residual Chromatic Dispersion',
         'Value': '-1074.0',
         'Unit': 'ps/nm'},
        {'Measurement': '11. Min Residual Chromatic Dispersion',
         'Value': '37858.0',
         'Unit': 'ps/nm'},
        {'Measurement': '12. Max Residual Chromatic Dispersion',
         'Value': '-37854.0',
         'Unit': 'ps/nm'},
        {'Measurement': '13. Current Differential Group Delay',
         'Value': '51.0',
         'Unit': 'ps'},
        {'Measurement': '14. Min Differential Group Delay',
         'Value': '0.0',
         'Unit': 'ps'},
        {'Measurement': '15. Max Differential Group Delay',
         'Value': '56.0',
         'Unit': 'ps'}
    ]
