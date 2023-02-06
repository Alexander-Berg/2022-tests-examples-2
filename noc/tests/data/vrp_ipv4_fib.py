from data.lib import Data


class Data1(Data):
    content = """
Route Flags: G - Gateway Route, H - Host Route,    U - Up Route
             S - Static Route,  D - Dynamic Route, B - Black Hole Route
--------------------------------------------------------------------------------
 FIB Table: _public_
 Total number of Routes: 484

 Destination/Mask   Nexthop          Flag   Interface               TunnelID             
    5.45.200.24/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4fc1         
   5.45.247.180/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4fc2         
     10.255.0.1/32  10.255.0.154     DGHU   Eth-Trunk161            0x01004c6a81         
     10.255.0.2/32  10.255.0.154     DGHU   Eth-Trunk161            0x01004c4bc5         
     10.255.0.5/32  10.255.0.131     DGHU   Eth-Trunk4.10           0x01004c5002         
                    10.255.0.139     DGHU   Eth-Trunk1.10           0x01004c5002         
                    10.255.0.149     DGHU   Eth-Trunk2.10           0x01004c5002         
                    10.255.0.157     DGHU   Eth-Trunk3.10           0x01004c5002         
     10.255.0.6/32  10.255.0.157     DGHU   Eth-Trunk3.10           0x01004c6841         
     10.255.0.8/32  10.255.0.139     DGHU   Eth-Trunk1.10           0x01004c6803         
     10.255.0.9/32  10.255.0.154     DGHU   Eth-Trunk161            0x01004c4c89         
    10.255.0.10/32  10.255.0.131     DGHU   Eth-Trunk4.10           0x01004c5183         
    10.255.0.11/32  10.255.0.131     DGHU   Eth-Trunk4.10           0x01004c4bc8         
                    10.255.0.139     DGHU   Eth-Trunk1.10           0x01004c4bc8         
                    10.255.0.149     DGHU   Eth-Trunk2.10           0x01004c4bc8         
                    10.255.0.154     DGHU   Eth-Trunk161            0x01004c4bc8         
                    10.255.0.157     DGHU   Eth-Trunk3.10           0x01004c4bc8         
    10.255.0.12/32  10.255.0.154     DGHU   Eth-Trunk161            0x01004c4bc9         
    10.255.0.13/32  10.255.0.154     DGHU   Eth-Trunk161            0x01004c4bca         
    10.255.0.14/32  127.0.0.1        HU     LoopBack10              -                    
    10.255.0.15/32  10.255.0.154     DGHU   Eth-Trunk161            0x01004c5484         
    10.255.0.16/32  10.255.0.154     DGHU   Eth-Trunk161            0x01004c4c85         
    10.255.0.17/32  10.255.0.154     DGHU   Eth-Trunk161            0x01004c4c86         
    10.255.0.18/32  10.255.0.149     DGHU   Eth-Trunk2.10           0x01004c5182         
    10.255.0.19/32  10.255.0.154     DGHU   Eth-Trunk161            0x01004c4c87         
    10.255.0.20/32  10.255.0.154     DGHU   Eth-Trunk161            0x01004c4c8a         
    10.255.0.21/32  10.255.0.154     DGHU   Eth-Trunk161            0x01004c4c84         
    10.255.0.22/32  10.255.0.154     DGHU   Eth-Trunk161            0x01004c58c7         
    10.255.0.30/32  10.255.0.157     DGHU   Eth-Trunk3.10           -                    
                    10.255.0.154     DGHU   Eth-Trunk161            -                    
                    10.255.0.149     DGHU   Eth-Trunk2.10           -                    
                    10.255.0.139     DGHU   Eth-Trunk1.10           -                    
                    10.255.0.131     DGHU   Eth-Trunk4.10           -                    
    10.255.0.34/32  10.255.0.154     DGHU   Eth-Trunk161            0x01004c4c81         
    10.255.0.35/32  10.255.0.154     DGHU   Eth-Trunk161            0x01004c58c5         
    10.255.0.36/32  10.255.0.154     DGHU   Eth-Trunk161            0x01004c5981         
    10.255.0.37/32  10.255.0.154     DGHU   Eth-Trunk161            0x01004c58d0         
    10.255.0.41/32  10.255.0.154     DGHU   Eth-Trunk161            0x01004c5942         
    10.255.0.42/32  10.255.0.154     DGHU   Eth-Trunk161            0x01004c5205         
    10.255.0.43/32  10.255.0.154     DGHU   Eth-Trunk161            0x01004c5802         
    10.255.0.44/32  10.255.0.154     DGHU   Eth-Trunk161            0x01004c5042         
    10.255.0.45/32  10.255.0.154     DGHU   Eth-Trunk161            0x01004c5881         
    10.255.0.46/32  10.255.0.154     DGHU   Eth-Trunk161            0x01004c5102         
    10.255.0.52/32  10.255.0.154     DGHU   Eth-Trunk161            0x01004c4c02         
    10.255.0.53/32  10.255.0.154     DGHU   Eth-Trunk161            0x29000004c2         
    10.255.0.55/32  10.255.0.154     DGHU   Eth-Trunk161            0x01004c5485         
    10.255.0.56/32  10.255.0.131     DGHU   Eth-Trunk4.10           0x01004c4d01         
                    10.255.0.139     DGHU   Eth-Trunk1.10           0x01004c4d01         
                    10.255.0.149     DGHU   Eth-Trunk2.10           0x01004c4d01         
                    10.255.0.154     DGHU   Eth-Trunk161            0x01004c4d01         
                    10.255.0.157     DGHU   Eth-Trunk3.10           0x01004c4d01         
    10.255.0.59/32  10.255.0.131     DGHU   Eth-Trunk4.10           0x01004c4bdb         
                    10.255.0.139     DGHU   Eth-Trunk1.10           0x01004c4bdb         
                    10.255.0.149     DGHU   Eth-Trunk2.10           0x01004c4bdb         
                    10.255.0.154     DGHU   Eth-Trunk161            0x01004c4bdb         
                    10.255.0.157     DGHU   Eth-Trunk3.10           0x01004c4bdb         
    10.255.0.61/32  10.255.0.154     DGHU   Eth-Trunk161            0x01004c694d         
    10.255.0.63/32  10.255.0.154     DGHU   Eth-Trunk161            0x01004c694c         
    10.255.0.64/32  10.255.0.154     DGHU   Eth-Trunk161            0x01004c694b         
    10.255.0.65/32  10.255.0.154     DGHU   Eth-Trunk161            0x01004c694a         
    10.255.0.66/32  10.255.0.154     DGHU   Eth-Trunk161            0x01004c6949         
    10.255.0.67/32  10.255.0.154     DGHU   Eth-Trunk161            0x01004c58c1         
    10.255.0.68/32  10.255.0.131     DGHU   Eth-Trunk4.10           0x01004c4be3         
                    10.255.0.139     DGHU   Eth-Trunk1.10           0x01004c4be3         
                    10.255.0.149     DGHU   Eth-Trunk2.10           0x01004c4be3         
                    10.255.0.154     DGHU   Eth-Trunk161            0x01004c4be3         
                    10.255.0.157     DGHU   Eth-Trunk3.10           0x01004c4be3         
    10.255.0.69/32  10.255.0.154     DGHU   Eth-Trunk161            0x01004c6947         
    10.255.0.71/32  10.255.0.154     DGHU   Eth-Trunk161            0x01004c59c5         
    10.255.0.75/32  10.255.0.154     DGHU   Eth-Trunk161            0x01004c4be6         
    10.255.0.99/32  10.255.0.154     DGHU   Eth-Trunk161            0x01004c4d82         
   10.255.0.100/32  10.255.0.154     DGHU   Eth-Trunk161            0x01004c5e01         
   10.255.0.104/32  10.255.0.154     DGHU   Eth-Trunk161            0x01004c5f4a         
   10.255.0.130/31  10.255.0.130     U      Eth-Trunk4.10           -                    
   10.255.0.130/32  127.0.0.1        HU     Eth-Trunk4.10           -                    
   10.255.0.138/31  10.255.0.138     U      Eth-Trunk1.10           -                    
   10.255.0.138/32  127.0.0.1        HU     Eth-Trunk1.10           -                    
   10.255.0.146/31  10.255.0.154     DGU    Eth-Trunk161            -                    
   10.255.0.148/31  10.255.0.148     U      Eth-Trunk2.10           -                    
   10.255.0.148/32  127.0.0.1        HU     Eth-Trunk2.10           -                    
   10.255.0.150/31  10.255.0.157     DGU    Eth-Trunk3.10           -                    
                    10.255.0.154     DGU    Eth-Trunk161            -                    
                    10.255.0.149     DGU    Eth-Trunk2.10           -                    
                    10.255.0.139     DGU    Eth-Trunk1.10           -                    
                    10.255.0.131     DGU    Eth-Trunk4.10           -                    
   10.255.0.152/31  10.255.0.154     DGU    Eth-Trunk161            -                    
   10.255.0.154/31  10.255.0.155     U      Eth-Trunk161            -                    
   10.255.0.155/32  127.0.0.1        HU     Eth-Trunk161            -                    
   10.255.0.156/31  10.255.0.156     U      Eth-Trunk3.10           -                    
   10.255.0.156/32  127.0.0.1        HU     Eth-Trunk3.10           -                    
   10.255.0.158/31  10.255.0.157     DGU    Eth-Trunk3.10           -                    
                    10.255.0.149     DGU    Eth-Trunk2.10           -                    
                    10.255.0.139     DGU    Eth-Trunk1.10           -                    
                    10.255.0.131     DGU    Eth-Trunk4.10           -                    
   10.255.0.160/31  10.255.0.157     DGU    Eth-Trunk3.10           -                    
                    10.255.0.154     DGU    Eth-Trunk161            -                    
                    10.255.0.149     DGU    Eth-Trunk2.10           -                    
                    10.255.0.139     DGU    Eth-Trunk1.10           -                    
                    10.255.0.131     DGU    Eth-Trunk4.10           -                    
   10.255.0.162/31  10.255.0.157     DGU    Eth-Trunk3.10           -                    
                    10.255.0.154     DGU    Eth-Trunk161            -                    
                    10.255.0.149     DGU    Eth-Trunk2.10           -                    
                    10.255.0.139     DGU    Eth-Trunk1.10           -                    
                    10.255.0.131     DGU    Eth-Trunk4.10           -                    
   10.255.0.164/31  10.255.0.154     DGU    Eth-Trunk161            -                    
   10.255.0.166/31  10.255.0.157     DGU    Eth-Trunk3.10           -                    
                    10.255.0.154     DGU    Eth-Trunk161            -                    
                    10.255.0.149     DGU    Eth-Trunk2.10           -                    
                    10.255.0.139     DGU    Eth-Trunk1.10           -                    
                    10.255.0.131     DGU    Eth-Trunk4.10           -                    
   10.255.0.170/31  10.255.0.154     DGU    Eth-Trunk161            -                    
   10.255.0.172/31  10.255.0.157     DGU    Eth-Trunk3.10           -                    
                    10.255.0.149     DGU    Eth-Trunk2.10           -                    
                    10.255.0.139     DGU    Eth-Trunk1.10           -                    
                    10.255.0.131     DGU    Eth-Trunk4.10           -                    
   10.255.0.174/31  10.255.0.157     DGU    Eth-Trunk3.10           -                    
                    10.255.0.149     DGU    Eth-Trunk2.10           -                    
                    10.255.0.139     DGU    Eth-Trunk1.10           -                    
                    10.255.0.131     DGU    Eth-Trunk4.10           -                    
   10.255.0.176/31  10.255.0.157     DGU    Eth-Trunk3.10           -                    
                    10.255.0.149     DGU    Eth-Trunk2.10           -                    
                    10.255.0.139     DGU    Eth-Trunk1.10           -                    
                    10.255.0.131     DGU    Eth-Trunk4.10           -                    
   10.255.0.182/31  10.255.0.154     DGU    Eth-Trunk161            -                    
   10.255.0.190/31  10.255.0.154     DGU    Eth-Trunk161            -                    
   10.255.0.194/31  10.255.0.157     DGU    Eth-Trunk3.10           -                    
                    10.255.0.154     DGU    Eth-Trunk161            -                    
                    10.255.0.149     DGU    Eth-Trunk2.10           -                    
                    10.255.0.139     DGU    Eth-Trunk1.10           -                    
                    10.255.0.131     DGU    Eth-Trunk4.10           -                    
   10.255.0.196/31  10.255.0.157     DGU    Eth-Trunk3.10           -                    
                    10.255.0.149     DGU    Eth-Trunk2.10           -                    
                    10.255.0.139     DGU    Eth-Trunk1.10           -                    
                    10.255.0.131     DGU    Eth-Trunk4.10           -                    
   10.255.0.204/31  10.255.0.154     DGU    Eth-Trunk161            -                    
   10.255.0.210/31  10.255.0.157     DGU    Eth-Trunk3.10           -                    
                    10.255.0.154     DGU    Eth-Trunk161            -                    
                    10.255.0.149     DGU    Eth-Trunk2.10           -                    
                    10.255.0.139     DGU    Eth-Trunk1.10           -                    
                    10.255.0.131     DGU    Eth-Trunk4.10           -                    
   10.255.0.212/31  10.255.0.157     DGU    Eth-Trunk3.10           -                    
                    10.255.0.154     DGU    Eth-Trunk161            -                    
                    10.255.0.149     DGU    Eth-Trunk2.10           -                    
                    10.255.0.139     DGU    Eth-Trunk1.10           -                    
                    10.255.0.131     DGU    Eth-Trunk4.10           -                    
   10.255.0.224/31  10.255.0.157     DGU    Eth-Trunk3.10           -                    
                    10.255.0.154     DGU    Eth-Trunk161            -                    
                    10.255.0.149     DGU    Eth-Trunk2.10           -                    
                    10.255.0.139     DGU    Eth-Trunk1.10           -                    
                    10.255.0.131     DGU    Eth-Trunk4.10           -                    
   10.255.0.226/31  10.255.0.154     DGU    Eth-Trunk161            -                    
   10.255.0.228/31  10.255.0.157     DGU    Eth-Trunk3.10           -                    
                    10.255.0.154     DGU    Eth-Trunk161            -                    
                    10.255.0.149     DGU    Eth-Trunk2.10           -                    
                    10.255.0.139     DGU    Eth-Trunk1.10           -                    
                    10.255.0.131     DGU    Eth-Trunk4.10           -                    
   10.255.0.232/31  10.255.0.154     DGU    Eth-Trunk161            -                    
   10.255.0.234/31  10.255.0.157     DGU    Eth-Trunk3.10           -                    
                    10.255.0.154     DGU    Eth-Trunk161            -                    
                    10.255.0.149     DGU    Eth-Trunk2.10           -                    
                    10.255.0.139     DGU    Eth-Trunk1.10           -                    
                    10.255.0.131     DGU    Eth-Trunk4.10           -                    
   10.255.0.236/31  10.255.0.154     DGU    Eth-Trunk161            -                    
   10.255.0.238/31  10.255.0.157     DGU    Eth-Trunk3.10           -                    
                    10.255.0.154     DGU    Eth-Trunk161            -                    
                    10.255.0.149     DGU    Eth-Trunk2.10           -                    
                    10.255.0.139     DGU    Eth-Trunk1.10           -                    
                    10.255.0.131     DGU    Eth-Trunk4.10           -                    
   10.255.0.240/31  10.255.0.154     DGU    Eth-Trunk161            -                    
   10.255.0.248/31  10.255.0.154     DGU    Eth-Trunk161            -                    
   10.255.0.250/31  10.255.0.154     DGU    Eth-Trunk161            -                    
   10.255.0.252/31  10.255.0.157     DGU    Eth-Trunk3.10           -                    
                    10.255.0.154     DGU    Eth-Trunk161            -                    
                    10.255.0.149     DGU    Eth-Trunk2.10           -                    
                    10.255.0.139     DGU    Eth-Trunk1.10           -                    
                    10.255.0.131     DGU    Eth-Trunk4.10           -                    
     10.255.1.0/31  10.255.0.154     DGU    Eth-Trunk161            -                    
     10.255.1.2/31  10.255.0.157     DGU    Eth-Trunk3.10           -                    
                    10.255.0.154     DGU    Eth-Trunk161            -                    
                    10.255.0.149     DGU    Eth-Trunk2.10           -                    
                    10.255.0.139     DGU    Eth-Trunk1.10           -                    
                    10.255.0.131     DGU    Eth-Trunk4.10           -                    
     10.255.1.4/31  10.255.0.154     DGU    Eth-Trunk161            -                    
     10.255.1.6/31  10.255.0.157     DGU    Eth-Trunk3.10           -                    
                    10.255.0.154     DGU    Eth-Trunk161            -                    
                    10.255.0.149     DGU    Eth-Trunk2.10           -                    
                    10.255.0.139     DGU    Eth-Trunk1.10           -                    
                    10.255.0.131     DGU    Eth-Trunk4.10           -                    
   10.255.1.220/31  10.255.0.157     DGU    Eth-Trunk3.10           -                    
                    10.255.0.154     DGU    Eth-Trunk161            -                    
                    10.255.0.149     DGU    Eth-Trunk2.10           -                    
                    10.255.0.139     DGU    Eth-Trunk1.10           -                    
                    10.255.0.131     DGU    Eth-Trunk4.10           -                    
   10.255.1.222/31  10.255.0.157     DGU    Eth-Trunk3.10           -                    
                    10.255.0.154     DGU    Eth-Trunk161            -                    
                    10.255.0.149     DGU    Eth-Trunk2.10           -                    
                    10.255.0.139     DGU    Eth-Trunk1.10           -                    
                    10.255.0.131     DGU    Eth-Trunk4.10           -                    
   10.255.1.224/31  10.255.0.157     DGU    Eth-Trunk3.10           -                    
                    10.255.0.154     DGU    Eth-Trunk161            -                    
                    10.255.0.149     DGU    Eth-Trunk2.10           -                    
                    10.255.0.139     DGU    Eth-Trunk1.10           -                    
                    10.255.0.131     DGU    Eth-Trunk4.10           -                    
   10.255.1.226/31  10.255.0.157     DGU    Eth-Trunk3.10           -                    
                    10.255.0.154     DGU    Eth-Trunk161            -                    
                    10.255.0.149     DGU    Eth-Trunk2.10           -                    
                    10.255.0.139     DGU    Eth-Trunk1.10           -                    
                    10.255.0.131     DGU    Eth-Trunk4.10           -                    
   10.255.1.228/31  10.255.0.157     DGU    Eth-Trunk3.10           -                    
                    10.255.0.154     DGU    Eth-Trunk161            -                    
                    10.255.0.149     DGU    Eth-Trunk2.10           -                    
                    10.255.0.139     DGU    Eth-Trunk1.10           -                    
                    10.255.0.131     DGU    Eth-Trunk4.10           -                    
   10.255.1.230/31  10.255.0.157     DGU    Eth-Trunk3.10           -                    
                    10.255.0.154     DGU    Eth-Trunk161            -                    
                    10.255.0.149     DGU    Eth-Trunk2.10           -                    
                    10.255.0.139     DGU    Eth-Trunk1.10           -                    
                    10.255.0.131     DGU    Eth-Trunk4.10           -                    
   10.255.1.232/31  10.255.0.154     DGU    Eth-Trunk161            -                    
   10.255.1.234/31  10.255.0.154     DGU    Eth-Trunk161            -                    
   10.255.1.236/31  10.255.0.154     DGU    Eth-Trunk161            -                    
   10.255.1.238/31  10.255.0.154     DGU    Eth-Trunk161            -                    
   10.255.1.240/31  10.255.0.154     DGU    Eth-Trunk161            -                    
   10.255.1.242/31  10.255.0.154     DGU    Eth-Trunk161            -                    
     10.255.2.8/31  10.255.0.157     DGU    Eth-Trunk3.10           -                    
                    10.255.0.154     DGU    Eth-Trunk161            -                    
                    10.255.0.149     DGU    Eth-Trunk2.10           -                    
                    10.255.0.139     DGU    Eth-Trunk1.10           -                    
                    10.255.0.131     DGU    Eth-Trunk4.10           -                    
    10.255.2.12/31  10.255.0.157     DGU    Eth-Trunk3.10           -                    
                    10.255.0.154     DGU    Eth-Trunk161            -                    
                    10.255.0.149     DGU    Eth-Trunk2.10           -                    
                    10.255.0.139     DGU    Eth-Trunk1.10           -                    
                    10.255.0.131     DGU    Eth-Trunk4.10           -                    
    10.255.2.16/31  10.255.0.157     DGU    Eth-Trunk3.10           -                    
                    10.255.0.154     DGU    Eth-Trunk161            -                    
                    10.255.0.149     DGU    Eth-Trunk2.10           -                    
                    10.255.0.139     DGU    Eth-Trunk1.10           -                    
                    10.255.0.131     DGU    Eth-Trunk4.10           -                    
    10.255.2.18/31  10.255.0.157     DGU    Eth-Trunk3.10           -                    
                    10.255.0.154     DGU    Eth-Trunk161            -                    
                    10.255.0.149     DGU    Eth-Trunk2.10           -                    
                    10.255.0.139     DGU    Eth-Trunk1.10           -                    
                    10.255.0.131     DGU    Eth-Trunk4.10           -                    
    10.255.2.20/31  10.255.0.154     DGU    Eth-Trunk161            -                    
    10.255.2.22/31  10.255.0.154     DGU    Eth-Trunk161            -                    
    10.255.2.24/31  10.255.0.157     DGU    Eth-Trunk3.10           -                    
                    10.255.0.154     DGU    Eth-Trunk161            -                    
                    10.255.0.149     DGU    Eth-Trunk2.10           -                    
                    10.255.0.139     DGU    Eth-Trunk1.10           -                    
                    10.255.0.131     DGU    Eth-Trunk4.10           -                    
    10.255.2.36/31  10.255.0.157     DGU    Eth-Trunk3.10           -                    
                    10.255.0.154     DGU    Eth-Trunk161            -                    
                    10.255.0.149     DGU    Eth-Trunk2.10           -                    
                    10.255.0.139     DGU    Eth-Trunk1.10           -                    
                    10.255.0.131     DGU    Eth-Trunk4.10           -                    
   10.255.2.192/31  10.255.0.157     DGU    Eth-Trunk3.10           -                    
                    10.255.0.154     DGU    Eth-Trunk161            -                    
                    10.255.0.149     DGU    Eth-Trunk2.10           -                    
                    10.255.0.139     DGU    Eth-Trunk1.10           -                    
                    10.255.0.131     DGU    Eth-Trunk4.10           -                    
   10.255.2.194/31  10.255.0.157     DGU    Eth-Trunk3.10           -                    
                    10.255.0.154     DGU    Eth-Trunk161            -                    
                    10.255.0.149     DGU    Eth-Trunk2.10           -                    
                    10.255.0.139     DGU    Eth-Trunk1.10           -                    
                    10.255.0.131     DGU    Eth-Trunk4.10           -                    
   10.255.2.198/31  10.255.0.154     DGU    Eth-Trunk161            -                    
   10.255.2.202/31  10.255.0.154     DGU    Eth-Trunk161            -                    
   10.255.2.204/31  10.255.0.154     DGU    Eth-Trunk161            -                    
   10.255.2.224/31  10.255.0.154     DGU    Eth-Trunk161            -                    
   10.255.2.226/31  10.255.0.157     DGU    Eth-Trunk3.10           -                    
                    10.255.0.154     DGU    Eth-Trunk161            -                    
                    10.255.0.149     DGU    Eth-Trunk2.10           -                    
                    10.255.0.139     DGU    Eth-Trunk1.10           -                    
                    10.255.0.131     DGU    Eth-Trunk4.10           -                    
     10.255.3.0/31  10.255.0.157     DGU    Eth-Trunk3.10           -                    
                    10.255.0.154     DGU    Eth-Trunk161            -                    
                    10.255.0.149     DGU    Eth-Trunk2.10           -                    
                    10.255.0.139     DGU    Eth-Trunk1.10           -                    
                    10.255.0.131     DGU    Eth-Trunk4.10           -                    
    10.255.3.26/31  10.255.0.154     DGU    Eth-Trunk161            -                    
    10.255.3.60/31  10.255.0.154     DGU    Eth-Trunk161            -                    
    10.255.3.66/31  10.255.0.157     DGU    Eth-Trunk3.10           -                    
                    10.255.0.154     DGU    Eth-Trunk161            -                    
                    10.255.0.149     DGU    Eth-Trunk2.10           -                    
                    10.255.0.139     DGU    Eth-Trunk1.10           -                    
                    10.255.0.131     DGU    Eth-Trunk4.10           -                    
    10.255.3.68/31  10.255.0.154     DGU    Eth-Trunk161            -                    
    10.255.3.70/31  10.255.0.154     DGU    Eth-Trunk161            -                    
    10.255.3.72/31  10.255.0.157     DGU    Eth-Trunk3.10           -                    
                    10.255.0.154     DGU    Eth-Trunk161            -                    
                    10.255.0.149     DGU    Eth-Trunk2.10           -                    
                    10.255.0.139     DGU    Eth-Trunk1.10           -                    
                    10.255.0.131     DGU    Eth-Trunk4.10           -                    
    10.255.3.76/31  10.255.0.154     DGU    Eth-Trunk161            -                    
    10.255.3.78/31  10.255.0.154     DGU    Eth-Trunk161            -                    
    10.255.3.80/31  10.255.0.157     DGU    Eth-Trunk3.10           -                    
                    10.255.0.154     DGU    Eth-Trunk161            -                    
                    10.255.0.149     DGU    Eth-Trunk2.10           -                    
                    10.255.0.139     DGU    Eth-Trunk1.10           -                    
                    10.255.0.131     DGU    Eth-Trunk4.10           -                    
    10.255.3.90/31  10.255.0.154     DGU    Eth-Trunk161            -                    
    10.255.3.94/31  10.255.0.154     DGU    Eth-Trunk161            -                    
   10.255.3.104/31  10.255.0.154     DGU    Eth-Trunk161            -                    
   10.255.3.108/31  10.255.0.154     DGU    Eth-Trunk161            -                    
   10.255.3.110/31  10.255.0.154     DGU    Eth-Trunk161            -                    
   10.255.3.112/31  10.255.0.154     DGU    Eth-Trunk161            -                    
   10.255.3.114/31  10.255.0.154     DGU    Eth-Trunk161            -                    
   10.255.3.116/31  10.255.0.154     DGU    Eth-Trunk161            -                    
  87.250.226.99/32  87.250.239.215   DGHU   Eth-Trunk1.1            0x01004c4b44         
                    87.250.239.217   DGHU   Eth-Trunk3.1            0x01004c4b44         
                    87.250.239.219   DGHU   Eth-Trunk2.1            0x01004c4b44         
                    87.250.239.221   DGHU   Eth-Trunk4.1            0x01004c4b44         
                    213.180.213.136  DGHU   Eth-Trunk81             0x01004c4b44         
 87.250.226.122/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c59c6         
 87.250.226.134/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c58c8         
 87.250.226.135/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c51c2         
 87.250.226.136/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c51c3         
 87.250.226.141/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4b7f         
 87.250.226.142/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4b93         
 87.250.226.143/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c5084         
 87.250.226.155/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c5941         
 87.250.226.156/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4f82         
 87.250.226.157/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c5803         
 87.250.226.158/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c5041         
 87.250.226.159/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4c82         
 87.250.226.160/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c5101         
 87.250.226.162/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c5103         
 87.250.226.194/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4b89         
 87.250.226.195/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4b8a         
 87.250.226.196/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4b45         
 87.250.226.197/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c51c4         
  87.250.228.28/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c5f4b         
 87.250.228.145/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4f01         
 87.250.228.146/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c58c6         
 87.250.228.149/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4b5f         
 87.250.228.150/32  87.250.239.215   DGHU   Eth-Trunk1.1            0x01004c4b71         
                    87.250.239.217   DGHU   Eth-Trunk3.1            0x01004c4b71         
                    87.250.239.219   DGHU   Eth-Trunk2.1            0x01004c4b71         
                    87.250.239.221   DGHU   Eth-Trunk4.1            0x01004c4b71         
 87.250.228.152/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c5483         
 87.250.228.153/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c58ca         
 87.250.228.167/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4b64         
 87.250.228.168/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c59c4         
 87.250.228.177/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c51c6         
 87.250.228.198/32  87.250.239.215   DGHU   Eth-Trunk1.1            0x01004c4b5c         
                    87.250.239.217   DGHU   Eth-Trunk3.1            0x01004c4b5c         
                    87.250.239.219   DGHU   Eth-Trunk2.1            0x01004c4b5c         
                    87.250.239.221   DGHU   Eth-Trunk4.1            0x01004c4b5c         
                    213.180.213.136  DGHU   Eth-Trunk81             0x01004c4b5c         
 87.250.228.199/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4b5d         
 87.250.228.224/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4b60         
 87.250.228.226/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4b63         
 87.250.228.228/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4b62         
 87.250.228.230/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4b61         
 87.250.228.231/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4b65         
 87.250.228.232/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4b72         
 87.250.228.233/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c5689         
 87.250.228.237/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c58c4         
 87.250.228.238/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c5982         
 87.250.228.239/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c58cf         
 87.250.233.131/32  87.250.239.215   DGHU   Eth-Trunk1.1            0x01004c4c88         
                    87.250.239.217   DGHU   Eth-Trunk3.1            0x01004c4c88         
                    87.250.239.219   DGHU   Eth-Trunk2.1            0x01004c4c88         
                    87.250.239.221   DGHU   Eth-Trunk4.1            0x01004c4c88         
 87.250.233.132/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c6743         
 87.250.233.133/32  87.250.239.215   DGHU   Eth-Trunk1.1            0x01004c4f81         
                    87.250.239.217   DGHU   Eth-Trunk3.1            0x01004c4f81         
                    87.250.239.219   DGHU   Eth-Trunk2.1            0x01004c4f81         
                    87.250.239.221   DGHU   Eth-Trunk4.1            0x01004c4f81         
 87.250.233.135/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c51c5         
 87.250.233.136/32  87.250.239.215   DGHU   Eth-Trunk1.1            0x01004c4b43         
                    87.250.239.217   DGHU   Eth-Trunk3.1            0x01004c4b43         
                    87.250.239.219   DGHU   Eth-Trunk2.1            0x01004c4b43         
                    87.250.239.221   DGHU   Eth-Trunk4.1            0x01004c4b43         
                    213.180.213.136  DGHU   Eth-Trunk81             0x01004c4b43         
 87.250.233.141/32  87.250.239.221   DGHU   Eth-Trunk4.1            -                    
                    87.250.239.219   DGHU   Eth-Trunk2.1            -                    
                    87.250.239.217   DGHU   Eth-Trunk3.1            -                    
                    87.250.239.215   DGHU   Eth-Trunk1.1            -                    
 87.250.233.150/32  213.180.213.136  DGHU   Eth-Trunk81             -                    
 87.250.233.166/32  213.180.213.136  DGHU   Eth-Trunk81             -                    
 87.250.233.190/32  213.180.213.136  DGHU   Eth-Trunk81             -                    
 87.250.233.199/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4b95         
 87.250.233.200/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4b98         
 87.250.233.233/32  87.250.239.215   DGHU   Eth-Trunk1.1            0x01004c4b47         
                    87.250.239.217   DGHU   Eth-Trunk3.1            0x01004c4b47         
                    87.250.239.219   DGHU   Eth-Trunk2.1            0x01004c4b47         
                    87.250.239.221   DGHU   Eth-Trunk4.1            0x01004c4b47         
 87.250.233.248/32  213.180.213.136  DGHU   Eth-Trunk81             -                    
   87.250.234.0/32  213.180.213.136  DGHU   Eth-Trunk81             -                    
   87.250.234.2/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4b48         
   87.250.234.8/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c59c2         
  87.250.234.12/32  93.158.172.227   DGHU   100GE1/0/31:1.100       0x01004c4b49         
  87.250.234.14/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4fc4         
  87.250.234.16/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c59c3         
  87.250.234.18/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c6742         
  87.250.234.19/32  93.158.172.223   DGHU   100GE1/0/31:1.50        0x01004c4b4a         
  87.250.234.21/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4b4b         
  87.250.234.22/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c5e02         
  87.250.234.41/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4b4c         
 87.250.234.121/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c59c1         
 87.250.234.179/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4b8c         
 87.250.234.234/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c56c7         
 87.250.234.255/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4c05         
   87.250.239.0/31  213.180.213.136  DGU    Eth-Trunk81             -                    
   87.250.239.4/31  213.180.213.136  DGU    Eth-Trunk81             -                    
                    87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
   87.250.239.6/31  213.180.213.136  DGU    Eth-Trunk81             -                    
                    87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
   87.250.239.8/31  213.180.213.136  DGU    Eth-Trunk81             -                    
                    87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
  87.250.239.10/31  213.180.213.136  DGU    Eth-Trunk81             -                    
                    87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
  87.250.239.12/31  213.180.213.136  DGU    Eth-Trunk81             -                    
  87.250.239.14/31  213.180.213.136  DGU    Eth-Trunk81             -                    
  87.250.239.16/31  87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
  87.250.239.18/31  213.180.213.136  DGU    Eth-Trunk81             -                    
                    87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
  87.250.239.20/31  213.180.213.136  DGU    Eth-Trunk81             -                    
                    87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
  87.250.239.24/31  87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
  87.250.239.26/31  213.180.213.136  DGU    Eth-Trunk81             -                    
  87.250.239.30/31  213.180.213.136  DGU    Eth-Trunk81             -                    
  87.250.239.32/31  213.180.213.136  DGU    Eth-Trunk81             -                    
  87.250.239.34/31  213.180.213.136  DGU    Eth-Trunk81             -                    
  87.250.239.36/31  213.180.213.136  DGU    Eth-Trunk81             -                    
  87.250.239.38/31  213.180.213.136  DGU    Eth-Trunk81             -                    
  87.250.239.40/31  213.180.213.136  DGU    Eth-Trunk81             -                    
  87.250.239.42/31  213.180.213.136  DGU    Eth-Trunk81             -                    
                    87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
  87.250.239.44/31  213.180.213.136  DGU    Eth-Trunk81             -                    
  87.250.239.50/31  213.180.213.136  DGU    Eth-Trunk81             -                    
                    87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
  87.250.239.52/31  87.250.239.215   DGU    Eth-Trunk1.1            -                    
  87.250.239.54/31  213.180.213.136  DGU    Eth-Trunk81             -                    
                    87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
  87.250.239.58/31  213.180.213.136  DGU    Eth-Trunk81             -                    
  87.250.239.62/31  213.180.213.136  DGU    Eth-Trunk81             -                    
  87.250.239.64/31  213.180.213.136  DGU    Eth-Trunk81             -                    
  87.250.239.66/31  213.180.213.136  DGU    Eth-Trunk81             -                    
  87.250.239.68/31  213.180.213.136  DGU    Eth-Trunk81             -                    
  87.250.239.70/31  87.250.239.219   DGU    Eth-Trunk2.1            -                    
  87.250.239.72/31  213.180.213.136  DGU    Eth-Trunk81             -                    
  87.250.239.74/31  213.180.213.136  DGU    Eth-Trunk81             -                    
                    87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
  87.250.239.76/31  213.180.213.136  DGU    Eth-Trunk81             -                    
  87.250.239.78/31  213.180.213.136  DGU    Eth-Trunk81             -                    
  87.250.239.80/31  213.180.213.136  DGU    Eth-Trunk81             -                    
  87.250.239.82/31  213.180.213.136  DGU    Eth-Trunk81             -                    
  87.250.239.84/31  213.180.213.136  DGU    Eth-Trunk81             -                    
  87.250.239.86/31  213.180.213.136  DGU    Eth-Trunk81             -                    
  87.250.239.90/31  87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
  87.250.239.92/31  87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
  87.250.239.94/31  213.180.213.136  DGU    Eth-Trunk81             -                    
                    87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
  87.250.239.96/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 87.250.239.100/31  87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
 87.250.239.104/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 87.250.239.106/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 87.250.239.108/31  87.250.239.217   DGU    Eth-Trunk3.1            -                    
 87.250.239.110/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 87.250.239.112/31  213.180.213.136  DGU    Eth-Trunk81             -                    
                    87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
 87.250.239.114/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 87.250.239.116/31  213.180.213.136  DGU    Eth-Trunk81             -                    
                    87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
 87.250.239.118/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 87.250.239.122/31  87.250.239.221   DGU    Eth-Trunk4.1            -                    
 87.250.239.124/31  87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
 87.250.239.126/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 87.250.239.128/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 87.250.239.132/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 87.250.239.136/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 87.250.239.138/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 87.250.239.140/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 87.250.239.144/29  87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
 87.250.239.152/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 87.250.239.154/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 87.250.239.162/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 87.250.239.164/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 87.250.239.166/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 87.250.239.172/31  213.180.213.136  DGU    Eth-Trunk81             -                    
                    87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
 87.250.239.176/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 87.250.239.178/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 87.250.239.180/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 87.250.239.182/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 87.250.239.184/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 87.250.239.186/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 87.250.239.188/30  213.180.213.136  DGU    Eth-Trunk81             -                    
 87.250.239.192/31  213.180.213.136  DGU    Eth-Trunk81             -                    
                    87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
 87.250.239.194/31  213.180.213.136  DGU    Eth-Trunk81             -                    
                    87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
 87.250.239.196/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 87.250.239.198/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 87.250.239.200/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 87.250.239.202/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 87.250.239.204/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 87.250.239.206/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 87.250.239.210/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 87.250.239.212/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 87.250.239.214/31  87.250.239.214   U      Eth-Trunk1.1            -                    
 87.250.239.214/32  127.0.0.1        HU     Eth-Trunk1.1            -                    
 87.250.239.216/31  87.250.239.216   U      Eth-Trunk3.1            -                    
 87.250.239.216/32  127.0.0.1        HU     Eth-Trunk3.1            -                    
 87.250.239.218/31  87.250.239.218   U      Eth-Trunk2.1            -                    
 87.250.239.218/32  127.0.0.1        HU     Eth-Trunk2.1            -                    
 87.250.239.220/31  87.250.239.220   U      Eth-Trunk4.1            -                    
 87.250.239.220/32  127.0.0.1        HU     Eth-Trunk4.1            -                    
 87.250.239.222/31  87.250.239.215   DGU    Eth-Trunk1.1            -                    
 87.250.239.224/31  87.250.239.217   DGU    Eth-Trunk3.1            -                    
 87.250.239.226/31  87.250.239.221   DGU    Eth-Trunk4.1            -                    
 87.250.239.228/31  87.250.239.219   DGU    Eth-Trunk2.1            -                    
 87.250.239.230/31  87.250.239.219   DGU    Eth-Trunk2.1            -                    
 87.250.239.232/31  87.250.239.215   DGU    Eth-Trunk1.1            -                    
 87.250.239.234/31  87.250.239.217   DGU    Eth-Trunk3.1            -                    
 87.250.239.244/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 87.250.239.248/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 87.250.239.250/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 87.250.239.252/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 87.250.239.254/31  87.250.239.221   DGU    Eth-Trunk4.1            -                    
   93.158.160.2/31  213.180.213.136  DGU    Eth-Trunk81             -                    
   93.158.160.6/31  213.180.213.136  DGU    Eth-Trunk81             -                    
  93.158.160.16/31  213.180.213.136  DGU    Eth-Trunk81             -                    
  93.158.160.34/31  213.180.213.136  DGU    Eth-Trunk81             -                    
  93.158.160.40/31  213.180.213.136  DGU    Eth-Trunk81             -                    
  93.158.160.60/31  213.180.213.136  DGU    Eth-Trunk81             -                    
  93.158.160.72/30  213.180.213.136  DGU    Eth-Trunk81             -                    
  93.158.160.82/31  213.180.213.136  DGU    Eth-Trunk81             -                    
                    87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
  93.158.160.86/31  213.180.213.136  DGU    Eth-Trunk81             -                    
  93.158.160.88/31  213.180.213.136  DGU    Eth-Trunk81             -                    
  93.158.160.90/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 93.158.160.102/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 93.158.160.106/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 93.158.160.124/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 93.158.160.126/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 93.158.160.128/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 93.158.160.130/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 93.158.160.132/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 93.158.160.134/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 93.158.160.136/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 93.158.160.138/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 93.158.160.248/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 93.158.160.250/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 93.158.160.252/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 93.158.160.254/31  213.180.213.136  DGU    Eth-Trunk81             -                    
   93.158.172.8/31  213.180.213.136  DGU    Eth-Trunk81             -                    
  93.158.172.10/31  213.180.213.136  DGU    Eth-Trunk81             -                    
  93.158.172.12/31  213.180.213.136  DGU    Eth-Trunk81             -                    
  93.158.172.14/31  213.180.213.136  DGU    Eth-Trunk81             -                    
  93.158.172.16/31  213.180.213.136  DGU    Eth-Trunk81             -                    
  93.158.172.18/31  213.180.213.136  DGU    Eth-Trunk81             -                    
                    87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
  93.158.172.20/31  213.180.213.136  DGU    Eth-Trunk81             -                    
  93.158.172.22/31  213.180.213.136  DGU    Eth-Trunk81             -                    
  93.158.172.24/31  213.180.213.136  DGU    Eth-Trunk81             -                    
  93.158.172.26/31  213.180.213.136  DGU    Eth-Trunk81             -                    
                    87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
  93.158.172.36/31  213.180.213.136  DGU    Eth-Trunk81             -                    
  93.158.172.38/31  213.180.213.136  DGU    Eth-Trunk81             -                    
  93.158.172.50/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 93.158.172.174/31  87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
 93.158.172.188/31  87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
 93.158.172.210/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 93.158.172.212/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 93.158.172.220/31  93.158.172.223   DGU    100GE1/0/31:1.50        -                    
 93.158.172.222/31  93.158.172.222   U      100GE1/0/31:1.50        -                    
 93.158.172.222/32  127.0.0.1        HU     100GE1/0/31:1.50        -                    
 93.158.172.224/31  93.158.172.227   DGU    100GE1/0/31:1.100       -                    
 93.158.172.226/31  93.158.172.226   U      100GE1/0/31:1.100       -                    
 93.158.172.226/32  127.0.0.1        HU     100GE1/0/31:1.100       -                    
 93.158.172.244/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 93.158.172.252/31  213.180.213.136  DGU    Eth-Trunk81             -                    
   95.108.237.1/32  213.180.213.238  DGHU   Eth-Trunk101            0x01004c4b80         
   95.108.237.3/32  87.250.239.215   DGHU   Eth-Trunk1.1            0x01004c4b92         
                    87.250.239.217   DGHU   Eth-Trunk3.1            0x01004c4b92         
                    87.250.239.219   DGHU   Eth-Trunk2.1            0x01004c4b92         
                    87.250.239.221   DGHU   Eth-Trunk4.1            0x01004c4b92         
   95.108.237.4/32  87.250.239.215   DGHU   Eth-Trunk1.1            0x01004c4c83         
                    87.250.239.217   DGHU   Eth-Trunk3.1            0x01004c4c83         
                    87.250.239.219   DGHU   Eth-Trunk2.1            0x01004c4c83         
                    87.250.239.221   DGHU   Eth-Trunk4.1            0x01004c4c83         
   95.108.237.5/32  213.180.213.132  DGHU   Eth-Trunk103            0x01004c4b7b         
  95.108.237.10/32  87.250.239.221   DGHU   Eth-Trunk4.1            0x01004c51c1         
  95.108.237.14/32  87.250.239.215   DGHU   Eth-Trunk1.1            0x01004c4b82         
                    87.250.239.217   DGHU   Eth-Trunk3.1            0x01004c4b82         
                    87.250.239.219   DGHU   Eth-Trunk2.1            0x01004c4b82         
                    87.250.239.221   DGHU   Eth-Trunk4.1            0x01004c4b82         
  95.108.237.19/32  87.250.239.217   DGHU   Eth-Trunk3.1            0x01004c6804         
  95.108.237.20/32  87.250.239.215   DGHU   Eth-Trunk1.1            0x01004c6802         
  95.108.237.27/32  213.180.213.204  DGHU   Eth-Trunk105            0x01004c4b70         
  95.108.237.30/32  213.180.213.200  DGHU   Eth-Trunk104            0x01004c4b86         
  95.108.237.32/32  87.250.239.215   DGHU   Eth-Trunk1.1            0x01004c4b9f         
                    87.250.239.217   DGHU   Eth-Trunk3.1            0x01004c4b9f         
                    87.250.239.219   DGHU   Eth-Trunk2.1            0x01004c4b9f         
                    87.250.239.221   DGHU   Eth-Trunk4.1            0x01004c4b9f         
  95.108.237.38/32  87.250.239.215   DGHU   Eth-Trunk1.1            0x01004c4b85         
                    87.250.239.217   DGHU   Eth-Trunk3.1            0x01004c4b85         
                    87.250.239.219   DGHU   Eth-Trunk2.1            0x01004c4b85         
                    87.250.239.221   DGHU   Eth-Trunk4.1            0x01004c4b85         
  95.108.237.39/32  213.180.213.146  DGHU   Eth-Trunk111            0x01004c6943         
  95.108.237.43/32  127.0.0.1        HU     LoopBack0               -                    
  95.108.237.47/32  87.250.239.219   DGHU   Eth-Trunk2.1            0x01004c5181         
  95.108.237.48/32  87.250.239.215   DGHU   Eth-Trunk1.1            0x01004c4b6f         
                    87.250.239.217   DGHU   Eth-Trunk3.1            0x01004c4b6f         
                    87.250.239.219   DGHU   Eth-Trunk2.1            0x01004c4b6f         
                    87.250.239.221   DGHU   Eth-Trunk4.1            0x01004c4b6f         
  95.108.237.49/32  87.250.239.215   DGHU   Eth-Trunk1.1            0x01004c6944         
                    87.250.239.217   DGHU   Eth-Trunk3.1            0x01004c6944         
                    87.250.239.219   DGHU   Eth-Trunk2.1            0x01004c6944         
                    87.250.239.221   DGHU   Eth-Trunk4.1            0x01004c6944         
  95.108.237.57/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4b87         
  95.108.237.58/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4b88         
  95.108.237.65/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4b83         
  95.108.237.76/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4b4e         
  95.108.237.78/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4b4f         
  95.108.237.96/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c56ca         
 95.108.237.100/32  213.180.213.136  DGHU   Eth-Trunk81             -                    
 95.108.237.141/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c6945         
 95.108.237.142/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c6946         
 95.108.237.171/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4b81         
 95.108.237.172/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4b8e         
 95.108.237.179/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c5f4e         
 95.108.237.253/32  87.250.239.215   DGHU   Eth-Trunk1.1            0x01004c4b50         
                    87.250.239.217   DGHU   Eth-Trunk3.1            0x01004c4b50         
                    87.250.239.219   DGHU   Eth-Trunk2.1            0x01004c4b50         
                    87.250.239.221   DGHU   Eth-Trunk4.1            0x01004c4b50         
                    213.180.213.136  DGHU   Eth-Trunk81             0x01004c4b50         
  100.43.92.159/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c5541         
      127.0.0.0/8   127.0.0.1        U      InLoopBack0             -                    
      127.0.0.1/32  127.0.0.1        HU     InLoopBack0             -                    
127.255.255.255/32  127.0.0.1        U      InLoopBack0             -                    
  141.8.136.128/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4b91         
  141.8.136.129/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4b8b         
  141.8.136.227/32  87.250.239.215   DGHU   Eth-Trunk1.1            0x01004c4b51         
                    87.250.239.217   DGHU   Eth-Trunk3.1            0x01004c4b51         
                    87.250.239.219   DGHU   Eth-Trunk2.1            0x01004c4b51         
                    87.250.239.221   DGHU   Eth-Trunk4.1            0x01004c4b51         
                    213.180.213.136  DGHU   Eth-Trunk81             0x01004c4b51         
  141.8.136.239/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4b52         
  141.8.136.255/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c58c3         
  141.8.140.160/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4b54         
  141.8.140.161/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4b55         
  141.8.140.162/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4b56         
  141.8.140.163/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4b57         
  141.8.140.164/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4b58         
  141.8.140.165/32  213.180.213.136  DGHU   Eth-Trunk81             0x01004c4b59         
     172.16.6.0/32  10.255.0.154     DGHU   Eth-Trunk161            0x01004c58c2         
  172.16.10.160/32  213.180.213.136  DGHU   Eth-Trunk81             -                    
  213.180.213.0/31  213.180.213.136  DGU    Eth-Trunk81             -                    
  213.180.213.2/31  213.180.213.136  DGU    Eth-Trunk81             -                    
  213.180.213.4/31  213.180.213.132  DGU    Eth-Trunk103            -                    
  213.180.213.6/31  213.180.213.136  DGU    Eth-Trunk81             -                    
  213.180.213.8/31  213.180.213.132  DGU    Eth-Trunk103            -                    
 213.180.213.10/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 213.180.213.12/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 213.180.213.14/31  87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
 213.180.213.16/31  87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
 213.180.213.18/31  213.180.213.136  DGU    Eth-Trunk81             -                    
                    87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
 213.180.213.20/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 213.180.213.22/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 213.180.213.26/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 213.180.213.32/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 213.180.213.34/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 213.180.213.38/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 213.180.213.56/31  87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
 213.180.213.68/31  213.180.213.136  DGU    Eth-Trunk81             -                    
                    87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
 213.180.213.88/31  213.180.213.136  DGU    Eth-Trunk81             -                    
                    87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
 213.180.213.90/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 213.180.213.92/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 213.180.213.94/31  213.180.213.136  DGU    Eth-Trunk81             -                    
 213.180.213.96/31  213.180.213.136  DGU    Eth-Trunk81             -                    
213.180.213.104/31  213.180.213.136  DGU    Eth-Trunk81             -                    
213.180.213.120/31  213.180.213.136  DGU    Eth-Trunk81             -                    
213.180.213.124/31  213.180.213.136  DGU    Eth-Trunk81             -                    
213.180.213.128/31  213.180.213.136  DGU    Eth-Trunk81             -                    
213.180.213.130/31  87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
213.180.213.132/31  213.180.213.133  U      Eth-Trunk103            -                    
213.180.213.133/32  127.0.0.1        HU     Eth-Trunk103            -                    
213.180.213.134/31  87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
213.180.213.136/31  213.180.213.137  U      Eth-Trunk81             -                    
213.180.213.137/32  127.0.0.1        HU     Eth-Trunk81             -                    
213.180.213.138/31  87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
213.180.213.140/31  213.180.213.136  DGU    Eth-Trunk81             -                    
213.180.213.142/31  213.180.213.136  DGU    Eth-Trunk81             -                    
213.180.213.144/31  87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
213.180.213.146/31  213.180.213.147  U      Eth-Trunk111            -                    
213.180.213.147/32  127.0.0.1        HU     Eth-Trunk111            -                    
213.180.213.162/31  213.180.213.136  DGU    Eth-Trunk81             -                    
213.180.213.164/31  213.180.213.136  DGU    Eth-Trunk81             -                    
213.180.213.166/31  213.180.213.136  DGU    Eth-Trunk81             -                    
213.180.213.168/31  213.180.213.136  DGU    Eth-Trunk81             -                    
213.180.213.170/31  213.180.213.136  DGU    Eth-Trunk81             -                    
                    87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
213.180.213.172/31  213.180.213.136  DGU    Eth-Trunk81             -                    
213.180.213.174/31  213.180.213.136  DGU    Eth-Trunk81             -                    
                    87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
213.180.213.178/31  213.180.213.136  DGU    Eth-Trunk81             -                    
213.180.213.188/30  213.180.213.136  DGU    Eth-Trunk81             -                    
213.180.213.192/31  213.180.213.136  DGU    Eth-Trunk81             -                    
213.180.213.194/31  213.180.213.136  DGU    Eth-Trunk81             -                    
213.180.213.196/31  213.180.213.136  DGU    Eth-Trunk81             -                    
213.180.213.198/31  213.180.213.200  DGU    Eth-Trunk104            -                    
213.180.213.200/31  213.180.213.201  U      Eth-Trunk104            -                    
213.180.213.201/32  127.0.0.1        HU     Eth-Trunk104            -                    
213.180.213.202/31  213.180.213.204  DGU    Eth-Trunk105            -                    
213.180.213.204/31  213.180.213.205  U      Eth-Trunk105            -                    
213.180.213.205/32  127.0.0.1        HU     Eth-Trunk105            -                    
213.180.213.206/31  213.180.213.136  DGU    Eth-Trunk81             -                    
213.180.213.208/31  87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
213.180.213.210/31  87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
213.180.213.212/31  213.180.213.136  DGU    Eth-Trunk81             -                    
213.180.213.220/31  87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
213.180.213.222/31  87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
213.180.213.224/31  213.180.213.136  DGU    Eth-Trunk81             -                    
213.180.213.226/31  213.180.213.136  DGU    Eth-Trunk81             -                    
213.180.213.228/31  213.180.213.136  DGU    Eth-Trunk81             -                    
213.180.213.230/31  213.180.213.136  DGU    Eth-Trunk81             -                    
213.180.213.232/31  213.180.213.136  DGU    Eth-Trunk81             -                    
213.180.213.234/31  213.180.213.136  DGU    Eth-Trunk81             -                    
213.180.213.236/31  213.180.213.136  DGU    Eth-Trunk81             -                    
213.180.213.238/31  213.180.213.239  U      Eth-Trunk101            -                    
213.180.213.239/32  127.0.0.1        HU     Eth-Trunk101            -                    
213.180.213.240/31  213.180.213.238  DGU    Eth-Trunk101            -                    
213.180.213.242/31  87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
213.180.213.244/31  87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
213.180.213.248/31  213.180.213.136  DGU    Eth-Trunk81             -                    
                    87.250.239.221   DGU    Eth-Trunk4.1            -                    
                    87.250.239.219   DGU    Eth-Trunk2.1            -                    
                    87.250.239.217   DGU    Eth-Trunk3.1            -                    
                    87.250.239.215   DGU    Eth-Trunk1.1            -                    
213.180.213.252/31  213.180.213.136  DGU    Eth-Trunk81             -                     
    """
    cmd = "dis ip fib slot 2"
    host = "myt-e2.yndx.net"
    version = """
Huawei Versatile Routing Platform Software
VRP (R) software, Version 8.191 (CE12800 V200R019C10SPC800)
Copyright (C) 2012-2020 Huawei Technologies Co., Ltd.
HUAWEI CE12804 uptime is 222 days, 3 hours, 21 minutes
Patch Version: V200R019SPH007

BKP  version information:
1.PCB      Version  : DE01BAK04A VER C
2.Board    Type     : CE-BAK04A 
3.MPU Slot Quantity : 2
4.LPU Slot Quantity : 4
5.SFU Slot Quantity : 6

MPU(Master) 5 : uptime is  222 days, 3 hours, 20 minutes
        StartupTime 2021/04/02   12:16:05+03:00
Memory     Size     : 16384 M bytes
Flash      Size     : 4096 M bytes
MPU version information:                             
1.PCB      Version  : CE01MPUB VER B
2.MAB      Version  : 1
3.Board    Type     : CE-MPUB
4.CPLD1    Version  : 270
5.BIOS     Version  : 1102
 
MPU(Slave) 6 : uptime is  222 days, 3 hours, 20 minutes
        StartupTime 2021/04/02   12:16:11+03:00
Memory     Size     : 16384 M bytes
Flash      Size     : 4096 M bytes
MPU version information:                             
1.PCB      Version  : CE01MPUB VER B
2.MAB      Version  : 1
3.Board    Type     : CE-MPUB
4.CPLD1    Version  : 270
5.BIOS     Version  : 1102
 
LPU 1 : uptime is 222 days, 3 hours, 13 minutes
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

LPU 2 : uptime is 222 days, 3 hours, 14 minutes
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

SFU 9 : uptime is 222 days, 3 hours, 20 minutes
        StartupTime 2021/04/02   12:16:37+03:00
Memory     Size     : 512 M bytes
Flash      Size     : 64  M bytes
SFU version information:
1.PCB      Version  : CESFU04G VER A
2.MAB      Version  : 1
3.Board    Type     : CE-SFU04G
4.CPLD1    Version  : 101
5.BIOS     Version  : 439

SFU 10 : uptime is 222 days, 3 hours, 20 minutes
        StartupTime 2021/04/02   12:16:37+03:00
Memory     Size     : 512 M bytes
Flash      Size     : 64  M bytes
SFU version information:
1.PCB      Version  : CESFU04G VER A
2.MAB      Version  : 1
3.Board    Type     : CE-SFU04G
4.CPLD1    Version  : 101
5.BIOS     Version  : 439

SFU 11 : uptime is 222 days, 3 hours, 20 minutes
        StartupTime 2021/04/02   12:16:37+03:00
Memory     Size     : 512 M bytes
Flash      Size     : 64  M bytes
SFU version information:
1.PCB      Version  : CESFU04G VER A
2.MAB      Version  : 1
3.Board    Type     : CE-SFU04G
4.CPLD1    Version  : 101
5.BIOS     Version  : 439

SFU 12 : uptime is 222 days, 3 hours, 20 minutes
        StartupTime 2021/04/02   12:16:37+03:00
Memory     Size     : 512 M bytes
Flash      Size     : 64  M bytes
SFU version information:
1.PCB      Version  : CESFU04G VER A
2.MAB      Version  : 1
3.Board    Type     : CE-SFU04G
4.CPLD1    Version  : 101
5.BIOS     Version  : 439

SFU 13 : uptime is 222 days, 3 hours, 20 minutes
        StartupTime 2021/04/02   12:16:37+03:00
Memory     Size     : 512 M bytes
Flash      Size     : 64  M bytes
SFU version information:
1.PCB      Version  : CESFU04G VER A
2.MAB      Version  : 1
3.Board    Type     : CE-SFU04G
4.CPLD1    Version  : 101
5.BIOS     Version  : 439

CMU(Master) 7 : uptime is 220 days, 20 hours, 14 minutes
        StartupTime 2021/04/02   15:16:16+03:00
Memory     Size     : 128 M bytes
Flash      Size     : 32  M bytes
CMU version information:
1.PCB      Version  : DE01CMUA VER B
2.MAB      Version  : 1
3.Board    Type     : CE-CMUA
4.CPLD1    Version  : 104
5.BIOS     Version  : 127

CMU(Slave) 8 : uptime is 221 days, 6 hours, 0 minute
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
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "5.45.247.180/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "10.255.0.1/32",
            "nh": "10.255.0.154",
            "flags": "DGHU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.2/32",
            "nh": "10.255.0.154",
            "flags": "DGHU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.5/32",
            "nh": "10.255.0.131",
            "flags": "DGHU",
            "iface": "Eth-Trunk4.10",
        },
        {
            "prefix": "10.255.0.6/32",
            "nh": "10.255.0.157",
            "flags": "DGHU",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.0.8/32",
            "nh": "10.255.0.139",
            "flags": "DGHU",
            "iface": "Eth-Trunk1.10",
        },
        {
            "prefix": "10.255.0.9/32",
            "nh": "10.255.0.154",
            "flags": "DGHU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.10/32",
            "nh": "10.255.0.131",
            "flags": "DGHU",
            "iface": "Eth-Trunk4.10",
        },
        {
            "prefix": "10.255.0.11/32",
            "nh": "10.255.0.131",
            "flags": "DGHU",
            "iface": "Eth-Trunk4.10",
        },
        {
            "prefix": "10.255.0.12/32",
            "nh": "10.255.0.154",
            "flags": "DGHU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.13/32",
            "nh": "10.255.0.154",
            "flags": "DGHU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.14/32",
            "nh": "127.0.0.1",
            "flags": "HU",
            "iface": "LoopBack10",
        },
        {
            "prefix": "10.255.0.15/32",
            "nh": "10.255.0.154",
            "flags": "DGHU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.16/32",
            "nh": "10.255.0.154",
            "flags": "DGHU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.17/32",
            "nh": "10.255.0.154",
            "flags": "DGHU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.18/32",
            "nh": "10.255.0.149",
            "flags": "DGHU",
            "iface": "Eth-Trunk2.10",
        },
        {
            "prefix": "10.255.0.19/32",
            "nh": "10.255.0.154",
            "flags": "DGHU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.20/32",
            "nh": "10.255.0.154",
            "flags": "DGHU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.21/32",
            "nh": "10.255.0.154",
            "flags": "DGHU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.22/32",
            "nh": "10.255.0.154",
            "flags": "DGHU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.30/32",
            "nh": "10.255.0.157",
            "flags": "DGHU",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.0.34/32",
            "nh": "10.255.0.154",
            "flags": "DGHU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.35/32",
            "nh": "10.255.0.154",
            "flags": "DGHU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.36/32",
            "nh": "10.255.0.154",
            "flags": "DGHU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.37/32",
            "nh": "10.255.0.154",
            "flags": "DGHU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.41/32",
            "nh": "10.255.0.154",
            "flags": "DGHU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.42/32",
            "nh": "10.255.0.154",
            "flags": "DGHU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.43/32",
            "nh": "10.255.0.154",
            "flags": "DGHU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.44/32",
            "nh": "10.255.0.154",
            "flags": "DGHU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.45/32",
            "nh": "10.255.0.154",
            "flags": "DGHU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.46/32",
            "nh": "10.255.0.154",
            "flags": "DGHU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.52/32",
            "nh": "10.255.0.154",
            "flags": "DGHU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.53/32",
            "nh": "10.255.0.154",
            "flags": "DGHU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.55/32",
            "nh": "10.255.0.154",
            "flags": "DGHU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.56/32",
            "nh": "10.255.0.131",
            "flags": "DGHU",
            "iface": "Eth-Trunk4.10",
        },
        {
            "prefix": "10.255.0.59/32",
            "nh": "10.255.0.131",
            "flags": "DGHU",
            "iface": "Eth-Trunk4.10",
        },
        {
            "prefix": "10.255.0.61/32",
            "nh": "10.255.0.154",
            "flags": "DGHU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.63/32",
            "nh": "10.255.0.154",
            "flags": "DGHU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.64/32",
            "nh": "10.255.0.154",
            "flags": "DGHU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.65/32",
            "nh": "10.255.0.154",
            "flags": "DGHU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.66/32",
            "nh": "10.255.0.154",
            "flags": "DGHU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.67/32",
            "nh": "10.255.0.154",
            "flags": "DGHU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.68/32",
            "nh": "10.255.0.131",
            "flags": "DGHU",
            "iface": "Eth-Trunk4.10",
        },
        {
            "prefix": "10.255.0.69/32",
            "nh": "10.255.0.154",
            "flags": "DGHU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.71/32",
            "nh": "10.255.0.154",
            "flags": "DGHU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.75/32",
            "nh": "10.255.0.154",
            "flags": "DGHU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.99/32",
            "nh": "10.255.0.154",
            "flags": "DGHU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.100/32",
            "nh": "10.255.0.154",
            "flags": "DGHU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.104/32",
            "nh": "10.255.0.154",
            "flags": "DGHU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.130/31",
            "nh": "10.255.0.130",
            "flags": "U",
            "iface": "Eth-Trunk4.10",
        },
        {
            "prefix": "10.255.0.130/32",
            "nh": "127.0.0.1",
            "flags": "HU",
            "iface": "Eth-Trunk4.10",
        },
        {
            "prefix": "10.255.0.138/31",
            "nh": "10.255.0.138",
            "flags": "U",
            "iface": "Eth-Trunk1.10",
        },
        {
            "prefix": "10.255.0.138/32",
            "nh": "127.0.0.1",
            "flags": "HU",
            "iface": "Eth-Trunk1.10",
        },
        {
            "prefix": "10.255.0.146/31",
            "nh": "10.255.0.154",
            "flags": "DGU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.148/31",
            "nh": "10.255.0.148",
            "flags": "U",
            "iface": "Eth-Trunk2.10",
        },
        {
            "prefix": "10.255.0.148/32",
            "nh": "127.0.0.1",
            "flags": "HU",
            "iface": "Eth-Trunk2.10",
        },
        {
            "prefix": "10.255.0.150/31",
            "nh": "10.255.0.157",
            "flags": "DGU",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.0.152/31",
            "nh": "10.255.0.154",
            "flags": "DGU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.154/31",
            "nh": "10.255.0.155",
            "flags": "U",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.155/32",
            "nh": "127.0.0.1",
            "flags": "HU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.156/31",
            "nh": "10.255.0.156",
            "flags": "U",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.0.156/32",
            "nh": "127.0.0.1",
            "flags": "HU",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.0.158/31",
            "nh": "10.255.0.157",
            "flags": "DGU",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.0.160/31",
            "nh": "10.255.0.157",
            "flags": "DGU",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.0.162/31",
            "nh": "10.255.0.157",
            "flags": "DGU",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.0.164/31",
            "nh": "10.255.0.154",
            "flags": "DGU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.166/31",
            "nh": "10.255.0.157",
            "flags": "DGU",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.0.170/31",
            "nh": "10.255.0.154",
            "flags": "DGU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.172/31",
            "nh": "10.255.0.157",
            "flags": "DGU",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.0.174/31",
            "nh": "10.255.0.157",
            "flags": "DGU",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.0.176/31",
            "nh": "10.255.0.157",
            "flags": "DGU",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.0.182/31",
            "nh": "10.255.0.154",
            "flags": "DGU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.190/31",
            "nh": "10.255.0.154",
            "flags": "DGU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.194/31",
            "nh": "10.255.0.157",
            "flags": "DGU",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.0.196/31",
            "nh": "10.255.0.157",
            "flags": "DGU",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.0.204/31",
            "nh": "10.255.0.154",
            "flags": "DGU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.210/31",
            "nh": "10.255.0.157",
            "flags": "DGU",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.0.212/31",
            "nh": "10.255.0.157",
            "flags": "DGU",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.0.224/31",
            "nh": "10.255.0.157",
            "flags": "DGU",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.0.226/31",
            "nh": "10.255.0.154",
            "flags": "DGU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.228/31",
            "nh": "10.255.0.157",
            "flags": "DGU",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.0.232/31",
            "nh": "10.255.0.154",
            "flags": "DGU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.234/31",
            "nh": "10.255.0.157",
            "flags": "DGU",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.0.236/31",
            "nh": "10.255.0.154",
            "flags": "DGU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.238/31",
            "nh": "10.255.0.157",
            "flags": "DGU",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.0.240/31",
            "nh": "10.255.0.154",
            "flags": "DGU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.248/31",
            "nh": "10.255.0.154",
            "flags": "DGU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.250/31",
            "nh": "10.255.0.154",
            "flags": "DGU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.0.252/31",
            "nh": "10.255.0.157",
            "flags": "DGU",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.1.0/31",
            "nh": "10.255.0.154",
            "flags": "DGU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.1.2/31",
            "nh": "10.255.0.157",
            "flags": "DGU",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.1.4/31",
            "nh": "10.255.0.154",
            "flags": "DGU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.1.6/31",
            "nh": "10.255.0.157",
            "flags": "DGU",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.1.220/31",
            "nh": "10.255.0.157",
            "flags": "DGU",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.1.222/31",
            "nh": "10.255.0.157",
            "flags": "DGU",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.1.224/31",
            "nh": "10.255.0.157",
            "flags": "DGU",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.1.226/31",
            "nh": "10.255.0.157",
            "flags": "DGU",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.1.228/31",
            "nh": "10.255.0.157",
            "flags": "DGU",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.1.230/31",
            "nh": "10.255.0.157",
            "flags": "DGU",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.1.232/31",
            "nh": "10.255.0.154",
            "flags": "DGU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.1.234/31",
            "nh": "10.255.0.154",
            "flags": "DGU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.1.236/31",
            "nh": "10.255.0.154",
            "flags": "DGU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.1.238/31",
            "nh": "10.255.0.154",
            "flags": "DGU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.1.240/31",
            "nh": "10.255.0.154",
            "flags": "DGU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.1.242/31",
            "nh": "10.255.0.154",
            "flags": "DGU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.2.8/31",
            "nh": "10.255.0.157",
            "flags": "DGU",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.2.12/31",
            "nh": "10.255.0.157",
            "flags": "DGU",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.2.16/31",
            "nh": "10.255.0.157",
            "flags": "DGU",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.2.18/31",
            "nh": "10.255.0.157",
            "flags": "DGU",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.2.20/31",
            "nh": "10.255.0.154",
            "flags": "DGU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.2.22/31",
            "nh": "10.255.0.154",
            "flags": "DGU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.2.24/31",
            "nh": "10.255.0.157",
            "flags": "DGU",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.2.36/31",
            "nh": "10.255.0.157",
            "flags": "DGU",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.2.192/31",
            "nh": "10.255.0.157",
            "flags": "DGU",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.2.194/31",
            "nh": "10.255.0.157",
            "flags": "DGU",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.2.198/31",
            "nh": "10.255.0.154",
            "flags": "DGU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.2.202/31",
            "nh": "10.255.0.154",
            "flags": "DGU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.2.204/31",
            "nh": "10.255.0.154",
            "flags": "DGU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.2.224/31",
            "nh": "10.255.0.154",
            "flags": "DGU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.2.226/31",
            "nh": "10.255.0.157",
            "flags": "DGU",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.3.0/31",
            "nh": "10.255.0.157",
            "flags": "DGU",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.3.26/31",
            "nh": "10.255.0.154",
            "flags": "DGU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.3.60/31",
            "nh": "10.255.0.154",
            "flags": "DGU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.3.66/31",
            "nh": "10.255.0.157",
            "flags": "DGU",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.3.68/31",
            "nh": "10.255.0.154",
            "flags": "DGU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.3.70/31",
            "nh": "10.255.0.154",
            "flags": "DGU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.3.72/31",
            "nh": "10.255.0.157",
            "flags": "DGU",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.3.76/31",
            "nh": "10.255.0.154",
            "flags": "DGU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.3.78/31",
            "nh": "10.255.0.154",
            "flags": "DGU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.3.80/31",
            "nh": "10.255.0.157",
            "flags": "DGU",
            "iface": "Eth-Trunk3.10",
        },
        {
            "prefix": "10.255.3.90/31",
            "nh": "10.255.0.154",
            "flags": "DGU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.3.94/31",
            "nh": "10.255.0.154",
            "flags": "DGU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.3.104/31",
            "nh": "10.255.0.154",
            "flags": "DGU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.3.108/31",
            "nh": "10.255.0.154",
            "flags": "DGU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.3.110/31",
            "nh": "10.255.0.154",
            "flags": "DGU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.3.112/31",
            "nh": "10.255.0.154",
            "flags": "DGU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.3.114/31",
            "nh": "10.255.0.154",
            "flags": "DGU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "10.255.3.116/31",
            "nh": "10.255.0.154",
            "flags": "DGU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "87.250.226.99/32",
            "nh": "87.250.239.215",
            "flags": "DGHU",
            "iface": "Eth-Trunk1.1",
        },
        {
            "prefix": "87.250.226.122/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.226.134/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.226.135/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.226.136/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.226.141/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.226.142/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.226.143/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.226.155/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.226.156/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.226.157/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.226.158/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.226.159/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.226.160/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.226.162/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.226.194/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.226.195/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.226.196/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.226.197/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.228.28/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.228.145/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.228.146/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.228.149/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.228.150/32",
            "nh": "87.250.239.215",
            "flags": "DGHU",
            "iface": "Eth-Trunk1.1",
        },
        {
            "prefix": "87.250.228.152/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.228.153/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.228.167/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.228.168/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.228.177/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.228.198/32",
            "nh": "87.250.239.215",
            "flags": "DGHU",
            "iface": "Eth-Trunk1.1",
        },
        {
            "prefix": "87.250.228.199/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.228.224/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.228.226/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.228.228/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.228.230/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.228.231/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.228.232/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.228.233/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.228.237/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.228.238/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.228.239/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.233.131/32",
            "nh": "87.250.239.215",
            "flags": "DGHU",
            "iface": "Eth-Trunk1.1",
        },
        {
            "prefix": "87.250.233.132/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.233.133/32",
            "nh": "87.250.239.215",
            "flags": "DGHU",
            "iface": "Eth-Trunk1.1",
        },
        {
            "prefix": "87.250.233.135/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.233.136/32",
            "nh": "87.250.239.215",
            "flags": "DGHU",
            "iface": "Eth-Trunk1.1",
        },
        {
            "prefix": "87.250.233.141/32",
            "nh": "87.250.239.221",
            "flags": "DGHU",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "87.250.233.150/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.233.166/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.233.190/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.233.199/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.233.200/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.233.233/32",
            "nh": "87.250.239.215",
            "flags": "DGHU",
            "iface": "Eth-Trunk1.1",
        },
        {
            "prefix": "87.250.233.248/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.234.0/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.234.2/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.234.8/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.234.12/32",
            "nh": "93.158.172.227",
            "flags": "DGHU",
            "iface": "100GE1/0/31:1.100",
        },
        {
            "prefix": "87.250.234.14/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.234.16/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.234.18/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.234.19/32",
            "nh": "93.158.172.223",
            "flags": "DGHU",
            "iface": "100GE1/0/31:1.50",
        },
        {
            "prefix": "87.250.234.21/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.234.22/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.234.41/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.234.121/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.234.179/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.234.234/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.234.255/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.0/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.4/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.6/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.8/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.10/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.12/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.14/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.16/31",
            "nh": "87.250.239.221",
            "flags": "DGU",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "87.250.239.18/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.20/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.24/31",
            "nh": "87.250.239.221",
            "flags": "DGU",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "87.250.239.26/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.30/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.32/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.34/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.36/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.38/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.40/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.42/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.44/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.50/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.52/31",
            "nh": "87.250.239.215",
            "flags": "DGU",
            "iface": "Eth-Trunk1.1",
        },
        {
            "prefix": "87.250.239.54/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.58/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.62/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.64/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.66/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.68/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.70/31",
            "nh": "87.250.239.219",
            "flags": "DGU",
            "iface": "Eth-Trunk2.1",
        },
        {
            "prefix": "87.250.239.72/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.74/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.76/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.78/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.80/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.82/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.84/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.86/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.90/31",
            "nh": "87.250.239.221",
            "flags": "DGU",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "87.250.239.92/31",
            "nh": "87.250.239.221",
            "flags": "DGU",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "87.250.239.94/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.96/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.100/31",
            "nh": "87.250.239.221",
            "flags": "DGU",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "87.250.239.104/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.106/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.108/31",
            "nh": "87.250.239.217",
            "flags": "DGU",
            "iface": "Eth-Trunk3.1",
        },
        {
            "prefix": "87.250.239.110/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.112/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.114/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.116/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.118/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.122/31",
            "nh": "87.250.239.221",
            "flags": "DGU",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "87.250.239.124/31",
            "nh": "87.250.239.221",
            "flags": "DGU",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "87.250.239.126/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.128/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.132/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.136/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.138/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.140/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.144/29",
            "nh": "87.250.239.221",
            "flags": "DGU",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "87.250.239.152/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.154/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.162/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.164/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.166/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.172/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.176/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.178/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.180/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.182/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.184/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.186/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.188/30",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.192/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.194/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.196/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.198/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.200/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.202/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.204/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.206/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.210/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.212/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.214/31",
            "nh": "87.250.239.214",
            "flags": "U",
            "iface": "Eth-Trunk1.1",
        },
        {
            "prefix": "87.250.239.214/32",
            "nh": "127.0.0.1",
            "flags": "HU",
            "iface": "Eth-Trunk1.1",
        },
        {
            "prefix": "87.250.239.216/31",
            "nh": "87.250.239.216",
            "flags": "U",
            "iface": "Eth-Trunk3.1",
        },
        {
            "prefix": "87.250.239.216/32",
            "nh": "127.0.0.1",
            "flags": "HU",
            "iface": "Eth-Trunk3.1",
        },
        {
            "prefix": "87.250.239.218/31",
            "nh": "87.250.239.218",
            "flags": "U",
            "iface": "Eth-Trunk2.1",
        },
        {
            "prefix": "87.250.239.218/32",
            "nh": "127.0.0.1",
            "flags": "HU",
            "iface": "Eth-Trunk2.1",
        },
        {
            "prefix": "87.250.239.220/31",
            "nh": "87.250.239.220",
            "flags": "U",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "87.250.239.220/32",
            "nh": "127.0.0.1",
            "flags": "HU",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "87.250.239.222/31",
            "nh": "87.250.239.215",
            "flags": "DGU",
            "iface": "Eth-Trunk1.1",
        },
        {
            "prefix": "87.250.239.224/31",
            "nh": "87.250.239.217",
            "flags": "DGU",
            "iface": "Eth-Trunk3.1",
        },
        {
            "prefix": "87.250.239.226/31",
            "nh": "87.250.239.221",
            "flags": "DGU",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "87.250.239.228/31",
            "nh": "87.250.239.219",
            "flags": "DGU",
            "iface": "Eth-Trunk2.1",
        },
        {
            "prefix": "87.250.239.230/31",
            "nh": "87.250.239.219",
            "flags": "DGU",
            "iface": "Eth-Trunk2.1",
        },
        {
            "prefix": "87.250.239.232/31",
            "nh": "87.250.239.215",
            "flags": "DGU",
            "iface": "Eth-Trunk1.1",
        },
        {
            "prefix": "87.250.239.234/31",
            "nh": "87.250.239.217",
            "flags": "DGU",
            "iface": "Eth-Trunk3.1",
        },
        {
            "prefix": "87.250.239.244/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.248/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.250/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.252/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "87.250.239.254/31",
            "nh": "87.250.239.221",
            "flags": "DGU",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "93.158.160.2/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.6/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.16/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.34/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.40/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.60/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.72/30",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.82/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.86/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.88/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.90/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.102/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.106/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.124/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.126/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.128/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.130/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.132/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.134/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.136/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.138/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.248/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.250/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.252/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.160.254/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.172.8/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.172.10/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.172.12/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.172.14/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.172.16/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.172.18/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.172.20/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.172.22/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.172.24/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.172.26/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.172.36/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.172.38/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.172.50/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.172.174/31",
            "nh": "87.250.239.221",
            "flags": "DGU",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "93.158.172.188/31",
            "nh": "87.250.239.221",
            "flags": "DGU",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "93.158.172.210/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.172.212/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.172.220/31",
            "nh": "93.158.172.223",
            "flags": "DGU",
            "iface": "100GE1/0/31:1.50",
        },
        {
            "prefix": "93.158.172.222/31",
            "nh": "93.158.172.222",
            "flags": "U",
            "iface": "100GE1/0/31:1.50",
        },
        {
            "prefix": "93.158.172.222/32",
            "nh": "127.0.0.1",
            "flags": "HU",
            "iface": "100GE1/0/31:1.50",
        },
        {
            "prefix": "93.158.172.224/31",
            "nh": "93.158.172.227",
            "flags": "DGU",
            "iface": "100GE1/0/31:1.100",
        },
        {
            "prefix": "93.158.172.226/31",
            "nh": "93.158.172.226",
            "flags": "U",
            "iface": "100GE1/0/31:1.100",
        },
        {
            "prefix": "93.158.172.226/32",
            "nh": "127.0.0.1",
            "flags": "HU",
            "iface": "100GE1/0/31:1.100",
        },
        {
            "prefix": "93.158.172.244/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "93.158.172.252/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "95.108.237.1/32",
            "nh": "213.180.213.238",
            "flags": "DGHU",
            "iface": "Eth-Trunk101",
        },
        {
            "prefix": "95.108.237.3/32",
            "nh": "87.250.239.215",
            "flags": "DGHU",
            "iface": "Eth-Trunk1.1",
        },
        {
            "prefix": "95.108.237.4/32",
            "nh": "87.250.239.215",
            "flags": "DGHU",
            "iface": "Eth-Trunk1.1",
        },
        {
            "prefix": "95.108.237.5/32",
            "nh": "213.180.213.132",
            "flags": "DGHU",
            "iface": "Eth-Trunk103",
        },
        {
            "prefix": "95.108.237.10/32",
            "nh": "87.250.239.221",
            "flags": "DGHU",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "95.108.237.14/32",
            "nh": "87.250.239.215",
            "flags": "DGHU",
            "iface": "Eth-Trunk1.1",
        },
        {
            "prefix": "95.108.237.19/32",
            "nh": "87.250.239.217",
            "flags": "DGHU",
            "iface": "Eth-Trunk3.1",
        },
        {
            "prefix": "95.108.237.20/32",
            "nh": "87.250.239.215",
            "flags": "DGHU",
            "iface": "Eth-Trunk1.1",
        },
        {
            "prefix": "95.108.237.27/32",
            "nh": "213.180.213.204",
            "flags": "DGHU",
            "iface": "Eth-Trunk105",
        },
        {
            "prefix": "95.108.237.30/32",
            "nh": "213.180.213.200",
            "flags": "DGHU",
            "iface": "Eth-Trunk104",
        },
        {
            "prefix": "95.108.237.32/32",
            "nh": "87.250.239.215",
            "flags": "DGHU",
            "iface": "Eth-Trunk1.1",
        },
        {
            "prefix": "95.108.237.38/32",
            "nh": "87.250.239.215",
            "flags": "DGHU",
            "iface": "Eth-Trunk1.1",
        },
        {
            "prefix": "95.108.237.39/32",
            "nh": "213.180.213.146",
            "flags": "DGHU",
            "iface": "Eth-Trunk111",
        },
        {
            "prefix": "95.108.237.43/32",
            "nh": "127.0.0.1",
            "flags": "HU",
            "iface": "LoopBack0",
        },
        {
            "prefix": "95.108.237.47/32",
            "nh": "87.250.239.219",
            "flags": "DGHU",
            "iface": "Eth-Trunk2.1",
        },
        {
            "prefix": "95.108.237.48/32",
            "nh": "87.250.239.215",
            "flags": "DGHU",
            "iface": "Eth-Trunk1.1",
        },
        {
            "prefix": "95.108.237.49/32",
            "nh": "87.250.239.215",
            "flags": "DGHU",
            "iface": "Eth-Trunk1.1",
        },
        {
            "prefix": "95.108.237.57/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "95.108.237.58/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "95.108.237.65/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "95.108.237.76/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "95.108.237.78/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "95.108.237.96/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "95.108.237.100/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "95.108.237.141/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "95.108.237.142/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "95.108.237.171/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "95.108.237.172/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "95.108.237.179/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "95.108.237.253/32",
            "nh": "87.250.239.215",
            "flags": "DGHU",
            "iface": "Eth-Trunk1.1",
        },
        {
            "prefix": "100.43.92.159/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "127.0.0.0/8",
            "nh": "127.0.0.1",
            "flags": "U",
            "iface": "InLoopBack0",
        },
        {
            "prefix": "127.0.0.1/32",
            "nh": "127.0.0.1",
            "flags": "HU",
            "iface": "InLoopBack0",
        },
        {
            "prefix": "127.255.255.255/32",
            "nh": "127.0.0.1",
            "flags": "U",
            "iface": "InLoopBack0",
        },
        {
            "prefix": "141.8.136.128/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "141.8.136.129/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "141.8.136.227/32",
            "nh": "87.250.239.215",
            "flags": "DGHU",
            "iface": "Eth-Trunk1.1",
        },
        {
            "prefix": "141.8.136.239/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "141.8.136.255/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "141.8.140.160/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "141.8.140.161/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "141.8.140.162/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "141.8.140.163/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "141.8.140.164/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "141.8.140.165/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "172.16.6.0/32",
            "nh": "10.255.0.154",
            "flags": "DGHU",
            "iface": "Eth-Trunk161",
        },
        {
            "prefix": "172.16.10.160/32",
            "nh": "213.180.213.136",
            "flags": "DGHU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.0/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.2/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.4/31",
            "nh": "213.180.213.132",
            "flags": "DGU",
            "iface": "Eth-Trunk103",
        },
        {
            "prefix": "213.180.213.6/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.8/31",
            "nh": "213.180.213.132",
            "flags": "DGU",
            "iface": "Eth-Trunk103",
        },
        {
            "prefix": "213.180.213.10/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.12/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.14/31",
            "nh": "87.250.239.221",
            "flags": "DGU",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "213.180.213.16/31",
            "nh": "87.250.239.221",
            "flags": "DGU",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "213.180.213.18/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.20/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.22/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.26/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.32/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.34/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.38/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.56/31",
            "nh": "87.250.239.221",
            "flags": "DGU",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "213.180.213.68/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.88/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.90/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.92/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.94/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.96/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.104/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.120/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.124/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.128/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.130/31",
            "nh": "87.250.239.221",
            "flags": "DGU",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "213.180.213.132/31",
            "nh": "213.180.213.133",
            "flags": "U",
            "iface": "Eth-Trunk103",
        },
        {
            "prefix": "213.180.213.133/32",
            "nh": "127.0.0.1",
            "flags": "HU",
            "iface": "Eth-Trunk103",
        },
        {
            "prefix": "213.180.213.134/31",
            "nh": "87.250.239.221",
            "flags": "DGU",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "213.180.213.136/31",
            "nh": "213.180.213.137",
            "flags": "U",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.137/32",
            "nh": "127.0.0.1",
            "flags": "HU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.138/31",
            "nh": "87.250.239.221",
            "flags": "DGU",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "213.180.213.140/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.142/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.144/31",
            "nh": "87.250.239.221",
            "flags": "DGU",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "213.180.213.146/31",
            "nh": "213.180.213.147",
            "flags": "U",
            "iface": "Eth-Trunk111",
        },
        {
            "prefix": "213.180.213.147/32",
            "nh": "127.0.0.1",
            "flags": "HU",
            "iface": "Eth-Trunk111",
        },
        {
            "prefix": "213.180.213.162/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.164/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.166/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.168/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.170/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.172/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.174/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.178/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.188/30",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.192/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.194/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.196/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.198/31",
            "nh": "213.180.213.200",
            "flags": "DGU",
            "iface": "Eth-Trunk104",
        },
        {
            "prefix": "213.180.213.200/31",
            "nh": "213.180.213.201",
            "flags": "U",
            "iface": "Eth-Trunk104",
        },
        {
            "prefix": "213.180.213.201/32",
            "nh": "127.0.0.1",
            "flags": "HU",
            "iface": "Eth-Trunk104",
        },
        {
            "prefix": "213.180.213.202/31",
            "nh": "213.180.213.204",
            "flags": "DGU",
            "iface": "Eth-Trunk105",
        },
        {
            "prefix": "213.180.213.204/31",
            "nh": "213.180.213.205",
            "flags": "U",
            "iface": "Eth-Trunk105",
        },
        {
            "prefix": "213.180.213.205/32",
            "nh": "127.0.0.1",
            "flags": "HU",
            "iface": "Eth-Trunk105",
        },
        {
            "prefix": "213.180.213.206/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.208/31",
            "nh": "87.250.239.221",
            "flags": "DGU",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "213.180.213.210/31",
            "nh": "87.250.239.221",
            "flags": "DGU",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "213.180.213.212/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.220/31",
            "nh": "87.250.239.221",
            "flags": "DGU",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "213.180.213.222/31",
            "nh": "87.250.239.221",
            "flags": "DGU",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "213.180.213.224/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.226/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.228/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.230/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.232/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.234/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.236/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.238/31",
            "nh": "213.180.213.239",
            "flags": "U",
            "iface": "Eth-Trunk101",
        },
        {
            "prefix": "213.180.213.239/32",
            "nh": "127.0.0.1",
            "flags": "HU",
            "iface": "Eth-Trunk101",
        },
        {
            "prefix": "213.180.213.240/31",
            "nh": "213.180.213.238",
            "flags": "DGU",
            "iface": "Eth-Trunk101",
        },
        {
            "prefix": "213.180.213.242/31",
            "nh": "87.250.239.221",
            "flags": "DGU",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "213.180.213.244/31",
            "nh": "87.250.239.221",
            "flags": "DGU",
            "iface": "Eth-Trunk4.1",
        },
        {
            "prefix": "213.180.213.248/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
        {
            "prefix": "213.180.213.252/31",
            "nh": "213.180.213.136",
            "flags": "DGU",
            "iface": "Eth-Trunk81",
        },
    ]
