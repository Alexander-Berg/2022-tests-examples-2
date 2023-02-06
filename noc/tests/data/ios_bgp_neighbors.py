cmd = "show bgp vpnv6 unicast all neighbors"
content = """
BGP neighbor is 5.45.200.24,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 5.45.200.24
  BGP state = Established, up for 4w2d
  Last read 00:00:13, last write 00:00:05, hold time is 90, keepalive interval is 30 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: advertised and received
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:            28698          0
    Keepalives:         93669      91386
    Route Refresh:          0          0
    Total:             122368      91387
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  Session: 5.45.200.24
  BGP table version 29827, neighbor version 29827/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             351          0
    Prefixes Total:             14418          0
    Implicit Withdraw:            320          0
    Explicit Withdraw:          14067          0
    Used as bestpath:             n/a          0
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                           13          0
    Total:                               13          0
  Number of NLRIs in the update sent: max 86, min 0

 For address family: VPNv6 Unicast
  Session: 5.45.200.24
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817          0
    Prefixes Total:              1734          0
    Implicit Withdraw:            825          0
    Explicit Withdraw:            884          0
    Used as bestpath:             n/a          0
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                          806          0
    Well-known Community:              1362        n/a
    Total:                             2168          0
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 5.45.200.24
  Connections established 21; dropped 20
  Last reset 4w2d, due to Active open failed
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 55086
Foreign host: 5.45.200.24, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BE964):
Timer          Starts    Wakeups            Next
Retrans        111728         19             0x0
TimeWait            0          0             0x0
AckHold         91387      89464             0x0
SendWnd             2          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger      8564159    8564158     0x2FE3BEA23
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 2927338615  snduna: 2931498969  sndnxt: 2931498969     sndwnd:  16384
irs: 3382633283  rcvnxt: 3384369689  rcvwnd:      15662  delrcvwnd:    722

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 44 ms, maxRTT: 1000 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 202799 (out of order: 0), with data: 91387, total data bytes: 1736405
Sent: 212003 (retransmit: 19 fastretransmit: 0),with data: 121325, total data bytes: 4160353

BGP neighbor is 5.45.247.180,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 5.45.247.180
  BGP state = Established, up for 15w4d
  Last read 00:00:24, last write 00:00:02, hold time is 90, keepalive interval is 30 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: advertised and received
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:            30717         16
    Keepalives:        338100     323189
    Route Refresh:          0          0
    Total:             368818     323206
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  Session: 5.45.247.180
  BGP table version 29827, neighbor version 29827/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             351          2 (Consumes 136 bytes)
    Prefixes Total:             14677          7
    Implicit Withdraw:            374          0
    Explicit Withdraw:          14322          5
    Used as bestpath:             n/a          2
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                          253          0
    Total:                              253          0
  Number of NLRIs in the update sent: max 86, min 0

 For address family: VPNv6 Unicast
  Session: 5.45.247.180
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817          2 (Consumes 192 bytes)
    Prefixes Total:              3046          4
    Implicit Withdraw:            921          0
    Explicit Withdraw:           2097          2
    Used as bestpath:             n/a          2
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                         5293          0
    Well-known Community:              6756        n/a
    Total:                            12049          0
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 5.45.247.180
  Connections established 4; dropped 3
  Last reset 15w4d, due to Active open failed
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 57568
Foreign host: 5.45.247.180, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BE998):
Timer          Starts    Wakeups            Next
Retrans        359812       1540             0x0
TimeWait            0          0             0x0
AckHold        323198     314960             0x0
SendWnd             5          2             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger     25396873   25396872     0x2FE3BEA23
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 2987436303  snduna: 2996457206  sndnxt: 2996457206     sndwnd:  16384
irs: 3192975290  rcvnxt: 3199117156  rcvwnd:      15852  delrcvwnd:    532

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 48 ms, maxRTT: 2808 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 683671 (out of order: 0), with data: 323198, total data bytes: 6141865
Sent: 688609 (retransmit: 1540 fastretransmit: 0),with data: 367509, total data bytes: 9020902

BGP neighbor is 10.255.0.3,  remote AS 13238, internal link
 Member of peer-group FB-RR-clients for session parameters
  BGP version 4, remote router ID 10.255.0.3
  BGP state = Established, up for 9w2d
  Last read 00:00:13, last write 00:00:20, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: advertised and received
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:              913        204
    Keepalives:        103661     109035
    Route Refresh:          0          0
    Total:             104575     109240
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  Session: 10.255.0.3
  BGP table version 29827, neighbor version 29827/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:               9          4 (Consumes 272 bytes)
    Prefixes Total:                12          4
    Implicit Withdraw:              4          0
    Explicit Withdraw:              5          0
    Used as bestpath:             n/a          4
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                        14570          0
    Total:                            14570          0
  Number of NLRIs in the update sent: max 3, min 0

 For address family: VPNv6 Unicast
  Session: 10.255.0.3
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             300         29 (Consumes 2784 bytes)
    Prefixes Total:              1676        170
    Implicit Withdraw:            346          0
    Explicit Withdraw:           1313        141
    Used as bestpath:             n/a         29
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                         4922          0
    Total:                             4922          0
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 97, min 0

  Address tracking is enabled, the RIB does have a route to 10.255.0.3
  Connections established 66; dropped 65
  Last reset 12w0d, due to Active open failed
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 10.255.0.100, Local port: 12809
Foreign host: 10.255.0.3, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BE9D0):
Timer          Starts    Wakeups            Next
Retrans        105479       1242             0x0
TimeWait            0          0             0x0
AckHold        109169     106738             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger      2320805    2320805             0x0
DeadWait            0          0             0x0
Linger              0          0             0x0

iss:  922707505  snduna:  924808174  sndnxt:  924808174     sndwnd:   8760
irs: 3992407525  rcvnxt: 3994498229  rcvwnd:      15909  delrcvwnd:    475

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 8 ms, maxRTT: 2808 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1460 bytes):
Rcvd: 214889 (out of order: 0), with data: 109227, total data bytes: 2090703
Sent: 213328 (retransmit: 1242 fastretransmit: 0),with data: 104439, total data bytes: 2100668

BGP neighbor is 10.255.0.4,  remote AS 13238, internal link
 Member of peer-group FB-RR-clients for session parameters
  BGP version 4, remote router ID 10.255.0.4
  BGP state = Established, up for 1w2d
  Last read 00:00:29, last write 00:00:41, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: advertised
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:              162         10
    Keepalives:         15693      16439
    Route Refresh:          0          0
    Total:              15856      16450
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  BGP table version 29827, neighbor version 0/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:               9          0
    Prefixes Total:                 0          0
    Implicit Withdraw:              0          0
    Explicit Withdraw:              0          0
    Used as bestpath:             n/a          0
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    Total:                                0          0
  Number of NLRIs in the update sent: max 4, min 0

 For address family: VPNv6 Unicast
  Session: 10.255.0.4
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             300         12 (Consumes 1152 bytes)
    Prefixes Total:               363         16
    Implicit Withdraw:            310          0
    Explicit Withdraw:             60          4
    Used as bestpath:             n/a         12
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                         2214          0
    Total:                             2214          0
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 97, min 0

  Address tracking is enabled, the RIB does have a route to 10.255.0.4
  Connections established 11; dropped 10
  Last reset 1w2d, due to Active open failed
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 10.255.0.100, Local port: 27294
Foreign host: 10.255.0.4, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BEA04):
Timer          Starts    Wakeups            Next
Retrans         15942        176             0x0
TimeWait            0          0             0x0
AckHold         16448      16164             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger      2722684    2722683     0x2FE3BEA23
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 2761709743  snduna: 2762030028  sndnxt: 2762030028     sndwnd:   8760
irs: 3231183508  rcvnxt: 3231496924  rcvwnd:      16080  delrcvwnd:    304

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 8 ms, maxRTT: 556 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1460 bytes):
Rcvd: 32264 (out of order: 0), with data: 16450, total data bytes: 313415
Sent: 32177 (retransmit: 176 fastretransmit: 0),with data: 15795, total data bytes: 320284

BGP neighbor is 10.255.0.8,  remote AS 13238, internal link
 Member of peer-group FB-RR-clients for session parameters
  BGP version 4, remote router ID 87.250.226.200
  BGP state = Established, up for 3w3d
  Last read 00:00:23, last write 00:00:52, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: advertised and received
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:              458        162
    Keepalives:         38818      39839
    Route Refresh:          0          2
    Total:              39277      40004
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  Session: 10.255.0.8
  BGP table version 29827, neighbor version 29827/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:               9          2 (Consumes 136 bytes)
    Prefixes Total:                16          2
    Implicit Withdraw:             14          0
    Explicit Withdraw:              0          0
    Used as bestpath:             n/a          2
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                        14532         99
    Total:                            14532         99
  Number of NLRIs in the update sent: max 4, min 0

 For address family: VPNv6 Unicast
  Session: 10.255.0.8
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             300         33 (Consumes 3168 bytes)
    Prefixes Total:               966         44
    Implicit Withdraw:            620          0
    Explicit Withdraw:            334         11
    Used as bestpath:             n/a         33
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                         4748         98
    Total:                             4748         98
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 97, min 0

  Address tracking is enabled, the RIB does have a route to 10.255.0.8
  Connections established 2; dropped 1
  Last reset 3w3d, due to BGP protocol initialization
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 10.255.0.100, Local port: 179
Foreign host: 10.255.0.8, Foreign port: 64422
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BEA38):
Timer          Starts    Wakeups            Next
Retrans         39201        157             0x0
TimeWait            0          0             0x0
AckHold         39977      39239             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger            0          0             0x0
DeadWait            0          0             0x0
Linger              0          0             0x0

iss:  653462416  snduna:  654265837  sndnxt:  654265837     sndwnd:   8616
irs:       8722  rcvnxt:     881161  rcvwnd:      16270  delrcvwnd:    114

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 0 ms, maxRTT: 704 ms, ACK hold: 200 ms
Status Flags: passive open, gen tcbs
Option Flags: nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 79058 (out of order: 0), with data: 40028, total data bytes: 872438
Sent: 78991 (retransmit: 157 fastretransmit: 0),with data: 39128, total data bytes: 803420

BGP neighbor is 10.255.0.13,  remote AS 13238, internal link
 Member of peer-group FB-RR-clients for session parameters
  BGP version 4, remote router ID 95.108.237.255
  BGP state = Established, up for 17w0d
  Last read 00:00:14, last write 00:00:27, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:             2989        284
    Keepalives:        187564     196944
    Route Refresh:          0          0
    Total:             190554     197229
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv6 Unicast
  Session: 10.255.0.13
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             300          2 (Consumes 192 bytes)
    Prefixes Total:              5415          4
    Implicit Withdraw:            433          0
    Explicit Withdraw:           5003          2
    Used as bestpath:             n/a          2
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                        10194        152
    Total:                            10194        152
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 97, min 0

  Address tracking is enabled, the RIB does have a route to 10.255.0.13
  Connections established 29; dropped 28
  Last reset 17w0d, due to Active open failed
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 10.255.0.100, Local port: 32435
Foreign host: 10.255.0.13, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BEA70):
Timer          Starts    Wakeups            Next
Retrans        190129        999             0x0
TimeWait            0          0             0x0
AckHold        197216     193192             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger     27670758   27670757     0x2FE3BEB53
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 2147559494  snduna: 2151565659  sndnxt: 2151565659     sndwnd:   8760
irs:  602505144  rcvnxt:  606276353  rcvwnd:      15168  delrcvwnd:   1216

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 4 ms, maxRTT: 2764 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1460 bytes):
Rcvd: 387570 (out of order: 0), with data: 197219, total data bytes: 3771208
Sent: 386557 (retransmit: 999 fastretransmit: 0),with data: 189940, total data bytes: 4006164

BGP neighbor is 10.255.0.15,  remote AS 13238, internal link
 Member of peer-group FB-RR-clients for session parameters
  BGP version 4, remote router ID 95.108.237.238
  BGP state = Established, up for 5w2d
  Last read 00:00:40, last write 00:00:06, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:              587          3
    Keepalives:         58546      59471
    Route Refresh:          0          0
    Total:              59134      59475
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv6 Unicast
  Session: 10.255.0.15
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             300          2 (Consumes 192 bytes)
    Prefixes Total:               883          2
    Implicit Withdraw:            343          0
    Explicit Withdraw:            521          0
    Used as bestpath:             n/a          2
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                         3520          2
    Total:                             3520          2
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 97, min 0

  Address tracking is enabled, the RIB does have a route to 10.255.0.15
  Connections established 2; dropped 1
  Last reset 5w2d, due to BGP protocol initialization
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 10.255.0.100, Local port: 18449
Foreign host: 10.255.0.15, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BEAAC):
Timer          Starts    Wakeups            Next
Retrans         59105        193             0x0
TimeWait            0          0             0x0
AckHold         59472      58425             0x0
SendWnd             1          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger     10249344   10249343     0x2FE3BEB5D
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 1439566539  snduna: 1440754158  sndnxt: 1440754158     sndwnd:   8760
irs: 4057192752  rcvnxt: 4058323051  rcvwnd:      15529  delrcvwnd:    855

SRTT: 300 ms, RTTO: 305 ms, RTV: 5 ms, KRTT: 0 ms
minRTT: 4 ms, maxRTT: 804 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1460 bytes):
Rcvd: 118468 (out of order: 0), with data: 59474, total data bytes: 1130298
Sent: 118277 (retransmit: 193 fastretransmit: 0),with data: 59039, total data bytes: 1187618

BGP neighbor is 10.255.0.18,  remote AS 13238, internal link
 Member of peer-group FB-RR-clients for session parameters
  BGP version 4, remote router ID 87.250.226.189
  BGP state = Established, up for 3w3d
  Last read 00:00:42, last write 00:00:54, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: advertised and received
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:              496        209
    Keepalives:         38900      39989
    Route Refresh:          0          2
    Total:              39397      40201
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  Session: 10.255.0.18
  BGP table version 29827, neighbor version 29827/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:               9          2 (Consumes 136 bytes)
    Prefixes Total:                18          2
    Implicit Withdraw:             14          0
    Explicit Withdraw:              2          0
    Used as bestpath:             n/a          2
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                        14598         98
    Total:                            14598         98
  Number of NLRIs in the update sent: max 4, min 0

 For address family: VPNv6 Unicast
  Session: 10.255.0.18
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             300         33 (Consumes 3168 bytes)
    Prefixes Total:               971         45
    Implicit Withdraw:            533          0
    Explicit Withdraw:            382         12
    Used as bestpath:             n/a         32
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                         4819        102
    Total:                             4819        102
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 97, min 0

  Address tracking is enabled, the RIB does have a route to 10.255.0.18
  Connections established 3; dropped 2
  Last reset 3w3d, due to User reset of session 1
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 10.255.0.100, Local port: 64165
Foreign host: 10.255.0.18, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BEAE4):
Timer          Starts    Wakeups            Next
Retrans         39341        187             0x0
TimeWait            0          0             0x0
AckHold         40149      39392             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger      6767035    6767034     0x2FE3BEB53
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 1820793807  snduna: 1821603306  sndnxt: 1821603306     sndwnd:   8760
irs: 3131038644  rcvnxt: 3131918310  rcvwnd:      15909  delrcvwnd:    475

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 4 ms, maxRTT: 1000 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1460 bytes):
Rcvd: 79378 (out of order: 0), with data: 40230, total data bytes: 879665
Sent: 79260 (retransmit: 187 fastretransmit: 0),with data: 39247, total data bytes: 809498

BGP neighbor is 10.255.0.33,  remote AS 13238, internal link
 Member of peer-group FB-RR-clients for session parameters
  BGP version 4, remote router ID 95.108.237.220
  BGP state = Established, up for 4w2d
  Last read 00:00:05, last write 00:00:39, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: advertised
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:              491         16
    Keepalives:         48376      50681
    Route Refresh:          0          0
    Total:              48868      50698
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  BGP table version 29827, neighbor version 0/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:               9          0
    Prefixes Total:                 0          0
    Implicit Withdraw:              0          0
    Explicit Withdraw:              0          0
    Used as bestpath:             n/a          0
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    Total:                                0          0
  Number of NLRIs in the update sent: max 0, min 0

 For address family: VPNv6 Unicast
  Session: 10.255.0.33
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             300          2 (Consumes 192 bytes)
    Prefixes Total:               802          6
    Implicit Withdraw:            331          2
    Explicit Withdraw:            454          2
    Used as bestpath:             n/a          2
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                         3086          9
    Total:                             3086          9
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 97, min 0

  Address tracking is enabled, the RIB does have a route to 10.255.0.33
  Connections established 2; dropped 1
  Last reset 4w2d, due to BGP protocol initialization
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 10.255.0.100, Local port: 12326
Foreign host: 10.255.0.33, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BEB18):
Timer          Starts    Wakeups            Next
Retrans         48902        242             0x0
TimeWait            0          0             0x0
AckHold         50690      49804             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger      8444103    8444102     0x2FE3BEB53
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 3036656364  snduna: 3037640527  sndnxt: 3037640527     sndwnd:   8760
irs: 2358569142  rcvnxt: 2359533719  rcvwnd:      15947  delrcvwnd:    437

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 4 ms, maxRTT: 800 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1460 bytes):
Rcvd: 99414 (out of order: 0), with data: 50693, total data bytes: 964576
Sent: 99260 (retransmit: 242 fastretransmit: 0),with data: 48771, total data bytes: 984162

BGP neighbor is 10.255.0.35,  remote AS 13238, internal link
 Member of peer-group FB-RR-clients for session parameters
  BGP version 4, remote router ID 95.108.237.200
  BGP state = Established, up for 3w3d
  Last read 00:00:30, last write 00:00:49, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: advertised
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:              375         13
    Keepalives:         38853      40592
    Route Refresh:          0          0
    Total:              39229      40606
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  BGP table version 29827, neighbor version 0/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:               9          0
    Prefixes Total:                 0          0
    Implicit Withdraw:              0          0
    Explicit Withdraw:              0          0
    Used as bestpath:             n/a          0
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    Total:                                0          0
  Number of NLRIs in the update sent: max 0, min 0

 For address family: VPNv6 Unicast
  Session: 10.255.0.35
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             300          2 (Consumes 192 bytes)
    Prefixes Total:               678          4
    Implicit Withdraw:            288          0
    Explicit Withdraw:            334          2
    Used as bestpath:             n/a          2
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                         2840          6
    Total:                             2840          6
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 97, min 0

  Address tracking is enabled, the RIB does have a route to 10.255.0.35
  Connections established 4; dropped 3
  Last reset 3w3d, due to Active open failed
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 10.255.0.100, Local port: 46182
Foreign host: 10.255.0.35, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BEB4C):
Timer          Starts    Wakeups            Next
Retrans         39261        195             0x0
TimeWait            0          0             0x0
AckHold         40598      39887             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger      6750009    6750008     0x2FE3BEB53
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 3877814485  snduna: 3878603509  sndnxt: 3878603509     sndwnd:   8760
irs:  940356813  rcvnxt:  941129285  rcvwnd:      14940  delrcvwnd:   1444

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 4 ms, maxRTT: 800 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1460 bytes):
Rcvd: 79706 (out of order: 0), with data: 40601, total data bytes: 772471
Sent: 79588 (retransmit: 195 fastretransmit: 0),with data: 39148, total data bytes: 789023

BGP neighbor is 10.255.0.37,  remote AS 13238, internal link
 Member of peer-group FB-RR-clients for session parameters
  BGP version 4, remote router ID 87.250.226.125
  BGP state = Established, up for 21w1d
  Last read 00:00:31, last write 00:00:05, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: advertised
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:           116348         18
    Keepalives:        211928     248784
    Route Refresh:          0         13
    Total:             328277     248816
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  BGP table version 29827, neighbor version 0/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:               9          0
    Prefixes Total:                 0          0
    Implicit Withdraw:              0          0
    Explicit Withdraw:              0          0
    Used as bestpath:             n/a          0
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    Total:                                0          0
  Number of NLRIs in the update sent: max 0, min 0

 For address family: VPNv6 Unicast
  Session: 10.255.0.37
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             300          6 (Consumes 576 bytes)
    Prefixes Total:             76034          9
    Implicit Withdraw:          22106          0
    Explicit Withdraw:          53630          3
    Used as bestpath:             n/a          6
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                        37735          7
    Total:                            37735          7
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 97, min 0

  Address tracking is enabled, the RIB does have a route to 10.255.0.37
  Connections established 1; dropped 0
  Last reset never
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 10.255.0.100, Local port: 179
Foreign host: 10.255.0.37, Foreign port: 52669
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BEB84):
Timer          Starts    Wakeups            Next
Retrans        281835       1400             0x0
TimeWait            0          0             0x0
AckHold        248807     243799             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger            0          0             0x0
DeadWait            0          0             0x0
Linger              0          0             0x0

iss:  978635432  snduna:  994872667  sndnxt:  994872667     sndwnd:   8616
irs:      13975  rcvnxt:    4743025  rcvwnd:      15016  delrcvwnd:   1368

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 0 ms, maxRTT: 2804 ms, ACK hold: 200 ms
Status Flags: passive open, gen tcbs
Option Flags: nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 530380 (out of order: 0), with data: 248810, total data bytes: 4729049
Sent: 574460 (retransmit: 1400 fastretransmit: 0),with data: 326566, total data bytes: 16237234

BGP neighbor is 10.255.0.38,  remote AS 13238, internal link
 Member of peer-group FB-RR-clients for session parameters
  BGP version 4, remote router ID 87.250.226.124
  BGP state = Established, up for 21w1d
  Last read 00:00:00, last write 00:00:02, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: advertised
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:           116001         20
    Keepalives:        211865     248828
    Route Refresh:          0          9
    Total:             327867     248858
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  BGP table version 29827, neighbor version 0/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:               9          0
    Prefixes Total:                 0          0
    Implicit Withdraw:              0          0
    Explicit Withdraw:              0          0
    Used as bestpath:             n/a          0
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    Total:                                0          0
  Number of NLRIs in the update sent: max 0, min 0

 For address family: VPNv6 Unicast
  Session: 10.255.0.38
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             300          6 (Consumes 576 bytes)
    Prefixes Total:             74922          9
    Implicit Withdraw:          20994          0
    Explicit Withdraw:          53631          3
    Used as bestpath:             n/a          6
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                        30103          8
    Total:                            30103          8
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 97, min 0

  Address tracking is enabled, the RIB does have a route to 10.255.0.38
  Connections established 1; dropped 0
  Last reset never
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 10.255.0.100, Local port: 179
Foreign host: 10.255.0.38, Foreign port: 54613
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BEBB8):
Timer          Starts    Wakeups            Next
Retrans        281518       1285             0x0
TimeWait            0          0             0x0
AckHold        248848     243843     0x2FE3BEBFC
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger            0          0             0x0
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 2851888729  snduna: 2868063097  sndnxt: 2868063097     sndwnd:   8616
irs:      47163  rcvnxt:    4777125  rcvwnd:      15529  delrcvwnd:    855

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 0 ms, maxRTT: 3208 ms, ACK hold: 200 ms
Status Flags: passive open, gen tcbs
Option Flags: nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 530268 (out of order: 0), with data: 248852, total data bytes: 4729961
Sent: 574366 (retransmit: 1285 fastretransmit: 0),with data: 326458, total data bytes: 16174367

BGP neighbor is 10.255.0.41,  remote AS 13238, internal link
 Member of peer-group FB-RR-clients for session parameters
  BGP version 4, remote router ID 141.8.136.241
  BGP state = Established, up for 3w1d
  Last read 00:00:48, last write 00:00:39, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:              297         28
    Keepalives:         36359      38499
    Route Refresh:          0          0
    Total:              36657      38528
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv6 Unicast
  Session: 10.255.0.41
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             300         10 (Consumes 960 bytes)
    Prefixes Total:               581         22
    Implicit Withdraw:            345         11
    Explicit Withdraw:            252          1
    Used as bestpath:             n/a         10
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                         2485         52
    Total:                             2485         52
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 97, min 0

  Address tracking is enabled, the RIB does have a route to 10.255.0.41
  Connections established 6; dropped 5
  Last reset 3w2d, due to Active open failed
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 10.255.0.100, Local port: 179
Foreign host: 10.255.0.41, Foreign port: 62188
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BEBEC):
Timer          Starts    Wakeups            Next
Retrans         36999        497             0x0
TimeWait            0          0             0x0
AckHold         38510      37844             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger            0          0             0x0
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 2253474245  snduna: 2254205392  sndnxt: 2254205392     sndwnd:   8760
irs:      45682  rcvnxt:     780944  rcvwnd:      15738  delrcvwnd:    646

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 20 ms, maxRTT: 804 ms, ACK hold: 200 ms
Status Flags: passive open, gen tcbs
Option Flags: nagle, path mtu capable

Datagrams (max data segment is 1460 bytes):
Rcvd: 75354 (out of order: 0), with data: 38515, total data bytes: 735261
Sent: 74949 (retransmit: 497 fastretransmit: 0),with data: 36576, total data bytes: 731146

BGP neighbor is 10.255.0.42,  remote AS 13238, internal link
 Member of peer-group FB-RR-clients for session parameters
  BGP version 4, remote router ID 141.8.136.242
  BGP state = Established, up for 3w3d
  Last read 00:00:15, last write 00:00:37, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:              433         63
    Keepalives:         38098      40334
    Route Refresh:          0          1
    Total:              38532      40399
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv6 Unicast
  Session: 10.255.0.42
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             300         14 (Consumes 1344 bytes)
    Prefixes Total:               962         39
    Implicit Withdraw:            669         22
    Explicit Withdraw:            306          3
    Used as bestpath:             n/a         14
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                         4690         57
    Total:                             4690         57
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 97, min 0

  Address tracking is enabled, the RIB does have a route to 10.255.0.42
  Connections established 2; dropped 1
  Last reset 3w3d, due to BGP protocol initialization
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 10.255.0.100, Local port: 22341
Foreign host: 10.255.0.42, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BEC20):
Timer          Starts    Wakeups            Next
Retrans         38817        525             0x0
TimeWait            0          0             0x0
AckHold         40373      39655             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger      6556903    6556902     0x2FE3BEC83
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 3547038105  snduna: 3547824878  sndnxt: 3547824878     sndwnd:   8760
irs: 4044882091  rcvnxt: 4045655912  rcvwnd:      15206  delrcvwnd:   1178

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 20 ms, maxRTT: 1000 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1460 bytes):
Rcvd: 79052 (out of order: 0), with data: 40389, total data bytes: 773820
Sent: 78601 (retransmit: 525 fastretransmit: 0),with data: 38379, total data bytes: 786772

BGP neighbor is 10.255.0.43,  remote AS 13238, internal link
 Member of peer-group FB-RR-clients for session parameters
  BGP version 4, remote router ID 141.8.136.243
  BGP state = Established, up for 3w2d
  Last read 00:00:32, last write 00:00:37, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:              414         63
    Keepalives:         37649      39788
    Route Refresh:          0          1
    Total:              38064      39853
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv6 Unicast
  Session: 10.255.0.43
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             300         14 (Consumes 1344 bytes)
    Prefixes Total:               934         15
    Implicit Withdraw:            658          0
    Explicit Withdraw:            287          1
    Used as bestpath:             n/a         14
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                         4615         57
    Total:                             4615         57
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 97, min 0

  Address tracking is enabled, the RIB does have a route to 10.255.0.43
  Connections established 2; dropped 1
  Last reset 3w2d, due to BGP protocol initialization
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 10.255.0.100, Local port: 17766
Foreign host: 10.255.0.43, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BEC58):
Timer          Starts    Wakeups            Next
Retrans         38477        645             0x0
TimeWait            0          0             0x0
AckHold         39834      39127             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger      6465789    6465788     0x2FE3BEC83
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 1133187672  snduna: 1133963309  sndnxt: 1133963309     sndwnd:   8760
irs:  734316631  rcvnxt:  735079986  rcvwnd:      15662  delrcvwnd:    722

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 24 ms, maxRTT: 1200 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1460 bytes):
Rcvd: 78129 (out of order: 0), with data: 39849, total data bytes: 763354
Sent: 77588 (retransmit: 645 fastretransmit: 0),with data: 37913, total data bytes: 775636

BGP neighbor is 10.255.0.44,  remote AS 13238, internal link
 Member of peer-group FB-RR-clients for session parameters
  BGP version 4, remote router ID 141.8.136.244
  BGP state = Established, up for 3w2d
  Last read 00:00:08, last write 00:00:42, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:              404         66
    Keepalives:         37468      39533
    Route Refresh:          0          1
    Total:              37873      39601
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv6 Unicast
  Session: 10.255.0.44
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             300         14 (Consumes 1344 bytes)
    Prefixes Total:               931         39
    Implicit Withdraw:            673          7
    Explicit Withdraw:            273         18
    Used as bestpath:             n/a         14
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                         4578         58
    Total:                             4578         58
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 97, min 0

  Address tracking is enabled, the RIB does have a route to 10.255.0.44
  Connections established 2; dropped 1
  Last reset 3w2d, due to BGP protocol initialization
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 10.255.0.100, Local port: 27225
Foreign host: 10.255.0.44, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BEC8C):
Timer          Starts    Wakeups            Next
Retrans         38139        508             0x0
TimeWait            0          0             0x0
AckHold         39575      38887             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger      6447143    6447142     0x2FE3BEDB3
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 2953493647  snduna: 2954264558  sndnxt: 2954264558     sndwnd:   8760
irs:  748690803  rcvnxt:  749449880  rcvwnd:      15529  delrcvwnd:    855

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 20 ms, maxRTT: 720 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1460 bytes):
Rcvd: 77559 (out of order: 0), with data: 39586, total data bytes: 759076
Sent: 77144 (retransmit: 508 fastretransmit: 0),with data: 37716, total data bytes: 770910

BGP neighbor is 10.255.0.45,  remote AS 13238, internal link
 Member of peer-group FB-RR-clients for session parameters
  BGP version 4, remote router ID 141.8.136.245
  BGP state = Established, up for 21w1d
  Last read 00:00:25, last write 00:00:24, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: advertised
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:           115308         89
    Keepalives:        211898     249247
    Route Refresh:          0          1
    Total:             327207     249338
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  BGP table version 29827, neighbor version 0/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:               9          0
    Prefixes Total:                 0          0
    Implicit Withdraw:              0          0
    Explicit Withdraw:              0          0
    Used as bestpath:             n/a          0
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    Total:                                0          0
  Number of NLRIs in the update sent: max 0, min 0

 For address family: VPNv6 Unicast
  Session: 10.255.0.45
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             300          6 (Consumes 576 bytes)
    Prefixes Total:             72710         19
    Implicit Withdraw:          18782          0
    Explicit Withdraw:          53630         13
    Used as bestpath:             n/a          6
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                        14832         77
    Total:                            14832         77
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 97, min 0

  Address tracking is enabled, the RIB does have a route to 10.255.0.45
  Connections established 1; dropped 0
  Last reset never
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 10.255.0.100, Local port: 179
Foreign host: 10.255.0.45, Foreign port: 64327
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BECC0):
Timer          Starts    Wakeups            Next
Retrans        282800       2861             0x0
TimeWait            0          0             0x0
AckHold        249311     244357             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger            0          0             0x0
DeadWait            0          0             0x0
Linger              0          0             0x0

iss:  306521137  snduna:  322573349  sndnxt:  322573349     sndwnd:   8616
irs:       4266  rcvnxt:    4749480  rcvwnd:      15339  delrcvwnd:   1045

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 20 ms, maxRTT: 2808 ms, ACK hold: 200 ms
Status Flags: passive open, gen tcbs
Option Flags: nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 531946 (out of order: 0), with data: 249322, total data bytes: 4745213
Sent: 574825 (retransmit: 2861 fastretransmit: 0),with data: 326379, total data bytes: 16052211

BGP neighbor is 10.255.0.46,  remote AS 13238, internal link
 Member of peer-group FB-RR-clients for session parameters
  BGP version 4, remote router ID 141.8.136.246
  BGP state = Established, up for 21w1d
  Last read 00:00:48, last write 00:00:34, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: advertised
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:           115308        108
    Keepalives:        211871     249428
    Route Refresh:          0          1
    Total:             327180     249538
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  BGP table version 29827, neighbor version 0/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:               9          0
    Prefixes Total:                 0          0
    Implicit Withdraw:              0          0
    Explicit Withdraw:              0          0
    Used as bestpath:             n/a          0
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    Total:                                0          0
  Number of NLRIs in the update sent: max 0, min 0

 For address family: VPNv6 Unicast
  Session: 10.255.0.46
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             300          6 (Consumes 576 bytes)
    Prefixes Total:             72710         23
    Implicit Withdraw:          18782          0
    Explicit Withdraw:          53630         17
    Used as bestpath:             n/a          6
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                        14832         97
    Total:                            14832         97
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 97, min 0

  Address tracking is enabled, the RIB does have a route to 10.255.0.46
  Connections established 1; dropped 0
  Last reset never
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 10.255.0.100, Local port: 179
Foreign host: 10.255.0.46, Foreign port: 55884
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BECF8):
Timer          Starts    Wakeups            Next
Retrans        282646       2789             0x0
TimeWait            0          0             0x0
AckHold        249501     244496             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger            0          0             0x0
DeadWait            0          0             0x0
Linger              0          0             0x0

iss:  771723429  snduna:  787775128  sndnxt:  787775128     sndwnd:   8616
irs:       7800  rcvnxt:    4758849  rcvwnd:      16080  delrcvwnd:    304

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 20 ms, maxRTT: 2808 ms, ACK hold: 200 ms
Status Flags: passive open, gen tcbs
Option Flags: nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 532166 (out of order: 0), with data: 249516, total data bytes: 4751048
Sent: 575002 (retransmit: 2789 fastretransmit: 0),with data: 326364, total data bytes: 16051698

BGP neighbor is 10.255.0.47,  remote AS 13238, internal link
 Member of peer-group FB-RR-clients for session parameters
  BGP version 4, remote router ID 141.8.136.247
  BGP state = Established, up for 21w1d
  Last read 00:00:04, last write 00:00:48, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: advertised
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:           115308         86
    Keepalives:        211887     249354
    Route Refresh:          0          1
    Total:             327196     249442
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  BGP table version 29827, neighbor version 0/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:               9          0
    Prefixes Total:                 0          0
    Implicit Withdraw:              0          0
    Explicit Withdraw:              0          0
    Used as bestpath:             n/a          0
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    Total:                                0          0
  Number of NLRIs in the update sent: max 0, min 0

 For address family: VPNv6 Unicast
  Session: 10.255.0.47
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             300          6 (Consumes 576 bytes)
    Prefixes Total:             72710         21
    Implicit Withdraw:          18782          0
    Explicit Withdraw:          53630         15
    Used as bestpath:             n/a          6
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                        14832         89
    Total:                            14832         89
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 97, min 0

  Address tracking is enabled, the RIB does have a route to 10.255.0.47
  Connections established 1; dropped 0
  Last reset never
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 10.255.0.100, Local port: 179
Foreign host: 10.255.0.47, Foreign port: 58707
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BED2C):
Timer          Starts    Wakeups            Next
Retrans        282837       3139             0x0
TimeWait            0          0             0x0
AckHold        249420     244433             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger            0          0             0x0
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 3163666417  snduna: 3179718420  sndnxt: 3179718420     sndwnd:   8616
irs:       4290  rcvnxt:    4751905  rcvwnd:      15168  delrcvwnd:   1216

SRTT: 300 ms, RTTO: 305 ms, RTV: 5 ms, KRTT: 0 ms
minRTT: 20 ms, maxRTT: 2912 ms, ACK hold: 200 ms
Status Flags: passive open, gen tcbs
Option Flags: nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 532134 (out of order: 0), with data: 249426, total data bytes: 4747614
Sent: 574931 (retransmit: 3139 fastretransmit: 0),with data: 326377, total data bytes: 16052002

BGP neighbor is 10.255.0.48,  remote AS 13238, internal link
 Member of peer-group FB-RR-clients for session parameters
  BGP version 4, remote router ID 141.8.136.248
  BGP state = Established, up for 21w1d
  Last read 00:00:34, last write 00:00:30, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: advertised
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:           115308         85
    Keepalives:        211938     249416
    Route Refresh:          0          1
    Total:             327247     249503
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  BGP table version 29827, neighbor version 0/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:               9          0
    Prefixes Total:                 0          0
    Implicit Withdraw:              0          0
    Explicit Withdraw:              0          0
    Used as bestpath:             n/a          0
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    Total:                                0          0
  Number of NLRIs in the update sent: max 0, min 0

 For address family: VPNv6 Unicast
  Session: 10.255.0.48
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             300          6 (Consumes 576 bytes)
    Prefixes Total:             72710         14
    Implicit Withdraw:          18782          0
    Explicit Withdraw:          53630          8
    Used as bestpath:             n/a          6
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                        14832         77
    Total:                            14832         77
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 97, min 0

  Address tracking is enabled, the RIB does have a route to 10.255.0.48
  Connections established 1; dropped 0
  Last reset never
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 10.255.0.100, Local port: 29695
Foreign host: 10.255.0.48, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BED64):
Timer          Starts    Wakeups            Next
Retrans        282704       2738             0x0
TimeWait            0          0             0x0
AckHold        249484     244536             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger     34975927   34975926     0x2FE3BEDB3
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 3759572343  snduna: 3775625323  sndnxt: 3775625323     sndwnd:   8760
irs: 1994550736  rcvnxt: 1999298427  rcvwnd:      16270  delrcvwnd:    114

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 20 ms, maxRTT: 2820 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1460 bytes):
Rcvd: 532009 (out of order: 0), with data: 249496, total data bytes: 4747690
Sent: 575033 (retransmit: 2738 fastretransmit: 0),with data: 326426, total data bytes: 16052979

BGP neighbor is 10.255.0.51,  remote AS 13238, internal link
 Member of peer-group FB-RR-clients for session parameters
  BGP version 4, remote router ID 141.8.136.191
  BGP state = Established, up for 8w0d
  Last read 00:00:39, last write 00:00:51, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:              771         52
    Keepalives:         89672      95172
    Route Refresh:          0          1
    Total:              90444      95226
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv6 Unicast
  Session: 10.255.0.51
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             300         18 (Consumes 1728 bytes)
    Prefixes Total:              1424         26
    Implicit Withdraw:            672          0
    Explicit Withdraw:            750          8
    Used as bestpath:             n/a         18
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                         5921         55
    Total:                             5921         55
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 97, min 0

  Address tracking is enabled, the RIB does have a route to 10.255.0.51
  Connections established 4; dropped 3
  Last reset 9w2d, due to Active open failed
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 10.255.0.100, Local port: 179
Foreign host: 10.255.0.51, Foreign port: 49755
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BED98):
Timer          Starts    Wakeups            Next
Retrans         91667       1567             0x0
TimeWait            0          0             0x0
AckHold         95214      93166             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger            0          0             0x0
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 2364390475  snduna: 2366201826  sndnxt: 2366201826     sndwnd:   8760
irs:      26550  rcvnxt:    1840659  rcvwnd:      15434  delrcvwnd:    950

SRTT: 302 ms, RTTO: 320 ms, RTV: 18 ms, KRTT: 0 ms
minRTT: 24 ms, maxRTT: 2840 ms, ACK hold: 200 ms
Status Flags: passive open, gen tcbs
Option Flags: nagle, path mtu capable

Datagrams (max data segment is 1460 bytes):
Rcvd: 187121 (out of order: 0), with data: 95222, total data bytes: 1814108
Sent: 185318 (retransmit: 1567 fastretransmit: 0),with data: 90261, total data bytes: 1811350

BGP neighbor is 10.255.0.52,  remote AS 13238, internal link
 Member of peer-group FB-RR-clients for session parameters
  BGP version 4, remote router ID 141.8.136.192
  BGP state = Established, up for 21w1d
  Last read 00:00:53, last write 00:00:27, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:           115433        215
    Keepalives:        211884     245627
    Route Refresh:          0          2
    Total:             327318     245845
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv6 Unicast
  Session: 10.255.0.52
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             300         18 (Consumes 1728 bytes)
    Prefixes Total:             73218         41
    Implicit Withdraw:          19290          0
    Explicit Withdraw:          53630         23
    Used as bestpath:             n/a         18
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                        16714        130
    Total:                            16714        130
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 97, min 0

  Address tracking is enabled, the RIB does have a route to 10.255.0.52
  Connections established 1; dropped 0
  Last reset never
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 10.255.0.100, Local port: 59189
Foreign host: 10.255.0.52, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BEDCC):
Timer          Starts    Wakeups            Next
Retrans        282567       2676             0x0
TimeWait            0          0             0x0
AckHold        245818     240892             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger     35053846   35053845     0x2FE3BEEE3
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 2763747044  snduna: 2779823206  sndnxt: 2779823206     sndwnd:   8760
irs: 3477528216  rcvnxt: 3482215619  rcvwnd:      16137  delrcvwnd:    247

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 20 ms, maxRTT: 2912 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1460 bytes):
Rcvd: 528479 (out of order: 0), with data: 245837, total data bytes: 4687402
Sent: 571297 (retransmit: 2676 fastretransmit: 0),with data: 326394, total data bytes: 16076161

BGP neighbor is 10.255.0.58,  remote AS 13238, internal link
 Member of peer-group FB-RR-clients for session parameters
  BGP version 4, remote router ID 95.108.237.48
  BGP state = Established, up for 3w3d
  Last read 00:00:16, last write 00:00:32, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:              458         24
    Keepalives:         38817      40515
    Route Refresh:          0          1
    Total:              39276      40541
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv6 Unicast
  Session: 10.255.0.58
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             300         27 (Consumes 2592 bytes)
    Prefixes Total:              1003         31
    Implicit Withdraw:            627          0
    Explicit Withdraw:            334          4
    Used as bestpath:             n/a         27
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                         4841         16
    Total:                             4841         16
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 97, min 0

  Address tracking is enabled, the RIB does have a route to 10.255.0.58
  Connections established 11; dropped 10
  Last reset 6w6d, due to Active open failed
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 10.255.0.100, Local port: 18042
Foreign host: 10.255.0.58, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BEE00):
Timer          Starts    Wakeups            Next
Retrans         39311        277             0x0
TimeWait            0          0             0x0
AckHold         40531      39826             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger      6735654    6735653     0x2FE3BEEE3
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 1565362607  snduna: 1566166670  sndnxt: 1566166670     sndwnd:   8760
irs: 2777147853  rcvnxt: 2777920711  rcvwnd:      16099  delrcvwnd:    285

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 8 ms, maxRTT: 800 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1460 bytes):
Rcvd: 79682 (out of order: 0), with data: 40534, total data bytes: 772857
Sent: 79507 (retransmit: 277 fastretransmit: 0),with data: 39124, total data bytes: 804062

BGP neighbor is 10.255.0.71,  remote AS 13238, internal link
 Member of peer-group FB-RR-clients for session parameters
  BGP version 4, remote router ID 141.8.136.251
  BGP state = Established, up for 3w0d
  Last read 00:00:04, last write 00:00:01, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family IPv6 Unicast: received
    Address family VPNv4 Unicast: advertised
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:              232          7
    Keepalives:         33417      35234
    Route Refresh:          0          0
    Total:              33650      35242
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  BGP table version 29827, neighbor version 0/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:               9          0
    Prefixes Total:                 0          0
    Implicit Withdraw:              0          0
    Explicit Withdraw:              0          0
    Used as bestpath:             n/a          0
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    Total:                                0          0
  Number of NLRIs in the update sent: max 0, min 0

 For address family: VPNv6 Unicast
  Session: 10.255.0.71
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             300          3 (Consumes 288 bytes)
    Prefixes Total:               415          3
    Implicit Withdraw:            325          0
    Explicit Withdraw:            112          0
    Used as bestpath:             n/a          3
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                         2458          4
    Total:                             2458          4
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 97, min 0

  Address tracking is enabled, the RIB does have a route to 10.255.0.71
  Connections established 6; dropped 5
  Last reset 3w0d, due to Active open failed
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 10.255.0.100, Local port: 59859
Foreign host: 10.255.0.71, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BEE38):
Timer          Starts    Wakeups            Next
Retrans         34139        614             0x0
TimeWait            0          0             0x0
AckHold         35238      34641             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger      5718074    5718073     0x2FE3BEEFC
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 4077773191  snduna: 4078437381  sndnxt: 4078437381     sndwnd:   8760
irs:  114436573  rcvnxt:  115106832  rcvwnd:      16194  delrcvwnd:    190

SRTT: 301 ms, RTTO: 308 ms, RTV: 7 ms, KRTT: 0 ms
minRTT: 24 ms, maxRTT: 888 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1460 bytes):
Rcvd: 69174 (out of order: 0), with data: 35240, total data bytes: 670258
Sent: 68704 (retransmit: 614 fastretransmit: 0),with data: 33582, total data bytes: 664189

BGP neighbor is 10.255.0.72,  remote AS 13238, internal link
 Member of peer-group FB-RR-clients for session parameters
  BGP version 4, remote router ID 141.8.136.252
  BGP state = Established, up for 2w3d
  Last read 00:00:44, last write 00:00:41, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: advertised
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:              223          4
    Keepalives:         28123      29673
    Route Refresh:          0          0
    Total:              28347      29678
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  BGP table version 29827, neighbor version 0/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:               9          0
    Prefixes Total:                 0          0
    Implicit Withdraw:              0          0
    Explicit Withdraw:              0          0
    Used as bestpath:             n/a          0
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    Total:                                0          0
  Number of NLRIs in the update sent: max 0, min 0

 For address family: VPNv6 Unicast
  Session: 10.255.0.72
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             300          3 (Consumes 288 bytes)
    Prefixes Total:               408          3
    Implicit Withdraw:            325          0
    Explicit Withdraw:            105          0
    Used as bestpath:             n/a          3
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                         2339          3
    Total:                             2339          3
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 97, min 0

  Address tracking is enabled, the RIB does have a route to 10.255.0.72
  Connections established 3; dropped 2
  Last reset 2w3d, due to BGP protocol initialization
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 10.255.0.100, Local port: 179
Foreign host: 10.255.0.72, Foreign port: 64586
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BEE6C):
Timer          Starts    Wakeups            Next
Retrans         28707        481             0x0
TimeWait            0          0             0x0
AckHold         29675      29188             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger            0          0             0x0
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 2166074438  snduna: 2166637093  sndnxt: 2166637093     sndwnd:   8760
irs:      16617  rcvnxt:     580892  rcvwnd:      15377  delrcvwnd:   1007

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 20 ms, maxRTT: 928 ms, ACK hold: 200 ms
Status Flags: passive open, gen tcbs
Option Flags: nagle, path mtu capable

Datagrams (max data segment is 1460 bytes):
Rcvd: 58268 (out of order: 0), with data: 29676, total data bytes: 564274
Sent: 57873 (retransmit: 481 fastretransmit: 0),with data: 28279, total data bytes: 562654

BGP neighbor is 10.255.0.73,  remote AS 13238, internal link
 Member of peer-group FB-RR-clients for session parameters
  BGP version 4, remote router ID 141.8.136.253
  BGP state = Established, up for 3w1d
  Last read 00:00:25, last write 00:00:34, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: advertised
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:              283          6
    Keepalives:         36210      38152
    Route Refresh:          0          0
    Total:              36494      38159
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  BGP table version 29827, neighbor version 0/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:               9          0
    Prefixes Total:                 0          0
    Implicit Withdraw:              0          0
    Explicit Withdraw:              0          0
    Used as bestpath:             n/a          0
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    Total:                                0          0
  Number of NLRIs in the update sent: max 0, min 0

 For address family: VPNv6 Unicast
  Session: 10.255.0.73
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             300          3 (Consumes 288 bytes)
    Prefixes Total:               537          3
    Implicit Withdraw:            327          0
    Explicit Withdraw:            234          0
    Used as bestpath:             n/a          3
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                         2482          4
    Total:                             2482          4
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 15, min 0

  Address tracking is enabled, the RIB does have a route to 10.255.0.73
  Connections established 6; dropped 5
  Last reset 3w1d, due to Active open failed
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 10.255.0.100, Local port: 34123
Foreign host: 10.255.0.73, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BEEA0):
Timer          Starts    Wakeups            Next
Retrans         37032        684             0x0
TimeWait            0          0             0x0
AckHold         38155      37519             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger      6199965    6199964     0x2FE3BEEE3
DeadWait            0          0             0x0
Linger              0          0             0x0

iss:   64416404  snduna:   65142178  sndnxt:   65142178     sndwnd:   8760
irs: 4019424764  rcvnxt: 4020150359  rcvwnd:      14978  delrcvwnd:   1406

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 20 ms, maxRTT: 1400 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1460 bytes):
Rcvd: 75047 (out of order: 0), with data: 38158, total data bytes: 725594
Sent: 74458 (retransmit: 684 fastretransmit: 0),with data: 36420, total data bytes: 725773

BGP neighbor is 10.255.0.74,  remote AS 13238, internal link
 Member of peer-group FB-RR-clients for session parameters
  BGP version 4, remote router ID 141.8.136.254
  BGP state = Established, up for 11w1d
  Last read 00:00:47, last write 00:00:32, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: advertised
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:             1122         29
    Keepalives:        124321     131168
    Route Refresh:          0          0
    Total:             125444     131198
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  BGP table version 29827, neighbor version 0/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:               9          0
    Prefixes Total:                 0          0
    Implicit Withdraw:              0          0
    Explicit Withdraw:              0          0
    Used as bestpath:             n/a          0
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    Total:                                0          0
  Number of NLRIs in the update sent: max 0, min 0

 For address family: VPNv6 Unicast
  Session: 10.255.0.74
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             300          3 (Consumes 288 bytes)
    Prefixes Total:              1917          9
    Implicit Withdraw:            377          0
    Explicit Withdraw:           1516          6
    Used as bestpath:             n/a          3
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                         6046          9
    Total:                             6046          9
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 97, min 0

  Address tracking is enabled, the RIB does have a route to 10.255.0.74
  Connections established 1; dropped 0
  Last reset never
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 10.255.0.100, Local port: 179
Foreign host: 10.255.0.74, Foreign port: 60126
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BEED4):
Timer          Starts    Wakeups            Next
Retrans        126678       1681             0x0
TimeWait            0          0             0x0
AckHold        131185     128443             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger            0          0             0x0
DeadWait            0          0             0x0
Linger              0          0             0x0

iss:  744685939  snduna:  747205977  sndnxt:  747205977     sndwnd:   8760
irs:      14104  rcvnxt:    2508888  rcvwnd:      16080  delrcvwnd:    304

SRTT: 307 ms, RTTO: 363 ms, RTV: 56 ms, KRTT: 0 ms
minRTT: 20 ms, maxRTT: 3072 ms, ACK hold: 200 ms
Status Flags: passive open, gen tcbs
Option Flags: nagle, path mtu capable

Datagrams (max data segment is 1460 bytes):
Rcvd: 258058 (out of order: 0), with data: 131197, total data bytes: 2494783
Sent: 256181 (retransmit: 1681 fastretransmit: 0),with data: 125263, total data bytes: 2520037

BGP neighbor is 10.255.0.76,  remote AS 13238, internal link
 Member of peer-group FB-RR-clients for session parameters
  BGP version 4, remote router ID 95.108.237.142
  BGP state = Established, up for 19w1d
  Last read 00:00:04, last write 00:00:06, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:            37920          3
    Keepalives:        205092     217263
    Route Refresh:          0          0
    Total:             243013     217267
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv6 Unicast
  Session: 10.255.0.76
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             300          2 (Consumes 192 bytes)
    Prefixes Total:             25741          2
    Implicit Withdraw:           5824          0
    Explicit Withdraw:          19941          0
    Used as bestpath:             n/a          2
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                        11451          2
    Total:                            11451          2
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 97, min 0

  Address tracking is enabled, the RIB does have a route to 10.255.0.76
  Connections established 3; dropped 2
  Last reset 19w1d, due to Active open failed
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 10.255.0.100, Local port: 179
Foreign host: 10.255.0.76, Foreign port: 56354
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BEF0C):
Timer          Starts    Wakeups            Next
Retrans        229127       1090             0x0
TimeWait            0          0             0x0
AckHold        217265     212978             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger            0          0             0x0
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 4165787256  snduna: 4173695631  sndnxt: 4173695631     sndwnd:   8760
irs:       6688  rcvnxt:    4135035  rcvwnd:      15168  delrcvwnd:   1216

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 4 ms, maxRTT: 2804 ms, ACK hold: 200 ms
Status Flags: passive open, gen tcbs
Option Flags: nagle, path mtu capable

Datagrams (max data segment is 1460 bytes):
Rcvd: 446653 (out of order: 0), with data: 217266, total data bytes: 4128346
Sent: 459011 (retransmit: 1090 fastretransmit: 0),with data: 242383, total data bytes: 7908374

BGP neighbor is 10.255.0.77,  remote AS 13238, internal link
 Member of peer-group FB-RR-clients for session parameters
  BGP version 4, remote router ID 95.108.237.143
  BGP state = Established, up for 19w1d
  Last read 00:00:35, last write 00:00:47, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:            37909          3
    Keepalives:        205144     217510
    Route Refresh:          0          0
    Total:             243054     217514
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv6 Unicast
  Session: 10.255.0.77
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             300          2 (Consumes 192 bytes)
    Prefixes Total:             25734          2
    Implicit Withdraw:           5823          0
    Explicit Withdraw:          19937          0
    Used as bestpath:             n/a          2
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                        11451          2
    Total:                            11451          2
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 97, min 0

  Address tracking is enabled, the RIB does have a route to 10.255.0.77
  Connections established 3; dropped 2
  Last reset 19w1d, due to Active open failed
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 10.255.0.100, Local port: 179
Foreign host: 10.255.0.77, Foreign port: 56198
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BEF44):
Timer          Starts    Wakeups            Next
Retrans        229086       1023             0x0
TimeWait            0          0             0x0
AckHold        217511     213119             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger            0          0             0x0
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 1187341850  snduna: 1195250025  sndnxt: 1195250025     sndwnd:   8760
irs:      29887  rcvnxt:    4162927  rcvwnd:      16327  delrcvwnd:     57

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 4 ms, maxRTT: 2808 ms, ACK hold: 200 ms
Status Flags: passive open, gen tcbs
Option Flags: nagle, path mtu capable

Datagrams (max data segment is 1460 bytes):
Rcvd: 447271 (out of order: 0), with data: 217513, total data bytes: 4133039
Sent: 459228 (retransmit: 1023 fastretransmit: 0),with data: 242421, total data bytes: 7908174

BGP neighbor is 10.255.0.78,  remote AS 13238, internal link
 Member of peer-group FB-RR-clients for session parameters
  BGP version 4, remote router ID 95.108.237.145
  BGP state = Established, up for 1w1d
  Last read 00:00:41, last write 00:00:26, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:              146          8
    Keepalives:         13637      13900
    Route Refresh:          0          0
    Total:              13784      13909
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv6 Unicast
  Session: 10.255.0.78
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             300          2 (Consumes 192 bytes)
    Prefixes Total:               348          4
    Implicit Withdraw:            320          0
    Explicit Withdraw:             45          2
    Used as bestpath:             n/a          2
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                         2175          6
    Total:                             2175          6
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 97, min 0

  Address tracking is enabled, the RIB does have a route to 10.255.0.78
  Connections established 33; dropped 32
  Last reset 1w1d, due to Active open failed
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 10.255.0.100, Local port: 64479
Foreign host: 10.255.0.78, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BEF78):
Timer          Starts    Wakeups            Next
Retrans         13749         52             0x0
TimeWait            0          0             0x0
AckHold         13906      13664             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger      2387517    2387516     0x2FE3BF0BB
DeadWait            0          0             0x0
Linger              0          0             0x0

iss:   42009645  snduna:   42289178  sndnxt:   42289178     sndwnd:   8760
irs: 1240676539  rcvnxt: 1240941605  rcvwnd:      16137  delrcvwnd:    247

SRTT: 303 ms, RTTO: 327 ms, RTV: 24 ms, KRTT: 0 ms
minRTT: 4 ms, maxRTT: 476 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1460 bytes):
Rcvd: 27614 (out of order: 0), with data: 13907, total data bytes: 265065
Sent: 27574 (retransmit: 52 fastretransmit: 0),with data: 13725, total data bytes: 279532

BGP neighbor is 10.255.0.80,  remote AS 13238, internal link
 Member of peer-group FB-RR-clients for session parameters
  BGP version 4, remote router ID 95.108.237.147
  BGP state = Established, up for 1w1d
  Last read 00:00:13, last write 00:00:30, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:              148          5
    Keepalives:         13680      13931
    Route Refresh:          0          0
    Total:              13829      13937
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv6 Unicast
  Session: 10.255.0.80
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             300          2 (Consumes 192 bytes)
    Prefixes Total:               350          2
    Implicit Withdraw:            320          0
    Explicit Withdraw:             47          0
    Used as bestpath:             n/a          2
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                         2177          4
    Total:                             2177          4
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 97, min 0

  Address tracking is enabled, the RIB does have a route to 10.255.0.80
  Connections established 47; dropped 46
  Last reset 1w1d, due to Active open failed
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 10.255.0.100, Local port: 48488
Foreign host: 10.255.0.80, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BEFAC):
Timer          Starts    Wakeups            Next
Retrans         13799         54             0x0
TimeWait            0          0             0x0
AckHold         13935      13699             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger      2385416    2385415     0x2FE3BF013
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 3005061506  snduna: 3005342072  sndnxt: 3005342072     sndwnd:   8760
irs:  919741505  rcvnxt:  920006782  rcvwnd:      15928  delrcvwnd:    456

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 8 ms, maxRTT: 604 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1460 bytes):
Rcvd: 28168 (out of order: 0), with data: 13936, total data bytes: 265276
Sent: 27662 (retransmit: 54 fastretransmit: 0),with data: 13768, total data bytes: 280565

BGP neighbor is 10.255.0.92,  remote AS 13238, internal link
 Member of peer-group FB-RR-clients for session parameters
  BGP version 4, remote router ID 87.250.226.114
  BGP state = Established, up for 21w1d
  Last read 00:00:21, last write 00:00:22, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:           115385        374
    Keepalives:        211844     249376
    Route Refresh:          0          2
    Total:             327230     249753
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv6 Unicast
  Session: 10.255.0.92
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             300          4 (Consumes 384 bytes)
    Prefixes Total:             72993          6
    Implicit Withdraw:          19065          0
    Explicit Withdraw:          53630          2
    Used as bestpath:             n/a          4
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                        16818        206
    Total:                            16818        206
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 97, min 0

  Address tracking is enabled, the RIB does have a route to 10.255.0.92
  Connections established 1; dropped 0
  Last reset never
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 10.255.0.100, Local port: 179
Foreign host: 10.255.0.92, Foreign port: 58122
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BEFDC):
Timer          Starts    Wakeups            Next
Retrans        281528       1389             0x0
TimeWait            0          0             0x0
AckHold        249659     244634             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger            0          0             0x0
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 4098002641  snduna: 4114068099  sndnxt: 4114068099     sndwnd:   8760
irs:      27324  rcvnxt:    4799325  rcvwnd:      15548  delrcvwnd:    836

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 0 ms, maxRTT: 2472 ms, ACK hold: 200 ms
Status Flags: passive open, gen tcbs
Option Flags: nagle, path mtu capable

Datagrams (max data segment is 1460 bytes):
Rcvd: 531941 (out of order: 0), with data: 249746, total data bytes: 4772000
Sent: 575067 (retransmit: 1389 fastretransmit: 0),with data: 326339, total data bytes: 16065457

BGP neighbor is 10.255.0.94,  remote AS 13238, internal link
 Member of peer-group FB-RR-clients for session parameters
  BGP version 4, remote router ID 87.250.226.113
  BGP state = Established, up for 21w1d
  Last read 00:00:14, last write 00:00:42, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:           115385        331
    Keepalives:        211931     249275
    Route Refresh:          0          2
    Total:             327317     249609
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv6 Unicast
  Session: 10.255.0.94
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             300          4 (Consumes 384 bytes)
    Prefixes Total:             72993          6
    Implicit Withdraw:          19065          0
    Explicit Withdraw:          53630          2
    Used as bestpath:             n/a          4
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                        16818        182
    Total:                            16818        182
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 97, min 0

  Address tracking is enabled, the RIB does have a route to 10.255.0.94
  Connections established 1; dropped 0
  Last reset never
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 10.255.0.100, Local port: 18182
Foreign host: 10.255.0.94, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF010):
Timer          Starts    Wakeups            Next
Retrans        281627       1310             0x0
TimeWait            0          0             0x0
AckHold        249513     244510             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger     35579398   35579397     0x2FE3BF0BC
DeadWait            0          0             0x0
Linger              0          0             0x0

iss:  248567038  snduna:  264634149  sndnxt:  264634149     sndwnd:   8760
irs: 2901762689  rcvnxt: 2906528594  rcvwnd:      15415  delrcvwnd:    969

SRTT: 303 ms, RTTO: 328 ms, RTV: 25 ms, KRTT: 0 ms
minRTT: 0 ms, maxRTT: 2720 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1460 bytes):
Rcvd: 531175 (out of order: 0), with data: 249603, total data bytes: 4765904
Sent: 574990 (retransmit: 1310 fastretransmit: 0),with data: 326423, total data bytes: 16067110

BGP neighbor is 10.255.0.96,  remote AS 13238, internal link
 Member of peer-group FB-RR-clients for session parameters
  BGP version 4, remote router ID 87.250.226.96
  BGP state = Established, up for 20w1d
  Last read 00:00:02, last write 00:00:28, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:            72670        226
    Keepalives:        209880     233843
    Route Refresh:          0          2
    Total:             282551     234072
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv6 Unicast
  Session: 10.255.0.96
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             300          3 (Consumes 288 bytes)
    Prefixes Total:             46610         13
    Implicit Withdraw:          12093          3
    Explicit Withdraw:          34730          7
    Used as bestpath:             n/a          3
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                        16167        119
    Total:                            16167        119
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 97, min 0

  Address tracking is enabled, the RIB does have a route to 10.255.0.96
  Connections established 1; dropped 0
  Last reset never
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 10.255.0.100, Local port: 179
Foreign host: 10.255.0.96, Foreign port: 49844
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF044):
Timer          Starts    Wakeups            Next
Retrans        254312       1116             0x0
TimeWait            0          0             0x0
AckHold        234057     229352             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger            0          0             0x0
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 1404674685  snduna: 1416253525  sndnxt: 1416253525     sndwnd:   8760
irs:      15580  rcvnxt:    4478982  rcvwnd:      15404  delrcvwnd:    980

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 0 ms, maxRTT: 2772 ms, ACK hold: 200 ms
Status Flags: passive open, gen tcbs
Option Flags: nagle, path mtu capable

Datagrams (max data segment is 1460 bytes):
Rcvd: 488310 (out of order: 0), with data: 234063, total data bytes: 4463401
Sent: 514969 (retransmit: 1116 fastretransmit: 0),with data: 281769, total data bytes: 11578839

BGP neighbor is 10.255.0.98,  remote AS 13238, internal link
 Member of peer-group FB-RR-clients for session parameters
  BGP version 4, remote router ID 87.250.226.93
  BGP state = Established, up for 20w6d
  Last read 00:00:46, last write 00:00:13, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:           102917        208
    Keepalives:        211947     242488
    Route Refresh:          0          4
    Total:             314865     242701
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv6 Unicast
  Session: 10.255.0.98
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 1, Offset 0, Mask 0x2
  Route-Reflector Client
  1 update-group member
  FB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is FB_RR_FILTERING
  Route map for outgoing advertisements is FB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             300          3 (Consumes 288 bytes)
    Prefixes Total:             65298          6
    Implicit Withdraw:          18206          0
    Explicit Withdraw:          47296          3
    Used as bestpath:             n/a          3
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                        20554        115
    Total:                            20554        115
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 97, min 0

  Address tracking is enabled, the RIB does have a route to 10.255.0.98
  Connections established 1; dropped 0
  Last reset never
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 10.255.0.100, Local port: 50734
Foreign host: 10.255.0.98, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF078):
Timer          Starts    Wakeups            Next
Retrans        274249       1244             0x0
TimeWait            0          0             0x0
AckHold        242696     237900             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger     35072162   35072161     0x2FE3BF143
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 3363795228  snduna: 3378551137  sndnxt: 3378551137     sndwnd:   8760
irs: 3559583866  rcvnxt: 3564209766  rcvwnd:      15087  delrcvwnd:   1297

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 0 ms, maxRTT: 2912 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1460 bytes):
Rcvd: 516859 (out of order: 0), with data: 242699, total data bytes: 4625899
Sent: 555773 (retransmit: 1244 fastretransmit: 0),with data: 313872, total data bytes: 14755908

BGP neighbor is 87.250.226.93,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 87.250.226.93
  BGP state = Established, up for 20w6d
  Last read 00:00:27, last write 00:00:37, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:             5787        208
    Keepalives:        231318     242534
    Route Refresh:          0          4
    Total:             237106     242747
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv6 Unicast
  Session: 87.250.226.93
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817          8 (Consumes 768 bytes)
    Prefixes Total:              7428        115
    Implicit Withdraw:           4136         17
    Explicit Withdraw:           3232         90
    Used as bestpath:             n/a          8
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                        65298          6
    Well-known Community:             13126        n/a
    Total:                            78424          6
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 87.250.226.93
  Connections established 1; dropped 0
  Last reset never
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 179
Foreign host: 87.250.226.93, Foreign port: 55185
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF0A8):
Timer          Starts    Wakeups            Next
Retrans        235920       1253             0x0
TimeWait            0          0             0x0
AckHold        242742     237781             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger            0          0             0x0
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 2169411556  snduna: 2174497143  sndnxt: 2174497143     sndwnd:   8616
irs:      15846  rcvnxt:    4642620  rcvwnd:      16346  delrcvwnd:     38

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 0 ms, maxRTT: 2792 ms, ACK hold: 200 ms
Status Flags: passive open, gen tcbs
Option Flags: nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 478504 (out of order: 0), with data: 242745, total data bytes: 4626773
Sent: 477470 (retransmit: 1253 fastretransmit: 0),with data: 235639, total data bytes: 5085586

BGP neighbor is 87.250.226.96,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 87.250.226.96
  BGP state = Established, up for 20w1d
  Last read 00:00:06, last write 00:00:31, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:             5087        226
    Keepalives:        223250     233930
    Route Refresh:          0          2
    Total:             228338     234159
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv6 Unicast
  Session: 87.250.226.96
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817          6 (Consumes 576 bytes)
    Prefixes Total:              5806        119
    Implicit Withdraw:           2669          7
    Explicit Withdraw:           3114        106
    Used as bestpath:             n/a          6
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                        46610         13
    Well-known Community:             10361        n/a
    Total:                            56971         13
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 87.250.226.96
  Connections established 1; dropped 0
  Last reset never
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 179
Foreign host: 87.250.226.96, Foreign port: 65221
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF0DC):
Timer          Starts    Wakeups            Next
Retrans        227481       1109             0x0
TimeWait            0          0             0x0
AckHold        234148     229345             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger            0          0             0x0
DeadWait            0          0             0x0
Linger              0          0             0x0

iss:  272262438  snduna:  277092793  sndnxt:  277092793     sndwnd:   8616
irs:       2550  rcvnxt:    4467605  rcvwnd:      15708  delrcvwnd:    676

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 0 ms, maxRTT: 2640 ms, ACK hold: 200 ms
Status Flags: passive open, gen tcbs
Option Flags: nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 461984 (out of order: 0), with data: 234150, total data bytes: 4465054
Sent: 460557 (retransmit: 1109 fastretransmit: 0),with data: 227285, total data bytes: 4830354

BGP neighbor is 87.250.226.113,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 87.250.226.113
  BGP state = Established, up for 21w1d
  Last read 00:00:16, last write 00:00:27, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: advertised and received
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:            33624        332
    Keepalives:        232372     249247
    Route Refresh:          0          2
    Total:             265997     249582
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  Session: 87.250.226.113
  BGP table version 29827, neighbor version 29827/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             351          0
    Prefixes Total:             14806          0
    Implicit Withdraw:              3          0
    Explicit Withdraw:          14451          0
    Used as bestpath:             n/a          0
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                          287          0
    Total:                              287          0
  Number of NLRIs in the update sent: max 86, min 0

 For address family: VPNv6 Unicast
  Session: 87.250.226.113
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817          4 (Consumes 384 bytes)
    Prefixes Total:              6025        182
    Implicit Withdraw:           1845         34
    Explicit Withdraw:           3361        144
    Used as bestpath:             n/a          4
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                        72993          6
    Well-known Community:             10793        n/a
    Total:                            83786          6
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 87.250.226.113
  Connections established 1; dropped 0
  Last reset never
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 27203
Foreign host: 87.250.226.113, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF114):
Timer          Starts    Wakeups            Next
Retrans        254498       1275             0x0
TimeWait            0          0             0x0
AckHold        249539     244353             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger     35510326   35510325     0x2FE3BF143
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 2624680172  snduna: 2632009231  sndnxt: 2632009231     sndwnd:   8616
irs: 3960300352  rcvnxt: 3965065761  rcvwnd:      15472  delrcvwnd:    912

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 0 ms, maxRTT: 2912 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 503943 (out of order: 0), with data: 249576, total data bytes: 4765408
Sent: 512398 (retransmit: 1275 fastretransmit: 0),with data: 263951, total data bytes: 7329058

BGP neighbor is 87.250.226.114,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 87.250.226.114
  BGP state = Established, up for 21w1d
  Last read 00:00:03, last write 00:00:37, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: advertised and received
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:            33624        375
    Keepalives:        232497     249297
    Route Refresh:          0          2
    Total:             266122     249675
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  Session: 87.250.226.114
  BGP table version 29827, neighbor version 29827/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             351          0
    Prefixes Total:             14806          0
    Implicit Withdraw:              3          0
    Explicit Withdraw:          14451          0
    Used as bestpath:             n/a          0
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                          287          0
    Total:                              287          0
  Number of NLRIs in the update sent: max 86, min 0

 For address family: VPNv6 Unicast
  Session: 87.250.226.114
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817          5 (Consumes 480 bytes)
    Prefixes Total:              6025        206
    Implicit Withdraw:           1845         37
    Explicit Withdraw:           3361        164
    Used as bestpath:             n/a          5
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                        72993          6
    Well-known Community:             10793        n/a
    Total:                            83786          6
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 87.250.226.114
  Connections established 1; dropped 0
  Last reset never
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 179
Foreign host: 87.250.226.114, Foreign port: 58268
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF148):
Timer          Starts    Wakeups            Next
Retrans        254678       1386             0x0
TimeWait            0          0             0x0
AckHold        249631     244342             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger            0          0             0x0
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 1077317590  snduna: 1084649024  sndnxt: 1084649024     sndwnd:   8616
irs:       9360  rcvnxt:    4779896  rcvwnd:      15035  delrcvwnd:   1349

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 0 ms, maxRTT: 2728 ms, ACK hold: 200 ms
Status Flags: passive open, gen tcbs
Option Flags: nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 504272 (out of order: 0), with data: 249668, total data bytes: 4770535
Sent: 512555 (retransmit: 1386 fastretransmit: 0),with data: 264080, total data bytes: 7331433

BGP neighbor is 87.250.226.124,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 87.250.226.124
  BGP state = Established, up for 21w1d
  Last read 00:00:32, last write 00:00:28, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:             7095         20
    Keepalives:        234124     248685
    Route Refresh:          0          9
    Total:             241220     248715
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv6 Unicast
  Session: 87.250.226.124
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817          5 (Consumes 480 bytes)
    Prefixes Total:             11478          8
    Implicit Withdraw:           7298          0
    Explicit Withdraw:           3361          3
    Used as bestpath:             n/a          5
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                        74922          9
    Well-known Community:             18625        n/a
    Total:                            93547          9
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 87.250.226.124
  Connections established 1; dropped 0
  Last reset never
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 54733
Foreign host: 87.250.226.124, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF17C):
Timer          Starts    Wakeups            Next
Retrans        238992       1299             0x0
TimeWait            0          0             0x0
AckHold        248704     243805             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger     35432592   35432591     0x2FE3BF273
DeadWait            0          0             0x0
Linger              0          0             0x0

iss:  456772822  snduna:  462125282  sndnxt:  462125282     sndwnd:   8616
irs: 2706993626  rcvnxt: 2711720871  rcvwnd:      15358  delrcvwnd:   1026

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 0 ms, maxRTT: 2908 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 487589 (out of order: 0), with data: 248709, total data bytes: 4727244
Sent: 486753 (retransmit: 1299 fastretransmit: 0),with data: 238871, total data bytes: 5352459

BGP neighbor is 87.250.226.125,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 87.250.226.125
  BGP state = Established, up for 21w1d
  Last read 00:00:03, last write 00:00:49, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:             7928         18
    Keepalives:        234223     248876
    Route Refresh:          0         13
    Total:             242152     248908
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv6 Unicast
  Session: 87.250.226.125
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817          5 (Consumes 480 bytes)
    Prefixes Total:             14615          7
    Implicit Withdraw:          10435          0
    Explicit Withdraw:           3361          2
    Used as bestpath:             n/a          5
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                        76034          9
    Well-known Community:             23120        n/a
    Total:                            99154          9
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 87.250.226.125
  Connections established 1; dropped 0
  Last reset never
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 50310
Foreign host: 87.250.226.125, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF1B0):
Timer          Starts    Wakeups            Next
Retrans        239186       1302             0x0
TimeWait            0          0             0x0
AckHold        248897     244058             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger     35460702   35460701     0x2FE3BF298
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 1275648465  snduna: 1281154164  sndnxt: 1281154164     sndwnd:   8616
irs: 1763167279  rcvnxt: 1767898077  rcvwnd:      16156  delrcvwnd:    228

SRTT: 301 ms, RTTO: 308 ms, RTV: 7 ms, KRTT: 0 ms
minRTT: 0 ms, maxRTT: 2732 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 487771 (out of order: 0), with data: 248902, total data bytes: 4730797
Sent: 487221 (retransmit: 1302 fastretransmit: 0),with data: 239088, total data bytes: 5505698

BGP neighbor is 87.250.226.189,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 87.250.226.189
  BGP state = Established, up for 3w3d
  Last read 00:00:51, last write 00:00:25, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: advertised and received
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:            28828        209
    Keepalives:         37131      39983
    Route Refresh:          0          2
    Total:              65960      40195
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  Session: 87.250.226.189
  BGP table version 29827, neighbor version 29827/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             351         67 (Consumes 4556 bytes)
    Prefixes Total:             14598         98
    Implicit Withdraw:            502          0
    Explicit Withdraw:          13996         31
    Used as bestpath:             n/a         67
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                           18          2
    Total:                               18          2
  Number of NLRIs in the update sent: max 86, min 0

 For address family: VPNv6 Unicast
  Session: 87.250.226.189
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817         81 (Consumes 7776 bytes)
    Prefixes Total:              2330        102
    Implicit Withdraw:           1464          0
    Explicit Withdraw:            767         21
    Used as bestpath:             n/a         81
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                          971         45
    Well-known Community:              2489        n/a
    Total:                             3460         45
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 87.250.226.189
  Connections established 2; dropped 1
  Last reset 3w3d, due to BGP protocol initialization
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 62448
Foreign host: 87.250.226.189, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF1E8):
Timer          Starts    Wakeups            Next
Retrans         55315        163             0x0
TimeWait            0          0             0x0
AckHold         40154      39269             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger      6778149    6778148     0x2FE3BF273
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 2842521807  snduna: 2845634864  sndnxt: 2845634864     sndwnd:   8616
irs: 2297987013  rcvnxt: 2298866565  rcvwnd:      15985  delrcvwnd:    399

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 4 ms, maxRTT: 800 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 95381 (out of order: 0), with data: 40224, total data bytes: 879551
Sent: 104638 (retransmit: 163 fastretransmit: 0),with data: 64728, total data bytes: 3113056

BGP neighbor is 87.250.226.192,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 87.250.226.192
  BGP state = Established, up for 21w1d
  Last read 00:00:20, last write 00:00:04, hold time is 90, keepalive interval is 30 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: advertised and received
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:            33206         52
    Keepalives:        462152     457286
    Route Refresh:          0          0
    Total:             495359     457339
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  Session: 87.250.226.192
  BGP table version 29827, neighbor version 29827/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             351         16 (Consumes 1088 bytes)
    Prefixes Total:             14806         28
    Implicit Withdraw:              3          0
    Explicit Withdraw:          14451         12
    Used as bestpath:             n/a         16
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                          287          0
    Total:                              287          0
  Number of NLRIs in the update sent: max 86, min 0

 For address family: VPNv6 Unicast
  Session: 87.250.226.192
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817          0
    Prefixes Total:              4485         13
    Implicit Withdraw:            305          2
    Explicit Withdraw:           3361         11
    Used as bestpath:             n/a          0
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                        72202          0
    Well-known Community:              8473        n/a
    Total:                            80675          0
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 87.250.226.192
  Connections established 1; dropped 0
  Last reset never
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 41137
Foreign host: 87.250.226.192, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF21C):
Timer          Starts    Wakeups            Next
Retrans        483886        872             0x0
TimeWait            0          0             0x0
AckHold        457315     446169             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger     36423979   36423978     0x2FE3BF273
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 2273701462  snduna: 2285321097  sndnxt: 2285321097     sndwnd:  16384
irs: 2793879538  rcvnxt: 2802572015  rcvwnd:      15415  delrcvwnd:    969

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 0 ms, maxRTT: 2828 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 941296 (out of order: 0), with data: 457316, total data bytes: 8692476
Sent: 947655 (retransmit: 872 fastretransmit: 0),with data: 493655, total data bytes: 11619634

BGP neighbor is 87.250.226.200,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 87.250.226.200
  BGP state = Established, up for 3w3d
  Last read 00:00:52, last write 00:00:36, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: advertised and received
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:            28777        162
    Keepalives:         37044      39830
    Route Refresh:          0          2
    Total:              65822      39995
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  Session: 87.250.226.200
  BGP table version 29827, neighbor version 29827/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             351         67 (Consumes 4556 bytes)
    Prefixes Total:             14532         99
    Implicit Withdraw:            502          0
    Explicit Withdraw:          13930         32
    Used as bestpath:             n/a         67
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                           16          2
    Total:                               16          2
  Number of NLRIs in the update sent: max 86, min 0

 For address family: VPNv6 Unicast
  Session: 87.250.226.200
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817         81 (Consumes 7776 bytes)
    Prefixes Total:              2251         98
    Implicit Withdraw:           1463          0
    Explicit Withdraw:            689         17
    Used as bestpath:             n/a         80
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                          966         44
    Well-known Community:              2497        n/a
    Total:                             3463         44
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 87.250.226.200
  Connections established 2; dropped 1
  Last reset 3w3d, due to BGP protocol initialization
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 179
Foreign host: 87.250.226.200, Foreign port: 51515
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF254):
Timer          Starts    Wakeups            Next
Retrans         55183        156             0x0
TimeWait            0          0             0x0
AckHold         39961      39085             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger            0          0             0x0
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 3153518076  snduna: 3156618872  sndnxt: 3156618872     sndwnd:   8616
irs:      18432  rcvnxt:     890700  rcvwnd:      15510  delrcvwnd:    874

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 0 ms, maxRTT: 1200 ms, ACK hold: 200 ms
Status Flags: passive open, gen tcbs
Option Flags: nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 95033 (out of order: 0), with data: 40022, total data bytes: 872267
Sent: 104306 (retransmit: 156 fastretransmit: 0),with data: 64596, total data bytes: 3100795

BGP neighbor is 87.250.228.176,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 87.250.228.176
  BGP state = Established, up for 8w1d
  Last read 00:00:26, last write 00:00:02, hold time is 90, keepalive interval is 30 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: advertised and received
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:            29712        320
    Keepalives:        177012     175140
    Route Refresh:          0          0
    Total:             206725     175461
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  Session: 87.250.228.176
  BGP table version 29827, neighbor version 29827/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             351         84 (Consumes 5712 bytes)
    Prefixes Total:             14475        103
    Implicit Withdraw:            232          0
    Explicit Withdraw:          14121         19
    Used as bestpath:             n/a         84
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                           12          0
    Total:                               12          0
  Number of NLRIs in the update sent: max 65, min 0

 For address family: VPNv6 Unicast
  Session: 87.250.228.176
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817        782 (Consumes 75072 bytes)
    Prefixes Total:              2372        922
    Implicit Withdraw:            760          0
    Explicit Withdraw:           1498        140
    Used as bestpath:             n/a        782
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                         1128          0
    Well-known Community:              1612        n/a
    Total:                             2740          0
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 50, min 0

  Address tracking is enabled, the RIB does have a route to 87.250.228.176
  Connections established 4; dropped 3
  Last reset 8w1d, due to BGP protocol initialization
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 16754
Foreign host: 87.250.228.176, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF28C):
Timer          Starts    Wakeups            Next
Retrans        196421        659             0x0
TimeWait            0          0             0x0
AckHold        175384     170320             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger     13773395   13773394     0x2FE3BF3A3
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 2513823008  snduna: 2519672020  sndnxt: 2519672020     sndwnd:  16384
irs:  184125580  rcvnxt:  187498398  rcvwnd:      15035  delrcvwnd:   1349

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 8 ms, maxRTT: 2908 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 372691 (out of order: 0), with data: 175393, total data bytes: 3372817
Sent: 379839 (retransmit: 659 fastretransmit: 0),with data: 205609, total data bytes: 5849011

BGP neighbor is 87.250.234.13,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 87.250.234.13
  BGP state = Established, up for 21w1d
  Last read 00:00:22, last write 00:00:26, hold time is 90, keepalive interval is 30 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: advertised and received
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:            33206          5
    Keepalives:        462087     458095
    Route Refresh:          0          0
    Total:             495294     458101
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  Session: 87.250.234.13
  BGP table version 29827, neighbor version 29827/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             351          0
    Prefixes Total:             14806         24
    Implicit Withdraw:              3          0
    Explicit Withdraw:          14451         24
    Used as bestpath:             n/a          0
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                          287          0
    Total:                              287          0
  Number of NLRIs in the update sent: max 86, min 0

 For address family: VPNv6 Unicast
  Session: 87.250.234.13
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817          0
    Prefixes Total:              4485          0
    Implicit Withdraw:            305          0
    Explicit Withdraw:           3361          0
    Used as bestpath:             n/a          0
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                        72202          0
    Well-known Community:              8473        n/a
    Total:                            80675          0
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 87.250.234.13
  Connections established 1; dropped 0
  Last reset never
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 37897
Foreign host: 87.250.234.13, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF2C0):
Timer          Starts    Wakeups            Next
Retrans        483905        920             0x0
TimeWait            0          0             0x0
AckHold        458100     446889             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger     36440512   36440511     0x2FE3BF3A3
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 3156088735  snduna: 3167707135  sndnxt: 3167707135     sndwnd:  16384
irs: 1166131378  rcvnxt: 1174836242  rcvwnd:      15985  delrcvwnd:    399

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 4 ms, maxRTT: 2712 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 942170 (out of order: 0), with data: 458100, total data bytes: 8704863
Sent: 948346 (retransmit: 920 fastretransmit: 0),with data: 493591, total data bytes: 11618399

BGP neighbor is 87.250.234.217,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 87.250.234.217
  BGP state = Established, up for 4w0d
  Last read 00:00:10, last write 00:00:04, hold time is 90, keepalive interval is 30 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: advertised and received
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:            28624          0
    Keepalives:         86696      87736
    Route Refresh:          0          0
    Total:             115321      87737
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  Session: 87.250.234.217
  BGP table version 29827, neighbor version 29827/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             351          0
    Prefixes Total:             14414          0
    Implicit Withdraw:            318          0
    Explicit Withdraw:          14063          0
    Used as bestpath:             n/a          0
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                           13          0
    Total:                               13          0
  Number of NLRIs in the update sent: max 86, min 0

 For address family: VPNv6 Unicast
  Session: 87.250.234.217
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817          0
    Prefixes Total:              1695          0
    Implicit Withdraw:            821          0
    Explicit Withdraw:            849          0
    Used as bestpath:             n/a          0
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                          773          0
    Well-known Community:              1326        n/a
    Total:                             2099          0
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 87.250.234.217
  Connections established 2; dropped 1
  Last reset 4w0d, due to BGP protocol initialization
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 42515
Foreign host: 87.250.234.217, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF2F8):
Timer          Starts    Wakeups            Next
Retrans        104667          5             0x0
TimeWait            0          0             0x0
AckHold         87737      85848             0x0
SendWnd             5          3             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger      7938183    7938182     0x2FE3BF3A3
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 4092929945  snduna: 4096950919  sndnxt: 4096950919     sndwnd:  16384
irs:  843688451  rcvnxt:  845355503  rcvwnd:      15719  delrcvwnd:    665

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 8 ms, maxRTT: 1000 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 192075 (out of order: 0), with data: 87737, total data bytes: 1667051
Sent: 201295 (retransmit: 5 fastretransmit: 0),with data: 114281, total data bytes: 4020973

BGP neighbor is 95.108.237.47,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 95.108.237.47
  BGP state = Established, up for 21w1d
  Last read 00:00:26, last write 00:00:18, hold time is 90, keepalive interval is 30 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: advertised and received
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:            33206       5471
    Keepalives:        462046     444945
    Route Refresh:          0          0
    Total:             495253     450417
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  Session: 95.108.237.47
  BGP table version 29827, neighbor version 29827/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             351         68 (Consumes 4624 bytes)
    Prefixes Total:             14806        101
    Implicit Withdraw:              3          0
    Explicit Withdraw:          14451         33
    Used as bestpath:             n/a         68
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                          287          0
    Total:                              287          0
  Number of NLRIs in the update sent: max 86, min 0

 For address family: VPNv6 Unicast
  Session: 95.108.237.47
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817        595 (Consumes 57120 bytes)
    Prefixes Total:              4485       5810
    Implicit Withdraw:            305         34
    Explicit Withdraw:           3361       5181
    Used as bestpath:             n/a        595
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                        72202          0
    Well-known Community:              8473        n/a
    Total:                            80675          0
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 95.108.237.47
  Connections established 1; dropped 0
  Last reset never
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 57754
Foreign host: 95.108.237.47, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF32C):
Timer          Starts    Wakeups            Next
Retrans        483868        923             0x0
TimeWait            0          0             0x0
AckHold        449683     438419             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger     36458725   36458724     0x2FE3BF3A3
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 3086891637  snduna: 3098509258  sndnxt: 3098509258     sndwnd:  16384
irs: 1338609033  rcvnxt: 1347658627  rcvwnd:      15700  delrcvwnd:    684

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 4 ms, maxRTT: 2812 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 933711 (out of order: 0), with data: 449705, total data bytes: 9049593
Sent: 940002 (retransmit: 923 fastretransmit: 0),with data: 493550, total data bytes: 11617620

BGP neighbor is 95.108.237.48,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 95.108.237.48
  BGP state = Established, up for 16w2d
  Last read 00:00:28, last write 00:00:30, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family IPv4 Unicast: received
    Address family VPNv4 Unicast: advertised and received
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:            31103        140
    Keepalives:        177905     190594
    Route Refresh:          0          1
    Total:             209009     190736
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  Session: 95.108.237.48
  BGP table version 29827, neighbor version 29827/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             351          8 (Consumes 544 bytes)
    Prefixes Total:             14704         12
    Implicit Withdraw:            383          0
    Explicit Withdraw:          14349          4
    Used as bestpath:             n/a          8
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                          253          0
    Total:                              253          0
  Number of NLRIs in the update sent: max 86, min 0

 For address family: VPNv6 Unicast
  Session: 95.108.237.48
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817         14 (Consumes 1344 bytes)
    Prefixes Total:              3962         45
    Implicit Withdraw:           1742          3
    Explicit Withdraw:           2196         28
    Used as bestpath:             n/a         14
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                         5689         67
    Well-known Community:              8026        n/a
    Total:                            13715         67
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 95.108.237.48
  Connections established 7; dropped 6
  Last reset 16w2d, due to Peer closed the session of session 1
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 179
Foreign host: 95.108.237.48, Foreign port: 59936
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF364):
Timer          Starts    Wakeups            Next
Retrans        198511       1227             0x0
TimeWait            0          0             0x0
AckHold        190721     186725             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger            0          0             0x0
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 3337021572  snduna: 3343054534  sndnxt: 3343054534     sndwnd:   8616
irs:       3060  rcvnxt:    3641596  rcvwnd:      15206  delrcvwnd:   1178

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 8 ms, maxRTT: 2840 ms, ACK hold: 200 ms
Status Flags: passive open, gen tcbs
Option Flags: nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 390085 (out of order: 0), with data: 190729, total data bytes: 3638535
Sent: 397558 (retransmit: 1227 fastretransmit: 0),with data: 207520, total data bytes: 6032961

BGP neighbor is 95.108.237.50,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 0.0.0.0
  BGP state = Idle
  Neighbor sessions:
    0 active, is multisession capable
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  BGP table version 29827, neighbor version 0/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             351          0
    Prefixes Total:                 0          0
    Implicit Withdraw:              0          0
    Explicit Withdraw:              0          0
    Used as bestpath:             n/a          0
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    Total:                                0          0
  Number of NLRIs in the update sent: max 0, min 0

 For address family: VPNv6 Unicast
  BGP table version 199130, neighbor version 0/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817          0
    Prefixes Total:                 0          0
    Implicit Withdraw:              0          0
    Explicit Withdraw:              0          0
    Used as bestpath:             n/a          0
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    Total:                                0          0
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 0, min 0

  Address tracking is enabled, the RIB does have a route to 95.108.237.50
  Connections established 0; dropped 0
  Last reset never
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
  No active TCP connection

BGP neighbor is 95.108.237.138,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 95.108.237.138
  BGP state = Established, up for 2w1d
  Last read 00:00:18, last write 00:00:29, hold time is 90, keepalive interval is 30 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:              585         43
    Keepalives:         49823      48139
    Route Refresh:          0          0
    Total:              50409      48183
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv6 Unicast
  Session: 95.108.237.138
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817          0
    Prefixes Total:              1037         22
    Implicit Withdraw:            827          0
    Explicit Withdraw:            193         22
    Used as bestpath:             n/a          0
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                          400          0
    Well-known Community:              1292        n/a
    Total:                             1692          0
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 46, min 0

  Address tracking is enabled, the RIB does have a route to 95.108.237.138
  Connections established 1; dropped 0
  Last reset never
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 58925
Foreign host: 95.108.237.138, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF3B0):
Timer          Starts    Wakeups            Next
Retrans         50134          1             0x0
TimeWait            0          0             0x0
AckHold         48182      47180             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger      4401390    4401389     0x2FE3BF4D3
DeadWait            0          0             0x0
Linger              0          0             0x0

iss:  618433147  snduna:  619453002  sndnxt:  619453002     sndwnd:  16384
irs: 3087486866  rcvnxt: 3088404999  rcvwnd:      15339  delrcvwnd:   1045

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 4 ms, maxRTT: 800 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 98131 (out of order: 0), with data: 48182, total data bytes: 918132
Sent: 98065 (retransmit: 1 fastretransmit: 0),with data: 50246, total data bytes: 1019854

BGP neighbor is 95.108.237.139,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 95.108.237.139
  BGP state = Established, up for 22:45:51
  Last read 00:00:04, last write 00:00:08, hold time is 90, keepalive interval is 30 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:              206          1
    Keepalives:          2977       2815
    Route Refresh:          0          0
    Total:               3184       2817
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv6 Unicast
  Session: 95.108.237.139
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817          2 (Consumes 192 bytes)
    Prefixes Total:               837          2
    Implicit Withdraw:            827          0
    Explicit Withdraw:             10          0
    Used as bestpath:             n/a          2
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                          305          0
    Well-known Community:              1217        n/a
    Total:                             1522          0
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 46, min 0

  Address tracking is enabled, the RIB does have a route to 95.108.237.139
  Connections established 3; dropped 2
  Last reset 23:07:20, due to Active open failed
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 22118
Foreign host: 95.108.237.139, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF3E4):
Timer          Starts    Wakeups            Next
Retrans          3016          0             0x0
TimeWait            0          0             0x0
AckHold          2817       2762             0x0
SendWnd             1          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger       262766     262765     0x2FE3BF4D3
DeadWait            0          0             0x0
Linger              0          0             0x0

iss:  759178095  snduna:  759272798  sndnxt:  759272798     sndwnd:  16384
irs:  186593311  rcvnxt:  186646988  rcvwnd:      16137  delrcvwnd:    247

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 4 ms, maxRTT: 436 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 5827 (out of order: 0), with data: 2817, total data bytes: 53676
Sent: 5841 (retransmit: 0 fastretransmit: 0),with data: 3039, total data bytes: 94702

BGP neighbor is 95.108.237.140,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 95.108.237.140
  BGP state = Established, up for 19w6d
  Last read 00:00:22, last write 00:00:07, hold time is 90, keepalive interval is 30 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:             5108         13
    Keepalives:        434246     414963
    Route Refresh:          0          2
    Total:             439355     414979
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv6 Unicast
  Session: 95.108.237.140
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817          0
    Prefixes Total:              5760         11
    Implicit Withdraw:           2685          4
    Explicit Withdraw:           3049          7
    Used as bestpath:             n/a          0
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                        38694          0
    Well-known Community:             10158        n/a
    Total:                            48852          0
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 95.108.237.140
  Connections established 1; dropped 0
  Last reset never
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 44013
Foreign host: 95.108.237.140, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF418):
Timer          Starts    Wakeups            Next
Retrans        438259       1000             0x0
TimeWait            0          0             0x0
AckHold        414979     404999             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger     33571997   33571996     0x2FE3BF4D3
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 2594506809  snduna: 2603350558  sndnxt: 2603350558     sndwnd:  16384
irs: 1995340664  rcvnxt: 2003226283  rcvwnd:      15037  delrcvwnd:   1347

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 4 ms, maxRTT: 2808 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 853496 (out of order: 0), with data: 414979, total data bytes: 7885618
Sent: 850440 (retransmit: 1000 fastretransmit: 0),with data: 438200, total data bytes: 8843748

BGP neighbor is 95.108.237.141,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 95.108.237.141
  BGP state = Established, up for 19w6d
  Last read 00:00:15, last write 00:00:23, hold time is 90, keepalive interval is 30 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:             5108          9
    Keepalives:        434239     415220
    Route Refresh:          0          2
    Total:             439348     415232
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv6 Unicast
  Session: 95.108.237.141
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817          2 (Consumes 192 bytes)
    Prefixes Total:              5760         10
    Implicit Withdraw:           2683          4
    Explicit Withdraw:           3049          4
    Used as bestpath:             n/a          2
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                        38694          0
    Well-known Community:             10158        n/a
    Total:                            48852          0
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 95.108.237.141
  Connections established 1; dropped 0
  Last reset never
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 63169
Foreign host: 95.108.237.141, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF44C):
Timer          Starts    Wakeups            Next
Retrans        438277       1018             0x0
TimeWait            0          0             0x0
AckHold        415232     405068             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger     33614981   33614980     0x2FE3BF4D3
DeadWait            0          0             0x0
Linger              0          0             0x0

iss:  859473508  snduna:  868317124  sndnxt:  868317124     sndwnd:  16384
irs: 1881529928  rcvnxt: 1889420174  rcvwnd:      16194  delrcvwnd:    190

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 4 ms, maxRTT: 2912 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 853717 (out of order: 0), with data: 415232, total data bytes: 7890245
Sent: 850544 (retransmit: 1018 fastretransmit: 0),with data: 438197, total data bytes: 8843615

BGP neighbor is 95.108.237.142,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 95.108.237.142
  BGP state = Established, up for 19w1d
  Last read 00:00:42, last write 00:00:29, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:             4410          3
    Keepalives:        212110     217402
    Route Refresh:          0          0
    Total:             216521     217406
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv6 Unicast
  Session: 95.108.237.142
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817          2 (Consumes 192 bytes)
    Prefixes Total:              4028          2
    Implicit Withdraw:           1079          0
    Explicit Withdraw:           2925          0
    Used as bestpath:             n/a          2
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                        25741          2
    Well-known Community:              7423        n/a
    Total:                            33164          2
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 95.108.237.142
  Connections established 4; dropped 3
  Last reset 19w1d, due to Active open failed
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 179
Foreign host: 95.108.237.142, Foreign port: 51837
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF480):
Timer          Starts    Wakeups            Next
Retrans        216095       1058             0x0
TimeWait            0          0             0x0
AckHold        217403     213064             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger            0          0             0x0
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 2225694901  snduna: 2230212688  sndnxt: 2230212688     sndwnd:   8616
irs:      22910  rcvnxt:    4153898  rcvwnd:      15244  delrcvwnd:   1140

SRTT: 300 ms, RTTO: 304 ms, RTV: 4 ms, KRTT: 0 ms
minRTT: 4 ms, maxRTT: 2760 ms, ACK hold: 200 ms
Status Flags: passive open, gen tcbs
Option Flags: nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 439041 (out of order: 0), with data: 217405, total data bytes: 4130987
Sent: 432566 (retransmit: 1058 fastretransmit: 0),with data: 215808, total data bytes: 4517786

BGP neighbor is 95.108.237.143,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 95.108.237.143
  BGP state = Established, up for 19w1d
  Last read 00:00:40, last write 00:00:34, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:             4410          3
    Keepalives:        212143     217512
    Route Refresh:          0          0
    Total:             216554     217516
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv6 Unicast
  Session: 95.108.237.143
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817          2 (Consumes 192 bytes)
    Prefixes Total:              4028          2
    Implicit Withdraw:           1081          0
    Explicit Withdraw:           2925          0
    Used as bestpath:             n/a          2
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                        25734          2
    Well-known Community:              7423        n/a
    Total:                            33157          2
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 95.108.237.143
  Connections established 3; dropped 2
  Last reset 19w1d, due to Active open failed
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 179
Foreign host: 95.108.237.143, Foreign port: 51572
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF4B4):
Timer          Starts    Wakeups            Next
Retrans        216047        987             0x0
TimeWait            0          0             0x0
AckHold        217513     213202             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger            0          0             0x0
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 4239971263  snduna: 4244489677  sndnxt: 4244489677     sndwnd:   8616
irs:       1674  rcvnxt:    4134752  rcvwnd:      16042  delrcvwnd:    342

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 4 ms, maxRTT: 3256 ms, ACK hold: 200 ms
Status Flags: passive open, gen tcbs
Option Flags: nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 433858 (out of order: 0), with data: 217515, total data bytes: 4133077
Sent: 432749 (retransmit: 987 fastretransmit: 0),with data: 215851, total data bytes: 4518413

BGP neighbor is 95.108.237.144,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 95.108.237.144
  BGP state = Established, up for 18w1d
  Last read 00:00:11, last write 00:00:05, hold time is 90, keepalive interval is 30 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:             5461         40
    Keepalives:        399522     388098
    Route Refresh:          0          6
    Total:             404984     388145
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv6 Unicast
  Session: 95.108.237.144
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817          4 (Consumes 384 bytes)
    Prefixes Total:              8626         24
    Implicit Withdraw:           5850          4
    Explicit Withdraw:           2743         16
    Used as bestpath:             n/a          4
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                         9881          0
    Well-known Community:             14510        n/a
    Total:                            24391          0
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 95.108.237.144
  Connections established 1; dropped 0
  Last reset never
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 14840
Foreign host: 95.108.237.144, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF4E8):
Timer          Starts    Wakeups            Next
Retrans        403303       1041             0x0
TimeWait            0          0             0x0
AckHold        388145     378466             0x0
SendWnd             1          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger     30750078   30750077     0x2FE3BF603
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 3360533127  snduna: 3368823227  sndnxt: 3368823227     sndwnd:  16384
irs:  996106264  rcvnxt: 1003483749  rcvwnd:      14978  delrcvwnd:   1406

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 4 ms, maxRTT: 2812 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 791961 (out of order: 0), with data: 388145, total data bytes: 7377484
Sent: 788616 (retransmit: 1041 fastretransmit: 0),with data: 403169, total data bytes: 8290099

BGP neighbor is 95.108.237.145,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 95.108.237.145
  BGP state = Established, up for 1w1d
  Last read 00:00:48, last write 00:00:29, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:              393          8
    Keepalives:         13605      13916
    Route Refresh:          0          0
    Total:              13999      13925
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv6 Unicast
  Session: 95.108.237.145
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817          4 (Consumes 384 bytes)
    Prefixes Total:               937          6
    Implicit Withdraw:            820          0
    Explicit Withdraw:             95          2
    Used as bestpath:             n/a          4
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                          348          4
    Well-known Community:              1238        n/a
    Total:                             1586          4
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 95.108.237.145
  Connections established 2; dropped 1
  Last reset 1w1d, due to BGP protocol initialization
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 30058
Foreign host: 95.108.237.145, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF520):
Timer          Starts    Wakeups            Next
Retrans         13864         67             0x0
TimeWait            0          0             0x0
AckHold         13922      13669             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger      2380014    2380013     0x2FE3BF603
DeadWait            0          0             0x0
Linger              0          0             0x0

iss:  507831154  snduna:  508145593  sndnxt:  508145593     sndwnd:   8616
irs: 3917107974  rcvnxt: 3917373344  rcvwnd:      15282  delrcvwnd:   1102

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 4 ms, maxRTT: 572 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 27744 (out of order: 0), with data: 13923, total data bytes: 265369
Sent: 27714 (retransmit: 67 fastretransmit: 0),with data: 13852, total data bytes: 314438

BGP neighbor is 95.108.237.146,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 95.108.237.146
  BGP state = Established, up for 18w1d
  Last read 00:00:28, last write 00:00:07, hold time is 90, keepalive interval is 30 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:             5461         40
    Keepalives:        399467     388313
    Route Refresh:          0          6
    Total:             404929     388360
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv6 Unicast
  Session: 95.108.237.146
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817          4 (Consumes 384 bytes)
    Prefixes Total:              8626         24
    Implicit Withdraw:           5850          4
    Explicit Withdraw:           2743         16
    Used as bestpath:             n/a          4
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                         9881          0
    Well-known Community:             14510        n/a
    Total:                            24391          0
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 95.108.237.146
  Connections established 1; dropped 0
  Last reset never
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 37784
Foreign host: 95.108.237.146, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF554):
Timer          Starts    Wakeups            Next
Retrans        403151        939             0x0
TimeWait            0          0             0x0
AckHold        388360     378752             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger     30742854   30742853     0x2FE3BF603
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 1776435499  snduna: 1784724554  sndnxt: 1784724554     sndwnd:  16384
irs: 3592009008  rcvnxt: 3599390578  rcvwnd:      15130  delrcvwnd:   1254

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 4 ms, maxRTT: 3072 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 791934 (out of order: 0), with data: 388360, total data bytes: 7381569
Sent: 788839 (retransmit: 939 fastretransmit: 1),with data: 403113, total data bytes: 8290490

BGP neighbor is 95.108.237.147,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 95.108.237.147
  BGP state = Established, up for 1w1d
  Last read 00:00:57, last write 00:00:49, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:              395          5
    Keepalives:         13616      13944
    Route Refresh:          0          0
    Total:              14012      13950
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv6 Unicast
  Session: 95.108.237.147
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817          4 (Consumes 384 bytes)
    Prefixes Total:               939          4
    Implicit Withdraw:            820          0
    Explicit Withdraw:             97          0
    Used as bestpath:             n/a          4
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                          350          2
    Well-known Community:              1238        n/a
    Total:                             1588          2
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 95.108.237.147
  Connections established 2; dropped 1
  Last reset 1w1d, due to BGP protocol initialization
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 179
Foreign host: 95.108.237.147, Foreign port: 63130
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF58C):
Timer          Starts    Wakeups            Next
Retrans         13866         61             0x0
TimeWait            0          0             0x0
AckHold         13948      13705             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger            0          0             0x0
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 3670877836  snduna: 3671192700  sndnxt: 3671192700     sndwnd:   8616
irs:       4785  rcvnxt:     270309  rcvwnd:      15130  delrcvwnd:   1254

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 4 ms, maxRTT: 600 ms, ACK hold: 200 ms
Status Flags: passive open, gen tcbs
Option Flags: nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 27776 (out of order: 0), with data: 13949, total data bytes: 265523
Sent: 27759 (retransmit: 61 fastretransmit: 0),with data: 13864, total data bytes: 314863

BGP neighbor is 95.108.237.168,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 95.108.237.168
  BGP state = Established, up for 6w0d
  Last read 00:00:29, last write 00:00:26, hold time is 90, keepalive interval is 30 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: advertised
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:            15295          1
    Keepalives:        133992     127946
    Route Refresh:          0         73
    Total:             149288     128021
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  BGP table version 29827, neighbor version 0/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             351          0
    Prefixes Total:                 0          0
    Implicit Withdraw:              0          0
    Explicit Withdraw:              0          0
    Used as bestpath:             n/a          0
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    Total:                                0          0
  Number of NLRIs in the update sent: max 0, min 0

 For address family: VPNv6 Unicast
  Session: 95.108.237.168
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817          2 (Consumes 192 bytes)
    Prefixes Total:             60213          2
    Implicit Withdraw:          58857          0
    Explicit Withdraw:           1319          0
    Used as bestpath:             n/a          2
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                        22590          0
    Well-known Community:             87674        n/a
    Total:                           110264          0
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 95.108.237.168
  Connections established 3; dropped 2
  Last reset 6w0d, due to Active open failed
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 55370
Foreign host: 95.108.237.168, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF5C0):
Timer          Starts    Wakeups            Next
Retrans        136413         16             0x0
TimeWait            0          0             0x0
AckHold        128020     125329             0x0
SendWnd            18          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger     11905270   11905269     0x2FE3BF603
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 2969925295  snduna: 2975285083  sndnxt: 2975285083     sndwnd:  16384
irs:  159821167  rcvnxt:  162254012  rcvwnd:      15377  delrcvwnd:   1007

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 4 ms, maxRTT: 1404 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 264266 (out of order: 0), with data: 128020, total data bytes: 2432844
Sent: 264655 (retransmit: 16 fastretransmit: 1),with data: 137611, total data bytes: 5361223

BGP neighbor is 95.108.237.169,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 95.108.237.169
  BGP state = Established, up for 5w2d
  Last read 00:00:27, last write 00:00:05, hold time is 90, keepalive interval is 30 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: advertised
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:             1582          1
    Keepalives:        118737     112757
    Route Refresh:          0          0
    Total:             120320     112759
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  BGP table version 29827, neighbor version 0/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             351          0
    Prefixes Total:                 0          0
    Implicit Withdraw:              0          0
    Explicit Withdraw:              0          0
    Used as bestpath:             n/a          0
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    Total:                                0          0
  Number of NLRIs in the update sent: max 0, min 0

 For address family: VPNv6 Unicast
  Session: 95.108.237.169
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817          2 (Consumes 192 bytes)
    Prefixes Total:              2117          2
    Implicit Withdraw:            834          0
    Explicit Withdraw:           1251          0
    Used as bestpath:             n/a          2
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                          889          0
    Well-known Community:              1420        n/a
    Total:                             2309          0
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 50, min 0

  Address tracking is enabled, the RIB does have a route to 95.108.237.169
  Connections established 1; dropped 0
  Last reset never
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 52486
Foreign host: 95.108.237.169, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF5F8):
Timer          Starts    Wakeups            Next
Retrans        119868         22             0x0
TimeWait            0          0             0x0
AckHold        112758     110478             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger     10562779   10562778     0x2FE3BF603
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 2689104981  snduna: 2691560536  sndnxt: 2691560536     sndwnd:  16384
irs: 4074934716  rcvnxt: 4077077291  rcvwnd:      15263  delrcvwnd:   1121

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 4 ms, maxRTT: 1404 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 232202 (out of order: 0), with data: 112758, total data bytes: 2142574
Sent: 232072 (retransmit: 22 fastretransmit: 0),with data: 120099, total data bytes: 2455554

BGP neighbor is 95.108.237.200,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 95.108.237.200
  BGP state = Established, up for 3w6d
  Last read 00:00:03, last write 00:00:25, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: advertised and received
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:            28618         48
    Keepalives:         42507      46288
    Route Refresh:          0          0
    Total:              71126      46337
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  Session: 95.108.237.200
  BGP table version 29827, neighbor version 29827/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             351          0
    Prefixes Total:             14414          0
    Implicit Withdraw:            318          0
    Explicit Withdraw:          14063          0
    Used as bestpath:             n/a          0
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                           13          0
    Total:                               13          0
  Number of NLRIs in the update sent: max 86, min 0

 For address family: VPNv6 Unicast
  Session: 95.108.237.200
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817          2 (Consumes 192 bytes)
    Prefixes Total:              1691          6
    Implicit Withdraw:            817          0
    Explicit Withdraw:            845          4
    Used as bestpath:             n/a          2
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                          771          4
    Well-known Community:              1326        n/a
    Total:                             2097          4
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 95.108.237.200
  Connections established 2; dropped 1
  Last reset 3w6d, due to BGP protocol initialization
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 44464
Foreign host: 95.108.237.200, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF62C):
Timer          Starts    Wakeups            Next
Retrans         60647        245             0x0
TimeWait            0          0             0x0
AckHold         46323      45415             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger      7715298    7715297     0x2FE3BF733
DeadWait            0          0             0x0
Linger              0          0             0x0

iss:  612379119  snduna:  615559926  sndnxt:  615559926     sndwnd:   8616
irs: 2731861845  rcvnxt: 2732852602  rcvwnd:      15966  delrcvwnd:    418

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 4 ms, maxRTT: 800 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 106808 (out of order: 0), with data: 46377, total data bytes: 990756
Sent: 116210 (retransmit: 245 fastretransmit: 0),with data: 70088, total data bytes: 3180806

BGP neighbor is 95.108.237.220,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 95.108.237.220
  BGP state = Established, up for 4w2d
  Last read 00:00:50, last write 00:00:32, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: advertised and received
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:            28694         51
    Keepalives:         46621      50700
    Route Refresh:          0          0
    Total:              75316      50752
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  Session: 95.108.237.220
  BGP table version 29827, neighbor version 29827/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             351          0
    Prefixes Total:             14418          0
    Implicit Withdraw:            320          0
    Explicit Withdraw:          14067          0
    Used as bestpath:             n/a          0
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                           13          0
    Total:                               13          0
  Number of NLRIs in the update sent: max 86, min 0

 For address family: VPNv6 Unicast
  Session: 95.108.237.220
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817          2 (Consumes 192 bytes)
    Prefixes Total:              1730          9
    Implicit Withdraw:            821          3
    Explicit Withdraw:            880          4
    Used as bestpath:             n/a          2
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                          802          6
    Well-known Community:              1356        n/a
    Total:                             2158          6
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 95.108.237.220
  Connections established 2; dropped 1
  Last reset 4w2d, due to BGP protocol initialization
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 65353
Foreign host: 95.108.237.220, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF660):
Timer          Starts    Wakeups            Next
Retrans         64886        255             0x0
TimeWait            0          0             0x0
AckHold         50751      49738             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger      8451808    8451807     0x2FE3BF733
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 4134959377  snduna: 4138225287  sndnxt: 4138225287     sndwnd:   8616
irs: 2433834415  rcvnxt: 2434909414  rcvwnd:      15491  delrcvwnd:    893

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 4 ms, maxRTT: 868 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 120907 (out of order: 0), with data: 50790, total data bytes: 1074998
Sent: 124803 (retransmit: 255 fastretransmit: 0),with data: 74277, total data bytes: 3265909

BGP neighbor is 95.108.237.238,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 95.108.237.238
  BGP state = Established, up for 5w2d
  Last read 00:00:22, last write 00:00:33, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: advertised
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:             1556          3
    Keepalives:         58324      59404
    Route Refresh:          0          0
    Total:              59881      59408
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  BGP table version 29827, neighbor version 0/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             351          0
    Prefixes Total:                 0          0
    Implicit Withdraw:              0          0
    Explicit Withdraw:              0          0
    Used as bestpath:             n/a          0
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    Total:                                0          0
  Number of NLRIs in the update sent: max 0, min 0

 For address family: VPNv6 Unicast
  Session: 95.108.237.238
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817          2 (Consumes 192 bytes)
    Prefixes Total:              2100          2
    Implicit Withdraw:            833          0
    Explicit Withdraw:           1234          0
    Used as bestpath:             n/a          2
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                          883          2
    Well-known Community:              1420        n/a
    Total:                             2303          2
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 95.108.237.238
  Connections established 2; dropped 1
  Last reset 5w2d, due to BGP protocol initialization
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 179
Foreign host: 95.108.237.238, Foreign port: 56605
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF698):
Timer          Starts    Wakeups            Next
Retrans         59633        190             0x0
TimeWait            0          0             0x0
AckHold         59406      58337             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger            0          0             0x0
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 1499770169  snduna: 1501075426  sndnxt: 1501075426     sndwnd:   8616
irs:       1505  rcvnxt:    1130531  rcvwnd:      15130  delrcvwnd:   1254

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 4 ms, maxRTT: 1244 ms, ACK hold: 200 ms
Status Flags: passive open, gen tcbs
Option Flags: nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 118932 (out of order: 0), with data: 59407, total data bytes: 1129025
Sent: 118816 (retransmit: 190 fastretransmit: 0),with data: 59665, total data bytes: 1305256

BGP neighbor is 95.108.237.255,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 95.108.237.255
  BGP state = Established, up for 17w0d
  Last read 00:00:32, last write 00:00:28, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: advertised
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:             3439        288
    Keepalives:        188803     198461
    Route Refresh:          0          1
    Total:             192243     198751
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  BGP table version 29827, neighbor version 0/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             351          0
    Prefixes Total:                 0          0
    Implicit Withdraw:              0          0
    Explicit Withdraw:              0          0
    Used as bestpath:             n/a          0
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    Total:                                0          0
  Number of NLRIs in the update sent: max 0, min 0

 For address family: VPNv6 Unicast
  Session: 95.108.237.255
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817          4 (Consumes 384 bytes)
    Prefixes Total:              4034        154
    Implicit Withdraw:           1770          4
    Explicit Withdraw:           2256        146
    Used as bestpath:             n/a          4
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                         5872          6
    Well-known Community:              8185        n/a
    Total:                            14057          6
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 95.108.237.255
  Connections established 2; dropped 1
  Last reset 17w0d, due to BGP protocol initialization
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 30841
Foreign host: 95.108.237.255, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF6CC):
Timer          Starts    Wakeups            Next
Retrans        192066       1030             0x0
TimeWait            0          0             0x0
AckHold        198738     194401             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger     27881095   27881094     0x2FE3BF733
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 3755061782  snduna: 3759059421  sndnxt: 3759059421     sndwnd:   8616
irs: 4075948642  rcvnxt: 4079749175  rcvwnd:      16194  delrcvwnd:    190

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 4 ms, maxRTT: 2948 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 391198 (out of order: 0), with data: 198740, total data bytes: 3800532
Sent: 389483 (retransmit: 1030 fastretransmit: 0),with data: 191558, total data bytes: 3997638

BGP neighbor is 100.43.92.159,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 100.43.92.159
  BGP state = Established, up for 11w2d
  Last read 00:00:21, last write 00:00:15, hold time is 90, keepalive interval is 30 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: advertised and received
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:            30170          4
    Keepalives:        244022     244465
    Route Refresh:          0          0
    Total:             274193     244470
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  Session: 100.43.92.159
  BGP table version 29827, neighbor version 29827/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             351          5 (Consumes 340 bytes)
    Prefixes Total:             14572          6
    Implicit Withdraw:            305          0
    Explicit Withdraw:          14218          1
    Used as bestpath:             n/a          5
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                           12          0
    Total:                               12          0
  Number of NLRIs in the update sent: max 86, min 0

 For address family: VPNv6 Unicast
  Session: 100.43.92.159
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817          2 (Consumes 192 bytes)
    Prefixes Total:              2680          2
    Implicit Withdraw:            838          0
    Explicit Withdraw:           1802          0
    Used as bestpath:             n/a          2
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                         1930          0
    Well-known Community:              3379        n/a
    Total:                             5309          0
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 100.43.92.159
  Connections established 6; dropped 5
  Last reset 11w2d, due to BGP protocol initialization
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 179
Foreign host: 100.43.92.159, Foreign port: 51909
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF708):
Timer          Starts    Wakeups            Next
Retrans        267850       4358             0x0
TimeWait            0          0             0x0
AckHold        244468     238051             0x0
SendWnd             1          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger            0          0             0x0
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 1374539327  snduna: 1381711939  sndnxt: 1381711939     sndwnd:  16384
irs: 2354837085  rcvnxt: 2359482393  rcvwnd:      14997  delrcvwnd:   1387

SRTT: 300 ms, RTTO: 306 ms, RTV: 6 ms, KRTT: 0 ms
minRTT: 128 ms, maxRTT: 3208 ms, ACK hold: 200 ms
Status Flags: passive open, gen tcbs
Option Flags: nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 513402 (out of order: 0), with data: 244468, total data bytes: 4645307
Sent: 516265 (retransmit: 4358 fastretransmit: 0),with data: 272981, total data bytes: 7172611

BGP neighbor is 141.8.136.191,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 141.8.136.191
  BGP state = Established, up for 12w0d
  Last read 00:00:13, last write 00:00:37, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:             3110         89
    Keepalives:        133653     142015
    Route Refresh:          0          3
    Total:             136764     142108
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv6 Unicast
  Session: 141.8.136.191
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817         45 (Consumes 4320 bytes)
    Prefixes Total:              5023         61
    Implicit Withdraw:           3112          0
    Explicit Withdraw:           1839         16
    Used as bestpath:             n/a         45
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                         3461         26
    Well-known Community:              8843        n/a
    Total:                            12304         26
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 141.8.136.191
  Connections established 2; dropped 1
  Last reset 12w1d, due to BGP protocol initialization
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 41532
Foreign host: 141.8.136.191, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF740):
Timer          Starts    Wakeups            Next
Retrans        137347       1871             0x0
TimeWait            0          0             0x0
AckHold        142098     139085             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger     18882911   18882910     0x2FE3BF863
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 2256927043  snduna: 2259871336  sndnxt: 2259871336     sndwnd:   8616
irs:  273228303  rcvnxt:  275936335  rcvwnd:      16213  delrcvwnd:    171

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 24 ms, maxRTT: 2760 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 279745 (out of order: 0), with data: 142103, total data bytes: 2708031
Sent: 277685 (retransmit: 1871 fastretransmit: 0),with data: 135917, total data bytes: 2944292

BGP neighbor is 141.8.136.192,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 141.8.136.192
  BGP state = Established, up for 21w1d
  Last read 00:00:20, last write 00:00:39, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:             5676        215
    Keepalives:        234140     245566
    Route Refresh:          0          2
    Total:             239817     245784
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv6 Unicast
  Session: 141.8.136.192
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817         64 (Consumes 6144 bytes)
    Prefixes Total:              5977        130
    Implicit Withdraw:           1797          0
    Explicit Withdraw:           3361         66
    Used as bestpath:             n/a         64
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                        73218         41
    Well-known Community:             10737        n/a
    Total:                            83955         41
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 141.8.136.192
  Connections established 1; dropped 0
  Last reset never
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 56104
Foreign host: 141.8.136.192, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF774):
Timer          Starts    Wakeups            Next
Retrans        240156       2557             0x0
TimeWait            0          0             0x0
AckHold        245767     240798             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger     35022230   35022229     0x2FE3BF863
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 1962830801  snduna: 1967922598  sndnxt: 1967922598     sndwnd:   8616
irs: 1070691739  rcvnxt: 1075377983  rcvwnd:      15415  delrcvwnd:    969

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 24 ms, maxRTT: 2764 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 486047 (out of order: 0), with data: 245777, total data bytes: 4686243
Sent: 483515 (retransmit: 2557 fastretransmit: 0),with data: 238655, total data bytes: 5091796

BGP neighbor is 141.8.136.241,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 141.8.136.241
  BGP state = Established, up for 3w0d
  Last read 00:00:19, last write 00:00:46, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: received
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:              632         25
    Keepalives:         33293      35321
    Route Refresh:          0          0
    Total:              33926      35347
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv6 Unicast
  Session: 141.8.136.241
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817         48 (Consumes 4608 bytes)
    Prefixes Total:              1062         52
    Implicit Withdraw:            778          0
    Explicit Withdraw:            218          4
    Used as bestpath:             n/a         48
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                          415         11
    Well-known Community:              1299        n/a
    Total:                             1714         11
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 141.8.136.241
  Connections established 3; dropped 2
  Last reset 3w0d, due to BGP protocol initialization
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 179
Foreign host: 141.8.136.241, Foreign port: 57238
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF7A8):
Timer          Starts    Wakeups            Next
Retrans         34225        582             0x0
TimeWait            0          0             0x0
AckHold         35332      34709             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger            0          0             0x0
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 3726895905  snduna: 3727606024  sndnxt: 3727606024     sndwnd:   8616
irs:      14160  rcvnxt:     688551  rcvwnd:      14967  delrcvwnd:   1417

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 24 ms, maxRTT: 800 ms, ACK hold: 200 ms
Status Flags: passive open, gen tcbs
Option Flags: nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 69399 (out of order: 0), with data: 35336, total data bytes: 674390
Sent: 68967 (retransmit: 582 fastretransmit: 0),with data: 33770, total data bytes: 710118

BGP neighbor is 141.8.136.242,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 141.8.136.242
  BGP state = Established, up for 3w3d
  Last read 00:00:09, last write 00:00:30, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: advertised and received
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:            28791      27446
    Keepalives:         36393      40346
    Route Refresh:          0          3
    Total:              65185      67796
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  Session: 141.8.136.242
  BGP table version 29827, neighbor version 29827/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             351         35 (Consumes 2380 bytes)
    Prefixes Total:             14919      13886
    Implicit Withdraw:            955          0
    Explicit Withdraw:          13930      13851
    Used as bestpath:             n/a         35
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                           27          0
    Total:                               27          0
  Number of NLRIs in the update sent: max 86, min 0

 For address family: VPNv6 Unicast
  Session: 141.8.136.242
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817         51 (Consumes 4896 bytes)
    Prefixes Total:              2193         57
    Implicit Withdraw:           1534          0
    Explicit Withdraw:            588          6
    Used as bestpath:             n/a         51
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                          969         39
    Well-known Community:              2497        n/a
    Total:                             3466         39
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 141.8.136.242
  Connections established 2; dropped 1
  Last reset 3w3d, due to BGP protocol initialization
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 26327
Foreign host: 141.8.136.242, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF7E4):
Timer          Starts    Wakeups            Next
Retrans         61538        605             0x0
TimeWait            0          0             0x0
AckHold         66422      39802             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger      6592810    6592809     0x2FE3BF863
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 2284188678  snduna: 2287281395  sndnxt: 2287281395     sndwnd:   8616
irs: 2247184434  rcvnxt: 2250001687  rcvwnd:      15094  delrcvwnd:   1290

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 20 ms, maxRTT: 1012 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 123080 (out of order: 0), with data: 67645, total data bytes: 2817252
Sent: 105657 (retransmit: 605 fastretransmit: 0),with data: 63911, total data bytes: 3092716

BGP neighbor is 141.8.136.243,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 141.8.136.243
  BGP state = Established, up for 3w2d
  Last read 00:00:26, last write 00:00:21, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: received
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:              739         29
    Keepalives:         36395      38472
    Route Refresh:          0          0
    Total:              37135      38502
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv6 Unicast
  Session: 141.8.136.243
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817         51 (Consumes 4896 bytes)
    Prefixes Total:              1213         56
    Implicit Withdraw:            723          0
    Explicit Withdraw:            369          5
    Used as bestpath:             n/a         51
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                          581         15
    Well-known Community:              1305        n/a
    Total:                             1886         15
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 141.8.136.243
  Connections established 3; dropped 2
  Last reset 3w2d, due to BGP protocol initialization
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 179
Foreign host: 141.8.136.243, Foreign port: 59591
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF81C):
Timer          Starts    Wakeups            Next
Retrans         37428        614             0x0
TimeWait            0          0             0x0
AckHold         38484      37815             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger            0          0             0x0
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 1182460270  snduna: 1183245088  sndnxt: 1183245088     sndwnd:   8616
irs:      11040  rcvnxt:     745966  rcvwnd:      15100  delrcvwnd:   1284

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 24 ms, maxRTT: 1060 ms, ACK hold: 200 ms
Status Flags: passive open, gen tcbs
Option Flags: nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 75712 (out of order: 0), with data: 38488, total data bytes: 734925
Sent: 75313 (retransmit: 614 fastretransmit: 0),with data: 36965, total data bytes: 784817

BGP neighbor is 141.8.136.244,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 141.8.136.244
  BGP state = Established, up for 3w0d
  Last read 00:00:41, last write 00:00:43, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: received
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:              642         28
    Keepalives:         33345      35252
    Route Refresh:          0          0
    Total:              33988      35281
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv6 Unicast
  Session: 141.8.136.244
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817         51 (Consumes 4896 bytes)
    Prefixes Total:              1108         56
    Implicit Withdraw:            773          0
    Explicit Withdraw:            264          5
    Used as bestpath:             n/a         51
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                          415         15
    Well-known Community:              1299        n/a
    Total:                             1714         15
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 141.8.136.244
  Connections established 3; dropped 2
  Last reset 3w0d, due to Peer closed the session of session 1
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 179
Foreign host: 141.8.136.244, Foreign port: 61370
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF850):
Timer          Starts    Wakeups            Next
Retrans         34156        459             0x0
TimeWait            0          0             0x0
AckHold         35263      34631             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger            0          0             0x0
DeadWait            0          0             0x0
Linger              0          0             0x0

iss:  171485083  snduna:  172198919  sndnxt:  172198919     sndwnd:   8616
irs:          0  rcvnxt:     673491  rcvwnd:      15852  delrcvwnd:    532

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 20 ms, maxRTT: 812 ms, ACK hold: 200 ms
Status Flags: passive open, gen tcbs
Option Flags: nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 69291 (out of order: 0), with data: 35267, total data bytes: 673490
Sent: 68945 (retransmit: 459 fastretransmit: 0),with data: 33826, total data bytes: 713835

BGP neighbor is 141.8.136.245,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 141.8.136.245
  BGP state = Established, up for 21w1d
  Last read 00:00:13, last write 00:00:34, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: advertised
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:             5444         89
    Keepalives:        234121     249452
    Route Refresh:          0          1
    Total:             239566     249543
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  BGP table version 29827, neighbor version 0/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             351          0
    Prefixes Total:                 0          0
    Implicit Withdraw:              0          0
    Explicit Withdraw:              0          0
    Used as bestpath:             n/a          0
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    Total:                                0          0
  Number of NLRIs in the update sent: max 0, min 0

 For address family: VPNv6 Unicast
  Session: 141.8.136.245
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817         20 (Consumes 1920 bytes)
    Prefixes Total:              5229         77
    Implicit Withdraw:           1049          0
    Explicit Withdraw:           3361         57
    Used as bestpath:             n/a         20
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                        72710         19
    Well-known Community:              9603        n/a
    Total:                            82313         19
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 141.8.136.245
  Connections established 1; dropped 0
  Last reset never
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 49576
Foreign host: 141.8.136.245, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF888):
Timer          Starts    Wakeups            Next
Retrans        240350       2797             0x0
TimeWait            0          0             0x0
AckHold        249520     244638             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger     34835174   34835173     0x2FE3BF993
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 3451050494  snduna: 3456102275  sndnxt: 3456102275     sndwnd:   8616
irs:  264295321  rcvnxt:  269044430  rcvwnd:      16118  delrcvwnd:    266

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 20 ms, maxRTT: 2804 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 489656 (out of order: 0), with data: 249527, total data bytes: 4749108
Sent: 487346 (retransmit: 2797 fastretransmit: 0),with data: 238592, total data bytes: 5051780

BGP neighbor is 141.8.136.246,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 141.8.136.246
  BGP state = Established, up for 21w1d
  Last read 00:00:27, last write 00:00:28, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: advertised
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:             5444        108
    Keepalives:        234104     249339
    Route Refresh:          0          1
    Total:             239549     249449
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  BGP table version 29827, neighbor version 0/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             351          0
    Prefixes Total:                 0          0
    Implicit Withdraw:              0          0
    Explicit Withdraw:              0          0
    Used as bestpath:             n/a          0
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    Total:                                0          0
  Number of NLRIs in the update sent: max 0, min 0

 For address family: VPNv6 Unicast
  Session: 141.8.136.246
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817         20 (Consumes 1920 bytes)
    Prefixes Total:              5229         97
    Implicit Withdraw:           1049          0
    Explicit Withdraw:           3361         77
    Used as bestpath:             n/a         19
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                        72710         23
    Well-known Community:              9603        n/a
    Total:                            82313         23
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 141.8.136.246
  Connections established 1; dropped 0
  Last reset never
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 179
Foreign host: 141.8.136.246, Foreign port: 54992
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF8BC):
Timer          Starts    Wakeups            Next
Retrans        240402       2858             0x0
TimeWait            0          0             0x0
AckHold        249419     244415             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger            0          0             0x0
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 1067044438  snduna: 1072095888  sndnxt: 1072095888     sndwnd:   8616
irs:       8448  rcvnxt:    4757806  rcvwnd:      15263  delrcvwnd:   1121

SRTT: 301 ms, RTTO: 308 ms, RTV: 7 ms, KRTT: 0 ms
minRTT: 20 ms, maxRTT: 2812 ms, ACK hold: 200 ms
Status Flags: passive open, gen tcbs
Option Flags: nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 489891 (out of order: 0), with data: 249427, total data bytes: 4749357
Sent: 487139 (retransmit: 2858 fastretransmit: 0),with data: 238575, total data bytes: 5051449

BGP neighbor is 141.8.136.247,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 141.8.136.247
  BGP state = Established, up for 21w1d
  Last read 00:00:38, last write 00:00:40, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: advertised
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:             5444         86
    Keepalives:        234203     249459
    Route Refresh:          0          1
    Total:             239648     249547
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  BGP table version 29827, neighbor version 0/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             351          0
    Prefixes Total:                 0          0
    Implicit Withdraw:              0          0
    Explicit Withdraw:              0          0
    Used as bestpath:             n/a          0
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    Total:                                0          0
  Number of NLRIs in the update sent: max 0, min 0

 For address family: VPNv6 Unicast
  Session: 141.8.136.247
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817         20 (Consumes 1920 bytes)
    Prefixes Total:              5229         89
    Implicit Withdraw:           1049          0
    Explicit Withdraw:           3361         69
    Used as bestpath:             n/a         19
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                        72710         21
    Well-known Community:              9603        n/a
    Total:                            82313         21
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 141.8.136.247
  Connections established 1; dropped 0
  Last reset never
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 26714
Foreign host: 141.8.136.247, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF8F0):
Timer          Starts    Wakeups            Next
Retrans        240501       2858             0x0
TimeWait            0          0             0x0
AckHold        249525     244586             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger     34780988   34780987     0x2FE3BF993
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 3484672891  snduna: 3489726230  sndnxt: 3489726230     sndwnd:   8616
irs: 1060666445  rcvnxt: 1065416055  rcvwnd:      15757  delrcvwnd:    627

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 20 ms, maxRTT: 2808 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 489905 (out of order: 0), with data: 249531, total data bytes: 4749609
Sent: 487346 (retransmit: 2858 fastretransmit: 0),with data: 238665, total data bytes: 5053338

BGP neighbor is 141.8.136.248,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 141.8.136.248
  BGP state = Established, up for 21w1d
  Last read 00:00:41, last write 00:00:34, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: advertised
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:             5444         85
    Keepalives:        234167     249300
    Route Refresh:          0          1
    Total:             239612     249387
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  BGP table version 29827, neighbor version 0/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             351          0
    Prefixes Total:                 0          0
    Implicit Withdraw:              0          0
    Explicit Withdraw:              0          0
    Used as bestpath:             n/a          0
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    Total:                                0          0
  Number of NLRIs in the update sent: max 0, min 0

 For address family: VPNv6 Unicast
  Session: 141.8.136.248
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817         20 (Consumes 1920 bytes)
    Prefixes Total:              5229         77
    Implicit Withdraw:           1049          0
    Explicit Withdraw:           3361         57
    Used as bestpath:             n/a         19
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                        72710         14
    Well-known Community:              9603        n/a
    Total:                            82313         14
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 141.8.136.248
  Connections established 1; dropped 0
  Last reset never
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 55554
Foreign host: 141.8.136.248, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF928):
Timer          Starts    Wakeups            Next
Retrans        240758       3161             0x0
TimeWait            0          0             0x0
AckHold        249375     244487             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger     34791804   34791803     0x2FE3BF9CF
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 1335659873  snduna: 1340712528  sndnxt: 1340712528     sndwnd:   8616
irs: 3694431475  rcvnxt: 3699176962  rcvwnd:      16099  delrcvwnd:    285

SRTT: 300 ms, RTTO: 307 ms, RTV: 7 ms, KRTT: 0 ms
minRTT: 24 ms, maxRTT: 3208 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 489801 (out of order: 0), with data: 249380, total data bytes: 4745486
Sent: 487224 (retransmit: 3161 fastretransmit: 0),with data: 238641, total data bytes: 5052654

BGP neighbor is 141.8.136.251,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 141.8.136.251
  BGP state = Established, up for 3w0d
  Last read 00:00:38, last write 00:00:28, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: advertised
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:              656          7
    Keepalives:         33354      35226
    Route Refresh:          0          0
    Total:              34011      35234
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  BGP table version 29827, neighbor version 0/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             351          0
    Prefixes Total:                 0          0
    Implicit Withdraw:              0          0
    Explicit Withdraw:              0          0
    Used as bestpath:             n/a          0
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    Total:                                0          0
  Number of NLRIs in the update sent: max 0, min 0

 For address family: VPNv6 Unicast
  Session: 141.8.136.251
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817          4 (Consumes 384 bytes)
    Prefixes Total:              1159          4
    Implicit Withdraw:            821          0
    Explicit Withdraw:            315          0
    Used as bestpath:             n/a          4
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                          415          3
    Well-known Community:              1299        n/a
    Total:                             1714          3
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 141.8.136.251
  Connections established 3; dropped 2
  Last reset 3w0d, due to BGP protocol initialization
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 13603
Foreign host: 141.8.136.251, Foreign port: 179
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF95C):
Timer          Starts    Wakeups            Next
Retrans         34348        633             0x0
TimeWait            0          0             0x0
AckHold         35231      34616             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger      5715373    5715372     0x2FE3BF9F7
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 2991001641  snduna: 2991719029  sndnxt: 2991719029     sndwnd:   8616
irs: 2716567314  rcvnxt: 2717237415  rcvwnd:      16308  delrcvwnd:     76

SRTT: 306 ms, RTTO: 355 ms, RTV: 49 ms, KRTT: 0 ms
minRTT: 20 ms, maxRTT: 1964 ms, ACK hold: 200 ms
Status Flags: none
Option Flags: higher precendence, nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 69396 (out of order: 0), with data: 35232, total data bytes: 670100
Sent: 68941 (retransmit: 633 fastretransmit: 0),with data: 33840, total data bytes: 717387

BGP neighbor is 141.8.136.252,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 141.8.136.252
  BGP state = Established, up for 2w3d
  Last read 00:00:38, last write 00:00:34, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: advertised
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:              606          4
    Keepalives:         28056      29661
    Route Refresh:          0          0
    Total:              28663      29666
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  BGP table version 29827, neighbor version 0/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             351          0
    Prefixes Total:                 0          0
    Implicit Withdraw:              0          0
    Explicit Withdraw:              0          0
    Used as bestpath:             n/a          0
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    Total:                                0          0
  Number of NLRIs in the update sent: max 0, min 0

 For address family: VPNv6 Unicast
  Session: 141.8.136.252
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817          3 (Consumes 288 bytes)
    Prefixes Total:              1047          3
    Implicit Withdraw:            821          0
    Explicit Withdraw:            203          0
    Used as bestpath:             n/a          3
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                          408          3
    Well-known Community:              1292        n/a
    Total:                             1700          3
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 141.8.136.252
  Connections established 3; dropped 2
  Last reset 2w3d, due to BGP protocol initialization
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 179
Foreign host: 141.8.136.252, Foreign port: 54832
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF990):
Timer          Starts    Wakeups            Next
Retrans         28960        573             0x0
TimeWait            0          0             0x0
AckHold         29663      29151             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger            0          0             0x0
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 1016347324  snduna: 1016955472  sndnxt: 1016955472     sndwnd:   8616
irs:      16353  rcvnxt:     580400  rcvwnd:      15491  delrcvwnd:    893

SRTT: 300 ms, RTTO: 304 ms, RTV: 4 ms, KRTT: 0 ms
minRTT: 24 ms, maxRTT: 800 ms, ACK hold: 200 ms
Status Flags: passive open, gen tcbs
Option Flags: nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 58472 (out of order: 0), with data: 29664, total data bytes: 564046
Sent: 58069 (retransmit: 573 fastretransmit: 0),with data: 28511, total data bytes: 608147

BGP neighbor is 141.8.136.253,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 141.8.136.253
  BGP state = Established, up for 3w1d
  Last read 00:00:09, last write 00:00:34, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: advertised
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:              691          6
    Keepalives:         36204      38162
    Route Refresh:          0          0
    Total:              36896      38169
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  BGP table version 29827, neighbor version 0/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             351          0
    Prefixes Total:                 0          0
    Implicit Withdraw:              0          0
    Explicit Withdraw:              0          0
    Used as bestpath:             n/a          0
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    Total:                                0          0
  Number of NLRIs in the update sent: max 0, min 0

 For address family: VPNv6 Unicast
  Session: 141.8.136.253
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817          4 (Consumes 384 bytes)
    Prefixes Total:              1177          4
    Implicit Withdraw:            816          0
    Explicit Withdraw:            333          0
    Used as bestpath:             n/a          4
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                          537          3
    Well-known Community:              1305        n/a
    Total:                             1842          3
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 141.8.136.253
  Connections established 2; dropped 1
  Last reset 3w1d, due to Active open failed
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 179
Foreign host: 141.8.136.253, Foreign port: 57995
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF9C4):
Timer          Starts    Wakeups            Next
Retrans         37302        724             0x0
TimeWait            0          0             0x0
AckHold         38167      37516             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger            0          0             0x0
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 3376953398  snduna: 3377728361  sndnxt: 3377728361     sndwnd:   8616
irs:      23560  rcvnxt:     749345  rcvwnd:      15624  delrcvwnd:    760

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 20 ms, maxRTT: 1000 ms, ACK hold: 200 ms
Status Flags: passive open, gen tcbs
Option Flags: nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 75271 (out of order: 0), with data: 38168, total data bytes: 725784
Sent: 74765 (retransmit: 724 fastretransmit: 0),with data: 36723, total data bytes: 774962

BGP neighbor is 141.8.136.254,  remote AS 13238, internal link
 Member of peer-group BB-RR-clients for session parameters
  BGP version 4, remote router ID 141.8.136.254
  BGP state = Established, up for 11w1d
  Last read 00:00:26, last write 00:00:35, hold time is 180, keepalive interval is 60 seconds
  Neighbor sessions:
    1 active, is not multisession capable
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family VPNv4 Unicast: advertised
    Address family VPNv6 Unicast: advertised and received
  Message statistics:
    InQ depth is 0
    OutQ depth is 0
   
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:             2435         29
    Keepalives:        123984     131189
    Route Refresh:          0          0
    Total:             126420     131219
  Default minimum time between advertisement runs is 0 seconds

 For address family: VPNv4 Unicast
  BGP table version 29827, neighbor version 0/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             351          0
    Prefixes Total:                 0          0
    Implicit Withdraw:              0          0
    Explicit Withdraw:              0          0
    Used as bestpath:             n/a          0
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    Total:                                0          0
  Number of NLRIs in the update sent: max 0, min 0

 For address family: VPNv6 Unicast
  Session: 141.8.136.254
  BGP table version 199130, neighbor version 199130/0
  Output queue size : 0
  Index 2, Offset 0, Mask 0x4
  Route-Reflector Client
  2 update-group member
  BB-RR-clients peer-group member
  Community attribute sent to this neighbor
  Inbound path policy configured
  Outbound path policy configured
  Route map for incoming advertisements is BB_RR_FILTERING
  Route map for outgoing advertisements is BB_RR_FILTERING
                                 Sent       Rcvd
  Prefix activity:               ----       ----
    Prefixes Current:             817          3 (Consumes 288 bytes)
    Prefixes Total:              2680          9
    Implicit Withdraw:            840          0
    Explicit Withdraw:           1802          6
    Used as bestpath:             n/a          3
    Used as multipath:            n/a          0

                                   Outbound    Inbound
  Local Policy Denied Prefixes:    --------    -------
    route-map:                         1917          9
    Well-known Community:              3366        n/a
    Total:                             5283          9
  Maximum prefixes allowed 3000
  Threshold for warning message 80%, restart interval 1 min
  Number of NLRIs in the update sent: max 75, min 0

  Address tracking is enabled, the RIB does have a route to 141.8.136.254
  Connections established 1; dropped 0
  Last reset never
  Transport(tcp) path-mtu-discovery is enabled
  Graceful-Restart is disabled
Connection state is ESTAB, I/O status: 1, unread input bytes: 0       
Connection is ECN Disabled
Mininum incoming TTL 0, Outgoing TTL 255
Local host: 87.250.234.40, Local port: 179
Foreign host: 141.8.136.254, Foreign port: 53799
Connection tableid (VRF): 0

Enqueued packets for retransmit: 0, input: 0  mis-ordered: 0 (0 bytes)

Event Timers (current time is 0x2FE3BF9FC):
Timer          Starts    Wakeups            Next
Retrans        127667       1974             0x0
TimeWait            0          0             0x0
AckHold        131209     128414             0x0
SendWnd             0          0             0x0
KeepAlive           0          0             0x0
GiveUp              0          0             0x0
PmtuAger            0          0             0x0
DeadWait            0          0             0x0
Linger              0          0             0x0

iss: 1256995893  snduna: 1259638404  sndnxt: 1259638404     sndwnd:   8616
irs:      21146  rcvnxt:    2516329  rcvwnd:      15073  delrcvwnd:   1311

SRTT: 300 ms, RTTO: 303 ms, RTV: 3 ms, KRTT: 0 ms
minRTT: 20 ms, maxRTT: 3072 ms, ACK hold: 200 ms
Status Flags: passive open, gen tcbs
Option Flags: nagle, path mtu capable

Datagrams (max data segment is 1436 bytes):
Rcvd: 259074 (out of order: 0), with data: 131218, total data bytes: 2495182
Sent: 256988 (retransmit: 1974 fastretransmit: 0),with data: 126074, total data bytes: 2642510
"""
