from data.lib import Data


class Data1(Data):
    content = """
Proto: Protocol        Pre: Preference
Route Flags: R - relay, D - download to fib, T - to vpn-instance, B - black hole route
------------------------------------------------------------------------------
Routing Table : _public_
         Destinations : 485      Routes : 1081     

Destination/Mask    Proto   Pre  Cost        Flags NextHop         Interface

    5.45.200.24/32  OSPF    10   6502          D   213.180.213.136 Eth-Trunk81
   5.45.247.180/32  OSPF    10   6502          D   213.180.213.136 Eth-Trunk81
     10.255.0.1/32  ISIS-L2 15   1400          D   10.255.0.154    Eth-Trunk161
     10.255.0.2/32  ISIS-L2 15   200           D   10.255.0.154    Eth-Trunk161
     10.255.0.5/32  ISIS-L2 15   400           D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   400           D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   400           D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   400           D   10.255.0.149    Eth-Trunk2.10
     10.255.0.6/32  ISIS-L2 15   200           D   10.255.0.157    Eth-Trunk3.10
     10.255.0.8/32  ISIS-L2 15   200           D   10.255.0.139    Eth-Trunk1.10
     10.255.0.9/32  ISIS-L2 15   1200          D   10.255.0.154    Eth-Trunk161
    10.255.0.10/32  ISIS-L2 15   200           D   10.255.0.131    Eth-Trunk4.10
    10.255.0.11/32  ISIS-L2 15   1000          D   10.255.0.154    Eth-Trunk161
                    ISIS-L2 15   1000          D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   1000          D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   1000          D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   1000          D   10.255.0.149    Eth-Trunk2.10
    10.255.0.12/32  ISIS-L2 15   1300          D   10.255.0.154    Eth-Trunk161
    10.255.0.13/32  ISIS-L2 15   1300          D   10.255.0.154    Eth-Trunk161
    10.255.0.14/32  Direct  0    0             D   127.0.0.1       LoopBack10
    10.255.0.15/32  ISIS-L2 15   2000          D   10.255.0.154    Eth-Trunk161
    10.255.0.16/32  ISIS-L2 15   2000          D   10.255.0.154    Eth-Trunk161
    10.255.0.17/32  ISIS-L2 15   2000          D   10.255.0.154    Eth-Trunk161
    10.255.0.18/32  ISIS-L2 15   200           D   10.255.0.149    Eth-Trunk2.10
    10.255.0.19/32  ISIS-L2 15   2000          D   10.255.0.154    Eth-Trunk161
    10.255.0.20/32  ISIS-L2 15   2000          D   10.255.0.154    Eth-Trunk161
    10.255.0.21/32  ISIS-L2 15   2000          D   10.255.0.154    Eth-Trunk161
    10.255.0.22/32  ISIS-L2 15   210600        D   10.255.0.154    Eth-Trunk161
    10.255.0.30/32  ISIS-L2 15   16777814      D   10.255.0.154    Eth-Trunk161
                    ISIS-L2 15   16777814      D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   16777814      D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   16777814      D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   16777814      D   10.255.0.149    Eth-Trunk2.10
    10.255.0.34/32  ISIS-L2 15   600           D   10.255.0.154    Eth-Trunk161
    10.255.0.35/32  ISIS-L2 15   1400          D   10.255.0.154    Eth-Trunk161
    10.255.0.36/32  ISIS-L2 15   1400          D   10.255.0.154    Eth-Trunk161
    10.255.0.37/32  ISIS-L2 15   16778614      D   10.255.0.154    Eth-Trunk161
    10.255.0.41/32  ISIS-L2 15   1400          D   10.255.0.154    Eth-Trunk161
    10.255.0.42/32  ISIS-L2 15   1400          D   10.255.0.154    Eth-Trunk161
    10.255.0.43/32  ISIS-L2 15   1400          D   10.255.0.154    Eth-Trunk161
    10.255.0.44/32  ISIS-L2 15   1400          D   10.255.0.154    Eth-Trunk161
    10.255.0.45/32  ISIS-L2 15   1400          D   10.255.0.154    Eth-Trunk161
    10.255.0.46/32  ISIS-L2 15   1400          D   10.255.0.154    Eth-Trunk161
    10.255.0.52/32  ISIS-L2 15   1400          D   10.255.0.154    Eth-Trunk161
    10.255.0.53/32  ISIS-L2 15   210600        D   10.255.0.154    Eth-Trunk161
    10.255.0.55/32  ISIS-L2 15   210600        D   10.255.0.154    Eth-Trunk161
    10.255.0.56/32  ISIS-L2 15   1000          D   10.255.0.154    Eth-Trunk161
                    ISIS-L2 15   1000          D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   1000          D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   1000          D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   1000          D   10.255.0.149    Eth-Trunk2.10
    10.255.0.59/32  ISIS-L2 15   1600          D   10.255.0.154    Eth-Trunk161
                    ISIS-L2 15   1600          D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   1600          D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   1600          D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   1600          D   10.255.0.149    Eth-Trunk2.10
    10.255.0.61/32  ISIS-L2 15   1400          D   10.255.0.154    Eth-Trunk161
    10.255.0.63/32  ISIS-L2 15   1400          D   10.255.0.154    Eth-Trunk161
    10.255.0.64/32  ISIS-L2 15   1400          D   10.255.0.154    Eth-Trunk161
    10.255.0.65/32  ISIS-L2 15   1400          D   10.255.0.154    Eth-Trunk161
    10.255.0.66/32  ISIS-L2 15   1400          D   10.255.0.154    Eth-Trunk161
    10.255.0.67/32  ISIS-L2 15   210600        D   10.255.0.154    Eth-Trunk161
    10.255.0.68/32  ISIS-L2 15   600           D   10.255.0.154    Eth-Trunk161
                    ISIS-L2 15   600           D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   600           D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   600           D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   600           D   10.255.0.149    Eth-Trunk2.10
    10.255.0.69/32  ISIS-L2 15   1400          D   10.255.0.154    Eth-Trunk161
    10.255.0.71/32  ISIS-L2 15   10600         D   10.255.0.154    Eth-Trunk161
    10.255.0.75/32  ISIS-L2 15   600           D   10.255.0.154    Eth-Trunk161
    10.255.0.99/32  ISIS-L2 15   600           D   10.255.0.154    Eth-Trunk161
   10.255.0.100/32  ISIS-L2 15   100200        D   10.255.0.154    Eth-Trunk161
   10.255.0.104/32  ISIS-L2 15   10600         D   10.255.0.154    Eth-Trunk161
   10.255.0.130/31  Direct  0    0             D   10.255.0.130    Eth-Trunk4.10
   10.255.0.130/32  Direct  0    0             D   127.0.0.1       Eth-Trunk4.10
   10.255.0.138/31  Direct  0    0             D   10.255.0.138    Eth-Trunk1.10
   10.255.0.138/32  Direct  0    0             D   127.0.0.1       Eth-Trunk1.10
   10.255.0.146/31  ISIS-L2 15   600           D   10.255.0.154    Eth-Trunk161
   10.255.0.148/31  Direct  0    0             D   10.255.0.148    Eth-Trunk2.10
   10.255.0.148/32  Direct  0    0             D   127.0.0.1       Eth-Trunk2.10
   10.255.0.150/31  ISIS-L2 15   1000          D   10.255.0.154    Eth-Trunk161
                    ISIS-L2 15   1000          D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   1000          D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   1000          D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   1000          D   10.255.0.149    Eth-Trunk2.10
   10.255.0.152/31  ISIS-L2 15   1200          D   10.255.0.154    Eth-Trunk161
   10.255.0.154/31  Direct  0    0             D   10.255.0.155    Eth-Trunk161
   10.255.0.155/32  Direct  0    0             D   127.0.0.1       Eth-Trunk161
   10.255.0.156/31  Direct  0    0             D   10.255.0.156    Eth-Trunk3.10
   10.255.0.156/32  Direct  0    0             D   127.0.0.1       Eth-Trunk3.10
   10.255.0.158/31  ISIS-L2 15   600           D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   600           D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   600           D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   600           D   10.255.0.149    Eth-Trunk2.10
   10.255.0.160/31  ISIS-L2 15   1700          D   10.255.0.154    Eth-Trunk161
                    ISIS-L2 15   1700          D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   1700          D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   1700          D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   1700          D   10.255.0.149    Eth-Trunk2.10
   10.255.0.162/31  ISIS-L2 15   1800          D   10.255.0.154    Eth-Trunk161
                    ISIS-L2 15   1800          D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   1800          D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   1800          D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   1800          D   10.255.0.149    Eth-Trunk2.10
   10.255.0.164/31  ISIS-L2 15   1400          D   10.255.0.154    Eth-Trunk161
   10.255.0.166/31  ISIS-L2 15   1800          D   10.255.0.154    Eth-Trunk161
                    ISIS-L2 15   1800          D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   1800          D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   1800          D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   1800          D   10.255.0.149    Eth-Trunk2.10
   10.255.0.170/31  ISIS-L2 15   1400          D   10.255.0.154    Eth-Trunk161
   10.255.0.172/31  ISIS-L2 15   600           D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   600           D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   600           D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   600           D   10.255.0.149    Eth-Trunk2.10
   10.255.0.174/31  ISIS-L2 15   600           D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   600           D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   600           D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   600           D   10.255.0.149    Eth-Trunk2.10
   10.255.0.176/31  ISIS-L2 15   600           D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   600           D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   600           D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   600           D   10.255.0.149    Eth-Trunk2.10
   10.255.0.182/31  ISIS-L2 15   1400          D   10.255.0.154    Eth-Trunk161
   10.255.0.190/31  ISIS-L2 15   600           D   10.255.0.154    Eth-Trunk161
   10.255.0.194/31  ISIS-L2 15   1800          D   10.255.0.154    Eth-Trunk161
                    ISIS-L2 15   1800          D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   1800          D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   1800          D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   1800          D   10.255.0.149    Eth-Trunk2.10
   10.255.0.196/31  ISIS-L2 15   600           D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   600           D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   600           D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   600           D   10.255.0.149    Eth-Trunk2.10
   10.255.0.204/31  ISIS-L2 15   1400          D   10.255.0.154    Eth-Trunk161
   10.255.0.210/31  ISIS-L2 15   1600          D   10.255.0.154    Eth-Trunk161
                    ISIS-L2 15   1600          D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   1600          D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   1600          D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   1600          D   10.255.0.149    Eth-Trunk2.10
   10.255.0.212/31  ISIS-L2 15   1000600       D   10.255.0.154    Eth-Trunk161
                    ISIS-L2 15   1000600       D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   1000600       D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   1000600       D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   1000600       D   10.255.0.149    Eth-Trunk2.10
   10.255.0.224/31  ISIS-L2 15   1800          D   10.255.0.154    Eth-Trunk161
                    ISIS-L2 15   1800          D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   1800          D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   1800          D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   1800          D   10.255.0.149    Eth-Trunk2.10
   10.255.0.226/31  ISIS-L2 15   1400          D   10.255.0.154    Eth-Trunk161
   10.255.0.228/31  ISIS-L2 15   1800          D   10.255.0.154    Eth-Trunk161
                    ISIS-L2 15   1800          D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   1800          D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   1800          D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   1800          D   10.255.0.149    Eth-Trunk2.10
   10.255.0.232/31  ISIS-L2 15   1400          D   10.255.0.154    Eth-Trunk161
   10.255.0.234/31  ISIS-L2 15   1800          D   10.255.0.154    Eth-Trunk161
                    ISIS-L2 15   1800          D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   1800          D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   1800          D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   1800          D   10.255.0.149    Eth-Trunk2.10
   10.255.0.236/31  ISIS-L2 15   1400          D   10.255.0.154    Eth-Trunk161
   10.255.0.238/31  ISIS-L2 15   1800          D   10.255.0.154    Eth-Trunk161
                    ISIS-L2 15   1800          D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   1800          D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   1800          D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   1800          D   10.255.0.149    Eth-Trunk2.10
   10.255.0.240/31  ISIS-L2 15   1400          D   10.255.0.154    Eth-Trunk161
   10.255.0.248/31  ISIS-L2 15   600           D   10.255.0.154    Eth-Trunk161
   10.255.0.250/31  ISIS-L2 15   1300          D   10.255.0.154    Eth-Trunk161
   10.255.0.252/31  ISIS-L2 15   1000          D   10.255.0.154    Eth-Trunk161
                    ISIS-L2 15   1000          D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   1000          D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   1000          D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   1000          D   10.255.0.149    Eth-Trunk2.10
     10.255.1.0/31  ISIS-L2 15   2000          D   10.255.0.154    Eth-Trunk161
     10.255.1.2/31  ISIS-L2 15   1700          D   10.255.0.154    Eth-Trunk161
                    ISIS-L2 15   1700          D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   1700          D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   1700          D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   1700          D   10.255.0.149    Eth-Trunk2.10
     10.255.1.4/31  ISIS-L2 15   2000          D   10.255.0.154    Eth-Trunk161
     10.255.1.6/31  ISIS-L2 15   1700          D   10.255.0.154    Eth-Trunk161
                    ISIS-L2 15   1700          D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   1700          D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   1700          D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   1700          D   10.255.0.149    Eth-Trunk2.10
   10.255.1.220/31  ISIS-L2 15   2400          D   10.255.0.154    Eth-Trunk161
                    ISIS-L2 15   2400          D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   2400          D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   2400          D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   2400          D   10.255.0.149    Eth-Trunk2.10
   10.255.1.222/31  ISIS-L2 15   2400          D   10.255.0.154    Eth-Trunk161
                    ISIS-L2 15   2400          D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   2400          D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   2400          D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   2400          D   10.255.0.149    Eth-Trunk2.10
   10.255.1.224/31  ISIS-L2 15   2400          D   10.255.0.154    Eth-Trunk161
                    ISIS-L2 15   2400          D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   2400          D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   2400          D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   2400          D   10.255.0.149    Eth-Trunk2.10
   10.255.1.226/31  ISIS-L2 15   2400          D   10.255.0.154    Eth-Trunk161
                    ISIS-L2 15   2400          D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   2400          D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   2400          D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   2400          D   10.255.0.149    Eth-Trunk2.10
   10.255.1.228/31  ISIS-L2 15   2400          D   10.255.0.154    Eth-Trunk161
                    ISIS-L2 15   2400          D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   2400          D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   2400          D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   2400          D   10.255.0.149    Eth-Trunk2.10
   10.255.1.230/31  ISIS-L2 15   2400          D   10.255.0.154    Eth-Trunk161
                    ISIS-L2 15   2400          D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   2400          D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   2400          D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   2400          D   10.255.0.149    Eth-Trunk2.10
   10.255.1.232/31  ISIS-L2 15   2000          D   10.255.0.154    Eth-Trunk161
   10.255.1.234/31  ISIS-L2 15   2000          D   10.255.0.154    Eth-Trunk161
   10.255.1.236/31  ISIS-L2 15   2000          D   10.255.0.154    Eth-Trunk161
   10.255.1.238/31  ISIS-L2 15   2000          D   10.255.0.154    Eth-Trunk161
   10.255.1.240/31  ISIS-L2 15   2000          D   10.255.0.154    Eth-Trunk161
   10.255.1.242/31  ISIS-L2 15   2000          D   10.255.0.154    Eth-Trunk161
     10.255.2.8/31  ISIS-L2 15   1800          D   10.255.0.154    Eth-Trunk161
                    ISIS-L2 15   1800          D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   1800          D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   1800          D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   1800          D   10.255.0.149    Eth-Trunk2.10
    10.255.2.12/31  ISIS-L2 15   1800          D   10.255.0.154    Eth-Trunk161
                    ISIS-L2 15   1800          D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   1800          D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   1800          D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   1800          D   10.255.0.149    Eth-Trunk2.10
    10.255.2.16/31  ISIS-L2 15   1800          D   10.255.0.154    Eth-Trunk161
                    ISIS-L2 15   1800          D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   1800          D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   1800          D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   1800          D   10.255.0.149    Eth-Trunk2.10
    10.255.2.18/31  ISIS-L2 15   1800          D   10.255.0.154    Eth-Trunk161
                    ISIS-L2 15   1800          D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   1800          D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   1800          D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   1800          D   10.255.0.149    Eth-Trunk2.10
    10.255.2.20/31  ISIS-L2 15   2200          D   10.255.0.154    Eth-Trunk161
    10.255.2.22/31  ISIS-L2 15   2200          D   10.255.0.154    Eth-Trunk161
    10.255.2.24/31  ISIS-L2 15   1800          D   10.255.0.154    Eth-Trunk161
                    ISIS-L2 15   1800          D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   1800          D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   1800          D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   1800          D   10.255.0.149    Eth-Trunk2.10
    10.255.2.36/31  ISIS-L2 15   1800          D   10.255.0.154    Eth-Trunk161
                    ISIS-L2 15   1800          D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   1800          D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   1800          D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   1800          D   10.255.0.149    Eth-Trunk2.10
   10.255.2.192/31  ISIS-L2 15   1800          D   10.255.0.154    Eth-Trunk161
                    ISIS-L2 15   1800          D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   1800          D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   1800          D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   1800          D   10.255.0.149    Eth-Trunk2.10
   10.255.2.194/31  ISIS-L2 15   1800          D   10.255.0.154    Eth-Trunk161
                    ISIS-L2 15   1800          D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   1800          D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   1800          D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   1800          D   10.255.0.149    Eth-Trunk2.10
   10.255.2.198/31  ISIS-L2 15   2200          D   10.255.0.154    Eth-Trunk161
   10.255.2.202/31  ISIS-L2 15   2200          D   10.255.0.154    Eth-Trunk161
   10.255.2.204/31  ISIS-L2 15   2200          D   10.255.0.154    Eth-Trunk161
   10.255.2.224/31  ISIS-L2 15   2200          D   10.255.0.154    Eth-Trunk161
   10.255.2.226/31  ISIS-L2 15   1800          D   10.255.0.154    Eth-Trunk161
                    ISIS-L2 15   1800          D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   1800          D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   1800          D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   1800          D   10.255.0.149    Eth-Trunk2.10
     10.255.3.0/31  ISIS-L2 15   1000          D   10.255.0.154    Eth-Trunk161
                    ISIS-L2 15   1000          D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   1000          D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   1000          D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   1000          D   10.255.0.149    Eth-Trunk2.10
    10.255.3.26/31  ISIS-L2 15   100200        D   10.255.0.154    Eth-Trunk161
    10.255.3.60/31  ISIS-L2 15   210600        D   10.255.0.154    Eth-Trunk161
    10.255.3.66/31  ISIS-L2 15   11000         D   10.255.0.154    Eth-Trunk161
                    ISIS-L2 15   11000         D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   11000         D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   11000         D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   11000         D   10.255.0.149    Eth-Trunk2.10
    10.255.3.68/31  ISIS-L2 15   410600        D   10.255.0.154    Eth-Trunk161
    10.255.3.70/31  ISIS-L2 15   2200          D   10.255.0.154    Eth-Trunk161
    10.255.3.72/31  ISIS-L2 15   1800          D   10.255.0.154    Eth-Trunk161
                    ISIS-L2 15   1800          D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   1800          D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   1800          D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   1800          D   10.255.0.149    Eth-Trunk2.10
    10.255.3.76/31  ISIS-L2 15   210600        D   10.255.0.154    Eth-Trunk161
    10.255.3.78/31  ISIS-L2 15   20600         D   10.255.0.154    Eth-Trunk161
    10.255.3.80/31  ISIS-L2 15   11000         D   10.255.0.154    Eth-Trunk161
                    ISIS-L2 15   11000         D   10.255.0.131    Eth-Trunk4.10
                    ISIS-L2 15   11000         D   10.255.0.157    Eth-Trunk3.10
                    ISIS-L2 15   11000         D   10.255.0.139    Eth-Trunk1.10
                    ISIS-L2 15   11000         D   10.255.0.149    Eth-Trunk2.10
    10.255.3.90/31  ISIS-L2 15   1400          D   10.255.0.154    Eth-Trunk161
    10.255.3.94/31  ISIS-L2 15   1400          D   10.255.0.154    Eth-Trunk161
   10.255.3.104/31  ISIS-L2 15   210610        D   10.255.0.154    Eth-Trunk161
   10.255.3.108/31  ISIS-L2 15   2000          D   10.255.0.154    Eth-Trunk161
   10.255.3.110/31  ISIS-L2 15   600           D   10.255.0.154    Eth-Trunk161
   10.255.3.112/31  ISIS-L2 15   210600        D   10.255.0.154    Eth-Trunk161
   10.255.3.114/31  ISIS-L2 15   410600        D   10.255.0.154    Eth-Trunk161
   10.255.3.116/31  ISIS-L2 15   210600        D   10.255.0.154    Eth-Trunk161
  87.250.226.99/32  OSPF    10   8             D   213.180.213.136 Eth-Trunk81
                    OSPF    10   8             D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   8             D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   8             D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   8             D   87.250.239.215  Eth-Trunk1.1
 87.250.226.122/32  OSPF    10   13            D   213.180.213.136 Eth-Trunk81
                    OSPF    10   13            D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   13            D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   13            D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   13            D   87.250.239.215  Eth-Trunk1.1
 87.250.226.134/32  OSPF    10   65643         D   213.180.213.136 Eth-Trunk81
                    OSPF    10   65643         D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   65643         D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   65643         D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   65643         D   87.250.239.215  Eth-Trunk1.1
 87.250.226.135/32  OSPF    10   108           D   213.180.213.136 Eth-Trunk81
                    OSPF    10   108           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   108           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   108           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   108           D   87.250.239.215  Eth-Trunk1.1
 87.250.226.136/32  OSPF    10   108           D   213.180.213.136 Eth-Trunk81
                    OSPF    10   108           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   108           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   108           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   108           D   87.250.239.215  Eth-Trunk1.1
 87.250.226.141/32  OSPF    10   108           D   213.180.213.136 Eth-Trunk81
                    OSPF    10   108           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   108           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   108           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   108           D   87.250.239.215  Eth-Trunk1.1
 87.250.226.142/32  OSPF    10   108           D   213.180.213.136 Eth-Trunk81
                    OSPF    10   108           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   108           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   108           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   108           D   87.250.239.215  Eth-Trunk1.1
 87.250.226.143/32  OSPF    10   1008          D   213.180.213.136 Eth-Trunk81
                    OSPF    10   1008          D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   1008          D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   1008          D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   1008          D   87.250.239.215  Eth-Trunk1.1
 87.250.226.155/32  OSPF    10   10            D   213.180.213.136 Eth-Trunk81
                    OSPF    10   10            D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   10            D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   10            D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   10            D   87.250.239.215  Eth-Trunk1.1
 87.250.226.156/32  OSPF    10   10            D   213.180.213.136 Eth-Trunk81
                    OSPF    10   10            D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   10            D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   10            D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   10            D   87.250.239.215  Eth-Trunk1.1
 87.250.226.157/32  OSPF    10   10            D   213.180.213.136 Eth-Trunk81
                    OSPF    10   10            D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   10            D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   10            D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   10            D   87.250.239.215  Eth-Trunk1.1
 87.250.226.158/32  OSPF    10   10            D   213.180.213.136 Eth-Trunk81
                    OSPF    10   10            D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   10            D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   10            D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   10            D   87.250.239.215  Eth-Trunk1.1
 87.250.226.159/32  OSPF    10   10            D   213.180.213.136 Eth-Trunk81
                    OSPF    10   10            D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   10            D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   10            D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   10            D   87.250.239.215  Eth-Trunk1.1
 87.250.226.160/32  OSPF    10   10            D   213.180.213.136 Eth-Trunk81
                    OSPF    10   10            D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   10            D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   10            D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   10            D   87.250.239.215  Eth-Trunk1.1
 87.250.226.162/32  OSPF    10   10            D   213.180.213.136 Eth-Trunk81
                    OSPF    10   10            D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   10            D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   10            D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   10            D   87.250.239.215  Eth-Trunk1.1
 87.250.226.194/32  OSPF    10   108           D   213.180.213.136 Eth-Trunk81
                    OSPF    10   108           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   108           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   108           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   108           D   87.250.239.215  Eth-Trunk1.1
 87.250.226.195/32  OSPF    10   108           D   213.180.213.136 Eth-Trunk81
                    OSPF    10   108           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   108           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   108           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   108           D   87.250.239.215  Eth-Trunk1.1
 87.250.226.196/32  OSPF    10   108           D   213.180.213.136 Eth-Trunk81
                    OSPF    10   108           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   108           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   108           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   108           D   87.250.239.215  Eth-Trunk1.1
 87.250.226.197/32  OSPF    10   108           D   213.180.213.136 Eth-Trunk81
                    OSPF    10   108           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   108           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   108           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   108           D   87.250.239.215  Eth-Trunk1.1
  87.250.228.28/32  OSPF    10   104           D   213.180.213.136 Eth-Trunk81
 87.250.228.145/32  OSPF    10   106           D   213.180.213.136 Eth-Trunk81
 87.250.228.146/32  OSPF    10   2104          D   213.180.213.136 Eth-Trunk81
 87.250.228.149/32  OSPF    10   7             D   213.180.213.136 Eth-Trunk81
 87.250.228.150/32  OSPF    10   10            D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   10            D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   10            D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   10            D   87.250.239.215  Eth-Trunk1.1
 87.250.228.152/32  OSPF    10   2104          D   213.180.213.136 Eth-Trunk81
 87.250.228.153/32  OSPF    10   2104          D   213.180.213.136 Eth-Trunk81
 87.250.228.167/32  OSPF    10   6             D   213.180.213.136 Eth-Trunk81
 87.250.228.168/32  OSPF    10   104           D   213.180.213.136 Eth-Trunk81
 87.250.228.177/32  OSPF    10   3503          D   213.180.213.136 Eth-Trunk81
 87.250.228.198/32  OSPF    10   10            D   213.180.213.136 Eth-Trunk81
                    OSPF    10   10            D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   10            D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   10            D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   10            D   87.250.239.215  Eth-Trunk1.1
 87.250.228.199/32  OSPF    10   6             D   213.180.213.136 Eth-Trunk81
 87.250.228.224/32  OSPF    10   6             D   213.180.213.136 Eth-Trunk81
 87.250.228.226/32  OSPF    10   6             D   213.180.213.136 Eth-Trunk81
 87.250.228.228/32  OSPF    10   6             D   213.180.213.136 Eth-Trunk81
 87.250.228.230/32  OSPF    10   6             D   213.180.213.136 Eth-Trunk81
 87.250.228.231/32  OSPF    10   6             D   213.180.213.136 Eth-Trunk81
 87.250.228.232/32  OSPF    10   2104          D   213.180.213.136 Eth-Trunk81
 87.250.228.233/32  OSPF    10   6             D   213.180.213.136 Eth-Trunk81
 87.250.228.237/32  OSPF    10   6             D   213.180.213.136 Eth-Trunk81
 87.250.228.238/32  OSPF    10   6             D   213.180.213.136 Eth-Trunk81
 87.250.228.239/32  OSPF    10   65541         D   213.180.213.136 Eth-Trunk81
 87.250.233.131/32  OSPF    10   2006          D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   2006          D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   2006          D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   2006          D   87.250.239.215  Eth-Trunk1.1
 87.250.233.132/32  OSPF    10   1102          D   213.180.213.136 Eth-Trunk81
 87.250.233.133/32  OSPF    10   1006          D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   1006          D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   1006          D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   1006          D   87.250.239.215  Eth-Trunk1.1
 87.250.233.135/32  OSPF    10   2003          D   213.180.213.136 Eth-Trunk81
 87.250.233.136/32  OSPF    10   6             D   213.180.213.136 Eth-Trunk81
                    OSPF    10   6             D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   6             D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   6             D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   6             D   87.250.239.215  Eth-Trunk1.1
 87.250.233.141/32  O_ASE   150  20            D   87.250.239.221  Eth-Trunk4.1
                    O_ASE   150  20            D   87.250.239.217  Eth-Trunk3.1
                    O_ASE   150  20            D   87.250.239.219  Eth-Trunk2.1
                    O_ASE   150  20            D   87.250.239.215  Eth-Trunk1.1
 87.250.233.150/32  O_ASE   150  20            D   213.180.213.136 Eth-Trunk81
 87.250.233.166/32  O_ASE   150  20            D   213.180.213.136 Eth-Trunk81
 87.250.233.190/32  O_ASE   150  20            D   213.180.213.136 Eth-Trunk81
 87.250.233.199/32  OSPF    10   102           D   213.180.213.136 Eth-Trunk81
 87.250.233.200/32  OSPF    10   102           D   213.180.213.136 Eth-Trunk81
 87.250.233.233/32  OSPF    10   6             D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   6             D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   6             D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   6             D   87.250.239.215  Eth-Trunk1.1
 87.250.233.248/32  O_ASE   150  20            D   213.180.213.136 Eth-Trunk81
   87.250.234.0/32  O_ASE   150  20            D   213.180.213.136 Eth-Trunk81
   87.250.234.2/32  OSPF    10   3             D   213.180.213.136 Eth-Trunk81
   87.250.234.8/32  OSPF    10   1102          D   213.180.213.136 Eth-Trunk81
  87.250.234.12/32  OSPF    10   65535         D   93.158.172.227  100GE1/0/31:1.100
  87.250.234.14/32  OSPF    10   1103          D   213.180.213.136 Eth-Trunk81
  87.250.234.16/32  OSPF    10   1102          D   213.180.213.136 Eth-Trunk81
  87.250.234.18/32  OSPF    10   1103          D   213.180.213.136 Eth-Trunk81
  87.250.234.19/32  OSPF    10   65535         D   93.158.172.223  100GE1/0/31:1.50
  87.250.234.21/32  OSPF    10   2             D   213.180.213.136 Eth-Trunk81
  87.250.234.22/32  OSPF    10   1003          D   213.180.213.136 Eth-Trunk81
  87.250.234.41/32  OSPF    10   65544         D   213.180.213.136 Eth-Trunk81
                    OSPF    10   65544         D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   65544         D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   65544         D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   65544         D   87.250.239.215  Eth-Trunk1.1
 87.250.234.121/32  OSPF    10   102           D   213.180.213.136 Eth-Trunk81
 87.250.234.179/32  OSPF    10   3502          D   213.180.213.136 Eth-Trunk81
 87.250.234.234/32  OSPF    10   1002          D   213.180.213.136 Eth-Trunk81
 87.250.234.255/32  OSPF    10   102           D   213.180.213.136 Eth-Trunk81
   87.250.239.0/31  OSPF    10   2007          D   213.180.213.136 Eth-Trunk81
   87.250.239.4/31  OSPF    10   108           D   213.180.213.136 Eth-Trunk81
                    OSPF    10   108           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   108           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   108           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   108           D   87.250.239.215  Eth-Trunk1.1
   87.250.239.6/31  OSPF    10   2011          D   213.180.213.136 Eth-Trunk81
                    OSPF    10   2011          D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   2011          D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   2011          D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   2011          D   87.250.239.215  Eth-Trunk1.1
   87.250.239.8/31  OSPF    10   2011          D   213.180.213.136 Eth-Trunk81
                    OSPF    10   2011          D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   2011          D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   2011          D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   2011          D   87.250.239.215  Eth-Trunk1.1
  87.250.239.10/31  OSPF    10   2011          D   213.180.213.136 Eth-Trunk81
                    OSPF    10   2011          D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   2011          D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   2011          D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   2011          D   87.250.239.215  Eth-Trunk1.1
  87.250.239.12/31  OSPF    10   113           D   213.180.213.136 Eth-Trunk81
                    OSPF    10   113           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   113           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   113           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   113           D   87.250.239.215  Eth-Trunk1.1
  87.250.239.14/31  OSPF    10   2007          D   213.180.213.136 Eth-Trunk81
  87.250.239.16/31  OSPF    10   66541         D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   66541         D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   66541         D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   66541         D   87.250.239.215  Eth-Trunk1.1
  87.250.239.18/31  OSPF    10   108           D   213.180.213.136 Eth-Trunk81
                    OSPF    10   108           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   108           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   108           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   108           D   87.250.239.215  Eth-Trunk1.1
  87.250.239.20/31  OSPF    10   2011          D   213.180.213.136 Eth-Trunk81
                    OSPF    10   2011          D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   2011          D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   2011          D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   2011          D   87.250.239.215  Eth-Trunk1.1
  87.250.239.24/31  OSPF    10   2011          D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   2011          D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   2011          D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   2011          D   87.250.239.215  Eth-Trunk1.1
  87.250.239.26/31  OSPF    10   104           D   213.180.213.136 Eth-Trunk81
  87.250.239.30/31  OSPF    10   1102          D   213.180.213.136 Eth-Trunk81
  87.250.239.32/31  OSPF    10   2008          D   213.180.213.136 Eth-Trunk81
  87.250.239.34/31  OSPF    10   5003          D   213.180.213.136 Eth-Trunk81
  87.250.239.36/31  OSPF    10   202           D   213.180.213.136 Eth-Trunk81
  87.250.239.38/31  OSPF    10   1102          D   213.180.213.136 Eth-Trunk81
  87.250.239.40/31  OSPF    10   2008          D   213.180.213.136 Eth-Trunk81
  87.250.239.42/31  OSPF    10   108           D   213.180.213.136 Eth-Trunk81
                    OSPF    10   108           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   108           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   108           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   108           D   87.250.239.215  Eth-Trunk1.1
  87.250.239.44/31  OSPF    10   2008          D   213.180.213.136 Eth-Trunk81
  87.250.239.50/31  OSPF    10   7             D   213.180.213.136 Eth-Trunk81
                    OSPF    10   7             D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   7             D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   7             D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   7             D   87.250.239.215  Eth-Trunk1.1
  87.250.239.52/31  OSPF    10   4             D   87.250.239.215  Eth-Trunk1.1
  87.250.239.54/31  OSPF    10   10            D   213.180.213.136 Eth-Trunk81
                    OSPF    10   10            D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   10            D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   10            D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   10            D   87.250.239.215  Eth-Trunk1.1
  87.250.239.58/31  OSPF    10   208           D   213.180.213.136 Eth-Trunk81
                    OSPF    10   208           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   208           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   208           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   208           D   87.250.239.215  Eth-Trunk1.1
  87.250.239.62/31  OSPF    10   202           D   213.180.213.136 Eth-Trunk81
  87.250.239.64/31  OSPF    10   202           D   213.180.213.136 Eth-Trunk81
  87.250.239.66/31  OSPF    10   113           D   213.180.213.136 Eth-Trunk81
                    OSPF    10   113           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   113           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   113           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   113           D   87.250.239.215  Eth-Trunk1.1
  87.250.239.68/31  OSPF    10   208           D   213.180.213.136 Eth-Trunk81
                    OSPF    10   208           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   208           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   208           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   208           D   87.250.239.215  Eth-Trunk1.1
  87.250.239.70/31  OSPF    10   4             D   87.250.239.219  Eth-Trunk2.1
  87.250.239.72/31  OSPF    10   208           D   213.180.213.136 Eth-Trunk81
                    OSPF    10   208           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   208           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   208           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   208           D   87.250.239.215  Eth-Trunk1.1
  87.250.239.74/31  OSPF    10   2506          D   213.180.213.136 Eth-Trunk81
                    OSPF    10   2506          D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   2506          D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   2506          D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   2506          D   87.250.239.215  Eth-Trunk1.1
  87.250.239.76/31  OSPF    10   2008          D   213.180.213.136 Eth-Trunk81
                    OSPF    10   2008          D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   2008          D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   2008          D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   2008          D   87.250.239.215  Eth-Trunk1.1
  87.250.239.78/31  OSPF    10   104           D   213.180.213.136 Eth-Trunk81
  87.250.239.80/31  OSPF    10   2008          D   213.180.213.136 Eth-Trunk81
                    OSPF    10   2008          D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   2008          D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   2008          D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   2008          D   87.250.239.215  Eth-Trunk1.1
  87.250.239.82/31  OSPF    10   202           D   213.180.213.136 Eth-Trunk81
  87.250.239.84/31  OSPF    10   2007          D   213.180.213.136 Eth-Trunk81
  87.250.239.86/31  OSPF    10   2008          D   213.180.213.136 Eth-Trunk81
  87.250.239.90/31  OSPF    10   2011          D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   2011          D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   2011          D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   2011          D   87.250.239.215  Eth-Trunk1.1
  87.250.239.92/31  OSPF    10   2011          D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   2011          D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   2011          D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   2011          D   87.250.239.215  Eth-Trunk1.1
  87.250.239.94/31  OSPF    10   8             D   213.180.213.136 Eth-Trunk81
                    OSPF    10   8             D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   8             D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   8             D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   8             D   87.250.239.215  Eth-Trunk1.1
  87.250.239.96/31  OSPF    10   202           D   213.180.213.136 Eth-Trunk81
 87.250.239.100/31  OSPF    10   2011          D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   2011          D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   2011          D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   2011          D   87.250.239.215  Eth-Trunk1.1
 87.250.239.104/31  OSPF    10   113           D   213.180.213.136 Eth-Trunk81
                    OSPF    10   113           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   113           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   113           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   113           D   87.250.239.215  Eth-Trunk1.1
 87.250.239.106/31  OSPF    10   2417          D   213.180.213.136 Eth-Trunk81
 87.250.239.108/31  OSPF    10   4             D   87.250.239.217  Eth-Trunk3.1
 87.250.239.110/31  OSPF    10   2104          D   213.180.213.136 Eth-Trunk81
 87.250.239.112/31  OSPF    10   106           D   213.180.213.136 Eth-Trunk81
                    OSPF    10   106           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   106           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   106           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   106           D   87.250.239.215  Eth-Trunk1.1
 87.250.239.114/31  OSPF    10   202           D   213.180.213.136 Eth-Trunk81
 87.250.239.116/31  OSPF    10   1106          D   213.180.213.136 Eth-Trunk81
                    OSPF    10   1106          D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   1106          D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   1106          D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   1106          D   87.250.239.215  Eth-Trunk1.1
 87.250.239.118/31  OSPF    10   2002          D   213.180.213.136 Eth-Trunk81
 87.250.239.122/31  OSPF    10   4             D   87.250.239.221  Eth-Trunk4.1
 87.250.239.124/31  OSPF    10   106           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   106           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   106           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   106           D   87.250.239.215  Eth-Trunk1.1
 87.250.239.126/31  OSPF    10   202           D   213.180.213.136 Eth-Trunk81
 87.250.239.128/31  OSPF    10   204           D   213.180.213.136 Eth-Trunk81
 87.250.239.132/31  OSPF    10   103           D   213.180.213.136 Eth-Trunk81
 87.250.239.136/31  OSPF    10   208           D   213.180.213.136 Eth-Trunk81
                    OSPF    10   208           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   208           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   208           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   208           D   87.250.239.215  Eth-Trunk1.1
 87.250.239.138/31  OSPF    10   8             D   213.180.213.136 Eth-Trunk81
 87.250.239.140/31  OSPF    10   8             D   213.180.213.136 Eth-Trunk81
 87.250.239.144/29  OSPF    10   10006         D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   10006         D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   10006         D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   10006         D   87.250.239.215  Eth-Trunk1.1
 87.250.239.152/31  OSPF    10   206           D   213.180.213.136 Eth-Trunk81
 87.250.239.154/31  OSPF    10   206           D   213.180.213.136 Eth-Trunk81
 87.250.239.162/31  OSPF    10   18            D   213.180.213.136 Eth-Trunk81
                    OSPF    10   18            D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   18            D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   18            D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   18            D   87.250.239.215  Eth-Trunk1.1
 87.250.239.164/31  OSPF    10   206           D   213.180.213.136 Eth-Trunk81
 87.250.239.166/31  OSPF    10   206           D   213.180.213.136 Eth-Trunk81
 87.250.239.172/31  OSPF    10   8             D   213.180.213.136 Eth-Trunk81
                    OSPF    10   8             D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   8             D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   8             D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   8             D   87.250.239.215  Eth-Trunk1.1
 87.250.239.176/31  OSPF    10   18            D   213.180.213.136 Eth-Trunk81
                    OSPF    10   18            D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   18            D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   18            D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   18            D   87.250.239.215  Eth-Trunk1.1
 87.250.239.178/31  OSPF    10   18            D   213.180.213.136 Eth-Trunk81
                    OSPF    10   18            D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   18            D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   18            D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   18            D   87.250.239.215  Eth-Trunk1.1
 87.250.239.180/31  OSPF    10   18            D   213.180.213.136 Eth-Trunk81
                    OSPF    10   18            D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   18            D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   18            D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   18            D   87.250.239.215  Eth-Trunk1.1
 87.250.239.182/31  OSPF    10   18            D   213.180.213.136 Eth-Trunk81
                    OSPF    10   18            D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   18            D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   18            D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   18            D   87.250.239.215  Eth-Trunk1.1
 87.250.239.184/31  OSPF    10   18            D   213.180.213.136 Eth-Trunk81
                    OSPF    10   18            D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   18            D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   18            D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   18            D   87.250.239.215  Eth-Trunk1.1
 87.250.239.186/31  OSPF    10   2008          D   213.180.213.136 Eth-Trunk81
 87.250.239.188/30  OSPF    10   1102          D   213.180.213.136 Eth-Trunk81
 87.250.239.192/31  OSPF    10   106           D   213.180.213.136 Eth-Trunk81
                    OSPF    10   106           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   106           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   106           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   106           D   87.250.239.215  Eth-Trunk1.1
 87.250.239.194/31  OSPF    10   2011          D   213.180.213.136 Eth-Trunk81
                    OSPF    10   2011          D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   2011          D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   2011          D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   2011          D   87.250.239.215  Eth-Trunk1.1
 87.250.239.196/31  OSPF    10   18            D   213.180.213.136 Eth-Trunk81
                    OSPF    10   18            D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   18            D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   18            D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   18            D   87.250.239.215  Eth-Trunk1.1
 87.250.239.198/31  OSPF    10   18            D   213.180.213.136 Eth-Trunk81
                    OSPF    10   18            D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   18            D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   18            D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   18            D   87.250.239.215  Eth-Trunk1.1
 87.250.239.200/31  OSPF    10   18            D   213.180.213.136 Eth-Trunk81
                    OSPF    10   18            D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   18            D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   18            D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   18            D   87.250.239.215  Eth-Trunk1.1
 87.250.239.202/31  OSPF    10   18            D   213.180.213.136 Eth-Trunk81
                    OSPF    10   18            D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   18            D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   18            D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   18            D   87.250.239.215  Eth-Trunk1.1
 87.250.239.204/31  OSPF    10   18            D   213.180.213.136 Eth-Trunk81
                    OSPF    10   18            D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   18            D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   18            D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   18            D   87.250.239.215  Eth-Trunk1.1
 87.250.239.206/31  OSPF    10   18            D   213.180.213.136 Eth-Trunk81
                    OSPF    10   18            D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   18            D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   18            D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   18            D   87.250.239.215  Eth-Trunk1.1
 87.250.239.210/31  OSPF    10   18            D   213.180.213.136 Eth-Trunk81
                    OSPF    10   18            D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   18            D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   18            D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   18            D   87.250.239.215  Eth-Trunk1.1
 87.250.239.212/31  OSPF    10   18            D   213.180.213.136 Eth-Trunk81
                    OSPF    10   18            D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   18            D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   18            D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   18            D   87.250.239.215  Eth-Trunk1.1
 87.250.239.214/31  Direct  0    0             D   87.250.239.214  Eth-Trunk1.1
 87.250.239.214/32  Direct  0    0             D   127.0.0.1       Eth-Trunk1.1
 87.250.239.216/31  Direct  0    0             D   87.250.239.216  Eth-Trunk3.1
 87.250.239.216/32  Direct  0    0             D   127.0.0.1       Eth-Trunk3.1
 87.250.239.218/31  Direct  0    0             D   87.250.239.218  Eth-Trunk2.1
 87.250.239.218/32  Direct  0    0             D   127.0.0.1       Eth-Trunk2.1
 87.250.239.220/31  Direct  0    0             D   87.250.239.220  Eth-Trunk4.1
 87.250.239.220/32  Direct  0    0             D   127.0.0.1       Eth-Trunk4.1
 87.250.239.222/31  OSPF    10   4             D   87.250.239.215  Eth-Trunk1.1
 87.250.239.224/31  OSPF    10   4             D   87.250.239.217  Eth-Trunk3.1
 87.250.239.226/31  OSPF    10   4             D   87.250.239.221  Eth-Trunk4.1
 87.250.239.228/31  OSPF    10   4             D   87.250.239.219  Eth-Trunk2.1
 87.250.239.230/31  OSPF    10   4             D   87.250.239.219  Eth-Trunk2.1
 87.250.239.232/31  OSPF    10   4             D   87.250.239.215  Eth-Trunk1.1
 87.250.239.234/31  OSPF    10   4             D   87.250.239.217  Eth-Trunk3.1
 87.250.239.244/31  OSPF    10   2008          D   213.180.213.136 Eth-Trunk81
 87.250.239.248/31  OSPF    10   1102          D   213.180.213.136 Eth-Trunk81
 87.250.239.250/31  OSPF    10   2002          D   213.180.213.136 Eth-Trunk81
 87.250.239.252/31  OSPF    10   2002          D   213.180.213.136 Eth-Trunk81
 87.250.239.254/31  OSPF    10   4             D   87.250.239.221  Eth-Trunk4.1
   93.158.160.2/31  OSPF    10   204           D   213.180.213.136 Eth-Trunk81
   93.158.160.6/31  OSPF    10   6             D   213.180.213.136 Eth-Trunk81
  93.158.160.16/31  OSPF    10   2002          D   213.180.213.136 Eth-Trunk81
  93.158.160.34/31  OSPF    10   9             D   213.180.213.136 Eth-Trunk81
  93.158.160.40/31  OSPF    10   1102          D   213.180.213.136 Eth-Trunk81
  93.158.160.60/31  OSPF    10   11002         D   213.180.213.136 Eth-Trunk81
  93.158.160.72/30  OSPF    10   3502          D   213.180.213.136 Eth-Trunk81
  93.158.160.82/31  OSPF    10   106           D   213.180.213.136 Eth-Trunk81
                    OSPF    10   106           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   106           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   106           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   106           D   87.250.239.215  Eth-Trunk1.1
  93.158.160.86/31  OSPF    10   1102          D   213.180.213.136 Eth-Trunk81
  93.158.160.88/31  OSPF    10   6502          D   213.180.213.136 Eth-Trunk81
  93.158.160.90/31  OSPF    10   3503          D   213.180.213.136 Eth-Trunk81
 93.158.160.102/31  OSPF    10   1102          D   213.180.213.136 Eth-Trunk81
 93.158.160.106/31  OSPF    10   2417          D   213.180.213.136 Eth-Trunk81
 93.158.160.124/31  OSPF    10   208           D   213.180.213.136 Eth-Trunk81
                    OSPF    10   208           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   208           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   208           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   208           D   87.250.239.215  Eth-Trunk1.1
 93.158.160.126/31  OSPF    10   208           D   213.180.213.136 Eth-Trunk81
                    OSPF    10   208           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   208           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   208           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   208           D   87.250.239.215  Eth-Trunk1.1
 93.158.160.128/31  OSPF    10   208           D   213.180.213.136 Eth-Trunk81
                    OSPF    10   208           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   208           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   208           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   208           D   87.250.239.215  Eth-Trunk1.1
 93.158.160.130/31  OSPF    10   208           D   213.180.213.136 Eth-Trunk81
                    OSPF    10   208           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   208           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   208           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   208           D   87.250.239.215  Eth-Trunk1.1
 93.158.160.132/31  OSPF    10   208           D   213.180.213.136 Eth-Trunk81
                    OSPF    10   208           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   208           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   208           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   208           D   87.250.239.215  Eth-Trunk1.1
 93.158.160.134/31  OSPF    10   208           D   213.180.213.136 Eth-Trunk81
                    OSPF    10   208           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   208           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   208           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   208           D   87.250.239.215  Eth-Trunk1.1
 93.158.160.136/31  OSPF    10   208           D   213.180.213.136 Eth-Trunk81
                    OSPF    10   208           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   208           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   208           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   208           D   87.250.239.215  Eth-Trunk1.1
 93.158.160.138/31  OSPF    10   208           D   213.180.213.136 Eth-Trunk81
                    OSPF    10   208           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   208           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   208           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   208           D   87.250.239.215  Eth-Trunk1.1
 93.158.160.248/31  OSPF    10   2103          D   213.180.213.136 Eth-Trunk81
 93.158.160.250/31  OSPF    10   202           D   213.180.213.136 Eth-Trunk81
 93.158.160.252/31  OSPF    10   202           D   213.180.213.136 Eth-Trunk81
 93.158.160.254/31  OSPF    10   4003          D   213.180.213.136 Eth-Trunk81
   93.158.172.8/31  OSPF    10   2007          D   213.180.213.136 Eth-Trunk81
  93.158.172.10/31  OSPF    10   104           D   213.180.213.136 Eth-Trunk81
  93.158.172.12/31  OSPF    10   2015          D   213.180.213.136 Eth-Trunk81
  93.158.172.14/31  OSPF    10   2007          D   213.180.213.136 Eth-Trunk81
  93.158.172.16/31  OSPF    10   6             D   213.180.213.136 Eth-Trunk81
  93.158.172.18/31  OSPF    10   10            D   213.180.213.136 Eth-Trunk81
                    OSPF    10   10            D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   10            D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   10            D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   10            D   87.250.239.215  Eth-Trunk1.1
  93.158.172.20/31  OSPF    10   6             D   213.180.213.136 Eth-Trunk81
  93.158.172.22/31  OSPF    10   14            D   213.180.213.136 Eth-Trunk81
  93.158.172.24/31  OSPF    10   6             D   213.180.213.136 Eth-Trunk81
  93.158.172.26/31  OSPF    10   10            D   213.180.213.136 Eth-Trunk81
                    OSPF    10   10            D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   10            D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   10            D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   10            D   87.250.239.215  Eth-Trunk1.1
  93.158.172.36/31  OSPF    10   6             D   213.180.213.136 Eth-Trunk81
  93.158.172.38/31  OSPF    10   6             D   213.180.213.136 Eth-Trunk81
  93.158.172.50/31  OSPF    10   6             D   213.180.213.136 Eth-Trunk81
 93.158.172.174/31  OSPF    10   2011          D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   2011          D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   2011          D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   2011          D   87.250.239.215  Eth-Trunk1.1
 93.158.172.188/31  OSPF    10   2011          D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   2011          D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   2011          D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   2011          D   87.250.239.215  Eth-Trunk1.1
 93.158.172.210/31  OSPF    10   6             D   213.180.213.136 Eth-Trunk81
 93.158.172.212/31  OSPF    10   6             D   213.180.213.136 Eth-Trunk81
 93.158.172.220/31  OSPF    10   65536         D   93.158.172.223  100GE1/0/31:1.50
 93.158.172.222/31  Direct  0    0             D   93.158.172.222  100GE1/0/31:1.50
 93.158.172.222/32  Direct  0    0             D   127.0.0.1       100GE1/0/31:1.50
 93.158.172.224/31  OSPF    10   65536         D   93.158.172.227  100GE1/0/31:1.100
 93.158.172.226/31  Direct  0    0             D   93.158.172.226  100GE1/0/31:1.100
 93.158.172.226/32  Direct  0    0             D   127.0.0.1       100GE1/0/31:1.100
 93.158.172.244/31  OSPF    10   6             D   213.180.213.136 Eth-Trunk81
 93.158.172.252/31  OSPF    10   103           D   213.180.213.136 Eth-Trunk81
   95.108.237.1/32  OSPF    10   100           D   213.180.213.238 Eth-Trunk101
   95.108.237.3/32  OSPF    10   104           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   104           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   104           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   104           D   87.250.239.215  Eth-Trunk1.1
   95.108.237.4/32  OSPF    10   4             D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   4             D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   4             D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   4             D   87.250.239.215  Eth-Trunk1.1
   95.108.237.5/32  OSPF    10   100           D   213.180.213.132 Eth-Trunk103
  95.108.237.10/32  OSPF    10   2             D   87.250.239.221  Eth-Trunk4.1
  95.108.237.14/32  OSPF    10   4             D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   4             D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   4             D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   4             D   87.250.239.215  Eth-Trunk1.1
  95.108.237.19/32  OSPF    10   2             D   87.250.239.217  Eth-Trunk3.1
  95.108.237.20/32  OSPF    10   2             D   87.250.239.215  Eth-Trunk1.1
  95.108.237.27/32  OSPF    10   100           D   213.180.213.204 Eth-Trunk105
  95.108.237.30/32  OSPF    10   100           D   213.180.213.200 Eth-Trunk104
  95.108.237.32/32  OSPF    10   104           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   104           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   104           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   104           D   87.250.239.215  Eth-Trunk1.1
  95.108.237.38/32  OSPF    10   104           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   104           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   104           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   104           D   87.250.239.215  Eth-Trunk1.1
  95.108.237.39/32  OSPF    10   100           D   213.180.213.146 Eth-Trunk111
  95.108.237.43/32  Direct  0    0             D   127.0.0.1       LoopBack0
  95.108.237.47/32  OSPF    10   2             D   87.250.239.219  Eth-Trunk2.1
  95.108.237.48/32  OSPF    10   4             D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   4             D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   4             D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   4             D   87.250.239.215  Eth-Trunk1.1
  95.108.237.49/32  OSPF    10   104           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   104           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   104           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   104           D   87.250.239.215  Eth-Trunk1.1
  95.108.237.57/32  OSPF    10   104           D   213.180.213.136 Eth-Trunk81
  95.108.237.58/32  OSPF    10   104           D   213.180.213.136 Eth-Trunk81
  95.108.237.65/32  OSPF    10   2011          D   213.180.213.136 Eth-Trunk81
  95.108.237.76/32  OSPF    10   104           D   213.180.213.136 Eth-Trunk81
  95.108.237.78/32  OSPF    10   104           D   213.180.213.136 Eth-Trunk81
  95.108.237.96/32  OSPF    10   1002          D   213.180.213.136 Eth-Trunk81
 95.108.237.100/32  O_ASE   150  20            D   213.180.213.136 Eth-Trunk81
 95.108.237.141/32  OSPF    10   104           D   213.180.213.136 Eth-Trunk81
 95.108.237.142/32  OSPF    10   104           D   213.180.213.136 Eth-Trunk81
 95.108.237.171/32  OSPF    10   104           D   213.180.213.136 Eth-Trunk81
 95.108.237.172/32  OSPF    10   104           D   213.180.213.136 Eth-Trunk81
 95.108.237.179/32  OSPF    10   4             D   213.180.213.136 Eth-Trunk81
 95.108.237.253/32  OSPF    10   8             D   213.180.213.136 Eth-Trunk81
                    OSPF    10   8             D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   8             D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   8             D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   8             D   87.250.239.215  Eth-Trunk1.1
  100.43.92.159/32  OSPF    10   16502         D   213.180.213.136 Eth-Trunk81
      127.0.0.0/8   Direct  0    0             D   127.0.0.1       InLoopBack0
      127.0.0.1/32  Direct  0    0             D   127.0.0.1       InLoopBack0
127.255.255.255/32  Direct  0    0             D   127.0.0.1       InLoopBack0
  141.8.136.128/32  OSPF    10   2503          D   213.180.213.136 Eth-Trunk81
  141.8.136.129/32  OSPF    10   2502          D   213.180.213.136 Eth-Trunk81
  141.8.136.227/32  OSPF    10   2011          D   213.180.213.136 Eth-Trunk81
                    OSPF    10   2011          D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   2011          D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   2011          D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   2011          D   87.250.239.215  Eth-Trunk1.1
  141.8.136.239/32  OSPF    10   2007          D   213.180.213.136 Eth-Trunk81
  141.8.136.255/32  OSPF    10   2017          D   213.180.213.136 Eth-Trunk81
  141.8.140.160/32  OSPF    10   2009          D   213.180.213.136 Eth-Trunk81
  141.8.140.161/32  OSPF    10   2009          D   213.180.213.136 Eth-Trunk81
  141.8.140.162/32  OSPF    10   2009          D   213.180.213.136 Eth-Trunk81
  141.8.140.163/32  OSPF    10   2009          D   213.180.213.136 Eth-Trunk81
  141.8.140.164/32  OSPF    10   2009          D   213.180.213.136 Eth-Trunk81
  141.8.140.165/32  OSPF    10   2009          D   213.180.213.136 Eth-Trunk81
     172.16.6.0/32  ISIS-L2 15   210600        D   10.255.0.154    Eth-Trunk161
  172.16.10.160/32  OSPF    10   1008          D   213.180.213.136 Eth-Trunk81
                    OSPF    10   1008          D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   1008          D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   1008          D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   1008          D   87.250.239.215  Eth-Trunk1.1
  213.180.213.0/31  OSPF    10   2503          D   213.180.213.136 Eth-Trunk81
  213.180.213.2/31  OSPF    10   3502          D   213.180.213.136 Eth-Trunk81
  213.180.213.4/31  OSPF    10   200           D   213.180.213.132 Eth-Trunk103
  213.180.213.6/31  OSPF    10   104           D   213.180.213.136 Eth-Trunk81
  213.180.213.8/31  OSPF    10   200           D   213.180.213.132 Eth-Trunk103
 213.180.213.10/31  OSPF    10   202           D   213.180.213.136 Eth-Trunk81
 213.180.213.12/31  OSPF    10   104           D   213.180.213.136 Eth-Trunk81
 213.180.213.14/31  OSPF    10   204           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   204           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   204           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   204           D   87.250.239.215  Eth-Trunk1.1
 213.180.213.16/31  OSPF    10   4006          D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   4006          D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   4006          D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   4006          D   87.250.239.215  Eth-Trunk1.1
 213.180.213.18/31  OSPF    10   2011          D   213.180.213.136 Eth-Trunk81
                    OSPF    10   2011          D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   2011          D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   2011          D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   2011          D   87.250.239.215  Eth-Trunk1.1
 213.180.213.20/31  OSPF    10   2104          D   213.180.213.136 Eth-Trunk81
 213.180.213.22/31  OSPF    10   2104          D   213.180.213.136 Eth-Trunk81
 213.180.213.26/31  OSPF    10   103           D   213.180.213.136 Eth-Trunk81
 213.180.213.32/31  OSPF    10   5002          D   213.180.213.136 Eth-Trunk81
 213.180.213.34/31  OSPF    10   2506          D   213.180.213.136 Eth-Trunk81
 213.180.213.38/31  OSPF    10   2104          D   213.180.213.136 Eth-Trunk81
 213.180.213.56/31  OSPF    10   2011          D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   2011          D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   2011          D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   2011          D   87.250.239.215  Eth-Trunk1.1
 213.180.213.68/31  OSPF    10   8             D   213.180.213.136 Eth-Trunk81
                    OSPF    10   8             D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   8             D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   8             D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   8             D   87.250.239.215  Eth-Trunk1.1
 213.180.213.88/31  OSPF    10   106           D   213.180.213.136 Eth-Trunk81
                    OSPF    10   106           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   106           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   106           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   106           D   87.250.239.215  Eth-Trunk1.1
 213.180.213.90/31  OSPF    10   3003          D   213.180.213.136 Eth-Trunk81
 213.180.213.92/31  OSPF    10   3002          D   213.180.213.136 Eth-Trunk81
 213.180.213.94/31  OSPF    10   6502          D   213.180.213.136 Eth-Trunk81
 213.180.213.96/31  OSPF    10   8502          D   213.180.213.136 Eth-Trunk81
213.180.213.104/31  OSPF    10   6503          D   213.180.213.136 Eth-Trunk81
213.180.213.120/31  OSPF    10   5002          D   213.180.213.136 Eth-Trunk81
213.180.213.124/31  OSPF    10   2007          D   213.180.213.136 Eth-Trunk81
213.180.213.128/31  OSPF    10   6503          D   213.180.213.136 Eth-Trunk81
213.180.213.130/31  OSPF    10   204           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   204           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   204           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   204           D   87.250.239.215  Eth-Trunk1.1
213.180.213.132/31  Direct  0    0             D   213.180.213.133 Eth-Trunk103
213.180.213.133/32  Direct  0    0             D   127.0.0.1       Eth-Trunk103
213.180.213.134/31  OSPF    10   6             D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   6             D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   6             D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   6             D   87.250.239.215  Eth-Trunk1.1
213.180.213.136/31  Direct  0    0             D   213.180.213.137 Eth-Trunk81
213.180.213.137/32  Direct  0    0             D   127.0.0.1       Eth-Trunk81
213.180.213.138/31  OSPF    10   1006          D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   1006          D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   1006          D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   1006          D   87.250.239.215  Eth-Trunk1.1
213.180.213.140/31  OSPF    10   204           D   213.180.213.136 Eth-Trunk81
213.180.213.142/31  OSPF    10   2007          D   213.180.213.136 Eth-Trunk81
213.180.213.144/31  OSPF    10   104           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   104           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   104           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   104           D   87.250.239.215  Eth-Trunk1.1
213.180.213.146/31  Direct  0    0             D   213.180.213.147 Eth-Trunk111
213.180.213.147/32  Direct  0    0             D   127.0.0.1       Eth-Trunk111
213.180.213.162/31  OSPF    10   2104          D   213.180.213.136 Eth-Trunk81
213.180.213.164/31  OSPF    10   2104          D   213.180.213.136 Eth-Trunk81
213.180.213.166/31  OSPF    10   2104          D   213.180.213.136 Eth-Trunk81
213.180.213.168/31  OSPF    10   104           D   213.180.213.136 Eth-Trunk81
213.180.213.170/31  OSPF    10   108           D   213.180.213.136 Eth-Trunk81
                    OSPF    10   108           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   108           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   108           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   108           D   87.250.239.215  Eth-Trunk1.1
213.180.213.172/31  OSPF    10   104           D   213.180.213.136 Eth-Trunk81
213.180.213.174/31  OSPF    10   108           D   213.180.213.136 Eth-Trunk81
                    OSPF    10   108           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   108           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   108           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   108           D   87.250.239.215  Eth-Trunk1.1
213.180.213.178/31  OSPF    10   2015          D   213.180.213.136 Eth-Trunk81
213.180.213.188/30  OSPF    10   1102          D   213.180.213.136 Eth-Trunk81
213.180.213.192/31  OSPF    10   16502         D   213.180.213.136 Eth-Trunk81
213.180.213.194/31  OSPF    10   2107          D   213.180.213.136 Eth-Trunk81
213.180.213.196/31  OSPF    10   202           D   213.180.213.136 Eth-Trunk81
213.180.213.198/31  OSPF    10   200           D   213.180.213.200 Eth-Trunk104
213.180.213.200/31  Direct  0    0             D   213.180.213.201 Eth-Trunk104
213.180.213.201/32  Direct  0    0             D   127.0.0.1       Eth-Trunk104
213.180.213.202/31  OSPF    10   200           D   213.180.213.204 Eth-Trunk105
213.180.213.204/31  Direct  0    0             D   213.180.213.205 Eth-Trunk105
213.180.213.205/32  Direct  0    0             D   127.0.0.1       Eth-Trunk105
213.180.213.206/31  OSPF    10   204           D   213.180.213.136 Eth-Trunk81
213.180.213.208/31  OSPF    10   104           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   104           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   104           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   104           D   87.250.239.215  Eth-Trunk1.1
213.180.213.210/31  OSPF    10   104           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   104           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   104           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   104           D   87.250.239.215  Eth-Trunk1.1
213.180.213.212/31  OSPF    10   2104          D   213.180.213.136 Eth-Trunk81
213.180.213.220/31  OSPF    10   104           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   104           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   104           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   104           D   87.250.239.215  Eth-Trunk1.1
213.180.213.222/31  OSPF    10   104           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   104           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   104           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   104           D   87.250.239.215  Eth-Trunk1.1
213.180.213.224/31  OSPF    10   204           D   213.180.213.136 Eth-Trunk81
213.180.213.226/31  OSPF    10   104           D   213.180.213.136 Eth-Trunk81
213.180.213.228/31  OSPF    10   104           D   213.180.213.136 Eth-Trunk81
213.180.213.230/31  OSPF    10   104           D   213.180.213.136 Eth-Trunk81
213.180.213.232/31  OSPF    10   104           D   213.180.213.136 Eth-Trunk81
213.180.213.234/31  OSPF    10   204           D   213.180.213.136 Eth-Trunk81
213.180.213.236/31  OSPF    10   204           D   213.180.213.136 Eth-Trunk81
213.180.213.238/31  Direct  0    0             D   213.180.213.239 Eth-Trunk101
213.180.213.239/32  Direct  0    0             D   127.0.0.1       Eth-Trunk101
213.180.213.240/31  OSPF    10   200           D   213.180.213.238 Eth-Trunk101
213.180.213.242/31  OSPF    10   104           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   104           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   104           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   104           D   87.250.239.215  Eth-Trunk1.1
213.180.213.244/31  OSPF    10   104           D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   104           D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   104           D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   104           D   87.250.239.215  Eth-Trunk1.1
213.180.213.248/31  OSPF    10   10            D   213.180.213.136 Eth-Trunk81
                    OSPF    10   10            D   87.250.239.221  Eth-Trunk4.1
                    OSPF    10   10            D   87.250.239.217  Eth-Trunk3.1
                    OSPF    10   10            D   87.250.239.219  Eth-Trunk2.1
                    OSPF    10   10            D   87.250.239.215  Eth-Trunk1.1
213.180.213.252/31  OSPF    10   1102          D   213.180.213.136 Eth-Trunk81
255.255.255.255/32  Direct  0    0             D   127.0.0.1       InLoopBack0
    """
    cmd = "dis ip routing-table"
    host = "myt-e2.yndx.net"
    version = """
Huawei Versatile Routing Platform Software
VRP (R) software, Version 8.191 (CE12800 V200R019C10SPC800)
Copyright (C) 2012-2020 Huawei Technologies Co., Ltd.
HUAWEI CE12804 uptime is 222 days, 0 hour, 22 minutes
Patch Version: V200R019SPH007

BKP  version information:
1.PCB      Version  : DE01BAK04A VER C
2.Board    Type     : CE-BAK04A 
3.MPU Slot Quantity : 2
4.LPU Slot Quantity : 4
5.SFU Slot Quantity : 6

MPU(Master) 5 : uptime is  222 days, 0 hour, 21 minutes
        StartupTime 2021/04/02   12:16:05+03:00
Memory     Size     : 16384 M bytes
Flash      Size     : 4096 M bytes
MPU version information:                             
1.PCB      Version  : CE01MPUB VER B
2.MAB      Version  : 1
3.Board    Type     : CE-MPUB
4.CPLD1    Version  : 270
5.BIOS     Version  : 1102
 
MPU(Slave) 6 : uptime is  222 days, 0 hour, 21 minutes
        StartupTime 2021/04/02   12:16:11+03:00
Memory     Size     : 16384 M bytes
Flash      Size     : 4096 M bytes
MPU version information:                             
1.PCB      Version  : CE01MPUB VER B
2.MAB      Version  : 1
3.Board    Type     : CE-MPUB
4.CPLD1    Version  : 270
5.BIOS     Version  : 1102
 
LPU 1 : uptime is 222 days, 0 hour, 14 minutes
        StartupTime 2021/04/02   12:22:53+03:00
Memory     Size     : 4096 M bytes
Flash      Size     : 128  M bytes
LPU version information:
1.PCB      Version  : CEL36CQFD VER A
2.MAB      Version  : 1
3.Board    Type     : CE-L36CQ-FD
4.CPLD1    Version  : 104
5.CPLD2    Version  : 104
6.BIOS     Version  : 205

LPU 2 : uptime is 222 days, 0 hour, 15 minutes
        StartupTime 2021/04/02   12:22:09+03:00
Memory     Size     : 4096 M bytes
Flash      Size     : 128  M bytes
LPU version information:
1.PCB      Version  : CEL36CQFD VER A
2.MAB      Version  : 1
3.Board    Type     : CE-L36CQ-FD
4.CPLD1    Version  : 104
5.CPLD2    Version  : 104
6.BIOS     Version  : 205

SFU 9 : uptime is 222 days, 0 hour, 21 minutes
        StartupTime 2021/04/02   12:16:37+03:00
Memory     Size     : 512 M bytes
Flash      Size     : 64  M bytes
SFU version information:
1.PCB      Version  : CESFU04G VER A
2.MAB      Version  : 1
3.Board    Type     : CE-SFU04G
4.CPLD1    Version  : 101
5.BIOS     Version  : 439

SFU 10 : uptime is 222 days, 0 hour, 21 minutes
        StartupTime 2021/04/02   12:16:37+03:00
Memory     Size     : 512 M bytes
Flash      Size     : 64  M bytes
SFU version information:
1.PCB      Version  : CESFU04G VER A
2.MAB      Version  : 1
3.Board    Type     : CE-SFU04G
4.CPLD1    Version  : 101
5.BIOS     Version  : 439

SFU 11 : uptime is 222 days, 0 hour, 21 minutes
        StartupTime 2021/04/02   12:16:37+03:00
Memory     Size     : 512 M bytes
Flash      Size     : 64  M bytes
SFU version information:
1.PCB      Version  : CESFU04G VER A
2.MAB      Version  : 1
3.Board    Type     : CE-SFU04G
4.CPLD1    Version  : 101
5.BIOS     Version  : 439

SFU 12 : uptime is 222 days, 0 hour, 21 minutes
        StartupTime 2021/04/02   12:16:37+03:00
Memory     Size     : 512 M bytes
Flash      Size     : 64  M bytes
SFU version information:
1.PCB      Version  : CESFU04G VER A
2.MAB      Version  : 1
3.Board    Type     : CE-SFU04G
4.CPLD1    Version  : 101
5.BIOS     Version  : 439

SFU 13 : uptime is 222 days, 0 hour, 21 minutes
        StartupTime 2021/04/02   12:16:37+03:00
Memory     Size     : 512 M bytes
Flash      Size     : 64  M bytes
SFU version information:
1.PCB      Version  : CESFU04G VER A
2.MAB      Version  : 1
3.Board    Type     : CE-SFU04G
4.CPLD1    Version  : 101
5.BIOS     Version  : 439

CMU(Master) 7 : uptime is 220 days, 17 hours, 16 minutes
        StartupTime 2021/04/02   15:16:16+03:00
Memory     Size     : 128 M bytes
Flash      Size     : 32  M bytes
CMU version information:
1.PCB      Version  : DE01CMUA VER B
2.MAB      Version  : 1
3.Board    Type     : CE-CMUA
4.CPLD1    Version  : 104
5.BIOS     Version  : 127

CMU(Slave) 8 : uptime is 221 days, 3 hours, 1 minute
        StartupTime 2021/04/02   15:16:16+03:00
Memory     Size     : 128 M bytes
Flash      Size     : 32  M bytes
CMU version information:
1.PCB      Version  : DE01CMUA VER B
2.MAB      Version  : 1
3.Board    Type     : CE-CMUA
4.CPLD1    Version  : 104
5.BIOS     Version  : 127
    """
    result = [
        {
            "prefix": "5.45.200.24/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "6502",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "5.45.247.180/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "6502",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "10.255.0.1/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1400",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.2/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "200",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.5/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "400",
            "flags": "D",
            "nh": "10.255.0.131",
            "iface": "Eth-Trunk4.10",
        },
        {
            "prefix": "10.255.0.6/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "200",
            "flags": "D",
            "nh": "10.255.0.157",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.0.8/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "200",
            "flags": "D",
            "nh": "10.255.0.139",
            "iface": "Eth-Trunk1.10",
        },
        {
            "prefix": "10.255.0.9/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1200",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.10/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "200",
            "flags": "D",
            "nh": "10.255.0.131",
            "iface": "Eth-Trunk4.10",
        },
        {
            "prefix": "10.255.0.11/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1000",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.12/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1300",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.13/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1300",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.14/32",
            "proto": "Direct",
            "pref": "0",
            "cost": "0",
            "flags": "D",
            "nh": "127.0.0.1",
            "iface": "LoopBack10",
        },
        {
            "prefix": "10.255.0.15/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "2000",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.16/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "2000",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.17/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "2000",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.18/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "200",
            "flags": "D",
            "nh": "10.255.0.149",
            "iface": "Eth-Trunk2.10",
        },
        {
            "prefix": "10.255.0.19/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "2000",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.20/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "2000",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.21/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "2000",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.22/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "210600",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.30/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "16777814",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.34/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "600",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.35/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1400",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.36/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1400",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.37/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "16778614",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.41/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1400",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.42/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1400",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.43/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1400",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.44/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1400",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.45/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1400",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.46/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1400",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.52/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1400",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.53/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "210600",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.55/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "210600",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.56/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1000",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.59/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1600",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.61/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1400",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.63/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1400",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.64/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1400",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.65/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1400",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.66/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1400",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.67/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "210600",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.68/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "600",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.69/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1400",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.71/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "10600",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.75/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "600",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.99/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "600",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.100/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "100200",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.104/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "10600",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.130/31",
            "proto": "Direct",
            "pref": "0",
            "cost": "0",
            "flags": "D",
            "nh": "10.255.0.130",
            "iface": "Eth-Trunk4.10",
        },
        {
            "prefix": "10.255.0.130/32",
            "proto": "Direct",
            "pref": "0",
            "cost": "0",
            "flags": "D",
            "nh": "127.0.0.1",
            "iface": "Eth-Trunk4.10",
        },
        {
            "prefix": "10.255.0.138/31",
            "proto": "Direct",
            "pref": "0",
            "cost": "0",
            "flags": "D",
            "nh": "10.255.0.138",
            "iface": "Eth-Trunk1.10",
        },
        {
            "prefix": "10.255.0.138/32",
            "proto": "Direct",
            "pref": "0",
            "cost": "0",
            "flags": "D",
            "nh": "127.0.0.1",
            "iface": "Eth-Trunk1.10",
        },
        {
            "prefix": "10.255.0.146/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "600",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.148/31",
            "proto": "Direct",
            "pref": "0",
            "cost": "0",
            "flags": "D",
            "nh": "10.255.0.148",
            "iface": "Eth-Trunk2.10",
        },
        {
            "prefix": "10.255.0.148/32",
            "proto": "Direct",
            "pref": "0",
            "cost": "0",
            "flags": "D",
            "nh": "127.0.0.1",
            "iface": "Eth-Trunk2.10",
        },
        {
            "prefix": "10.255.0.150/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1000",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.152/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1200",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.154/31",
            "proto": "Direct",
            "pref": "0",
            "cost": "0",
            "flags": "D",
            "nh": "10.255.0.155",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.155/32",
            "proto": "Direct",
            "pref": "0",
            "cost": "0",
            "flags": "D",
            "nh": "127.0.0.1",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.156/31",
            "proto": "Direct",
            "pref": "0",
            "cost": "0",
            "flags": "D",
            "nh": "10.255.0.156",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.0.156/32",
            "proto": "Direct",
            "pref": "0",
            "cost": "0",
            "flags": "D",
            "nh": "127.0.0.1",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.0.158/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "600",
            "flags": "D",
            "nh": "10.255.0.131",
            "iface": "Eth-Trunk4.10",
        },
        {
            "prefix": "10.255.0.160/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1700",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.162/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1800",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.164/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1400",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.166/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1800",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.170/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1400",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.172/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "600",
            "flags": "D",
            "nh": "10.255.0.131",
            "iface": "Eth-Trunk4.10",
        },
        {
            "prefix": "10.255.0.174/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "600",
            "flags": "D",
            "nh": "10.255.0.131",
            "iface": "Eth-Trunk4.10",
        },
        {
            "prefix": "10.255.0.176/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "600",
            "flags": "D",
            "nh": "10.255.0.131",
            "iface": "Eth-Trunk4.10",
        },
        {
            "prefix": "10.255.0.182/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1400",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.190/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "600",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.194/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1800",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.196/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "600",
            "flags": "D",
            "nh": "10.255.0.131",
            "iface": "Eth-Trunk4.10",
        },
        {
            "prefix": "10.255.0.204/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1400",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.210/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1600",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.212/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1000600",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.224/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1800",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.226/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1400",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.228/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1800",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.232/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1400",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.234/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1800",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.236/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1400",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.238/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1800",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.240/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1400",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.248/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "600",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.250/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1300",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.252/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1000",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.1.0/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "2000",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.1.2/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1700",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.1.4/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "2000",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.1.6/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1700",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.1.220/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "2400",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.1.222/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "2400",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.1.224/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "2400",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.1.226/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "2400",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.1.228/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "2400",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.1.230/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "2400",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.1.232/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "2000",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.1.234/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "2000",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.1.236/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "2000",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.1.238/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "2000",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.1.240/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "2000",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.1.242/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "2000",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.2.8/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1800",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.2.12/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1800",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.2.16/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1800",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.2.18/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1800",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.2.20/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "2200",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.2.22/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "2200",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.2.24/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1800",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.2.36/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1800",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.2.192/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1800",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.2.194/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1800",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.2.198/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "2200",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.2.202/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "2200",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.2.204/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "2200",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.2.224/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "2200",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.2.226/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1800",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.3.0/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1000",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.3.26/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "100200",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.3.60/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "210600",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.3.66/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "11000",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.3.68/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "410600",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.3.70/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "2200",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.3.72/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1800",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.3.76/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "210600",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.3.78/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "20600",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.3.80/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "11000",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.3.90/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1400",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.3.94/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "1400",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.3.104/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "210610",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.3.108/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "2000",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.3.110/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "600",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.3.112/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "210600",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.3.114/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "410600",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.3.116/31",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "210600",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "87.250.226.99/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "8",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.226.122/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "13",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.226.134/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "65643",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.226.135/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "108",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.226.136/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "108",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.226.141/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "108",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.226.142/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "108",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.226.143/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "1008",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.226.155/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "10",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.226.156/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "10",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.226.157/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "10",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.226.158/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "10",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.226.159/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "10",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.226.160/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "10",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.226.162/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "10",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.226.194/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "108",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.226.195/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "108",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.226.196/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "108",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.226.197/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "108",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.228.28/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "104",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.228.145/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "106",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.228.146/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2104",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.228.149/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "7",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.228.150/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "10",
            "flags": "D",
            "nh": "87.250.239.221",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "87.250.228.152/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2104",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.228.153/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2104",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.228.167/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "6",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.228.168/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "104",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.228.177/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "3503",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.228.198/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "10",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.228.199/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "6",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.228.224/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "6",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.228.226/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "6",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.228.228/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "6",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.228.230/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "6",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.228.231/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "6",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.228.232/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2104",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.228.233/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "6",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.228.237/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "6",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.228.238/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "6",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.228.239/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "65541",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.233.131/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2006",
            "flags": "D",
            "nh": "87.250.239.221",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "87.250.233.132/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "1102",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.233.133/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "1006",
            "flags": "D",
            "nh": "87.250.239.221",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "87.250.233.135/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2003",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.233.136/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "6",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.233.141/32",
            "proto": "O_ASE",
            "pref": "150",
            "cost": "20",
            "flags": "D",
            "nh": "87.250.239.221",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "87.250.233.150/32",
            "proto": "O_ASE",
            "pref": "150",
            "cost": "20",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.233.166/32",
            "proto": "O_ASE",
            "pref": "150",
            "cost": "20",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.233.190/32",
            "proto": "O_ASE",
            "pref": "150",
            "cost": "20",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.233.199/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "102",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.233.200/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "102",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.233.233/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "6",
            "flags": "D",
            "nh": "87.250.239.221",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "87.250.233.248/32",
            "proto": "O_ASE",
            "pref": "150",
            "cost": "20",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.234.0/32",
            "proto": "O_ASE",
            "pref": "150",
            "cost": "20",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.234.2/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "3",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.234.8/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "1102",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.234.12/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "65535",
            "flags": "D",
            "nh": "93.158.172.227",
            "iface": "100GE1/0/31:1.100",
        },
        {
            "prefix": "87.250.234.14/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "1103",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.234.16/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "1102",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.234.18/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "1103",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.234.19/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "65535",
            "flags": "D",
            "nh": "93.158.172.223",
            "iface": "100GE1/0/31:1.50",
        },
        {
            "prefix": "87.250.234.21/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.234.22/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "1003",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.234.41/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "65544",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.234.121/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "102",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.234.179/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "3502",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.234.234/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "1002",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.234.255/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "102",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.0/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2007",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.4/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "108",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.6/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2011",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.8/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2011",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.10/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2011",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.12/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "113",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.14/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2007",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.16/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "66541",
            "flags": "D",
            "nh": "87.250.239.221",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "87.250.239.18/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "108",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.20/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2011",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.24/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2011",
            "flags": "D",
            "nh": "87.250.239.221",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "87.250.239.26/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "104",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.30/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "1102",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.32/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2008",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.34/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "5003",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.36/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "202",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.38/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "1102",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.40/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2008",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.42/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "108",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.44/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2008",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.50/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "7",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.52/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "4",
            "flags": "D",
            "nh": "87.250.239.215",
            "iface": "Eth-Trunk1.1",
        },
        {
            "prefix": "87.250.239.54/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "10",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.58/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "208",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.62/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "202",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.64/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "202",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.66/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "113",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.68/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "208",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.70/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "4",
            "flags": "D",
            "nh": "87.250.239.219",
            "iface": "Eth-Trunk2.1",
        },
        {
            "prefix": "87.250.239.72/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "208",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.74/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2506",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.76/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2008",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.78/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "104",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.80/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2008",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.82/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "202",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.84/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2007",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.86/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2008",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.90/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2011",
            "flags": "D",
            "nh": "87.250.239.221",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "87.250.239.92/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2011",
            "flags": "D",
            "nh": "87.250.239.221",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "87.250.239.94/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "8",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.96/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "202",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.100/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2011",
            "flags": "D",
            "nh": "87.250.239.221",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "87.250.239.104/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "113",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.106/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2417",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.108/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "4",
            "flags": "D",
            "nh": "87.250.239.217",
            "iface": "Eth-Trunk3.1",
        },
        {
            "prefix": "87.250.239.110/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2104",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.112/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "106",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.114/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "202",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.116/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "1106",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.118/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2002",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.122/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "4",
            "flags": "D",
            "nh": "87.250.239.221",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "87.250.239.124/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "106",
            "flags": "D",
            "nh": "87.250.239.221",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "87.250.239.126/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "202",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.128/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "204",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.132/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "103",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.136/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "208",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.138/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "8",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.140/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "8",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.144/29",
            "proto": "OSPF",
            "pref": "10",
            "cost": "10006",
            "flags": "D",
            "nh": "87.250.239.221",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "87.250.239.152/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "206",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.154/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "206",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.162/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "18",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.164/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "206",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.166/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "206",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.172/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "8",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.176/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "18",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.178/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "18",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.180/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "18",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.182/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "18",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.184/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "18",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.186/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2008",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.188/30",
            "proto": "OSPF",
            "pref": "10",
            "cost": "1102",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.192/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "106",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.194/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2011",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.196/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "18",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.198/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "18",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.200/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "18",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.202/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "18",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.204/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "18",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.206/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "18",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.210/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "18",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.212/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "18",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.214/31",
            "proto": "Direct",
            "pref": "0",
            "cost": "0",
            "flags": "D",
            "nh": "87.250.239.214",
            "iface": "Eth-Trunk1.1",
        },
        {
            "prefix": "87.250.239.214/32",
            "proto": "Direct",
            "pref": "0",
            "cost": "0",
            "flags": "D",
            "nh": "127.0.0.1",
            "iface": "Eth-Trunk1.1",
        },
        {
            "prefix": "87.250.239.216/31",
            "proto": "Direct",
            "pref": "0",
            "cost": "0",
            "flags": "D",
            "nh": "87.250.239.216",
            "iface": "Eth-Trunk3.1",
        },
        {
            "prefix": "87.250.239.216/32",
            "proto": "Direct",
            "pref": "0",
            "cost": "0",
            "flags": "D",
            "nh": "127.0.0.1",
            "iface": "Eth-Trunk3.1",
        },
        {
            "prefix": "87.250.239.218/31",
            "proto": "Direct",
            "pref": "0",
            "cost": "0",
            "flags": "D",
            "nh": "87.250.239.218",
            "iface": "Eth-Trunk2.1",
        },
        {
            "prefix": "87.250.239.218/32",
            "proto": "Direct",
            "pref": "0",
            "cost": "0",
            "flags": "D",
            "nh": "127.0.0.1",
            "iface": "Eth-Trunk2.1",
        },
        {
            "prefix": "87.250.239.220/31",
            "proto": "Direct",
            "pref": "0",
            "cost": "0",
            "flags": "D",
            "nh": "87.250.239.220",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "87.250.239.220/32",
            "proto": "Direct",
            "pref": "0",
            "cost": "0",
            "flags": "D",
            "nh": "127.0.0.1",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "87.250.239.222/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "4",
            "flags": "D",
            "nh": "87.250.239.215",
            "iface": "Eth-Trunk1.1",
        },
        {
            "prefix": "87.250.239.224/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "4",
            "flags": "D",
            "nh": "87.250.239.217",
            "iface": "Eth-Trunk3.1",
        },
        {
            "prefix": "87.250.239.226/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "4",
            "flags": "D",
            "nh": "87.250.239.221",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "87.250.239.228/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "4",
            "flags": "D",
            "nh": "87.250.239.219",
            "iface": "Eth-Trunk2.1",
        },
        {
            "prefix": "87.250.239.230/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "4",
            "flags": "D",
            "nh": "87.250.239.219",
            "iface": "Eth-Trunk2.1",
        },
        {
            "prefix": "87.250.239.232/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "4",
            "flags": "D",
            "nh": "87.250.239.215",
            "iface": "Eth-Trunk1.1",
        },
        {
            "prefix": "87.250.239.234/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "4",
            "flags": "D",
            "nh": "87.250.239.217",
            "iface": "Eth-Trunk3.1",
        },
        {
            "prefix": "87.250.239.244/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2008",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.248/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "1102",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.250/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2002",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.252/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2002",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.254/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "4",
            "flags": "D",
            "nh": "87.250.239.221",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "93.158.160.2/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "204",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.6/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "6",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.16/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2002",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.34/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "9",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.40/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "1102",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.60/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "11002",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.72/30",
            "proto": "OSPF",
            "pref": "10",
            "cost": "3502",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.82/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "106",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.86/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "1102",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.88/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "6502",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.90/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "3503",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.102/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "1102",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.106/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2417",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.124/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "208",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.126/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "208",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.128/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "208",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.130/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "208",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.132/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "208",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.134/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "208",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.136/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "208",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.138/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "208",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.248/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2103",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.250/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "202",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.252/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "202",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.254/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "4003",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.172.8/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2007",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.172.10/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "104",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.172.12/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2015",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.172.14/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2007",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.172.16/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "6",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.172.18/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "10",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.172.20/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "6",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.172.22/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "14",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.172.24/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "6",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.172.26/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "10",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.172.36/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "6",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.172.38/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "6",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.172.50/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "6",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.172.174/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2011",
            "flags": "D",
            "nh": "87.250.239.221",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "93.158.172.188/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2011",
            "flags": "D",
            "nh": "87.250.239.221",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "93.158.172.210/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "6",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.172.212/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "6",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.172.220/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "65536",
            "flags": "D",
            "nh": "93.158.172.223",
            "iface": "100GE1/0/31:1.50",
        },
        {
            "prefix": "93.158.172.222/31",
            "proto": "Direct",
            "pref": "0",
            "cost": "0",
            "flags": "D",
            "nh": "93.158.172.222",
            "iface": "100GE1/0/31:1.50",
        },
        {
            "prefix": "93.158.172.222/32",
            "proto": "Direct",
            "pref": "0",
            "cost": "0",
            "flags": "D",
            "nh": "127.0.0.1",
            "iface": "100GE1/0/31:1.50",
        },
        {
            "prefix": "93.158.172.224/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "65536",
            "flags": "D",
            "nh": "93.158.172.227",
            "iface": "100GE1/0/31:1.100",
        },
        {
            "prefix": "93.158.172.226/31",
            "proto": "Direct",
            "pref": "0",
            "cost": "0",
            "flags": "D",
            "nh": "93.158.172.226",
            "iface": "100GE1/0/31:1.100",
        },
        {
            "prefix": "93.158.172.226/32",
            "proto": "Direct",
            "pref": "0",
            "cost": "0",
            "flags": "D",
            "nh": "127.0.0.1",
            "iface": "100GE1/0/31:1.100",
        },
        {
            "prefix": "93.158.172.244/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "6",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.172.252/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "103",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "95.108.237.1/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "100",
            "flags": "D",
            "nh": "213.180.213.238",
            "iface": "Eth-Trunk101",
        },
        {
            "prefix": "95.108.237.3/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "104",
            "flags": "D",
            "nh": "87.250.239.221",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "95.108.237.4/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "4",
            "flags": "D",
            "nh": "87.250.239.221",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "95.108.237.5/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "100",
            "flags": "D",
            "nh": "213.180.213.132",
            "iface": "Eth-Trunk103",
        },
        {
            "prefix": "95.108.237.10/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2",
            "flags": "D",
            "nh": "87.250.239.221",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "95.108.237.14/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "4",
            "flags": "D",
            "nh": "87.250.239.221",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "95.108.237.19/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2",
            "flags": "D",
            "nh": "87.250.239.217",
            "iface": "Eth-Trunk3.1",
        },
        {
            "prefix": "95.108.237.20/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2",
            "flags": "D",
            "nh": "87.250.239.215",
            "iface": "Eth-Trunk1.1",
        },
        {
            "prefix": "95.108.237.27/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "100",
            "flags": "D",
            "nh": "213.180.213.204",
            "iface": "Eth-Trunk105",
        },
        {
            "prefix": "95.108.237.30/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "100",
            "flags": "D",
            "nh": "213.180.213.200",
            "iface": "Eth-Trunk104",
        },
        {
            "prefix": "95.108.237.32/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "104",
            "flags": "D",
            "nh": "87.250.239.221",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "95.108.237.38/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "104",
            "flags": "D",
            "nh": "87.250.239.221",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "95.108.237.39/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "100",
            "flags": "D",
            "nh": "213.180.213.146",
            "iface": "Eth-Trunk111",
        },
        {
            "prefix": "95.108.237.43/32",
            "proto": "Direct",
            "pref": "0",
            "cost": "0",
            "flags": "D",
            "nh": "127.0.0.1",
            "iface": "LoopBack0",
        },
        {
            "prefix": "95.108.237.47/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2",
            "flags": "D",
            "nh": "87.250.239.219",
            "iface": "Eth-Trunk2.1",
        },
        {
            "prefix": "95.108.237.48/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "4",
            "flags": "D",
            "nh": "87.250.239.221",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "95.108.237.49/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "104",
            "flags": "D",
            "nh": "87.250.239.221",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "95.108.237.57/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "104",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "95.108.237.58/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "104",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "95.108.237.65/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2011",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "95.108.237.76/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "104",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "95.108.237.78/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "104",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "95.108.237.96/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "1002",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "95.108.237.100/32",
            "proto": "O_ASE",
            "pref": "150",
            "cost": "20",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "95.108.237.141/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "104",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "95.108.237.142/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "104",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "95.108.237.171/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "104",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "95.108.237.172/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "104",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "95.108.237.179/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "4",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "95.108.237.253/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "8",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "100.43.92.159/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "16502",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "127.0.0.0/8",
            "proto": "Direct",
            "pref": "0",
            "cost": "0",
            "flags": "D",
            "nh": "127.0.0.1",
            "iface": "InLoopBack0",
        },
        {
            "prefix": "127.0.0.1/32",
            "proto": "Direct",
            "pref": "0",
            "cost": "0",
            "flags": "D",
            "nh": "127.0.0.1",
            "iface": "InLoopBack0",
        },
        {
            "prefix": "127.255.255.255/32",
            "proto": "Direct",
            "pref": "0",
            "cost": "0",
            "flags": "D",
            "nh": "127.0.0.1",
            "iface": "InLoopBack0",
        },
        {
            "prefix": "141.8.136.128/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2503",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "141.8.136.129/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2502",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "141.8.136.227/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2011",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "141.8.136.239/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2007",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "141.8.136.255/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2017",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "141.8.140.160/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2009",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "141.8.140.161/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2009",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "141.8.140.162/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2009",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "141.8.140.163/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2009",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "141.8.140.164/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2009",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "141.8.140.165/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2009",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "172.16.6.0/32",
            "proto": "ISIS-L2",
            "pref": "15",
            "cost": "210600",
            "flags": "D",
            "nh": "10.255.0.154",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "172.16.10.160/32",
            "proto": "OSPF",
            "pref": "10",
            "cost": "1008",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.0/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2503",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.2/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "3502",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.4/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "200",
            "flags": "D",
            "nh": "213.180.213.132",
            "iface": "Eth-Trunk103",
        },
        {
            "prefix": "213.180.213.6/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "104",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.8/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "200",
            "flags": "D",
            "nh": "213.180.213.132",
            "iface": "Eth-Trunk103",
        },
        {
            "prefix": "213.180.213.10/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "202",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.12/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "104",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.14/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "204",
            "flags": "D",
            "nh": "87.250.239.221",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "213.180.213.16/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "4006",
            "flags": "D",
            "nh": "87.250.239.221",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "213.180.213.18/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2011",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.20/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2104",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.22/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2104",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.26/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "103",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.32/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "5002",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.34/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2506",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.38/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2104",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.56/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2011",
            "flags": "D",
            "nh": "87.250.239.221",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "213.180.213.68/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "8",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.88/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "106",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.90/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "3003",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.92/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "3002",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.94/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "6502",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.96/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "8502",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.104/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "6503",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.120/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "5002",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.124/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2007",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.128/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "6503",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.130/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "204",
            "flags": "D",
            "nh": "87.250.239.221",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "213.180.213.132/31",
            "proto": "Direct",
            "pref": "0",
            "cost": "0",
            "flags": "D",
            "nh": "213.180.213.133",
            "iface": "Eth-Trunk103",
        },
        {
            "prefix": "213.180.213.133/32",
            "proto": "Direct",
            "pref": "0",
            "cost": "0",
            "flags": "D",
            "nh": "127.0.0.1",
            "iface": "Eth-Trunk103",
        },
        {
            "prefix": "213.180.213.134/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "6",
            "flags": "D",
            "nh": "87.250.239.221",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "213.180.213.136/31",
            "proto": "Direct",
            "pref": "0",
            "cost": "0",
            "flags": "D",
            "nh": "213.180.213.137",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.137/32",
            "proto": "Direct",
            "pref": "0",
            "cost": "0",
            "flags": "D",
            "nh": "127.0.0.1",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.138/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "1006",
            "flags": "D",
            "nh": "87.250.239.221",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "213.180.213.140/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "204",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.142/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2007",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.144/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "104",
            "flags": "D",
            "nh": "87.250.239.221",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "213.180.213.146/31",
            "proto": "Direct",
            "pref": "0",
            "cost": "0",
            "flags": "D",
            "nh": "213.180.213.147",
            "iface": "Eth-Trunk111",
        },
        {
            "prefix": "213.180.213.147/32",
            "proto": "Direct",
            "pref": "0",
            "cost": "0",
            "flags": "D",
            "nh": "127.0.0.1",
            "iface": "Eth-Trunk111",
        },
        {
            "prefix": "213.180.213.162/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2104",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.164/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2104",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.166/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2104",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.168/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "104",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.170/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "108",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.172/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "104",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.174/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "108",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.178/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2015",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.188/30",
            "proto": "OSPF",
            "pref": "10",
            "cost": "1102",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.192/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "16502",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.194/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2107",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.196/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "202",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.198/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "200",
            "flags": "D",
            "nh": "213.180.213.200",
            "iface": "Eth-Trunk104",
        },
        {
            "prefix": "213.180.213.200/31",
            "proto": "Direct",
            "pref": "0",
            "cost": "0",
            "flags": "D",
            "nh": "213.180.213.201",
            "iface": "Eth-Trunk104",
        },
        {
            "prefix": "213.180.213.201/32",
            "proto": "Direct",
            "pref": "0",
            "cost": "0",
            "flags": "D",
            "nh": "127.0.0.1",
            "iface": "Eth-Trunk104",
        },
        {
            "prefix": "213.180.213.202/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "200",
            "flags": "D",
            "nh": "213.180.213.204",
            "iface": "Eth-Trunk105",
        },
        {
            "prefix": "213.180.213.204/31",
            "proto": "Direct",
            "pref": "0",
            "cost": "0",
            "flags": "D",
            "nh": "213.180.213.205",
            "iface": "Eth-Trunk105",
        },
        {
            "prefix": "213.180.213.205/32",
            "proto": "Direct",
            "pref": "0",
            "cost": "0",
            "flags": "D",
            "nh": "127.0.0.1",
            "iface": "Eth-Trunk105",
        },
        {
            "prefix": "213.180.213.206/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "204",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.208/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "104",
            "flags": "D",
            "nh": "87.250.239.221",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "213.180.213.210/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "104",
            "flags": "D",
            "nh": "87.250.239.221",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "213.180.213.212/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "2104",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.220/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "104",
            "flags": "D",
            "nh": "87.250.239.221",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "213.180.213.222/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "104",
            "flags": "D",
            "nh": "87.250.239.221",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "213.180.213.224/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "204",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.226/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "104",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.228/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "104",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.230/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "104",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.232/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "104",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.234/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "204",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.236/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "204",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.238/31",
            "proto": "Direct",
            "pref": "0",
            "cost": "0",
            "flags": "D",
            "nh": "213.180.213.239",
            "iface": "Eth-Trunk101",
        },
        {
            "prefix": "213.180.213.239/32",
            "proto": "Direct",
            "pref": "0",
            "cost": "0",
            "flags": "D",
            "nh": "127.0.0.1",
            "iface": "Eth-Trunk101",
        },
        {
            "prefix": "213.180.213.240/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "200",
            "flags": "D",
            "nh": "213.180.213.238",
            "iface": "Eth-Trunk101",
        },
        {
            "prefix": "213.180.213.242/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "104",
            "flags": "D",
            "nh": "87.250.239.221",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "213.180.213.244/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "104",
            "flags": "D",
            "nh": "87.250.239.221",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "213.180.213.248/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "10",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.252/31",
            "proto": "OSPF",
            "pref": "10",
            "cost": "1102",
            "flags": "D",
            "nh": "213.180.213.136",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "255.255.255.255/32",
            "proto": "Direct",
            "pref": "0",
            "cost": "0",
            "flags": "D",
            "nh": "127.0.0.1",
            "iface": "InLoopBack0",
        },
    ]
