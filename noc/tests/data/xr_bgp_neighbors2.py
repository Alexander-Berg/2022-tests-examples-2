cmd = "show bgp neighbors detail"
host = "kor-arr1"

content = """
Thu Aug 16 21:10:26.896 MSK

BGP neighbor is 5.45.192.45
 Remote AS 13238, local AS 13238, internal link
 Remote router ID 0.0.0.0
 Cluster ID 87.250.234.14
  BGP state = Active
  NSR State: None
  Last read 00:00:00, Last read before reset 6w1d
  Hold time is 180, keepalive interval is 60 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 6w1d, attempted 108, written 108
  Second last write 6w1d, attempted 187, written 187
  Last write before reset 6w1d, attempted 108, written 108
  Second last write before reset 6w1d, attempted 187, written 187
  Last write pulse rcvd  Jul  4 16:09:42.249 last full Jun 26 15:02:34.296 pulse count 205857
  Last write pulse rcvd before reset 6w1d
  Socket not armed for io, not armed for read, not armed for write
  Last write thread event before reset 6w1d, second last 6w1d
  Last KA expiry before reset 6w1d, second last 6w1d
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 6w1d, second last 6w1d
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Jun 26 15:02:28.884      933  Jun 26 15:02:28.897        6
    Notification:   Jun 26 14:14:40.553        1  Jul  4 16:09:42.248        4
    Update:         Jul  4 16:09:42.232   343475  Jun 26 15:02:29.125        5
    Keepalive:      Jul  4 09:01:14.841     1248  Jul  4 16:09:36.439    14488
    Route_Refresh:  ---                        0  ---                        0
    Total:                                345657                         14503
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 0
  Update group: 0.6 Filter-group: 0.0  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is DENY_ALL
  Policy for outgoing advertisements is EXPORT_SLB
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 0, suppressed 0, withdrawn 0
  Maximum prefixes allowed 131072
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 0, Last synced ack version 0
  Outstanding version objects: current 0, max 12
  Additional-paths operation: Send and Receive
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

  Connections established 5; dropped 5
  Local host: 87.250.234.14, Local port: 12004, IF Handle: 0x00000000
  Foreign host: 5.45.192.45, Foreign port: 179
  Last reset 6w1d, due to BGP Notification received: administrative shutdown
  Time since last notification sent to neighbor: 7w2d
  Error Code: unsupported/disjoint capability
  Notification data sent:
    None
  Time since last notification received from neighbor: 6w1d
  Error Code: administrative shutdown
  Notification data received:
    None

BGP neighbor is 5.45.200.24
 Remote AS 13238, local AS 13238, internal link
 Description: fra1-b1
 Remote router ID 5.45.200.24
 Cluster ID 87.250.234.14
  BGP state = Established, up for 2w0d
  NSR State: None
  BFD enabled (session up): mininterval: 3000 multiplier: 3
  Last read 00:00:08, Last read before reset 2w0d
  Hold time is 90, keepalive interval is 30 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 179, written 179
  Second last write 00:00:00, attempted 187, written 187
  Last write before reset 2w0d, attempted 54, written 54
  Second last write before reset 2w0d, attempted 54, written 54
  Last write pulse rcvd  Aug 16 21:10:26.995 last full Aug  2 11:03:50.115 pulse count 7698200
  Last write pulse rcvd before reset 2w0d
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 2w0d, second last 2w0d
  Last KA expiry before reset 2w0d, second last 2w0d
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 2w0d, second last 2w0d
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Aug  2 11:02:14.763       28  Aug  2 11:02:14.899       28
    Notification:   ---                        0  Jul 13 00:40:07.106        3
    Update:         Aug 16 21:10:26.866 12097518  Aug  2 11:02:24.289       65
    Keepalive:      Aug 16 16:00:09.146   146068  Aug 16 21:10:18.152   811702
    Route_Refresh:  ---                        0  ---                        0
    Total:                              12243614                        811798
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.6 Filter-group: 0.2  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB
  5 accepted prefixes, 5 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 197787, suppressed 0, withdrawn 115707
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 23
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470206
  Update group: 0.6 Filter-group: 0.2  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB
  4 accepted prefixes, 4 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 716691, suppressed 0, withdrawn 367602
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470204, Last synced ack version 0
  Outstanding version objects: current 4, max 57
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 26; dropped 25
  Local host: 87.250.234.14, Local port: 22018, IF Handle: 0x00000000
  Foreign host: 5.45.200.24, Foreign port: 179
  Last reset 2w0d, due to BFD (Bidirectional forwarding detection) session down
  Time since last notification received from neighbor: 4w6d
  Error Code: connection rejected
  Notification data received:
    None

BGP neighbor is 5.45.247.180
 Remote AS 13238, local AS 13238, internal link
 Description: ams1-b1
 Remote router ID 5.45.247.180
 Cluster ID 87.250.234.14
  BGP state = Established, up for 01:52:52
  NSR State: None
  BFD enabled (session up): mininterval: 3000 multiplier: 3
  Last read 00:00:00, Last read before reset 01:53:18
  Hold time is 90, keepalive interval is 30 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 179, written 179
  Second last write 00:00:00, attempted 187, written 187
  Last write before reset 01:53:18, attempted 586, written 586
  Second last write before reset 01:53:18, attempted 232, written 232
  Last write pulse rcvd  Aug 16 21:10:26.999 last full Aug 16 19:18:03.591 pulse count 7699679
  Last write pulse rcvd before reset 01:53:17
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 01:53:17, second last 01:53:17
  Last KA expiry before reset 05:10:17, second last 14:09:02
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 01:53:18, second last 01:53:18
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Aug 16 19:17:34.521        7  Aug 16 19:17:34.657        7
    Notification:   ---                        0  Jun 14 22:03:38.410        1
    Update:         Aug 16 21:10:26.866 12076636  Aug 16 19:18:32.054    30135
    Keepalive:      Aug 16 19:17:55.050   146029  Aug 16 21:10:26.106   809207
    Route_Refresh:  ---                        0  ---                        0
    Total:                              12222672                        839350
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.6 Filter-group: 0.2  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB
  156 accepted prefixes, 31 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 14388, suppressed 0, withdrawn 1581
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 28
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470206
  Update group: 0.6 Filter-group: 0.2  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB
  86 accepted prefixes, 26 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 26140, suppressed 0, withdrawn 4728
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470204, Last synced ack version 0
  Outstanding version objects: current 4, max 70
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 6; dropped 5
  Local host: 87.250.234.14, Local port: 65234, IF Handle: 0x00000000
  Foreign host: 5.45.247.180, Foreign port: 179
  Last reset 01:53:17, due to BFD (Bidirectional forwarding detection) session down
  Time since last notification received from neighbor: 8w6d
  Error Code: connection rejected
  Notification data received:
    None

BGP neighbor is 37.140.141.80
 Remote AS 13238, local AS 13238, internal link
 Description: cloud-sas2-9fvrr1
 Remote router ID 37.140.141.80
 Cluster ID 87.250.234.14
  BGP state = Established, up for 15:00:43
  NSR State: None
  BFD enabled (session up): mininterval: 3000 multiplier: 3
  Last read 00:00:06, Last read before reset 15:01:00
  Hold time is 90, keepalive interval is 30 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:22, attempted 19, written 19
  Second last write 00:00:52, attempted 19, written 19
  Last write before reset 15:01:03, attempted 19, written 19
  Second last write before reset 15:01:33, attempted 19, written 19
  Last write pulse rcvd  Aug 16 21:10:20.976 last full Aug 16 06:09:49.007 pulse count 905592
  Last write pulse rcvd before reset 15:01:00
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 15:01:00, second last 15:01:00
  Last KA expiry before reset 15:01:03, second last 15:01:33
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 15:01:03, second last 15:01:33
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         No
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Aug 16 06:09:43.482       20  Aug 16 06:09:43.490       20
    Notification:   ---                        0  Aug  8 15:38:29.728        2
    Update:         Aug 16 21:07:04.690   803744  Aug 16 06:09:45.079     4220
    Keepalive:      Aug 16 21:10:04.696   182922  Aug 16 21:10:20.976   283661
    Route_Refresh:  ---                        0  ---                        0
    Total:                                986686                        287903
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised and received
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  2 accepted prefixes, 2 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 25554, suppressed 0, withdrawn 6761
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 42
  Additional-paths operation: Send and Receive
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 0
  Update group: 0.3 Filter-group: 0.0  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 0, suppressed 0, withdrawn 0
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 0, Last synced ack version 0
  Outstanding version objects: current 0, max 0
  Additional-paths operation: None
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 20; dropped 19
  Local host: 87.250.234.14, Local port: 40038, IF Handle: 0x00000000
  Foreign host: 37.140.141.80, Foreign port: 179
  Last reset 15:01:00, due to BFD (Bidirectional forwarding detection) session down
  Time since last notification received from neighbor: 1w1d
  Error Code: peer unconfigured
  Notification data received:
    None

BGP neighbor is 37.140.141.81
 Remote AS 13238, local AS 13238, internal link
 Description: cloud-vla1-2fvrr1
 Remote router ID 37.140.141.81
 Cluster ID 87.250.234.14
  BGP state = Established, up for 2d18h
  NSR State: None
  BFD enabled (session up): mininterval: 3000 multiplier: 3
  Last read 00:00:04, Last read before reset 2d18h
  Hold time is 90, keepalive interval is 30 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:22, attempted 19, written 19
  Second last write 00:00:52, attempted 19, written 19
  Last write before reset 2d18h, attempted 41, written 41
  Second last write before reset 2d18h, attempted 19, written 19
  Last write pulse rcvd  Aug 16 21:10:22.826 last full Aug 14 02:13:54.914 pulse count 905596
  Last write pulse rcvd before reset 2d18h
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 2d18h, second last 2d18h
  Last KA expiry before reset 2d18h, second last 2d18h
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 2d18h, second last 2d18h
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         No
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Aug 14 02:13:49.445       21  Aug 14 02:13:49.449       21
    Notification:   ---                        0  ---                        0
    Update:         Aug 16 21:07:04.690   802079  Aug 15 23:09:49.370     4019
    Keepalive:      Aug 16 21:10:04.696   183279  Aug 16 21:10:22.826   284179
    Route_Refresh:  ---                        0  ---                        0
    Total:                                985379                        288219
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised and received
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 79234, suppressed 0, withdrawn 40670
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 42
  Additional-paths operation: Send and Receive
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 0
  Update group: 0.3 Filter-group: 0.0  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 0, suppressed 0, withdrawn 0
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 0, Last synced ack version 0
  Outstanding version objects: current 0, max 0
  Additional-paths operation: None
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 21; dropped 20
  Local host: 87.250.234.14, Local port: 34667, IF Handle: 0x00000000
  Foreign host: 37.140.141.81, Foreign port: 179
  Last reset 2d18h, due to BFD (Bidirectional forwarding detection) session down

BGP neighbor is 37.140.141.82
 Remote AS 13238, local AS 13238, internal link
 Description: cloud-myt-6fvrr1
 Remote router ID 37.140.141.82
 Cluster ID 87.250.234.14
  BGP state = Established, up for 1d20h
  NSR State: None
  BFD enabled (session up): mininterval: 3000 multiplier: 3
  Last read 00:00:06, Last read before reset 1d20h
  Hold time is 90, keepalive interval is 30 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:22, attempted 19, written 19
  Second last write 00:00:52, attempted 19, written 19
  Last write before reset 1d20h, attempted 41, written 41
  Second last write before reset 1d20h, attempted 19, written 19
  Last write pulse rcvd  Aug 16 21:10:20.107 last full Aug 15 00:55:38.984 pulse count 812805
  Last write pulse rcvd before reset 1d20h
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 1d20h, second last 1d20h
  Last KA expiry before reset 1d20h, second last 1d20h
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 1d20h, second last 1d20h
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         No
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Aug 15 00:55:33.535       26  Aug 15 00:55:33.535       25
    Notification:   Jul 31 15:16:59.971        1  ---                        0
    Update:         Aug 16 21:07:04.690   730754  Aug 15 23:09:57.447     3593
    Keepalive:      Aug 16 21:10:04.696   161891  Aug 16 21:10:20.107   253403
    Route_Refresh:  ---                        0  ---                        0
    Total:                                892672                        257021
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised and received
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 55757, suppressed 0, withdrawn 24909
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 52
  Additional-paths operation: Send and Receive
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 0
  Update group: 0.3 Filter-group: 0.0  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 0, suppressed 0, withdrawn 0
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 0, Last synced ack version 0
  Outstanding version objects: current 0, max 0
  Additional-paths operation: None
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 25; dropped 24
  Local host: 87.250.234.14, Local port: 179, IF Handle: 0x00000000
  Foreign host: 37.140.141.82, Foreign port: 50243
  Last reset 1d20h, due to BFD (Bidirectional forwarding detection) session down
  Time since last notification sent to neighbor: 2w2d
  Error Code: hold time expired
  Notification data sent:
    None

BGP neighbor is 37.140.141.95
 Remote AS 13238, local AS 13238, internal link
 Description: cloud-test-sas2-9fvrr1
 Remote router ID 0.0.0.0
 Cluster ID 87.250.234.14
  BGP state = Active
  NSR State: None
  BFD enabled (session down)
  Last read 00:00:00, Last read before reset 01:47:03
  Hold time is 180, keepalive interval is 60 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 01:46:52, attempted 292, written 292
  Second last write 01:46:53, attempted 100, written 100
  Last write before reset 01:46:52, attempted 292, written 292
  Second last write before reset 01:46:53, attempted 100, written 100
  Last write pulse rcvd  Aug 16 19:23:26.917 last full Aug 16 03:35:04.328 pulse count 827716
  Last write pulse rcvd before reset 01:47:00
  Socket not armed for io, not armed for read, not armed for write
  Last write thread event before reset 01:46:51, second last 01:46:51
  Last KA expiry before reset 02:20:37, second last 02:22:33
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 01:46:52, second last 01:46:53
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Aug 16 03:34:58.803       41  Aug 16 03:34:58.811       40
    Notification:   Jul  6 12:22:52.281        3  Jul  6 12:26:49.754        3
    Update:         Aug 16 19:23:34.315   737941  Aug 16 17:09:13.295      351
    Keepalive:      Aug 16 18:49:49.316   168046  Aug 16 19:23:23.943   262085
    Route_Refresh:  ---                        0  ---                        0
    Total:                                906031                        262479
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 0
  Update group: 0.4 Filter-group: 0.0  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 0, suppressed 0, withdrawn 0
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 0, Last synced ack version 0
  Outstanding version objects: current 0, max 44
  Additional-paths operation: Send and Receive
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 0
  Update group: 0.3 Filter-group: 0.0  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 0, suppressed 0, withdrawn 0
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 0, Last synced ack version 0
  Outstanding version objects: current 0, max 0
  Additional-paths operation: None
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 36; dropped 36
  Local host: 87.250.234.14, Local port: 51835, IF Handle: 0x00000000
  Foreign host: 37.140.141.95, Foreign port: 179
  Last reset 01:46:51, due to BFD (Bidirectional forwarding detection) session down
  Time since last notification sent to neighbor: 5w6d
  Error Code: hold time expired
  Notification data sent:
    None
  Time since last notification received from neighbor: 5w6d
  Error Code: connection rejected
  Notification data received:
    None

BGP neighbor is 87.250.226.93
 Remote AS 13238, local AS 13238, internal link
 Description: sas2-9d8-lo0
 Remote router ID 87.250.226.93
 Cluster ID 87.250.234.14
  BGP state = Established, up for 21w1d
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:21, Last read before reset 00:00:00
  Hold time is 180, keepalive interval is 60 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 179, written 179
  Second last write 00:00:00, attempted 187, written 187
  Last write before reset 00:00:00, attempted 0, written 0
  Second last write before reset 00:00:00, attempted 0, written 0
  Last write pulse rcvd  Aug 16 21:10:26.992 last full Aug 15 22:05:30.086 pulse count 3972180
  Last write pulse rcvd before reset 00:00:00
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 00:00:00, second last 00:00:00
  Last KA expiry before reset 00:00:00, second last 00:00:00
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 00:00:00, second last 00:00:00
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Mar 21 18:48:59.755        1  Mar 21 18:48:59.755        1
    Notification:   ---                        0  ---                        0
    Update:         Aug 16 21:10:26.878  6899862  Aug 16 20:27:07.722      833
    Keepalive:      Aug 16 06:10:07.693    21094  Aug 16 21:10:05.645   244227
    Route_Refresh:  ---                        0  Aug 15 22:05:27.204        3
    Total:                               6920957                        245064
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 1, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  19 accepted prefixes, 18 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 1584194, suppressed 0, withdrawn 801981
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 26
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470206
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 2, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  21 accepted prefixes, 20 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 4628440, suppressed 0, withdrawn 2149996
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470204, Last synced ack version 0
  Outstanding version objects: current 4, max 20
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 1; dropped 0
  Local host: 87.250.234.14, Local port: 179, IF Handle: 0x00000000
  Foreign host: 87.250.226.93, Foreign port: 49569
  Last reset 00:00:00

BGP neighbor is 87.250.226.96
 Remote AS 13238, local AS 13238, internal link
 Description: sas2-9d6-lo0
 Remote router ID 87.250.226.96
 Cluster ID 87.250.234.14
  BGP state = Established, up for 21w1d
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:32, Last read before reset 00:00:00
  Hold time is 180, keepalive interval is 60 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 179, written 179
  Second last write 00:00:00, attempted 187, written 187
  Last write before reset 00:00:00, attempted 0, written 0
  Second last write before reset 00:00:00, attempted 0, written 0
  Last write pulse rcvd  Aug 16 21:10:26.985 last full Aug  2 11:02:05.183 pulse count 3972421
  Last write pulse rcvd before reset 00:00:00
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 00:00:00, second last 00:00:00
  Last KA expiry before reset 00:00:00, second last 00:00:00
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 00:00:00, second last 00:00:00
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Mar 21 18:49:06.474        1  Mar 21 18:49:06.474        1
    Notification:   ---                        0  ---                        0
    Update:         Aug 16 21:10:26.878  6899138  Aug 16 20:27:07.719      776
    Keepalive:      Aug 16 06:10:07.693    21093  Aug 16 21:09:54.614   244088
    Route_Refresh:  ---                        0  Aug 15 22:15:50.079        2
    Total:                               6920232                        244867
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  19 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 1572765, suppressed 0, withdrawn 801981
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 23
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470206
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 2, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  21 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 4628433, suppressed 0, withdrawn 2149995
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470204, Last synced ack version 0
  Outstanding version objects: current 4, max 21
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 1; dropped 0
  Local host: 87.250.234.14, Local port: 179, IF Handle: 0x00000000
  Foreign host: 87.250.226.96, Foreign port: 54526
  Last reset 00:00:00

BGP neighbor is 87.250.226.113
 Remote AS 13238, local AS 13238, internal link
 Description: sas2-9d4-lo0
 Remote router ID 87.250.226.113
 Cluster ID 87.250.234.14
  BGP state = Established, up for 22w0d
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:24, Last read before reset 22w0d
  Hold time is 180, keepalive interval is 60 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 179, written 179
  Second last write 00:00:00, attempted 187, written 187
  Last write before reset 22w0d, attempted 19, written 19
  Second last write before reset 22w0d, attempted 25189, written 0
  Last write pulse rcvd  Aug 16 21:10:26.972 last full Aug 15 21:39:59.210 pulse count 7215568
  Last write pulse rcvd before reset 22w0d
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 22w0d, second last 22w0d
  Last KA expiry before reset 22w0d, second last 22w0d
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 22w0d, second last 22w0d
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Mar 15 15:19:31.847        2  Mar 15 15:19:31.847        2
    Notification:   Mar 15 14:24:09.403        1  ---                        0
    Update:         Aug 16 21:10:26.878 12085976  Aug 16 20:27:07.722     1237
    Keepalive:      Aug 16 06:10:07.693    36103  Aug 16 21:10:02.093   456760
    Route_Refresh:  ---                        0  Aug 15 21:39:56.328        5
    Total:                              12122082                        458004
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 2, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  19 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 1626438, suppressed 0, withdrawn 819232
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 23
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470206
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 3, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  21 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 4738110, suppressed 0, withdrawn 2199996
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470204, Last synced ack version 0
  Outstanding version objects: current 4, max 21
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 2; dropped 1
  Local host: 87.250.234.14, Local port: 179, IF Handle: 0x00000000
  Foreign host: 87.250.226.113, Foreign port: 62538
  Last reset 22w0d, due to BGP Notification sent: hold time expired
  Time since last notification sent to neighbor: 22w0d
  Error Code: hold time expired
  Notification data sent:
    None

BGP neighbor is 87.250.226.114
 Remote AS 13238, local AS 13238, internal link
 Description: sas2-9d2-lo0
 Remote router ID 87.250.226.114
 Cluster ID 87.250.234.14
  BGP state = Established, up for 22w0d
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:17, Last read before reset 22w0d
  Hold time is 180, keepalive interval is 60 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 179, written 179
  Second last write 00:00:00, attempted 187, written 187
  Last write before reset 22w0d, attempted 25189, written 0
  Second last write before reset 22w0d, attempted 24619, written 0
  Last write pulse rcvd  Aug 16 21:10:27.186 last full Aug 15 21:26:29.577 pulse count 7213067
  Last write pulse rcvd before reset 22w0d
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 22w0d, second last 22w0d
  Last KA expiry before reset 22w0d, second last 22w0d
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 22w0d, second last 22w0d
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Mar 15 15:19:31.582        4  Mar 15 15:19:31.582        4
    Notification:   Mar 15 14:24:17.271        3  ---                        0
    Update:         Aug 16 21:10:26.878 12090307  Aug 16 20:27:07.723     1264
    Keepalive:      Aug 16 06:10:07.693    36101  Aug 16 21:10:09.551   456895
    Route_Refresh:  ---                        0  Aug 15 21:26:26.695        9
    Total:                              12126415                        458172
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 3, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  19 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 1626434, suppressed 0, withdrawn 819232
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 32
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470206
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 6, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  21 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 4750702, suppressed 0, withdrawn 2199996
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470204, Last synced ack version 0
  Outstanding version objects: current 4, max 47
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 4; dropped 3
  Local host: 87.250.234.14, Local port: 179, IF Handle: 0x00000000
  Foreign host: 87.250.226.114, Foreign port: 53558
  Last reset 22w0d, due to BGP Notification sent: hold time expired
  Time since last notification sent to neighbor: 22w0d
  Error Code: hold time expired
  Notification data sent:
    None

BGP neighbor is 87.250.226.124
 Remote AS 13238, local AS 13238, internal link
 Description: sas2-5d2-lo0
 Remote router ID 87.250.226.124
 Cluster ID 87.250.234.14
  BGP state = Established, up for 22w0d
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:14, Last read before reset 22w0d
  Hold time is 180, keepalive interval is 60 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 179, written 179
  Second last write 00:00:00, attempted 187, written 187
  Last write before reset 22w0d, attempted 25189, written 0
  Second last write before reset 22w0d, attempted 24619, written 0
  Last write pulse rcvd  Aug 16 21:10:27.118 last full Aug  2 11:02:05.183 pulse count 7211374
  Last write pulse rcvd before reset 22w0d
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 22w0d, second last 22w0d
  Last KA expiry before reset 22w0d, second last 22w0d
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 22w0d, second last 22w0d
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Mar 15 15:19:34.331        6  Mar 15 15:19:34.331        6
    Notification:   Mar 15 14:24:13.225        3  Jan 19 20:33:04.259        2
    Update:         Aug 16 21:10:26.878 12086019  Aug 16 10:17:15.559      192
    Keepalive:      Aug 16 06:10:07.693    36104  Aug 16 21:10:13.190   456161
    Route_Refresh:  ---                        0  Jun 29 18:28:52.822        7
    Total:                              12122132                        456368
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 3, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  10 accepted prefixes, 10 are bestpaths
  Cumulative no. of prefixes denied: 2.
    No policy: 0, Failed RT match: 0
    By ORF policy: 0, By policy: 2
  Prefix advertised 1615021, suppressed 0, withdrawn 819232
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 67
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470206
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 4, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  10 accepted prefixes, 10 are bestpaths
  Cumulative no. of prefixes denied: 2.
    No policy: 0, Failed RT match: 0
    By ORF policy: 0, By policy: 2
  Prefix advertised 4734641, suppressed 0, withdrawn 2199996
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470204, Last synced ack version 0
  Outstanding version objects: current 4, max 135
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 6; dropped 5
  Local host: 87.250.234.14, Local port: 179, IF Handle: 0x00000000
  Foreign host: 87.250.226.124, Foreign port: 52056
  Last reset 22w0d, due to Peer closing down the session
  Peer reset reason: Remote closed the session (Function not implemented)
  Time since last notification sent to neighbor: 22w0d
  Error Code: hold time expired
  Notification data sent:
    None
  Time since last notification received from neighbor: 29w6d
  Error Code: hold time expired
  Notification data received:
    None

BGP neighbor is 87.250.226.125
 Remote AS 13238, local AS 13238, internal link
 Description: sas2-5d4-lo0
 Remote router ID 87.250.226.125
 Cluster ID 87.250.234.14
  BGP state = Established, up for 22w0d
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:35, Last read before reset 22w0d
  Hold time is 180, keepalive interval is 60 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 179, written 179
  Second last write 00:00:00, attempted 187, written 187
  Last write before reset 22w0d, attempted 25189, written 0
  Second last write before reset 22w0d, attempted 24619, written 0
  Last write pulse rcvd  Aug 16 21:10:27.108 last full Aug  2 11:02:05.312 pulse count 7210530
  Last write pulse rcvd before reset 22w0d
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 22w0d, second last 22w0d
  Last KA expiry before reset 22w0d, second last 22w0d
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 22w0d, second last 22w0d
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Mar 15 15:19:31.772        2  Mar 15 15:19:31.772        2
    Notification:   Mar 15 14:24:39.963        1  ---                        0
    Update:         Aug 16 21:10:26.878 12084769  Aug 16 10:17:15.559      182
    Keepalive:      Aug 16 06:10:07.693    36103  Aug 16 21:09:51.947   456073
    Route_Refresh:  ---                        0  Jun 29 18:21:01.552        3
    Total:                              12120875                        456260
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 1, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  10 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 2.
    No policy: 0, Failed RT match: 0
    By ORF policy: 0, By policy: 2
  Prefix advertised 1615019, suppressed 0, withdrawn 819232
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 20
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470206
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 2, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  10 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 2.
    No policy: 0, Failed RT match: 0
    By ORF policy: 0, By policy: 2
  Prefix advertised 4722045, suppressed 0, withdrawn 2199996
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470204, Last synced ack version 0
  Outstanding version objects: current 4, max 21
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 2; dropped 1
  Local host: 87.250.234.14, Local port: 179, IF Handle: 0x00000000
  Foreign host: 87.250.226.125, Foreign port: 60877
  Last reset 22w0d, due to Peer closing down the session
  Peer reset reason: Remote closed the session (Function not implemented)
  Time since last notification sent to neighbor: 22w0d
  Error Code: hold time expired
  Notification data sent:
    None

BGP neighbor is 87.250.226.189
 Remote AS 13238, local AS 13238, internal link
 Description: sas1-2d2-lo0
 Remote router ID 87.250.226.189
 Cluster ID 87.250.234.14
  BGP state = Established, up for 4w2d
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:00, Last read before reset 4w2d
  Hold time is 180, keepalive interval is 60 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 179, written 179
  Second last write 00:00:00, attempted 187, written 187
  Last write before reset 4w2d, attempted 108, written 108
  Second last write before reset 4w2d, attempted 207, written 207
  Last write pulse rcvd  Aug 16 21:10:27.063 last full Aug  2 11:02:05.184 pulse count 7928411
  Last write pulse rcvd before reset 4w2d
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 4w2d, second last 4w2d
  Last KA expiry before reset 4w2d, second last 4w2d
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 4w2d, second last 4w2d
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Jul 16 23:13:19.400        3  Jul 16 23:13:19.478        3
    Notification:   Jul 16 22:57:59.487        2  ---                        0
    Update:         Aug 16 21:10:26.878 12086292  Aug 16 21:10:26.845   707046
    Keepalive:      Aug 16 06:10:07.694    36099  Aug 16 21:10:14.341   447251
    Route_Refresh:  ---                        0  Jun 29 17:32:27.567        4
    Total:                              12122396                       1154304
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 2, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  1406 accepted prefixes, 1341 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 362464, suppressed 0, withdrawn 199614
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 20
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470206
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 2, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  2356 accepted prefixes, 2353 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 1249620, suppressed 0, withdrawn 618517
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470204, Last synced ack version 0
  Outstanding version objects: current 4, max 21
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 3; dropped 2
  Local host: 87.250.234.14, Local port: 30438, IF Handle: 0x00000000
  Foreign host: 87.250.226.189, Foreign port: 179
  Last reset 4w2d, due to BGP Notification sent: hold time expired
  Time since last notification sent to neighbor: 4w2d
  Error Code: hold time expired
  Notification data sent:
    None

BGP neighbor is 87.250.226.192
 Remote AS 13238, local AS 13238, internal link
 Description: sas1-c1
 Remote router ID 87.250.226.192
 Cluster ID 87.250.234.14
  BGP state = Established, up for 22w0d
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:09, Last read before reset 22w0d
  Hold time is 90, keepalive interval is 30 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 179, written 179
  Second last write 00:00:00, attempted 187, written 187
  Last write before reset 22w0d, attempted 25189, written 0
  Second last write before reset 22w0d, attempted 24619, written 0
  Last write pulse rcvd  Aug 16 21:10:27.078 last full Aug  2 11:02:06.835 pulse count 9614957
  Last write pulse rcvd before reset 22w0d
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 22w0d, second last 22w0d
  Last KA expiry before reset 22w0d, second last 22w0d
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 22w0d, second last 22w0d
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Mar 15 15:20:29.040        2  Mar 15 15:20:29.039        2
    Notification:   Mar 15 14:23:12.266        1  ---                        0
    Update:         Aug 16 21:10:26.878 12082611  Aug 16 21:00:32.542  2029465
    Keepalive:      Aug 16 16:00:09.146   146140  Aug 16 21:10:18.346   839906
    Route_Refresh:  ---                        0  ---                        0
    Total:                              12228754                       2869373
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised and received
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  423 accepted prefixes, 365 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 1605065, suppressed 0, withdrawn 819202
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 17
  Additional-paths operation: Send and Receive
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470206
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised and received
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  750 accepted prefixes, 648 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 4697399, suppressed 0, withdrawn 2199991
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470204, Last synced ack version 0
  Outstanding version objects: current 4, max 24
  Additional-paths operation: Send and Receive
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 2; dropped 1
  Local host: 87.250.234.14, Local port: 179, IF Handle: 0x00000000
  Foreign host: 87.250.226.192, Foreign port: 64515
  Last reset 22w0d, due to BGP Notification sent: hold time expired
  Time since last notification sent to neighbor: 22w0d
  Error Code: hold time expired
  Notification data sent:
    None

BGP neighbor is 87.250.226.200
 Remote AS 13238, local AS 13238, internal link
 Description: sas1-2d1-lo0
 Remote router ID 87.250.226.200
 Cluster ID 87.250.234.14
  BGP state = Established, up for 4w2d
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:00, Last read before reset 4w2d
  Hold time is 180, keepalive interval is 60 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 179, written 179
  Second last write 00:00:00, attempted 187, written 187
  Last write before reset 4w2d, attempted 187, written 187
  Second last write before reset 4w2d, attempted 100, written 100
  Last write pulse rcvd  Aug 16 21:10:27.163 last full Aug  2 11:02:05.184 pulse count 7898108
  Last write pulse rcvd before reset 4w2d
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 4w2d, second last 4w2d
  Last KA expiry before reset 4w2d, second last 4w2d
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 4w2d, second last 4w2d
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Jul 17 00:23:24.363        5  Jul 17 00:23:24.362        5
    Notification:   Jul 17 00:05:16.944        4  ---                        0
    Update:         Aug 16 21:10:26.878 12088645  Aug 16 21:10:26.857   678560
    Keepalive:      Aug 16 06:10:07.694    36102  Aug 16 21:09:50.684   446350
    Route_Refresh:  ---                        0  Jun 29 17:31:16.897        8
    Total:                              12124756                       1124923
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 4, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  1406 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 356620, suppressed 0, withdrawn 196443
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 33
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470206
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 4, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  2355 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 1240983, suppressed 0, withdrawn 614002
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470204, Last synced ack version 0
  Outstanding version objects: current 4, max 57
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 5; dropped 4
  Local host: 87.250.234.14, Local port: 179, IF Handle: 0x00000000
  Foreign host: 87.250.226.200, Foreign port: 53677
  Last reset 4w2d, due to BGP Notification sent: hold time expired
  Time since last notification sent to neighbor: 4w2d
  Error Code: hold time expired
  Notification data sent:
    None

BGP neighbor is 87.250.228.81
 Remote AS 13238, local AS 13238, internal link
 Description: fol5-c2
 Remote router ID 0.0.0.0
 Cluster ID 87.250.234.14
  BGP state = Active
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:00, Last read before reset 00:00:00
  Hold time is 180, keepalive interval is 60 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 0, written 0
  Second last write 00:00:00, attempted 0, written 0
  Last write before reset 00:00:00, attempted 0, written 0
  Second last write before reset 00:00:00, attempted 0, written 0
  Last write pulse rcvd  not set last full not set pulse count 0
  Last write pulse rcvd before reset 00:00:00
  Socket not armed for io, not armed for read, not armed for write
  Last write thread event before reset 00:00:00, second last 00:00:00
  Last KA expiry before reset 00:00:00, second last 00:00:00
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 00:00:00, second last 00:00:00
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability not received
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           ---                        0  ---                        0
    Notification:   ---                        0  ---                        0
    Update:         ---                        0  ---                        0
    Keepalive:      ---                        0  ---                        0
    Route_Refresh:  ---                        0  ---                        0
    Total:                                     0                             0
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 0
  Update group: 0.2 Filter-group: 0.0  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 0, suppressed 0, withdrawn 0
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 1, Last synced ack version 0
  Outstanding version objects: current 0, max 0
  Additional-paths operation: None
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 0
  Update group: 0.2 Filter-group: 0.0  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 0, suppressed 0, withdrawn 0
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 1, Last synced ack version 0
  Outstanding version objects: current 0, max 0
  Additional-paths operation: None
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 0; dropped 0
  Local host: 87.250.234.14, Local port: 0, IF Handle: 0x00000000
  Foreign host: 87.250.228.81, Foreign port: 0
  Last reset 00:00:00

BGP neighbor is 87.250.228.176
 Remote AS 13238, local AS 13238, internal link
 Description: iva-b-c2
 Remote router ID 87.250.228.176
 Cluster ID 87.250.234.14
  BGP state = Established, up for 2w0d
  NSR State: None
  BFD enabled (session up): mininterval: 3000 multiplier: 3
  Last read 00:00:01, Last read before reset 2w0d
  Hold time is 90, keepalive interval is 30 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 179, written 179
  Second last write 00:00:00, attempted 187, written 187
  Last write before reset 2w0d, attempted 276, written 276
  Second last write before reset 2w0d, attempted 266, written 266
  Last write pulse rcvd  Aug 16 21:10:27.073 last full Aug  2 11:03:52.850 pulse count 9403382
  Last write pulse rcvd before reset 2w0d
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 2w0d, second last 2w0d
  Last KA expiry before reset 2w0d, second last 2w0d
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 2w0d, second last 2w0d
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Aug  2 11:03:31.214        6  Aug  2 11:03:31.284        5
    Notification:   ---                        0  Aug  2 11:03:06.380        2
    Update:         Aug 16 21:10:26.878 12083381  Aug 16 21:10:26.296  1925684
    Keepalive:      Aug 16 16:00:09.146   146141  Aug 16 21:10:19.386   830611
    Route_Refresh:  ---                        0  ---                        0
    Total:                              12229528                       2756302
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised and received
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  3261 accepted prefixes, 953 are bestpaths
  Cumulative no. of prefixes denied: 5.
    No policy: 0, Failed RT match: 0
    By ORF policy: 0, By policy: 5
  Prefix advertised 197997, suppressed 0, withdrawn 115725
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 19
  Additional-paths operation: Send and Receive
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470206
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised and received
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  4591 accepted prefixes, 954 are bestpaths
  Cumulative no. of prefixes denied: 3.
    No policy: 0, Failed RT match: 0
    By ORF policy: 0, By policy: 3
  Prefix advertised 718210, suppressed 0, withdrawn 367774
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470204, Last synced ack version 0
  Outstanding version objects: current 4, max 20
  Additional-paths operation: Send and Receive
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 3; dropped 2
  Local host: 87.250.234.14, Local port: 13892, IF Handle: 0x00000000
  Foreign host: 87.250.228.176, Foreign port: 179
  Last reset 2w0d, due to BGP Notification received: connection rejected
  Time since last notification received from neighbor: 2w0d
  Error Code: connection rejected
  Notification data received:
    None

BGP neighbor is 87.250.228.209
 Remote AS 13238, local AS 13238, internal link
 Description: fol2-c4
 Remote router ID 0.0.0.0
 Cluster ID 87.250.234.14
  BGP state = Active
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:00, Last read before reset 00:00:00
  Hold time is 180, keepalive interval is 60 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 0, written 0
  Second last write 00:00:00, attempted 0, written 0
  Last write before reset 00:00:00, attempted 0, written 0
  Second last write before reset 00:00:00, attempted 0, written 0
  Last write pulse rcvd  not set last full not set pulse count 0
  Last write pulse rcvd before reset 00:00:00
  Socket not armed for io, not armed for read, not armed for write
  Last write thread event before reset 00:00:00, second last 00:00:00
  Last KA expiry before reset 00:00:00, second last 00:00:00
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 00:00:00, second last 00:00:00
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability not received
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           ---                        0  ---                        0
    Notification:   ---                        0  ---                        0
    Update:         ---                        0  ---                        0
    Keepalive:      ---                        0  ---                        0
    Route_Refresh:  ---                        0  ---                        0
    Total:                                     0                             0
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 0
  Update group: 0.2 Filter-group: 0.0  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 0, suppressed 0, withdrawn 0
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 1, Last synced ack version 0
  Outstanding version objects: current 0, max 0
  Additional-paths operation: None
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 0
  Update group: 0.2 Filter-group: 0.0  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 0, suppressed 0, withdrawn 0
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 1, Last synced ack version 0
  Outstanding version objects: current 0, max 0
  Additional-paths operation: None
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 0; dropped 0
  Local host: 87.250.234.14, Local port: 0, IF Handle: 0x00000000
  Foreign host: 87.250.228.209, Foreign port: 0
  Last reset 00:00:00

BGP neighbor is 87.250.233.129
 Remote AS 13238, local AS 13238, internal link
 Description: neun
 Remote router ID 0.0.0.0
 Cluster ID 87.250.234.14
  BGP state = Active
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:00, Last read before reset 00:00:00
  Hold time is 180, keepalive interval is 60 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 0, written 0
  Second last write 00:00:00, attempted 0, written 0
  Last write before reset 00:00:00, attempted 0, written 0
  Second last write before reset 00:00:00, attempted 0, written 0
  Last write pulse rcvd  not set last full not set pulse count 0
  Last write pulse rcvd before reset 00:00:00
  Socket not armed for io, not armed for read, not armed for write
  Last write thread event before reset 00:00:00, second last 00:00:00
  Last KA expiry before reset 00:00:00, second last 00:00:00
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 00:00:00, second last 00:00:00
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability not received
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           ---                        0  ---                        0
    Notification:   ---                        0  ---                        0
    Update:         ---                        0  ---                        0
    Keepalive:      ---                        0  ---                        0
    Route_Refresh:  ---                        0  ---                        0
    Total:                                     0                             0
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 0
  Update group: 0.2 Filter-group: 0.0  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 0, suppressed 0, withdrawn 0
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 1, Last synced ack version 0
  Outstanding version objects: current 0, max 0
  Additional-paths operation: None
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 0
  Update group: 0.2 Filter-group: 0.0  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 0, suppressed 0, withdrawn 0
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 1, Last synced ack version 0
  Outstanding version objects: current 0, max 0
  Additional-paths operation: None
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 0; dropped 0
  Local host: 87.250.234.14, Local port: 0, IF Handle: 0x00000000
  Foreign host: 87.250.233.129, Foreign port: 0
  Last reset 00:00:00

BGP neighbor is 87.250.233.137
 Remote AS 13238, local AS 13238, internal link
 Description: oksana
 Remote router ID 0.0.0.0
 Cluster ID 87.250.234.14
  BGP state = Active
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:00, Last read before reset 00:00:00
  Hold time is 180, keepalive interval is 60 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 0, written 0
  Second last write 00:00:00, attempted 0, written 0
  Last write before reset 00:00:00, attempted 0, written 0
  Second last write before reset 00:00:00, attempted 0, written 0
  Last write pulse rcvd  not set last full not set pulse count 0
  Last write pulse rcvd before reset 00:00:00
  Socket not armed for io, not armed for read, not armed for write
  Last write thread event before reset 00:00:00, second last 00:00:00
  Last KA expiry before reset 00:00:00, second last 00:00:00
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 00:00:00, second last 00:00:00
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability not received
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           ---                        0  ---                        0
    Notification:   ---                        0  ---                        0
    Update:         ---                        0  ---                        0
    Keepalive:      ---                        0  ---                        0
    Route_Refresh:  ---                        0  ---                        0
    Total:                                     0                             0
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 0
  Update group: 0.2 Filter-group: 0.0  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 0, suppressed 0, withdrawn 0
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 1, Last synced ack version 0
  Outstanding version objects: current 0, max 0
  Additional-paths operation: None
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 0
  Update group: 0.2 Filter-group: 0.0  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 0, suppressed 0, withdrawn 0
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 1, Last synced ack version 0
  Outstanding version objects: current 0, max 0
  Additional-paths operation: None
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 0; dropped 0
  Local host: 87.250.234.14, Local port: 0, IF Handle: 0x00000000
  Foreign host: 87.250.233.137, Foreign port: 0
  Last reset 00:00:00

BGP neighbor is 87.250.233.142
 Remote AS 13238, local AS 13238, internal link
 Description: aurora
 Remote router ID 87.250.233.142
 Cluster ID 87.250.234.14
  BGP state = Established, up for 1d20h
  NSR State: None
  BFD enabled (session up): mininterval: 3000 multiplier: 3
  Last read 00:00:08, Last read before reset 1d20h
  Hold time is 90, keepalive interval is 30 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 179, written 179
  Second last write 00:00:00, attempted 187, written 187
  Last write before reset 1d20h, attempted 266, written 266
  Second last write before reset 1d20h, attempted 133, written 133
  Last write pulse rcvd  Aug 16 21:10:27.081 last full Aug 15 00:24:01.992 pulse count 7774997
  Last write pulse rcvd before reset 1d20h
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 1d20h, second last 1d20h
  Last KA expiry before reset 2d02h, second last 2d04h
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 1d20h, second last 1d20h
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Aug 15 00:23:38.196        7  Aug 15 00:23:38.220        6
    Notification:   ---                        0  Aug 15 00:16:01.253        2
    Update:         Aug 16 21:10:26.878 12084810  Aug 16 21:06:52.586     1089
    Keepalive:      Aug 16 16:00:09.146   146146  Aug 16 21:10:19.074   824251
    Route_Refresh:  ---                        0  ---                        0
    Total:                              12230963                        825348
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  70 accepted prefixes, 54 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 56036, suppressed 0, withdrawn 25106
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 18
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470206
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  45 accepted prefixes, 40 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 154444, suppressed 0, withdrawn 68321
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470204, Last synced ack version 0
  Outstanding version objects: current 4, max 35
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 5; dropped 4
  Local host: 87.250.234.14, Local port: 48994, IF Handle: 0x00000000
  Foreign host: 87.250.233.142, Foreign port: 179
  Last reset 1d20h, due to BFD (Bidirectional forwarding detection) session down
  Time since last notification sent to neighbor: 38w5d
  Error Code: hold time expired
  Notification data sent:
    None
  Time since last notification received from neighbor: 1d20h
  Error Code: peer unconfigured
  Notification data received:
    None

BGP neighbor is 87.250.233.199
 Remote AS 13238, local AS 13238, internal link
 Description: dante
 Remote router ID 87.250.233.199
 Cluster ID 87.250.234.14
  BGP state = Established, up for 5w0d
  NSR State: None
  BFD enabled (session up): mininterval: 3000 multiplier: 3
  Last read 00:00:24, Last read before reset 5w0d
  Hold time is 90, keepalive interval is 30 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 179, written 179
  Second last write 00:00:00, attempted 187, written 187
  Last write before reset 5w0d, attempted 258, written 258
  Second last write before reset 5w0d, attempted 387, written 387
  Last write pulse rcvd  Aug 16 21:10:27.074 last full Aug  2 11:02:05.380 pulse count 7847962
  Last write pulse rcvd before reset 5w0d
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 5w0d, second last 5w0d
  Last KA expiry before reset 5w0d, second last 5w0d
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 5w0d, second last 5w0d
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Jul 12 01:18:12.206        7  Jul 12 01:18:12.206        5
    Notification:   Jul  6 09:28:53.215        2  Jul 12 01:08:04.290        1
    Update:         Aug 16 21:10:26.878 12085506  Aug 16 16:13:53.395    85473
    Keepalive:      Aug 16 16:00:09.146   146141  Aug 16 21:10:02.926   815386
    Route_Refresh:  ---                        0  ---                        0
    Total:                              12231656                        900865
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  491 accepted prefixes, 154 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 440157, suppressed 0, withdrawn 229511
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 25
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470206
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  362 accepted prefixes, 117 are bestpaths
  Cumulative no. of prefixes denied: 2.
    No policy: 0, Failed RT match: 0
    By ORF policy: 0, By policy: 2
  Prefix advertised 1380878, suppressed 0, withdrawn 684936
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470204, Last synced ack version 0
  Outstanding version objects: current 4, max 47
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 5; dropped 4
  Local host: 87.250.234.14, Local port: 179, IF Handle: 0x00000000
  Foreign host: 87.250.233.199, Foreign port: 54559
  Last reset 5w0d, due to BFD (Bidirectional forwarding detection) session down
  Time since last notification sent to neighbor: 5w6d
  Error Code: hold time expired
  Notification data sent:
    None
  Time since last notification received from neighbor: 5w0d
  Error Code: peer unconfigured
  Notification data received:
    None

BGP neighbor is 87.250.233.255
 Remote AS 13238, local AS 13238, internal link
 Description: kuchum
 Remote router ID 0.0.0.0
 Cluster ID 87.250.234.14
  BGP state = Idle
  NSR State: None
  BFD enabled (session down, BFD not configured on remote neighbor)
  Last read 00:00:00, Last read before reset 19w6d
  Hold time is 180, keepalive interval is 60 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 19w6d, attempted 187, written 187
  Second last write 19w6d, attempted 266, written 266
  Last write before reset 19w6d, attempted 187, written 187
  Second last write before reset 19w6d, attempted 266, written 266
  Last write pulse rcvd  Mar 30 14:39:30.584 last full Mar 29 22:47:55.511 pulse count 3704569
  Last write pulse rcvd before reset 19w6d
  Socket not armed for io, not armed for read, not armed for write
  Last write thread event before reset 19w6d, second last 19w6d
  Last KA expiry before reset 19w6d, second last 19w6d
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 19w6d, second last 19w6d
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Mar 15 15:19:30.753       24  Mar 15 15:19:30.737       19
    Notification:   ---                        0  Mar 30 14:39:30.850        8
    Update:         Mar 30 14:39:30.316  5529993  Mar 30 14:22:42.944      328
    Keepalive:      Mar 30 14:29:41.030    71318  Mar 30 14:39:01.522   408473
    Route_Refresh:  ---                        0  ---                        0
    Total:                               5601335                        408828
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 0
  Update group: 0.4 Filter-group: 0.0  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 0, suppressed 0, withdrawn 0
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 0, Last synced ack version 0
  Outstanding version objects: current 0, max 35
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 0
  Update group: 0.4 Filter-group: 0.0  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 0, suppressed 0, withdrawn 0
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 0, Last synced ack version 0
  Outstanding version objects: current 0, max 59
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 12; dropped 12
  Local host: 87.250.234.14, Local port: 179, IF Handle: 0x00000000
  Foreign host: 87.250.233.255, Foreign port: 59923
  Last reset 19w6d, due to BGP Notification received: peer unconfigured
  Time since last notification received from neighbor: 19w6d
  Error Code: peer unconfigured
  Notification data received:
    None

BGP neighbor is 87.250.234.8
 Remote AS 13238, local AS 13238, internal link
 Remote router ID 87.250.234.8
  BGP state = Established, up for 4w6d
  NSR State: None
  Last read 00:00:28, Last read before reset 4w6d
  Hold time is 90, keepalive interval is 30 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:16, attempted 19, written 19
  Second last write 00:00:46, attempted 19, written 19
  Last write before reset 4w6d, attempted 19, written 19
  Second last write before reset 4w6d, attempted 19, written 19
  Last write pulse rcvd  Aug 16 21:10:10.996 last full not set pulse count 560731
  Last write pulse rcvd before reset 4w6d
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 4w6d, second last 4w6d
  Last KA expiry before reset 4w6d, second last 4w6d
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 4w6d, second last 4w6d
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Jul 13 01:10:57.912        2  Jul 13 01:10:57.919        2
    Notification:   Jul 13 01:04:40.388        1  ---                        0
    Update:         Jul 13 01:11:03.013        6  Aug 16 20:01:40.457    11845
    Keepalive:      Aug 16 21:10:10.896   268695  Aug 16 21:09:59.305   282376
    Route_Refresh:  ---                        0  ---                        0
    Total:                                268704                        294223
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Labeled-unicast
  BGP neighbor version 3530286
  Update group: 0.8 Filter-group: 0.6  No Refresh request being processed
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised and received
    Additional-paths Receive: advertised
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is LU_IMPORT
  Policy for outgoing advertisements is LU_EXPORT
  8 accepted prefixes, 4 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 1, suppressed 0, withdrawn 0
  Maximum prefixes allowed 1000
  Threshold for warning message 80%, restart interval 0 min
  My AS number is allowed 10 times in received updates
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 2
  Additional-paths operation: Receive
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

  Connections established 2; dropped 1
  Local host: 87.250.234.14, Local port: 11660, IF Handle: 0x00000000
  Foreign host: 87.250.234.8, Foreign port: 179
  Last reset 4w6d, due to BGP Notification sent: hold time expired
  Time since last notification sent to neighbor: 4w6d
  Error Code: hold time expired
  Notification data sent:
    None

BGP neighbor is 87.250.234.10
 Remote AS 13238, local AS 13238, internal link
 Description: demidov
 Remote router ID 87.250.234.10
 Cluster ID 87.250.234.14
  BGP state = Established, up for 1w3d
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:22, Last read before reset 1w3d
  Hold time is 90, keepalive interval is 30 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 179, written 179
  Second last write 00:00:00, attempted 187, written 187
  Last write before reset 1w3d, attempted 54, written 54
  Second last write before reset 1w3d, attempted 203, written 203
  Last write pulse rcvd  Aug 16 21:10:27.110 last full Aug  6 15:45:04.315 pulse count 2437246
  Last write pulse rcvd before reset 1w3d
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 1w3d, second last 1w3d
  Last KA expiry before reset 1w3d, second last 1w3d
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 1w3d, second last 1w3d
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Aug  6 15:44:58.306        4  Aug  6 15:44:58.450        4
    Notification:   ---                        0  Aug  6 15:38:19.549        3
    Update:         Aug 16 21:10:26.878  4106501  Aug  6 22:00:30.181       37
    Keepalive:      Aug 16 16:00:09.146    33041  Aug 16 21:10:05.030   245462
    Route_Refresh:  ---                        0  ---                        0
    Total:                               4139546                        245506
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  12 accepted prefixes, 12 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 163515, suppressed 0, withdrawn 97272
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 19
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470206
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  11 accepted prefixes, 11 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 574081, suppressed 0, withdrawn 294391
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470204, Last synced ack version 0
  Outstanding version objects: current 4, max 27
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 4; dropped 3
  Local host: 87.250.234.14, Local port: 31753, IF Handle: 0x00000000
  Foreign host: 87.250.234.10, Foreign port: 179
  Last reset 1w3d, due to BGP Notification received: peer unconfigured
  Time since last notification received from neighbor: 1w3d
  Error Code: peer unconfigured
  Notification data received:
    None

BGP neighbor is 87.250.234.11
 Remote AS 13238, local AS 13238, internal link
 Remote router ID 87.250.234.11
  BGP state = Established, up for 5w0d
  NSR State: None
  Last read 00:00:47, Last read before reset 5w0d
  Hold time is 180, keepalive interval is 60 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:29, attempted 19, written 19
  Second last write 00:01:29, attempted 19, written 19
  Last write before reset 5w0d, attempted 19, written 19
  Second last write before reset 5w0d, attempted 19, written 19
  Last write pulse rcvd  Aug 16 21:09:58.453 last full not set pulse count 272949
  Last write pulse rcvd before reset 5w0d
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 5w0d, second last 5w0d
  Last KA expiry before reset 5w0d, second last 5w0d
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 5w0d, second last 5w0d
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Jul 12 01:19:00.771        3  Jul 12 01:19:00.770        3
    Notification:   Jul 12 01:11:15.525        1  Jul  5 20:07:08.382        1
    Update:         Jul 12 01:19:05.919        8  Aug 16 20:01:40.454    13625
    Keepalive:      Aug 16 21:09:58.250   134342  Aug 16 21:09:40.472   131162
    Route_Refresh:  ---                        0  ---                        0
    Total:                                134354                        144791
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Labeled-unicast
  BGP neighbor version 3530286
  Update group: 0.9 Filter-group: 0.4  No Refresh request being processed
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised and received
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is LU_IMPORT
  Policy for outgoing advertisements is LU_EXPORT
  8 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 1, suppressed 0, withdrawn 0
  Maximum prefixes allowed 1000
  Threshold for warning message 80%, restart interval 0 min
  My AS number is allowed 10 times in received updates
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 2
  Additional-paths operation: Send and Receive
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

  Connections established 3; dropped 2
  Local host: 87.250.234.14, Local port: 179, IF Handle: 0x00000000
  Foreign host: 87.250.234.11, Foreign port: 16392
  Last reset 5w0d, due to BGP Notification sent: hold time expired
  Time since last notification sent to neighbor: 5w0d
  Error Code: hold time expired
  Notification data sent:
    None
  Time since last notification received from neighbor: 6w0d
  Error Code: hold time expired
  Notification data received:
    None

BGP neighbor is 87.250.234.13
 Remote AS 13238, local AS 13238, internal link
 Description: red-c3
 Remote router ID 87.250.234.13
 Cluster ID 87.250.234.14
  BGP state = Established, up for 22w0d
  NSR State: None
  BFD enabled (session up): mininterval: 3000 multiplier: 3
  Last read 00:00:09, Last read before reset 22w0d
  Hold time is 90, keepalive interval is 30 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 179, written 179
  Second last write 00:00:00, attempted 187, written 187
  Last write before reset 22w0d, attempted 19, written 19
  Second last write before reset 22w0d, attempted 25189, written 0
  Last write pulse rcvd  Aug 16 21:10:27.072 last full Aug  2 11:03:51.345 pulse count 7808629
  Last write pulse rcvd before reset 22w0d
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 22w0d, second last 22w0d
  Last KA expiry before reset 22w0d, second last 22w0d
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 22w0d, second last 22w0d
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Mar 15 15:20:55.648        3  Mar 15 15:20:55.648        3
    Notification:   Mar 15 14:22:54.760        2  ---                        0
    Update:         Aug 16 21:10:26.878 12080422  Aug 16 17:15:55.964      957
    Keepalive:      Aug 16 16:00:09.146   146141  Aug 16 21:10:18.248   840996
    Route_Refresh:  ---                        0  ---                        0
    Total:                              12226568                        841956
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised and received
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  196 accepted prefixes, 132 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 1605031, suppressed 0, withdrawn 819170
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 17
  Additional-paths operation: Send and Receive
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470206
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised and received
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  119 accepted prefixes, 71 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 4697393, suppressed 0, withdrawn 2199986
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470204, Last synced ack version 0
  Outstanding version objects: current 4, max 28
  Additional-paths operation: Send and Receive
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 3; dropped 2
  Local host: 87.250.234.14, Local port: 179, IF Handle: 0x00000000
  Foreign host: 87.250.234.13, Foreign port: 62020
  Last reset 22w0d, due to BGP Notification sent: hold time expired
  Time since last notification sent to neighbor: 22w0d
  Error Code: hold time expired
  Notification data sent:
    None

BGP neighbor is 87.250.234.42
 Remote AS 13238, local AS 13238, internal link
 Description: korova
 Remote router ID 87.250.234.42
 Cluster ID 87.250.234.14
  BGP state = Established, up for 22w0d
  NSR State: None
  BFD enabled (session up): mininterval: 3000 multiplier: 3
  Last read 00:00:00, Last read before reset 22w0d
  Hold time is 90, keepalive interval is 30 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 179, written 179
  Second last write 00:00:00, attempted 187, written 187
  Last write before reset 22w0d, attempted 25189, written 0
  Second last write before reset 22w0d, attempted 21394, written 0
  Last write pulse rcvd  Aug 16 21:10:27.472 last full Aug  2 11:02:06.834 pulse count 7803501
  Last write pulse rcvd before reset 22w0d
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 22w0d, second last 22w0d
  Last KA expiry before reset 22w0d, second last 22w0d
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 22w0d, second last 22w0d
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Mar 15 15:19:51.127        2  Mar 15 15:19:51.128        2
    Notification:   ---                        0  ---                        0
    Update:         Aug 16 21:10:26.878 12087554  Aug 16 15:49:27.432    13026
    Keepalive:      Aug 16 16:00:09.146   146138  Aug 16 21:10:27.472   836809
    Route_Refresh:  ---                        0  Mar 30 17:37:54.748        8
    Total:                              12233694                        849845
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 4, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  349 accepted prefixes, 217 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 1623524, suppressed 0, withdrawn 819202
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 20
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470206
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 4, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  309 accepted prefixes, 175 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 4721410, suppressed 0, withdrawn 2199991
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470204, Last synced ack version 0
  Outstanding version objects: current 4, max 24
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 2; dropped 1
  Local host: 87.250.234.14, Local port: 32301, IF Handle: 0x00000000
  Foreign host: 87.250.234.42, Foreign port: 179
  Last reset 22w0d, due to BFD (Bidirectional forwarding detection) session down

BGP neighbor is 87.250.234.118
 Remote AS 13238, local AS 13238, internal link
 Description: sverdlov
 Remote router ID 87.250.234.118
 Cluster ID 87.250.234.14
  BGP state = Established, up for 1w2d
  NSR State: None
  BFD enabled (session up): mininterval: 3000 multiplier: 3
  Last read 00:00:23, Last read before reset 1w2d
  Hold time is 90, keepalive interval is 30 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 179, written 179
  Second last write 00:00:00, attempted 187, written 187
  Last write before reset 1w2d, attempted 258, written 258
  Second last write before reset 1w2d, attempted 258, written 258
  Last write pulse rcvd  Aug 16 21:10:27.112 last full Aug  7 16:22:05.588 pulse count 7763196
  Last write pulse rcvd before reset 1w2d
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 1w2d, second last 1w2d
  Last KA expiry before reset 1w2d, second last 1w2d
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 1w2d, second last 1w2d
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Aug  7 16:20:22.217       16  Aug  7 16:20:22.295       14
    Notification:   ---                        0  Aug  7 16:06:58.981        8
    Update:         Aug 16 21:10:26.878 12088086  Aug  7 16:20:26.521      274
    Keepalive:      Aug 16 16:00:09.146   146150  Aug 16 21:10:04.395   838368
    Route_Refresh:  ---                        0  Aug  6 21:59:25.945        2
    Total:                              12234252                        838666
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 1, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 153814, suppressed 0, withdrawn 91902
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 38
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470206
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 1, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  1 accepted prefixes, 1 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 529944, suppressed 0, withdrawn 271735
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470204, Last synced ack version 0
  Outstanding version objects: current 4, max 181
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 7; dropped 6
  Local host: 87.250.234.14, Local port: 19045, IF Handle: 0x00000000
  Foreign host: 87.250.234.118, Foreign port: 179
  Last reset 1w2d, due to BFD (Bidirectional forwarding detection) session down
  Time since last notification received from neighbor: 1w2d
  Error Code: peer unconfigured
  Notification data received:
    None

BGP neighbor is 87.250.234.121
 Remote AS 13238, local AS 13238, internal link
 Description: styri
 Remote router ID 87.250.234.121
 Cluster ID 87.250.234.14
  BGP state = Established, up for 4w6d
  NSR State: None
  BFD enabled (session up): mininterval: 3000 multiplier: 3
  Last read 00:00:24, Last read before reset 4w6d
  Hold time is 180, keepalive interval is 60 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 391, written 391
  Second last write 00:00:01, attempted 179, written 179
  Last write before reset 4w6d, attempted 203, written 203
  Second last write before reset 4w6d, attempted 54, written 54
  Last write pulse rcvd  Aug 16 21:10:27.072 last full Aug  2 11:02:05.380 pulse count 7291155
  Last write pulse rcvd before reset 4w6d
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 4w6d, second last 4w6d
  Last KA expiry before reset 4w6d, second last 4w6d
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 4w6d, second last 4w6d
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Jul 13 01:10:44.551        3  Jul 13 01:10:44.551        3
    Notification:   ---                        0  Jul 13 01:03:09.499        1
    Update:         Aug 16 21:10:28.169 12087395  Aug 16 18:20:05.862    26651
    Keepalive:      Aug 16 06:10:07.693    36103  Aug 16 21:10:03.403   412399
    Route_Refresh:  ---                        0  May 24 17:09:38.996        6
    Total:                              12123501                        439060
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 3, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  572 accepted prefixes, 282 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 418763, suppressed 0, withdrawn 217073
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 19
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470208
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 3, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  336 accepted prefixes, 152 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 1340833, suppressed 0, withdrawn 662391
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470206, Last synced ack version 0
  Outstanding version objects: current 1, max 16
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 3; dropped 2
  Local host: 87.250.234.14, Local port: 179, IF Handle: 0x00000000
  Foreign host: 87.250.234.121, Foreign port: 55720
  Last reset 4w6d, due to BFD (Bidirectional forwarding detection) session down
  Time since last notification received from neighbor: 4w6d
  Error Code: peer unconfigured
  Notification data received:
    None

BGP neighbor is 87.250.234.217
 Remote AS 13238, local AS 13238, internal link
 Description: red-c1
 Remote router ID 87.250.234.217
 Cluster ID 87.250.234.14
  BGP state = Established, up for 4w6d
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:05, Last read before reset 4w6d
  Hold time is 90, keepalive interval is 30 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 391, written 391
  Second last write 00:00:01, attempted 179, written 179
  Last write before reset 4w6d, attempted 19, written 19
  Second last write before reset 4w6d, attempted 3155, written 0
  Last write pulse rcvd  Aug 16 21:10:27.072 last full Aug  2 11:02:06.791 pulse count 7811237
  Last write pulse rcvd before reset 4w6d
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 4w6d, second last 4w6d
  Last KA expiry before reset 4w6d, second last 4w6d
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 4w6d, second last 4w6d
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Jul 13 01:12:43.730        3  Jul 13 01:12:43.730        3
    Notification:   Jul 13 01:04:52.765        2  ---                        0
    Update:         Aug 16 21:10:28.169 12083283  Aug 16 17:15:56.064     1044
    Keepalive:      Aug 16 16:00:09.146   146144  Aug 16 21:10:23.046   841242
    Route_Refresh:  ---                        0  ---                        0
    Total:                              12229432                        842289
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised and received
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  217 accepted prefixes, 78 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 418735, suppressed 0, withdrawn 217062
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 20
  Additional-paths operation: Send and Receive
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470208
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised and received
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  125 accepted prefixes, 47 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 1340750, suppressed 0, withdrawn 662330
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470206, Last synced ack version 0
  Outstanding version objects: current 1, max 28
  Additional-paths operation: Send and Receive
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 3; dropped 2
  Local host: 87.250.234.14, Local port: 179, IF Handle: 0x00000000
  Foreign host: 87.250.234.217, Foreign port: 52146
  Last reset 4w6d, due to BGP Notification sent: hold time expired
  Time since last notification sent to neighbor: 4w6d
  Error Code: hold time expired
  Notification data sent:
    None

BGP neighbor is 87.250.234.228
 Remote AS 13238, local AS 13238, internal link
 Description: marionetka
 Remote router ID 0.0.0.0
 Cluster ID 87.250.234.14
  BGP state = Active
  NSR State: None
  BFD enabled (session down, BFD not configured on remote neighbor)
  Last read 00:00:00, Last read before reset 16w1d
  Hold time is 180, keepalive interval is 60 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 16w1d, attempted 129, written 129
  Second last write 16w1d, attempted 258, written 258
  Last write before reset 16w1d, attempted 129, written 129
  Second last write before reset 16w1d, attempted 258, written 258
  Last write pulse rcvd  Apr 25 10:58:48.388 last full Mar 27 23:55:57.048 pulse count 4339609
  Last write pulse rcvd before reset 16w1d
  Socket not armed for io, not armed for read, not armed for write
  Last write thread event before reset 16w1d, second last 16w1d
  Last KA expiry before reset 16w1d, second last 16w1d
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 16w1d, second last 16w1d
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Mar 15 15:19:34.074        4  Mar 15 15:19:34.074        4
    Notification:   ---                        0  Apr 25 10:59:10.573        2
    Update:         Apr 25 10:58:48.286  6983263  Apr 24 01:28:01.147     8197
    Keepalive:      Apr 25 10:58:14.183    19004  Apr 25 10:58:29.218   244117
    Route_Refresh:  ---                        0  Mar 26 19:03:27.116       10
    Total:                               7002271                        252330
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 0
  Update group: 0.4 Filter-group: 0.0  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  Route refresh request: received 5, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 0, suppressed 0, withdrawn 0
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 0, Last synced ack version 0
  Outstanding version objects: current 0, max 16
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 0
  Update group: 0.4 Filter-group: 0.0  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  Route refresh request: received 5, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 0, suppressed 0, withdrawn 0
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 0, Last synced ack version 0
  Outstanding version objects: current 0, max 18
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 3; dropped 3
  Local host: 87.250.234.14, Local port: 179, IF Handle: 0x00000000
  Foreign host: 87.250.234.228, Foreign port: 64603
  Last reset 16w1d, due to BGP Notification received: peer unconfigured
  Time since last notification received from neighbor: 16w1d
  Error Code: peer unconfigured
  Notification data received:
    None

BGP neighbor is 87.250.234.255
 Remote AS 13238, local AS 13238, internal link
 Remote router ID 87.250.234.255
 Cluster ID 87.250.234.14
  BGP state = Established, up for 2w6d
  NSR State: None
  BFD disabled (interface type not supported)
  Last read 00:00:12, Last read before reset 2w6d
  Hold time is 90, keepalive interval is 30 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 391, written 391
  Second last write 00:00:01, attempted 179, written 179
  Last write before reset 2w6d, attempted 183, written 183
  Second last write before reset 2w6d, attempted 312, written 312
  Last write pulse rcvd  Aug 16 21:10:27.073 last full Aug  2 11:02:09.051 pulse count 4233493
  Last write pulse rcvd before reset 2w6d
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 2w6d, second last 2w6d
  Last KA expiry before reset 2w6d, second last 2w6d
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 2w6d, second last 2w6d
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Jul 27 00:09:09.108        7  Jul 27 00:09:09.236        6
    Notification:   Jul 26 16:56:18.092        2  Jul 27 00:01:37.126        1
    Update:         Aug 16 21:10:28.170  6820419  Aug 16 02:49:36.311     1463
    Keepalive:      Aug 16 16:00:09.146    78802  Aug 16 21:10:15.837   444417
    Route_Refresh:  ---                        0  ---                        0
    Total:                               6899230                        445887
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  71 accepted prefixes, 36 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 257379, suppressed 0, withdrawn 148666
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 15
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470208
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  40 accepted prefixes, 26 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 954549, suppressed 0, withdrawn 481184
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470206, Last synced ack version 0
  Outstanding version objects: current 1, max 27
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 6; dropped 5
  Local host: 87.250.234.14, Local port: 16989, IF Handle: 0x00000000
  Foreign host: 87.250.234.255, Foreign port: 179
  Last reset 2w6d, due to BGP Notification received: peer unconfigured
  Time since last notification sent to neighbor: 3w0d
  Error Code: hold time expired
  Notification data sent:
    None
  Time since last notification received from neighbor: 2w6d
  Error Code: peer unconfigured
  Notification data received:
    None

BGP neighbor is 95.108.237.47
 Remote AS 13238, local AS 13238, internal link
 Description: myt-c1
 Remote router ID 0.0.0.0
 Cluster ID 87.250.234.14
  BGP state = Idle (Neighbor is marked down)
  NSR State: None
  BFD enabled (session down, BFD not configured on remote neighbor)
  Last read 00:00:00, Last read before reset 28w6d
  Hold time is 180, keepalive interval is 60 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 28w6d, attempted 27, written 27
  Second last write 28w6d, attempted 241, written 241
  Last write before reset 28w6d, attempted 241, written 241
  Second last write before reset 28w6d, attempted 755, written 755
  Last write pulse rcvd  Jan 26 14:46:06.994 last full Nov 16 17:41:47.882 pulse count 2371821
  Last write pulse rcvd before reset 28w6d
  Socket not armed for io, not armed for read, not armed for write
  Last write thread event before reset 28w6d, second last 28w6d
  Last KA expiry before reset 28w6d, second last 28w6d
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 28w6d, second last 28w6d
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Nov 16 17:41:40.093        1  Nov 16 17:41:40.092        1
    Notification:   Jan 26 14:46:06.995        1  ---                        0
    Update:         Jan 26 14:46:06.805  3048797  Jan 26 14:46:06.994   477840
    Keepalive:      Jan 26 14:45:30.884    37457  Jan 26 14:45:55.809   211923
    Route_Refresh:  ---                        0  ---                        0
    Total:                               3086256                        689764
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 0
  Update group: 0.4 Filter-group: 0.0  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 0, Last synced ack version 0
  Outstanding version objects: current 0, max 16
  Additional-paths operation: Send and Receive
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 0
  Update group: 0.4 Filter-group: 0.0  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 0, Last synced ack version 0
  Outstanding version objects: current 0, max 15
  Additional-paths operation: Send and Receive
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 1; dropped 1
  Local host: 87.250.234.14, Local port: 179, IF Handle: 0x00000000
  Foreign host: 95.108.237.47, Foreign port: 62958
  Last reset 28w6d, due to Peer exceeding maximum prefix limit (CEASE notification sent - maximum number of prefixes reached)
  Peer had exceeded the max. no. of prefixes configured.
  Reduce the no. of prefix and use 'clear bgp 95.108.237.47' to restore peering
  Time since last notification sent to neighbor: 28w6d
  Error Code: maximum number of prefixes reached
  Notification data sent:
    02040000 1388

BGP neighbor is 95.108.237.128
 Remote AS 13238, local AS 13238, internal link
 Description: ugr-b-c1
 Remote router ID 0.0.0.0
 Cluster ID 87.250.234.14
  BGP state = Idle
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:00, Last read before reset 00:00:00
  Hold time is 180, keepalive interval is 60 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:12, attempted 73, written 73
  Second last write 00:00:33, attempted 73, written 73
  Last write before reset 00:00:00, attempted 0, written 0
  Second last write before reset 00:00:00, attempted 0, written 0
  Last write pulse rcvd  Aug 16 21:10:16.123 last full not set pulse count 187665
  Last write pulse rcvd before reset 00:00:00
  Socket not armed for io, not armed for read, not armed for write
  Last write thread event before reset 00:00:00, second last 00:00:00
  Last KA expiry before reset 00:00:00, second last 00:00:00
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 00:00:00, second last 00:00:00
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability not received
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Aug 16 21:10:16.123   187071  ---                        0
    Notification:   ---                        0  ---                        0
    Update:         ---                        0  ---                        0
    Keepalive:      ---                        0  ---                        0
    Route_Refresh:  ---                        0  ---                        0
    Total:                                187071                             0
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 0
  Update group: 0.2 Filter-group: 0.0  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 0, suppressed 0, withdrawn 0
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 1, Last synced ack version 0
  Outstanding version objects: current 0, max 0
  Additional-paths operation: None
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 0
  Update group: 0.2 Filter-group: 0.0  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 0, suppressed 0, withdrawn 0
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 1, Last synced ack version 0
  Outstanding version objects: current 0, max 0
  Additional-paths operation: None
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 0; dropped 0
  Local host: 87.250.234.14, Local port: 46901, IF Handle: 0x00000000
  Foreign host: 95.108.237.128, Foreign port: 179
  Last reset 00:00:12, due to Peer closing down the session
  Peer reset reason: Remote closed the session (Connection timed out)

BGP neighbor is 95.108.237.138
 Remote AS 13238, local AS 13238, internal link
 Description: vla1-2d1
 Remote router ID 95.108.237.138
 Cluster ID 87.250.234.14
  BGP state = Established, up for 2w0d
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:05, Last read before reset 2w0d
  Hold time is 90, keepalive interval is 30 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 391, written 391
  Second last write 00:00:01, attempted 179, written 179
  Last write before reset 2w0d, attempted 266, written 266
  Second last write before reset 2w0d, attempted 96, written 96
  Last write pulse rcvd  Aug 16 21:10:27.078 last full Aug  2 11:02:05.184 pulse count 856743
  Last write pulse rcvd before reset 2w0d
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 2w0d, second last 2w0d
  Last KA expiry before reset 00:00:00, second last 00:00:00
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 2w0d, second last 2w0d
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Aug  1 21:13:35.417        3  Aug  1 21:13:35.422        3
    Notification:   Aug  1 21:13:05.633        2  ---                        0
    Update:         Aug 16 21:10:28.170  1478205  Aug 16 21:05:54.658    24496
    Keepalive:      Aug 16 16:00:09.146     7891  Aug 16 21:10:22.865    66855
    Route_Refresh:  ---                        0  ---                        0
    Total:                               1486101                         91354
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  161 accepted prefixes, 54 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 205759, suppressed 0, withdrawn 120122
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 15
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470208
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  482 accepted prefixes, 46 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 746970, suppressed 0, withdrawn 382011
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470206, Last synced ack version 0
  Outstanding version objects: current 1, max 54
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 3; dropped 2
  Local host: 87.250.234.14, Local port: 46357, IF Handle: 0x00000000
  Foreign host: 95.108.237.138, Foreign port: 179
  Last reset 2w0d, due to BGP Notification sent: hold time expired
  Time since last notification sent to neighbor: 2w0d
  Error Code: hold time expired
  Notification data sent:
    None

BGP neighbor is 95.108.237.139
 Remote AS 13238, local AS 13238, internal link
 Description: vla1-2d1
 Remote router ID 95.108.237.139
 Cluster ID 87.250.234.14
  BGP state = Established, up for 1d04h
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:14, Last read before reset 1d04h
  Hold time is 90, keepalive interval is 30 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 391, written 391
  Second last write 00:00:01, attempted 179, written 179
  Last write before reset 1d04h, attempted 187, written 187
  Second last write before reset 1d04h, attempted 102, written 102
  Last write pulse rcvd  Aug 16 21:10:27.078 last full Aug 15 16:31:09.899 pulse count 852692
  Last write pulse rcvd before reset 1d04h
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 1d04h, second last 1d04h
  Last KA expiry before reset 00:00:00, second last 00:00:00
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 1d04h, second last 1d04h
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Aug 15 16:31:01.817        6  Aug 15 16:31:01.822        6
    Notification:   Aug  8 14:25:12.622        2  Aug 15 16:12:34.797        3
    Update:         Aug 16 21:10:28.170  1475489  Aug 16 21:05:54.707    24372
    Keepalive:      Aug 16 16:00:09.146     7896  Aug 16 21:10:14.178    66695
    Route_Refresh:  ---                        0  ---                        0
    Total:                               1483393                         91076
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  161 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 36212, suppressed 0, withdrawn 12502
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 15
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470208
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  482 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 107690, suppressed 0, withdrawn 43437
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470206, Last synced ack version 0
  Outstanding version objects: current 1, max 97
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 6; dropped 5
  Local host: 87.250.234.14, Local port: 49103, IF Handle: 0x00000000
  Foreign host: 95.108.237.139, Foreign port: 179
  Last reset 1d04h, due to BGP Notification received: peer unconfigured
  Time since last notification sent to neighbor: 1w1d
  Error Code: hold time expired
  Notification data sent:
    None
  Time since last notification received from neighbor: 1d04h
  Error Code: peer unconfigured
  Notification data received:
    None

BGP neighbor is 95.108.237.140
 Remote AS 13238, local AS 13238, internal link
 Description: vla1-3d1-lo0
 Remote router ID 95.108.237.140
 Cluster ID 87.250.234.14
  BGP state = Established, up for 2w1d
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:13, Last read before reset 2w1d
  Hold time is 90, keepalive interval is 30 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 391, written 391
  Second last write 00:00:01, attempted 179, written 179
  Last write before reset 2w1d, attempted 108, written 108
  Second last write before reset 2w1d, attempted 523, written 523
  Last write pulse rcvd  Aug 16 21:10:27.177 last full Aug  2 11:02:05.184 pulse count 1688765
  Last write pulse rcvd before reset 2w1d
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 2w1d, second last 2w1d
  Last KA expiry before reset 2w1d, second last 2w1d
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 2w1d, second last 2w1d
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Aug  1 21:07:56.946        2  Aug  1 21:07:56.961        2
    Notification:   Aug  1 21:07:26.339        1  ---                        0
    Update:         Aug 16 21:10:28.170  2911880  Aug 13 19:07:20.373       86
    Keepalive:      Aug 16 16:00:09.146    17425  Aug 16 21:10:15.176   145294
    Route_Refresh:  ---                        0  ---                        0
    Total:                               2929308                        145382
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  31 accepted prefixes, 31 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 205798, suppressed 0, withdrawn 120137
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 29
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470208
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  23 accepted prefixes, 23 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 747307, suppressed 0, withdrawn 382202
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470206, Last synced ack version 0
  Outstanding version objects: current 1, max 59
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 2; dropped 1
  Local host: 87.250.234.14, Local port: 42389, IF Handle: 0x00000000
  Foreign host: 95.108.237.140, Foreign port: 179
  Last reset 2w1d, due to BGP Notification sent: hold time expired
  Time since last notification sent to neighbor: 2w1d
  Error Code: hold time expired
  Notification data sent:
    None

BGP neighbor is 95.108.237.141
 Remote AS 13238, local AS 13238, internal link
 Description: vla1-3d3-lo0
 Remote router ID 95.108.237.141
 Cluster ID 87.250.234.14
  BGP state = Established, up for 6w6d
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:17, Last read before reset 00:00:00
  Hold time is 90, keepalive interval is 30 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 391, written 391
  Second last write 00:00:01, attempted 179, written 179
  Last write before reset 00:00:00, attempted 0, written 0
  Second last write before reset 00:00:00, attempted 0, written 0
  Last write pulse rcvd  Aug 16 21:10:27.074 last full Aug  2 11:02:05.183 pulse count 1688359
  Last write pulse rcvd before reset 00:00:00
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 00:00:00, second last 00:00:00
  Last KA expiry before reset 00:00:00, second last 00:00:00
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 00:00:00, second last 00:00:00
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Jun 29 00:44:22.724        1  Jun 29 00:44:22.728        1
    Notification:   ---                        0  ---                        0
    Update:         Aug 16 21:10:28.169  2910733  Aug 13 19:07:20.354       72
    Keepalive:      Aug 16 16:00:09.146    17425  Aug 16 21:10:10.326   145291
    Route_Refresh:  ---                        0  ---                        0
    Total:                               2928159                        145364
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  31 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 594634, suppressed 0, withdrawn 299892
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 37
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470208
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  23 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 1995299, suppressed 0, withdrawn 985130
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470206, Last synced ack version 0
  Outstanding version objects: current 1, max 72
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 1; dropped 0
  Local host: 87.250.234.14, Local port: 36557, IF Handle: 0x00000000
  Foreign host: 95.108.237.141, Foreign port: 179
  Last reset 00:00:00

BGP neighbor is 95.108.237.142
 Remote AS 13238, local AS 13238, internal link
 Description: vla1-3d2-lo0
 Remote router ID 95.108.237.142
 Cluster ID 87.250.234.14
  BGP state = Established, up for 6w6d
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:38, Last read before reset 00:00:00
  Hold time is 180, keepalive interval is 60 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 258, written 258
  Second last write 00:00:00, attempted 391, written 391
  Last write before reset 00:00:00, attempted 0, written 0
  Second last write before reset 00:00:00, attempted 0, written 0
  Last write pulse rcvd  Aug 16 21:10:28.318 last full Aug  2 11:02:18.508 pulse count 1595372
  Last write pulse rcvd before reset 00:00:00
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 00:00:00, second last 00:00:00
  Last KA expiry before reset 00:00:00, second last 00:00:00
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 00:00:00, second last 00:00:00
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Jun 29 00:44:40.692        1  Jun 29 00:44:40.898        1
    Notification:   ---                        0  ---                        0
    Update:         Aug 16 21:10:28.490  2911380  Aug 13 19:29:32.810      105
    Keepalive:      Aug 16 06:10:07.693     3890  Aug 16 21:09:50.048    78614
    Route_Refresh:  ---                        0  Jun 29 18:21:25.858        1
    Total:                               2915271                         78721
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  31 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 594634, suppressed 0, withdrawn 299892
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 46
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470209
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 1, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  25 accepted prefixes, 2 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 2007874, suppressed 0, withdrawn 985129
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470208, Last synced ack version 0
  Outstanding version objects: current 1, max 98
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 1; dropped 0
  Local host: 87.250.234.14, Local port: 30536, IF Handle: 0x00000000
  Foreign host: 95.108.237.142, Foreign port: 179
  Last reset 00:00:00

BGP neighbor is 95.108.237.143
 Remote AS 13238, local AS 13238, internal link
 Description: vla1-3d4-lo0
 Remote router ID 95.108.237.143
 Cluster ID 87.250.234.14
  BGP state = Established, up for 6w6d
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:20, Last read before reset 00:00:00
  Hold time is 180, keepalive interval is 60 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 258, written 258
  Second last write 00:00:00, attempted 391, written 391
  Last write before reset 00:00:00, attempted 0, written 0
  Second last write before reset 00:00:00, attempted 0, written 0
  Last write pulse rcvd  Aug 16 21:10:28.221 last full Aug  2 11:02:05.183 pulse count 1596003
  Last write pulse rcvd before reset 00:00:00
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 00:00:00, second last 00:00:00
  Last KA expiry before reset 00:00:00, second last 00:00:00
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 00:00:00, second last 00:00:00
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Jun 29 00:44:03.581        1  Jun 29 00:44:03.581        1
    Notification:   ---                        0  ---                        0
    Update:         Aug 16 21:10:28.490  2911388  Aug 13 19:29:32.813      102
    Keepalive:      Aug 16 06:10:07.693     3892  Aug 16 21:10:08.220    78650
    Route_Refresh:  ---                        0  Jun 29 18:21:28.262        1
    Total:                               2915281                         78754
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  31 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 594634, suppressed 0, withdrawn 299892
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 34
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470209
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 1, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  25 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 2007880, suppressed 0, withdrawn 985132
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470208, Last synced ack version 0
  Outstanding version objects: current 1, max 52
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 1; dropped 0
  Local host: 87.250.234.14, Local port: 179, IF Handle: 0x00000000
  Foreign host: 95.108.237.143, Foreign port: 63797
  Last reset 00:00:00

BGP neighbor is 95.108.237.144
 Remote AS 13238, local AS 13238, internal link
 Description: vla1-4d1
 Remote router ID 95.108.237.144
 Cluster ID 87.250.234.14
  BGP state = Established, up for 3w6d
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:25, Last read before reset 00:00:00
  Hold time is 90, keepalive interval is 30 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 258, written 258
  Second last write 00:00:00, attempted 391, written 391
  Last write before reset 00:00:00, attempted 0, written 0
  Second last write before reset 00:00:00, attempted 0, written 0
  Last write pulse rcvd  Aug 16 21:10:28.283 last full Aug  2 11:02:05.184 pulse count 944128
  Last write pulse rcvd before reset 00:00:00
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 00:00:00, second last 00:00:00
  Last KA expiry before reset 00:00:00, second last 00:00:00
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 00:00:00, second last 00:00:00
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Jul 20 17:54:06.785        1  Jul 20 17:54:06.791        1
    Notification:   ---                        0  ---                        0
    Update:         Aug 16 21:10:28.490  1659587  ---                        0
    Keepalive:      Aug 16 16:00:09.146    10893  Aug 16 21:10:03.161    81041
    Route_Refresh:  ---                        0  ---                        0
    Total:                               1670481                         81042
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 303431, suppressed 0, withdrawn 175054
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 19
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470209
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 1117916, suppressed 0, withdrawn 561032
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470208, Last synced ack version 0
  Outstanding version objects: current 1, max 35
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 1; dropped 0
  Local host: 87.250.234.14, Local port: 49824, IF Handle: 0x00000000
  Foreign host: 95.108.237.144, Foreign port: 179
  Last reset 00:00:00

BGP neighbor is 95.108.237.145
 Remote AS 13238, local AS 13238, internal link
 Description: vla1-4d2
 Remote router ID 95.108.237.145
 Cluster ID 87.250.234.14
  BGP state = Established, up for 2w0d
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:23, Last read before reset 2w0d
  Hold time is 180, keepalive interval is 60 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 258, written 258
  Second last write 00:00:00, attempted 391, written 391
  Last write before reset 2w0d, attempted 266, written 266
  Second last write before reset 2w0d, attempted 133, written 133
  Last write pulse rcvd  Aug 16 21:10:28.274 last full Aug  2 11:02:05.184 pulse count 890464
  Last write pulse rcvd before reset 2w0d
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 2w0d, second last 2w0d
  Last KA expiry before reset 2w1d, second last 2w1d
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 2w0d, second last 2w0d
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Aug  1 22:26:32.051        2  Aug  1 22:26:32.197        2
    Notification:   Aug  1 22:15:54.588        1  ---                        0
    Update:         Aug 16 21:10:28.491  1660178  Aug  2 13:15:13.932       63
    Keepalive:      Aug 16 06:10:07.694     2607  Aug 16 21:10:04.586    43884
    Route_Refresh:  ---                        0  ---                        0
    Total:                               1662788                         43949
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  3 accepted prefixes, 3 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 205475, suppressed 0, withdrawn 120012
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 19
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470209
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  7 accepted prefixes, 7 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 744228, suppressed 0, withdrawn 380471
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470208, Last synced ack version 0
  Outstanding version objects: current 1, max 99
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 2; dropped 1
  Local host: 87.250.234.14, Local port: 20903, IF Handle: 0x00000000
  Foreign host: 95.108.237.145, Foreign port: 179
  Last reset 2w0d, due to BGP Notification sent: hold time expired
  Time since last notification sent to neighbor: 2w0d
  Error Code: hold time expired
  Notification data sent:
    None

BGP neighbor is 95.108.237.146
 Remote AS 13238, local AS 13238, internal link
 Description: vla1-4d3
 Remote router ID 95.108.237.146
 Cluster ID 87.250.234.14
  BGP state = Established, up for 2w1d
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:07, Last read before reset 2w1d
  Hold time is 90, keepalive interval is 30 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 258, written 258
  Second last write 00:00:00, attempted 391, written 391
  Last write before reset 2w1d, attempted 258, written 258
  Second last write before reset 2w1d, attempted 587, written 587
  Last write pulse rcvd  Aug 16 21:10:28.287 last full Aug  2 11:03:50.077 pulse count 944009
  Last write pulse rcvd before reset 2w1d
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 2w1d, second last 2w1d
  Last KA expiry before reset 2w1d, second last 2w1d
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 2w1d, second last 2w1d
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Aug  1 21:07:48.959        2  Aug  1 21:07:48.973        2
    Notification:   Aug  1 21:07:18.524        1  ---                        0
    Update:         Aug 16 21:10:28.491  1660739  ---                        0
    Keepalive:      Aug 16 16:00:09.146    10895  Aug 16 21:10:21.370    81061
    Route_Refresh:  ---                        0  ---                        0
    Total:                               1671637                         81063
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 205814, suppressed 0, withdrawn 120137
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 19
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470209
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 747322, suppressed 0, withdrawn 382203
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470208, Last synced ack version 0
  Outstanding version objects: current 1, max 54
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 2; dropped 1
  Local host: 87.250.234.14, Local port: 25273, IF Handle: 0x00000000
  Foreign host: 95.108.237.146, Foreign port: 179
  Last reset 2w1d, due to BGP Notification sent: hold time expired
  Time since last notification sent to neighbor: 2w1d
  Error Code: hold time expired
  Notification data sent:
    None

BGP neighbor is 95.108.237.147
 Remote AS 13238, local AS 13238, internal link
 Description: vla1-4d4
 Remote router ID 95.108.237.147
 Cluster ID 87.250.234.14
  BGP state = Established, up for 2w0d
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:33, Last read before reset 2w0d
  Hold time is 180, keepalive interval is 60 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 258, written 258
  Second last write 00:00:00, attempted 391, written 391
  Last write before reset 2w0d, attempted 179, written 179
  Second last write before reset 2w0d, attempted 258, written 258
  Last write pulse rcvd  Aug 16 21:10:28.231 last full Aug  2 11:02:29.396 pulse count 890588
  Last write pulse rcvd before reset 2w0d
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 2w0d, second last 2w0d
  Last KA expiry before reset 2w1d, second last 2w1d
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 2w0d, second last 2w0d
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Aug  1 21:59:15.489        2  Aug  1 21:59:15.488        2
    Notification:   Aug  1 21:48:12.545        1  ---                        0
    Update:         Aug 16 21:10:28.491  1660131  Aug  2 13:15:13.932       63
    Keepalive:      Aug 16 06:10:07.694     2608  Aug 16 21:09:55.103    43908
    Route_Refresh:  ---                        0  ---                        0
    Total:                               1662742                         43973
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  3 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 205585, suppressed 0, withdrawn 120056
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 26
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470209
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  7 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 745283, suppressed 0, withdrawn 381039
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470208, Last synced ack version 0
  Outstanding version objects: current 1, max 116
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 2; dropped 1
  Local host: 87.250.234.14, Local port: 179, IF Handle: 0x00000000
  Foreign host: 95.108.237.147, Foreign port: 51039
  Last reset 2w0d, due to BGP Notification sent: hold time expired
  Time since last notification sent to neighbor: 2w0d
  Error Code: hold time expired
  Notification data sent:
    None

BGP neighbor is 95.108.237.168
 Remote AS 13238, local AS 13238, internal link
 Description: vla1-1d1-lo0
 Remote router ID 95.108.237.168
 Cluster ID 87.250.234.14
  BGP state = Established, up for 2w1d
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:01, Last read before reset 2w1d
  Hold time is 90, keepalive interval is 30 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 258, written 258
  Second last write 00:00:00, attempted 391, written 391
  Last write before reset 2w1d, attempted 266, written 266
  Second last write before reset 2w1d, attempted 258, written 258
  Last write pulse rcvd  Aug 16 21:10:28.277 last full Aug 16 15:56:54.494 pulse count 1693750
  Last write pulse rcvd before reset 2w1d
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 2w1d, second last 2w1d
  Last KA expiry before reset 2w1d, second last 2w1d
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 2w1d, second last 2w1d
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Aug  1 21:07:34.070       43  Aug  1 21:07:34.084       34
    Notification:   Aug  1 21:07:14.782        1  Jun 28 13:27:22.785       32
    Update:         Aug 16 21:10:28.491  2879113  Aug 16 21:00:26.038    92710
    Keepalive:      Aug 16 16:00:09.146    16546  Aug 16 21:10:27.226   134694
    Route_Refresh:  ---                        0  Aug 16 15:56:52.152      152
    Total:                               2895703                        227622
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 76, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  378 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 397724, suppressed 0, withdrawn 120137
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 16
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470209
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 76, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  664 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 1015980, suppressed 0, withdrawn 382207
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470208, Last synced ack version 0
  Outstanding version objects: current 1, max 52
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 2; dropped 1
  Local host: 87.250.234.14, Local port: 61009, IF Handle: 0x00000000
  Foreign host: 95.108.237.168, Foreign port: 179
  Last reset 2w1d, due to BGP Notification sent: hold time expired
  Time since last notification sent to neighbor: 2w1d
  Error Code: hold time expired
  Notification data sent:
    None
  Time since last notification received from neighbor: 7w0d
  Error Code: connection rejected
  Notification data received:
    None

BGP neighbor is 95.108.237.169
 Remote AS 13238, local AS 13238, internal link
 Description: vla1-1d3
 Remote router ID 95.108.237.169
 Cluster ID 87.250.234.14
  BGP state = Established, up for 2w1d
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:11, Last read before reset 2w1d
  Hold time is 90, keepalive interval is 30 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 258, written 258
  Second last write 00:00:00, attempted 391, written 391
  Last write before reset 2w1d, attempted 266, written 266
  Second last write before reset 2w1d, attempted 179, written 179
  Last write pulse rcvd  Aug 16 21:10:28.278 last full Aug  2 11:02:05.184 pulse count 1650186
  Last write pulse rcvd before reset 2w1d
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 2w1d, second last 2w1d
  Last KA expiry before reset 2w1d, second last 2w1d
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 2w1d, second last 2w1d
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Aug  1 21:07:45.932        2  Aug  1 21:07:46.034        2
    Notification:   Aug  1 21:07:22.696        1  ---                        0
    Update:         Aug 16 21:10:28.491  2716470  Aug 16 21:00:26.036    90385
    Keepalive:      Aug 16 16:00:09.146    16267  Aug 16 21:10:16.985   131136
    Route_Refresh:  ---                        0  ---                        0
    Total:                               2732740                        221523
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  378 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 205814, suppressed 0, withdrawn 120137
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 16
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470209
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  664 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 747322, suppressed 0, withdrawn 382203
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470208, Last synced ack version 0
  Outstanding version objects: current 1, max 57
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 2; dropped 1
  Local host: 87.250.234.14, Local port: 12194, IF Handle: 0x00000000
  Foreign host: 95.108.237.169, Foreign port: 179
  Last reset 2w1d, due to BGP Notification sent: hold time expired
  Time since last notification sent to neighbor: 2w1d
  Error Code: hold time expired
  Notification data sent:
    None

BGP neighbor is 95.108.237.200
 Remote AS 13238, local AS 13238, internal link
 Description: vla1-2d4-lo0
 Remote router ID 95.108.237.200
 Cluster ID 87.250.234.14
  BGP state = Established, up for 4w6d
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:25, Last read before reset 4w6d
  Hold time is 180, keepalive interval is 60 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 258, written 258
  Second last write 00:00:00, attempted 391, written 391
  Last write before reset 4w6d, attempted 262, written 262
  Second last write before reset 4w6d, attempted 391, written 391
  Last write pulse rcvd  Aug 16 21:10:28.445 last full Aug  2 11:02:05.184 pulse count 7337535
  Last write pulse rcvd before reset 4w6d
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 4w6d, second last 4w6d
  Last KA expiry before reset 4w6d, second last 4w6d
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 4w6d, second last 4w6d
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Jul 13 14:18:32.047        3  Jul 13 14:18:32.277        3
    Notification:   Jul 13 14:07:04.177        2  ---                        0
    Update:         Aug 16 21:10:28.490 12087406  Aug 16 21:06:09.169   112972
    Keepalive:      Aug 16 06:10:07.694    36106  Aug 16 21:10:02.695   455688
    Route_Refresh:  ---                        0  Jun 29 18:21:23.353        6
    Total:                              12123517                        568669
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 4, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  161 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 411597, suppressed 0, withdrawn 215052
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 132
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470209
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 2, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  482 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 1323944, suppressed 0, withdrawn 654066
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470208, Last synced ack version 0
  Outstanding version objects: current 1, max 175
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 3; dropped 2
  Local host: 87.250.234.14, Local port: 58711, IF Handle: 0x00000000
  Foreign host: 95.108.237.200, Foreign port: 179
  Last reset 4w6d, due to BGP Notification sent: hold time expired
  Time since last notification sent to neighbor: 4w6d
  Error Code: hold time expired
  Notification data sent:
    None

BGP neighbor is 95.108.237.217
 Remote AS 13238, local AS 13238, internal link
 Description: vla1-5d3
 Remote router ID 95.108.237.217
 Cluster ID 87.250.234.14
  BGP state = Established, up for 06:09:06
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:01, Last read before reset 00:00:00
  Hold time is 90, keepalive interval is 30 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 258, written 258
  Second last write 00:00:00, attempted 391, written 391
  Last write before reset 00:00:00, attempted 0, written 0
  Second last write before reset 00:00:00, attempted 0, written 0
  Last write pulse rcvd  Aug 16 21:10:28.276 last full Aug 16 15:01:28.779 pulse count 20170
  Last write pulse rcvd before reset 00:00:00
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 00:00:00, second last 00:00:00
  Last KA expiry before reset 00:00:00, second last 00:00:00
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 00:00:00, second last 00:00:00
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Aug 16 15:01:22.168        1  Aug 16 15:01:22.173        1
    Notification:   ---                        0  ---                        0
    Update:         Aug 16 21:10:28.491    42607  ---                        0
    Keepalive:      Aug 16 16:00:09.146        3  Aug 16 21:10:26.720      797
    Route_Refresh:  ---                        0  ---                        0
    Total:                                 42611                           798
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 19650, suppressed 0, withdrawn 4436
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 8
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470209
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 43954, suppressed 0, withdrawn 13207
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470208, Last synced ack version 0
  Outstanding version objects: current 1, max 11
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 1; dropped 0
  Local host: 87.250.234.14, Local port: 26775, IF Handle: 0x00000000
  Foreign host: 95.108.237.217, Foreign port: 179
  Last reset 00:00:00

BGP neighbor is 95.108.237.218
 Remote AS 13238, local AS 13238, internal link
 Description: vla1-5d4
 Remote router ID 0.0.0.0
 Cluster ID 87.250.234.14
  BGP state = Active
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:00, Last read before reset 00:00:00
  Hold time is 180, keepalive interval is 60 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 0, written 0
  Second last write 00:00:00, attempted 0, written 0
  Last write before reset 00:00:00, attempted 0, written 0
  Second last write before reset 00:00:00, attempted 0, written 0
  Last write pulse rcvd  not set last full not set pulse count 0
  Last write pulse rcvd before reset 00:00:00
  Socket not armed for io, not armed for read, not armed for write
  Last write thread event before reset 00:00:00, second last 00:00:00
  Last KA expiry before reset 00:00:00, second last 00:00:00
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 00:00:00, second last 00:00:00
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability not received
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           ---                        0  ---                        0
    Notification:   ---                        0  ---                        0
    Update:         ---                        0  ---                        0
    Keepalive:      ---                        0  ---                        0
    Route_Refresh:  ---                        0  ---                        0
    Total:                                     0                             0
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 0
  Update group: 0.2 Filter-group: 0.0  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 0, suppressed 0, withdrawn 0
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 1, Last synced ack version 0
  Outstanding version objects: current 0, max 0
  Additional-paths operation: None
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 0
  Update group: 0.2 Filter-group: 0.0  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 0, suppressed 0, withdrawn 0
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 1, Last synced ack version 0
  Outstanding version objects: current 0, max 0
  Additional-paths operation: None
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 0; dropped 0
  Local host: 87.250.234.14, Local port: 0, IF Handle: 0x00000000
  Foreign host: 95.108.237.218, Foreign port: 0
  Last reset 00:00:00

BGP neighbor is 95.108.237.220
 Remote AS 13238, local AS 13238, internal link
 Description: vla1-2d2-lo0
 Remote router ID 95.108.237.220
 Cluster ID 87.250.234.14
  BGP state = Established, up for 5w1d
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:25, Last read before reset 5w1d
  Hold time is 180, keepalive interval is 60 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 179, written 179
  Second last write 00:00:00, attempted 258, written 258
  Last write before reset 5w1d, attempted 254, written 254
  Second last write before reset 5w1d, attempted 188, written 188
  Last write pulse rcvd  Aug 16 21:10:28.897 last full Aug  2 11:02:05.183 pulse count 7336478
  Last write pulse rcvd before reset 5w1d
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 5w1d, second last 5w1d
  Last KA expiry before reset 5w6d, second last 5w6d
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 5w1d, second last 5w1d
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Jul 10 23:26:02.089        3  Jul 10 23:26:02.296        3
    Notification:   Jul 10 23:15:25.492        2  ---                        0
    Update:         Aug 16 21:10:28.874 12085717  Aug 16 21:06:06.018   111913
    Keepalive:      Aug 16 06:10:07.693    36105  Aug 16 21:10:03.750   455372
    Route_Refresh:  ---                        0  Jun 29 18:21:20.734        3
    Total:                              12121827                        567291
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 1, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  161 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 450387, suppressed 0, withdrawn 234886
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 75
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470210
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 2, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  482 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 1417142, suppressed 0, withdrawn 706032
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470209, Last synced ack version 0
  Outstanding version objects: current 2, max 104
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 3; dropped 2
  Local host: 87.250.234.14, Local port: 30796, IF Handle: 0x00000000
  Foreign host: 95.108.237.220, Foreign port: 179
  Last reset 5w1d, due to BGP Notification sent: hold time expired
  Time since last notification sent to neighbor: 5w1d
  Error Code: hold time expired
  Notification data sent:
    None

BGP neighbor is 95.108.237.238
 Remote AS 13238, local AS 13238, internal link
 Description: vla1-1d4-lo0
 Remote router ID 95.108.237.238
 Cluster ID 87.250.234.14
  BGP state = Established, up for 6w1d
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:29, Last read before reset 6w1d
  Hold time is 180, keepalive interval is 60 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 179, written 179
  Second last write 00:00:00, attempted 258, written 258
  Last write before reset 6w1d, attempted 133, written 133
  Second last write before reset 6w1d, attempted 262, written 262
  Last write pulse rcvd  Aug 16 21:10:28.600 last full Aug  2 11:02:05.303 pulse count 8040151
  Last write pulse rcvd before reset 6w1d
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 6w1d, second last 6w1d
  Last KA expiry before reset 6w1d, second last 6w1d
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 6w1d, second last 6w1d
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Jul  4 13:07:32.241        3  Jul  4 13:07:32.440        3
    Notification:   Jul  4 12:57:05.920        2  ---                        0
    Update:         Aug 16 21:10:28.874 12085380  Aug 16 21:00:25.841   809502
    Keepalive:      Aug 16 06:10:07.693    36104  Aug 16 21:09:59.358   453214
    Route_Refresh:  ---                        0  Jun 29 18:21:18.312        3
    Total:                              12121489                       1262722
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 1, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  378 accepted prefixes, 68 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 532121, suppressed 0, withdrawn 273064
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 52
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470210
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 2, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  664 accepted prefixes, 84 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 1813798, suppressed 0, withdrawn 902695
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470209, Last synced ack version 0
  Outstanding version objects: current 2, max 106
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 3; dropped 2
  Local host: 87.250.234.14, Local port: 64118, IF Handle: 0x00000000
  Foreign host: 95.108.237.238, Foreign port: 179
  Last reset 6w1d, due to BGP Notification sent: hold time expired
  Time since last notification sent to neighbor: 6w1d
  Error Code: hold time expired
  Notification data sent:
    None

BGP neighbor is 95.108.237.241
 Remote AS 13238, local AS 13238, internal link
 Description: vla1-5d1
 Remote router ID 95.108.237.241
 Cluster ID 87.250.234.14
  BGP state = Established, up for 06:09:12
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:11, Last read before reset 00:00:00
  Hold time is 90, keepalive interval is 30 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 179, written 179
  Second last write 00:00:00, attempted 258, written 258
  Last write before reset 00:00:00, attempted 0, written 0
  Second last write before reset 00:00:00, attempted 0, written 0
  Last write pulse rcvd  Aug 16 21:10:28.599 last full Aug 16 15:01:22.307 pulse count 20166
  Last write pulse rcvd before reset 00:00:00
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 00:00:00, second last 00:00:00
  Last KA expiry before reset 00:00:00, second last 00:00:00
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 00:00:00, second last 00:00:00
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Aug 16 15:01:16.205        1  Aug 16 15:01:16.210        1
    Notification:   ---                        0  ---                        0
    Update:         Aug 16 21:10:28.875    42615  ---                        0
    Keepalive:      Aug 16 16:00:09.146        3  Aug 16 21:10:16.944      798
    Route_Refresh:  ---                        0  ---                        0
    Total:                                 42619                           799
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 19653, suppressed 0, withdrawn 4437
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 8
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470210
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 43959, suppressed 0, withdrawn 13209
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470209, Last synced ack version 0
  Outstanding version objects: current 2, max 10
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 1; dropped 0
  Local host: 87.250.234.14, Local port: 17186, IF Handle: 0x00000000
  Foreign host: 95.108.237.241, Foreign port: 179
  Last reset 00:00:00

BGP neighbor is 95.108.237.242
 Remote AS 13238, local AS 13238, internal link
 Description: vla1-5d2
 Remote router ID 0.0.0.0
 Cluster ID 87.250.234.14
  BGP state = Active
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:00, Last read before reset 00:00:00
  Hold time is 180, keepalive interval is 60 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 0, written 0
  Second last write 00:00:00, attempted 0, written 0
  Last write before reset 00:00:00, attempted 0, written 0
  Second last write before reset 00:00:00, attempted 0, written 0
  Last write pulse rcvd  not set last full not set pulse count 0
  Last write pulse rcvd before reset 00:00:00
  Socket not armed for io, not armed for read, not armed for write
  Last write thread event before reset 00:00:00, second last 00:00:00
  Last KA expiry before reset 00:00:00, second last 00:00:00
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 00:00:00, second last 00:00:00
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability not received
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           ---                        0  ---                        0
    Notification:   ---                        0  ---                        0
    Update:         ---                        0  ---                        0
    Keepalive:      ---                        0  ---                        0
    Route_Refresh:  ---                        0  ---                        0
    Total:                                     0                             0
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 0
  Update group: 0.2 Filter-group: 0.0  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 0, suppressed 0, withdrawn 0
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 1, Last synced ack version 0
  Outstanding version objects: current 0, max 0
  Additional-paths operation: None
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 0
  Update group: 0.2 Filter-group: 0.0  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 0, suppressed 0, withdrawn 0
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 1, Last synced ack version 0
  Outstanding version objects: current 0, max 0
  Additional-paths operation: None
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 0; dropped 0
  Local host: 87.250.234.14, Local port: 0, IF Handle: 0x00000000
  Foreign host: 95.108.237.242, Foreign port: 0
  Last reset 00:00:00

BGP neighbor is 95.108.237.255
 Remote AS 13238, local AS 13238, internal link
 Description: vla1-1d2-lo0
 Remote router ID 95.108.237.255
 Cluster ID 87.250.234.14
  BGP state = Established, up for 18w0d
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:31, Last read before reset 18w0d
  Hold time is 180, keepalive interval is 60 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 179, written 179
  Second last write 00:00:00, attempted 258, written 258
  Last write before reset 18w0d, attempted 254, written 254
  Second last write before reset 18w0d, attempted 254, written 254
  Last write pulse rcvd  Aug 16 21:10:28.678 last full Aug  2 11:02:05.185 pulse count 8042194
  Last write pulse rcvd before reset 18w0d
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 18w0d, second last 18w0d
  Last KA expiry before reset 18w0d, second last 18w0d
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 18w0d, second last 18w0d
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Apr 12 14:37:38.155        3  Apr 12 14:37:38.155        3
    Notification:   Apr 12 14:14:26.888        2  ---                        0
    Update:         Aug 16 21:10:28.874 12087473  Aug 16 21:00:25.840   806294
    Keepalive:      Aug 16 06:10:07.693    36107  Aug 16 21:09:57.668   453416
    Route_Refresh:  ---                        0  Jun 29 18:29:06.341        8
    Total:                              12123585                       1259721
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 4, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  378 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 1350125, suppressed 0, withdrawn 682805
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 65
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470210
  Update group: 0.4 Filter-group: 0.3  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 4, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_RU
  664 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 3954639, suppressed 0, withdrawn 1831686
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470209, Last synced ack version 0
  Outstanding version objects: current 2, max 120
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 3; dropped 2
  Local host: 87.250.234.14, Local port: 179, IF Handle: 0x00000000
  Foreign host: 95.108.237.255, Foreign port: 64433
  Last reset 18w0d, due to BGP Notification sent: hold time expired
  Time since last notification sent to neighbor: 18w0d
  Error Code: hold time expired
  Notification data sent:
    None

BGP neighbor is 141.8.136.128
 Remote AS 13238, local AS 13238, internal link
 Description: jansson
 Remote router ID 141.8.136.128
 Cluster ID 87.250.234.14
  BGP state = Established, up for 1d20h
  NSR State: None
  BFD enabled (session up): mininterval: 3000 multiplier: 3
  Last read 00:00:10, Last read before reset 1d20h
  Hold time is 90, keepalive interval is 30 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 179, written 179
  Second last write 00:00:00, attempted 258, written 258
  Last write before reset 1d20h, attempted 203, written 203
  Second last write before reset 1d20h, attempted 179, written 179
  Last write pulse rcvd  Aug 16 21:10:28.609 last full Aug 15 00:24:27.142 pulse count 7762319
  Last write pulse rcvd before reset 1d20h
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 1d20h, second last 1d20h
  Last KA expiry before reset 2d02h, second last 2d04h
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 1d20h, second last 1d20h
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Aug 15 00:24:19.762        4  Aug 15 00:24:19.778        4
    Notification:   ---                        0  Jan 24 00:13:26.843        1
    Update:         Aug 16 21:10:28.875 12074019  Aug 15 00:24:23.526      388
    Keepalive:      Aug 16 16:00:09.146   146024  Aug 16 21:10:18.617   835263
    Route_Refresh:  ---                        0  ---                        0
    Total:                              12220047                        835656
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.6 Filter-group: 0.2  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB
  12 accepted prefixes, 12 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 55783, suppressed 0, withdrawn 24930
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 33
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470210
  Update group: 0.6 Filter-group: 0.2  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB
  9 accepted prefixes, 9 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 153992, suppressed 0, withdrawn 68165
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470209, Last synced ack version 0
  Outstanding version objects: current 2, max 29
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 4; dropped 3
  Local host: 87.250.234.14, Local port: 54713, IF Handle: 0x00000000
  Foreign host: 141.8.136.128, Foreign port: 179
  Last reset 1d20h, due to BFD (Bidirectional forwarding detection) session down
  Time since last notification received from neighbor: 29w1d
  Error Code: peer unconfigured
  Notification data received:
    None

BGP neighbor is 141.8.136.129
 Remote AS 13238, local AS 13238, internal link
 Description: sibelius
 Remote router ID 141.8.136.129
 Cluster ID 87.250.234.14
  BGP state = Established, up for 4w6d
  NSR State: None
  BFD enabled (session up): mininterval: 3000 multiplier: 3
  Last read 00:00:28, Last read before reset 4w6d
  Hold time is 90, keepalive interval is 30 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 179, written 179
  Second last write 00:00:00, attempted 258, written 258
  Last write before reset 4w6d, attempted 183, written 183
  Second last write before reset 4w6d, attempted 19, written 19
  Last write pulse rcvd  Aug 16 21:10:28.606 last full Aug  2 11:02:05.189 pulse count 7787163
  Last write pulse rcvd before reset 4w6d
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 4w6d, second last 4w6d
  Last KA expiry before reset 4w6d, second last 4w6d
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 4w6d, second last 4w6d
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Jul 13 00:39:21.856       20  Jul 13 00:39:21.856       12
    Notification:   Jul 12 09:17:57.657        8  Jul 13 00:31:36.368        2
    Update:         Aug 16 21:10:28.875 12081333  Aug 16 20:14:27.475    43300
    Keepalive:      Aug 16 16:00:09.146   146032  Aug 16 21:10:00.548   832644
    Route_Refresh:  ---                        0  ---                        0
    Total:                              12227393                        875958
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.6 Filter-group: 0.2  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB
  785 accepted prefixes, 121 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 420493, suppressed 0, withdrawn 218322
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 21
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470210
  Update group: 0.6 Filter-group: 0.2  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB
  641 accepted prefixes, 148 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 1340199, suppressed 0, withdrawn 663129
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470209, Last synced ack version 0
  Outstanding version objects: current 2, max 19
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 12; dropped 11
  Local host: 87.250.234.14, Local port: 179, IF Handle: 0x00000000
  Foreign host: 141.8.136.129, Foreign port: 50617
  Last reset 4w6d, due to BFD (Bidirectional forwarding detection) session down
  Time since last notification sent to neighbor: 5w0d
  Error Code: hold time expired
  Notification data sent:
    None
  Time since last notification received from neighbor: 4w6d
  Error Code: peer unconfigured
  Notification data received:
    None

BGP neighbor is 141.8.136.191
 Remote AS 13238, local AS 13238, internal link
 Description: man1-d1
 Remote router ID 141.8.136.191
 Cluster ID 87.250.234.14
  BGP state = Established, up for 13w0d
  NSR State: None
  Last read 00:00:45, Last read before reset 13w0d
  Hold time is 180, keepalive interval is 60 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 179, written 179
  Second last write 00:00:00, attempted 258, written 258
  Last write before reset 13w0d, attempted 187, written 187
  Second last write before reset 13w0d, attempted 133, written 133
  Last write pulse rcvd  Aug 16 21:10:28.549 last full Aug  2 11:02:05.566 pulse count 8009179
  Last write pulse rcvd before reset 13w0d
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 13w0d, second last 13w0d
  Last KA expiry before reset 13w0d, second last 13w0d
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 13w0d, second last 13w0d
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           May 17 13:13:28.280        4  May 17 13:13:28.279        4
    Notification:   May 17 10:12:06.211        2  ---                        0
    Update:         Aug 16 21:10:28.875 12073049  Aug 16 21:00:55.090   898027
    Keepalive:      Aug 10 05:14:59.868    35981  Aug 16 21:09:43.211   339550
    Route_Refresh:  ---                        0  Jun 29 18:19:21.900        5
    Total:                              12109036                       1237586
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.5 Filter-group: 0.1  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 2, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_NXOS
  326 accepted prefixes, 95 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 1056292, suppressed 0, withdrawn 548320
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 186
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470210
  Update group: 0.5 Filter-group: 0.1  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 3, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_NXOS
  430 accepted prefixes, 125 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 3068732, suppressed 0, withdrawn 1457810
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470209, Last synced ack version 0
  Outstanding version objects: current 2, max 37
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 4; dropped 3
  Local host: 87.250.234.14, Local port: 179, IF Handle: 0x00000000
  Foreign host: 141.8.136.191, Foreign port: 51926
  Last reset 13w0d, due to BGP Notification sent: hold time expired
  Time since last notification sent to neighbor: 13w0d
  Error Code: hold time expired
  Notification data sent:
    None

BGP neighbor is 141.8.136.192
 Remote AS 13238, local AS 13238, internal link
 Description: man1-d2
 Remote router ID 141.8.136.192
 Cluster ID 87.250.234.14
  BGP state = Established, up for 22w0d
  NSR State: None
  Last read 00:00:01, Last read before reset 22w0d
  Hold time is 180, keepalive interval is 60 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 00:00:00, attempted 179, written 179
  Second last write 00:00:00, attempted 258, written 258
  Last write before reset 22w0d, attempted 25221, written 0
  Second last write before reset 22w0d, attempted 24650, written 0
  Last write pulse rcvd  Aug 16 21:10:28.922 last full Jul  4 18:04:17.982 pulse count 7546842
  Last write pulse rcvd before reset 22w0d
  Socket not armed for io, armed for read, armed for write
  Last write thread event before reset 22w0d, second last 22w0d
  Last KA expiry before reset 22w0d, second last 22w0d
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 22w0d, second last 22w0d
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability received
  Neighbor capabilities:            Adv         Rcvd
    Route refresh:                  Yes         Yes
    4-byte AS:                      Yes         Yes
    Address family IPv4 Unicast:    Yes         Yes
    Address family IPv6 Labeled-unicast:  Yes         Yes
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           Mar 15 15:19:49.691       12  Mar 15 15:19:49.902       10
    Notification:   Mar 15 14:24:24.313        3  Mar  6 23:24:18.462        3
    Update:         Aug 16 21:10:28.875 12052059  Aug 16 21:00:52.931   361851
    Keepalive:      Aug 10 05:14:59.868    36022  Aug 16 21:10:27.032   428242
    Route_Refresh:  ---                        0  Jun 29 18:20:15.376        9
    Total:                              12088096                        790115
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 3530286
  Update group: 0.5 Filter-group: 0.1  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 6, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_NXOS
  326 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 1631058, suppressed 0, withdrawn 819237
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 3530286, Last synced ack version 0
  Outstanding version objects: current 0, max 96
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 7470210
  Update group: 0.5 Filter-group: 0.1  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  AF-dependent capabilities:
    Additional-paths Send: advertised
    Additional-paths Receive: advertised and received
  Route refresh request: received 3, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB_NXOS
  430 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 4707004, suppressed 0, withdrawn 2199919
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 7470209, Last synced ack version 0
  Outstanding version objects: current 2, max 120
  Additional-paths operation: Send
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 10; dropped 9
  Local host: 87.250.234.14, Local port: 21810, IF Handle: 0x00000000
  Foreign host: 141.8.136.192, Foreign port: 179
  Last reset 22w0d, due to BGP Notification sent: hold time expired
  Time since last notification sent to neighbor: 22w0d
  Error Code: hold time expired
  Notification data sent:
    None
  Time since last notification received from neighbor: 23w1d
  Error Code: configuration change
  Notification data received:
    None

BGP neighbor is 141.8.136.241
 Remote AS 13238, local AS 13238, internal link
 Administratively shut down
 Description: man1-4d1
 Remote router ID 0.0.0.0
 Cluster ID 87.250.234.14
  BGP state = Idle (Neighbor is shutdown)
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:00, Last read before reset 00:00:00
  Hold time is 180, keepalive interval is 60 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 39w0d, attempted 21, written 0
  Second last write 00:00:00, attempted 0, written 0
  Last write before reset 00:00:00, attempted 0, written 0
  Second last write before reset 00:00:00, attempted 0, written 0
  Last write pulse rcvd  not set last full not set pulse count 0
  Last write pulse rcvd before reset 00:00:00
  Socket not armed for io, not armed for read, not armed for write
  Last write thread event before reset 00:00:00, second last 00:00:00
  Last KA expiry before reset 00:00:00, second last 00:00:00
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 00:00:00, second last 00:00:00
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability not received
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           ---                        0  ---                        0
    Notification:   ---                        0  ---                        0
    Update:         ---                        0  ---                        0
    Keepalive:      ---                        0  ---                        0
    Route_Refresh:  ---                        0  ---                        0
    Total:                                     0                             0
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 0
  Update group: 0.1 Filter-group: 0.0  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 0, suppressed 0, withdrawn 0
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 1, Last synced ack version 0
  Outstanding version objects: current 0, max 0
  Additional-paths operation: None
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 0
  Update group: 0.1 Filter-group: 0.0  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 0, suppressed 0, withdrawn 0
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 1, Last synced ack version 0
  Outstanding version objects: current 0, max 0
  Additional-paths operation: None
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 0; dropped 0
  Local host: 0.0.0.0, Local port: 0, IF Handle: 0x00000000
  Foreign host: 141.8.136.241, Foreign port: 0
  Last reset 39w0d, due to Admin. shutdown (CEASE notification sent - administrative shutdown)
  Time since last notification sent to neighbor: 39w0d
  Error Code: administrative shutdown
  Notification data sent:
    None

BGP neighbor is 141.8.136.242
 Remote AS 13238, local AS 13238, internal link
 Administratively shut down
 Description: man1-4d2
 Remote router ID 0.0.0.0
 Cluster ID 87.250.234.14
  BGP state = Idle (Neighbor is shutdown)
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:00, Last read before reset 00:00:00
  Hold time is 180, keepalive interval is 60 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 39w0d, attempted 21, written 0
  Second last write 00:00:00, attempted 0, written 0
  Last write before reset 00:00:00, attempted 0, written 0
  Second last write before reset 00:00:00, attempted 0, written 0
  Last write pulse rcvd  not set last full not set pulse count 0
  Last write pulse rcvd before reset 00:00:00
  Socket not armed for io, not armed for read, not armed for write
  Last write thread event before reset 00:00:00, second last 00:00:00
  Last KA expiry before reset 00:00:00, second last 00:00:00
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 00:00:00, second last 00:00:00
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability not received
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           ---                        0  ---                        0
    Notification:   ---                        0  ---                        0
    Update:         ---                        0  ---                        0
    Keepalive:      ---                        0  ---                        0
    Route_Refresh:  ---                        0  ---                        0
    Total:                                     0                             0
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 0
  Update group: 0.1 Filter-group: 0.0  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 0, suppressed 0, withdrawn 0
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 1, Last synced ack version 0
  Outstanding version objects: current 0, max 0
  Additional-paths operation: None
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 0
  Update group: 0.1 Filter-group: 0.0  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 0, suppressed 0, withdrawn 0
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 1, Last synced ack version 0
  Outstanding version objects: current 0, max 0
  Additional-paths operation: None
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 0; dropped 0
  Local host: 0.0.0.0, Local port: 0, IF Handle: 0x00000000
  Foreign host: 141.8.136.242, Foreign port: 0
  Last reset 39w0d, due to Admin. shutdown (CEASE notification sent - administrative shutdown)
  Time since last notification sent to neighbor: 39w0d
  Error Code: administrative shutdown
  Notification data sent:
    None

BGP neighbor is 141.8.136.243
 Remote AS 13238, local AS 13238, internal link
 Administratively shut down
 Description: man1-4d3
 Remote router ID 0.0.0.0
 Cluster ID 87.250.234.14
  BGP state = Idle (Neighbor is shutdown)
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:00, Last read before reset 00:00:00
  Hold time is 180, keepalive interval is 60 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 39w0d, attempted 21, written 0
  Second last write 00:00:00, attempted 0, written 0
  Last write before reset 00:00:00, attempted 0, written 0
  Second last write before reset 00:00:00, attempted 0, written 0
  Last write pulse rcvd  not set last full not set pulse count 0
  Last write pulse rcvd before reset 00:00:00
  Socket not armed for io, not armed for read, not armed for write
  Last write thread event before reset 00:00:00, second last 00:00:00
  Last KA expiry before reset 00:00:00, second last 00:00:00
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 00:00:00, second last 00:00:00
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability not received
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           ---                        0  ---                        0
    Notification:   ---                        0  ---                        0
    Update:         ---                        0  ---                        0
    Keepalive:      ---                        0  ---                        0
    Route_Refresh:  ---                        0  ---                        0
    Total:                                     0                             0
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 0
  Update group: 0.1 Filter-group: 0.0  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 0, suppressed 0, withdrawn 0
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 1, Last synced ack version 0
  Outstanding version objects: current 0, max 0
  Additional-paths operation: None
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 0
  Update group: 0.1 Filter-group: 0.0  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 0, suppressed 0, withdrawn 0
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 1, Last synced ack version 0
  Outstanding version objects: current 0, max 0
  Additional-paths operation: None
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 0; dropped 0
  Local host: 0.0.0.0, Local port: 0, IF Handle: 0x00000000
  Foreign host: 141.8.136.243, Foreign port: 0
  Last reset 39w0d, due to Admin. shutdown (CEASE notification sent - administrative shutdown)
  Time since last notification sent to neighbor: 39w0d
  Error Code: administrative shutdown
  Notification data sent:
    None

BGP neighbor is 141.8.136.244
 Remote AS 13238, local AS 13238, internal link
 Administratively shut down
 Description: man1-4d4
 Remote router ID 0.0.0.0
 Cluster ID 87.250.234.14
  BGP state = Idle (Neighbor is shutdown)
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:00, Last read before reset 00:00:00
  Hold time is 180, keepalive interval is 60 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 39w0d, attempted 21, written 0
  Second last write 00:00:00, attempted 0, written 0
  Last write before reset 00:00:00, attempted 0, written 0
  Second last write before reset 00:00:00, attempted 0, written 0
  Last write pulse rcvd  not set last full not set pulse count 0
  Last write pulse rcvd before reset 00:00:00
  Socket not armed for io, not armed for read, not armed for write
  Last write thread event before reset 00:00:00, second last 00:00:00
  Last KA expiry before reset 00:00:00, second last 00:00:00
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 00:00:00, second last 00:00:00
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability not received
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           ---                        0  ---                        0
    Notification:   ---                        0  ---                        0
    Update:         ---                        0  ---                        0
    Keepalive:      ---                        0  ---                        0
    Route_Refresh:  ---                        0  ---                        0
    Total:                                     0                             0
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 0
  Update group: 0.1 Filter-group: 0.0  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 0, suppressed 0, withdrawn 0
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 1, Last synced ack version 0
  Outstanding version objects: current 0, max 0
  Additional-paths operation: None
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 0
  Update group: 0.1 Filter-group: 0.0  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 0, suppressed 0, withdrawn 0
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 1, Last synced ack version 0
  Outstanding version objects: current 0, max 0
  Additional-paths operation: None
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 0; dropped 0
  Local host: 0.0.0.0, Local port: 0, IF Handle: 0x00000000
  Foreign host: 141.8.136.244, Foreign port: 0
  Last reset 39w0d, due to Admin. shutdown (CEASE notification sent - administrative shutdown)
  Time since last notification sent to neighbor: 39w0d
  Error Code: administrative shutdown
  Notification data sent:
    None

BGP neighbor is 141.8.136.245
 Remote AS 13238, local AS 13238, internal link
 Administratively shut down
 Description: man1-5d1
 Remote router ID 0.0.0.0
 Cluster ID 87.250.234.14
  BGP state = Idle (Neighbor is shutdown)
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:00, Last read before reset 00:00:00
  Hold time is 180, keepalive interval is 60 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 39w0d, attempted 21, written 0
  Second last write 00:00:00, attempted 0, written 0
  Last write before reset 00:00:00, attempted 0, written 0
  Second last write before reset 00:00:00, attempted 0, written 0
  Last write pulse rcvd  not set last full not set pulse count 0
  Last write pulse rcvd before reset 00:00:00
  Socket not armed for io, not armed for read, not armed for write
  Last write thread event before reset 00:00:00, second last 00:00:00
  Last KA expiry before reset 00:00:00, second last 00:00:00
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 00:00:00, second last 00:00:00
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability not received
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           ---                        0  ---                        0
    Notification:   ---                        0  ---                        0
    Update:         ---                        0  ---                        0
    Keepalive:      ---                        0  ---                        0
    Route_Refresh:  ---                        0  ---                        0
    Total:                                     0                             0
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 0
  Update group: 0.1 Filter-group: 0.0  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 0, suppressed 0, withdrawn 0
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 1, Last synced ack version 0
  Outstanding version objects: current 0, max 0
  Additional-paths operation: None
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 0
  Update group: 0.1 Filter-group: 0.0  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 0, suppressed 0, withdrawn 0
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 1, Last synced ack version 0
  Outstanding version objects: current 0, max 0
  Additional-paths operation: None
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 0; dropped 0
  Local host: 0.0.0.0, Local port: 0, IF Handle: 0x00000000
  Foreign host: 141.8.136.245, Foreign port: 0
  Last reset 39w0d, due to Admin. shutdown (CEASE notification sent - administrative shutdown)
  Time since last notification sent to neighbor: 39w0d
  Error Code: administrative shutdown
  Notification data sent:
    None

BGP neighbor is 141.8.136.246
 Remote AS 13238, local AS 13238, internal link
 Administratively shut down
 Description: man1-5d2
 Remote router ID 0.0.0.0
 Cluster ID 87.250.234.14
  BGP state = Idle (Neighbor is shutdown)
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:00, Last read before reset 00:00:00
  Hold time is 180, keepalive interval is 60 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 39w0d, attempted 21, written 0
  Second last write 00:00:00, attempted 0, written 0
  Last write before reset 00:00:00, attempted 0, written 0
  Second last write before reset 00:00:00, attempted 0, written 0
  Last write pulse rcvd  not set last full not set pulse count 0
  Last write pulse rcvd before reset 00:00:00
  Socket not armed for io, not armed for read, not armed for write
  Last write thread event before reset 00:00:00, second last 00:00:00
  Last KA expiry before reset 00:00:00, second last 00:00:00
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 00:00:00, second last 00:00:00
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability not received
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           ---                        0  ---                        0
    Notification:   ---                        0  ---                        0
    Update:         ---                        0  ---                        0
    Keepalive:      ---                        0  ---                        0
    Route_Refresh:  ---                        0  ---                        0
    Total:                                     0                             0
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 0
  Update group: 0.1 Filter-group: 0.0  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 0, suppressed 0, withdrawn 0
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 1, Last synced ack version 0
  Outstanding version objects: current 0, max 0
  Additional-paths operation: None
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 0
  Update group: 0.1 Filter-group: 0.0  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 0, suppressed 0, withdrawn 0
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 1, Last synced ack version 0
  Outstanding version objects: current 0, max 0
  Additional-paths operation: None
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 0; dropped 0
  Local host: 0.0.0.0, Local port: 0, IF Handle: 0x00000000
  Foreign host: 141.8.136.246, Foreign port: 0
  Last reset 39w0d, due to Admin. shutdown (CEASE notification sent - administrative shutdown)
  Time since last notification sent to neighbor: 39w0d
  Error Code: administrative shutdown
  Notification data sent:
    None

BGP neighbor is 141.8.136.247
 Remote AS 13238, local AS 13238, internal link
 Administratively shut down
 Description: man1-5d3
 Remote router ID 0.0.0.0
 Cluster ID 87.250.234.14
  BGP state = Idle (Neighbor is shutdown)
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:00, Last read before reset 00:00:00
  Hold time is 180, keepalive interval is 60 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 39w0d, attempted 21, written 0
  Second last write 00:00:00, attempted 0, written 0
  Last write before reset 00:00:00, attempted 0, written 0
  Second last write before reset 00:00:00, attempted 0, written 0
  Last write pulse rcvd  not set last full not set pulse count 0
  Last write pulse rcvd before reset 00:00:00
  Socket not armed for io, not armed for read, not armed for write
  Last write thread event before reset 00:00:00, second last 00:00:00
  Last KA expiry before reset 00:00:00, second last 00:00:00
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 00:00:00, second last 00:00:00
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability not received
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           ---                        0  ---                        0
    Notification:   ---                        0  ---                        0
    Update:         ---                        0  ---                        0
    Keepalive:      ---                        0  ---                        0
    Route_Refresh:  ---                        0  ---                        0
    Total:                                     0                             0
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 0
  Update group: 0.1 Filter-group: 0.0  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 0, suppressed 0, withdrawn 0
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 1, Last synced ack version 0
  Outstanding version objects: current 0, max 0
  Additional-paths operation: None
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 0
  Update group: 0.1 Filter-group: 0.0  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 0, suppressed 0, withdrawn 0
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 1, Last synced ack version 0
  Outstanding version objects: current 0, max 0
  Additional-paths operation: None
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 0; dropped 0
  Local host: 0.0.0.0, Local port: 0, IF Handle: 0x00000000
  Foreign host: 141.8.136.247, Foreign port: 0
  Last reset 39w0d, due to Admin. shutdown (CEASE notification sent - administrative shutdown)
  Time since last notification sent to neighbor: 39w0d
  Error Code: administrative shutdown
  Notification data sent:
    None

BGP neighbor is 141.8.136.248
 Remote AS 13238, local AS 13238, internal link
 Administratively shut down
 Description: man1-5d4
 Remote router ID 0.0.0.0
 Cluster ID 87.250.234.14
  BGP state = Idle (Neighbor is shutdown)
  NSR State: None
  BFD enabled (initializing)
  Last read 00:00:00, Last read before reset 00:00:00
  Hold time is 180, keepalive interval is 60 seconds
  Configured hold time: 180, keepalive: 60, min acceptable hold time: 3
  Last write 39w0d, attempted 21, written 0
  Second last write 00:00:00, attempted 0, written 0
  Last write before reset 00:00:00, attempted 0, written 0
  Second last write before reset 00:00:00, attempted 0, written 0
  Last write pulse rcvd  not set last full not set pulse count 0
  Last write pulse rcvd before reset 00:00:00
  Socket not armed for io, not armed for read, not armed for write
  Last write thread event before reset 00:00:00, second last 00:00:00
  Last KA expiry before reset 00:00:00, second last 00:00:00
  Last KA error before reset 00:00:00, KA not sent 00:00:00
  Last KA start before reset 00:00:00, second last 00:00:00
  Precedence: internet
  Non-stop routing is enabled
  Entered Neighbor NSR TCP mode:
    TCP Initial Sync :              ---               
    TCP Initial Sync Phase Two :    ---               
    TCP Initial Sync Done :         ---               
  Multi-protocol capability not received
  Message stats:
    InQ depth: 0, OutQ depth: 0
                    Last_Sent               Sent  Last_Rcvd               Rcvd
    Open:           ---                        0  ---                        0
    Notification:   ---                        0  ---                        0
    Update:         ---                        0  ---                        0
    Keepalive:      ---                        0  ---                        0
    Route_Refresh:  ---                        0  ---                        0
    Total:                                     0                             0
  Minimum time between advertisement runs is 0 secs
  Inbound message logging enabled, 3 messages buffered
  Outbound message logging enabled, 3 messages buffered

 For Address Family: IPv4 Unicast
  BGP neighbor version 0
  Update group: 0.1 Filter-group: 0.0  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 0, suppressed 0, withdrawn 0
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 1, Last synced ack version 0
  Outstanding version objects: current 0, max 0
  Additional-paths operation: None
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with Local with stitching-RT option
  Advertise VPNv6 routes is enabled with Reoriginate,Local with stitching-RT option

 For Address Family: IPv6 Labeled-unicast
  BGP neighbor version 0
  Update group: 0.1 Filter-group: 0.0  No Refresh request being processed
  Route-Reflector Client
  Inbound soft reconfiguration allowed (override route-refresh)
  Route refresh request: received 0, sent 0
  Policy for incoming advertisements is IMPORT_SLB
  Policy for outgoing advertisements is EXPORT_SLB
  0 accepted prefixes, 0 are bestpaths
  Cumulative no. of prefixes denied: 0.
  Prefix advertised 0, suppressed 0, withdrawn 0
  Maximum prefixes allowed 5000
  Threshold for warning message 75%, restart interval 0 min
  AIGP is enabled
  An EoR was not received during read-only mode
  Last ack version 1, Last synced ack version 0
  Outstanding version objects: current 0, max 0
  Additional-paths operation: None
  Send Multicast Attributes
  Advertise VPNv4 routes enabled with  option
  Advertise VPNv6 routes is enabled with defaultReoriginate, option

  Connections established 0; dropped 0
  Local host: 0.0.0.0, Local port: 0, IF Handle: 0x00000000
  Foreign host: 141.8.136.248, Foreign port: 0
  Last reset 39w0d, due to Admin. shutdown (CEASE notification sent - administrative shutdown)
  Time since last notification sent to neighbor: 39w0d
  Error Code: administrative shutdown
  Notification data sent:
    None
"""