from data.lib import Data


class Data1(Data):
    content = """
IPv6 Address                 Linklayer Address  State       Exp Rtr Secure Interface
fe80::e10:d1                 f0:2f:a7:38:29:92  reachable   15  yes no      et-2/0/16.3000
fe80::e11:d1                 9c:7d:a3:83:95:d2  reachable   37  yes no      et-2/0/15.3000
fe80::e12:d1                 f0:2f:a7:38:2a:72  reachable   22  yes no      et-2/0/14.3000
fe80::e13:d1                 9c:7d:a3:83:96:72  reachable   36  yes no      et-2/0/13.3000
fe80::e14:d1                 9c:7d:a3:83:96:c2  reachable   14  yes no      et-2/0/12.3000
fe80::e15:d1                 f0:2f:a7:38:28:72  reachable   17  yes no      et-4/0/17.3000
fe80::e16:d1                 f0:2f:a7:38:28:32  delay       4   yes no      et-4/0/16.3000
fe80::e17:d1                 9c:7d:a3:83:97:32  reachable   30  yes no      et-4/0/15.3000
fe80::e18:d1                 f0:2f:a7:38:29:c2  reachable   12  yes no      et-4/0/14.3000
fe80::e19:d1                 f0:2f:a7:38:2c:f2  reachable   17  yes no      et-8/0/10.3000
fe80::e20:d1                 f0:2f:a7:38:2b:82  reachable   14  yes no      et-8/0/9.3000
fe80::e21:d1                 f0:2f:a7:38:29:d2  reachable   13  yes no      et-8/0/7.3000
fe80::e22:d1                 9c:7d:a3:83:97:42  reachable   7   yes no      et-8/0/6.3000
fe80::e23:d1                 f0:2f:a7:38:2b:62  delay       2   yes no      et-10/0/11.3000
fe80::e24:d1                 9c:7d:a3:83:96:22  reachable   28  yes no      et-10/0/10.3000
fe80::e25:d1                 9c:7d:a3:83:95:f2  delay       4   yes no      et-8/0/8.3000
fe80::e26:d1                 f0:2f:a7:38:2b:92  reachable   14  yes no      et-8/0/21.3000
fe80::e27:d1                 f0:2f:a7:38:2a:f2  reachable   36  yes no      et-8/0/20.3000
fe80::e28:d1                 f0:2f:a7:38:2a:d2  reachable   6   yes no      et-8/0/19.3000
fe80::e30:d1                 9c:7d:a3:83:96:a2  reachable   14  yes no      et-9/0/11.3000
fe80::e31:d1                 f0:2f:a7:38:28:22  reachable   17  yes no      et-9/0/10.3000
fe80::e32:d1                 9c:7d:a3:83:98:42  reachable   18  yes no      et-9/0/9.3000
fe80::e33:d1                 f0:2f:a7:38:2a:b2  reachable   24  yes no      et-9/0/8.3000
fe80::e34:d1                 f0:2f:a7:38:2a:e2  reachable   13  yes no      et-9/0/6.3000
fe80::e36:d1                 f0:2f:a7:38:2b:a2  reachable   34  yes no      et-9/0/4.3000
fe80::e37:d1                 9c:7d:a3:83:97:a2  reachable   19  yes no      et-10/0/9.3000
fe80::e38:d1                 9c:7d:a3:83:97:d2  reachable   14  yes no      et-10/0/8.3000
fe80::e39:d1                 9c:7d:a3:83:98:02  reachable   19  yes no      et-10/0/7.3000
fe80::e40:d1                 f0:2f:a7:38:2c:82  reachable   22  yes no      et-10/0/26.3000
fe80::e41:d1                 9c:7d:a3:83:96:42  reachable   27  yes no      et-10/0/25.3000
fe80::e44:d1                 9c:7d:a3:83:97:22  reachable   28  yes no      et-10/0/22.3000
fe80::e45:d1                 9c:7d:a3:83:96:b2  reachable   5   yes no      et-10/0/21.3000
fe80::e46:d1                 f0:2f:a7:38:2a:92  reachable   4   yes no      et-10/0/18.3000
fe80::e47:d1                 f0:2f:a7:38:2d:02  reachable   16  yes no      et-11/0/10.3000
fe80::e48:d1                 f0:2f:a7:38:28:e2  reachable   11  yes no      et-11/0/8.3000
fe80::e49:d1                 f0:2f:a7:38:29:02  reachable   35  yes no      et-11/0/9.3000
fe80::e50:d1                 9c:7d:a3:83:98:12  delay       1   yes no      et-11/0/21.3000
fe80::e51:d1                 9c:7d:a3:83:96:f2  reachable   26  yes no      et-12/0/2.3000
fe80::e52:d1                 9c:7d:a3:83:94:d2  reachable   31  yes no      et-12/0/27.3000
fe80::e53:d1                 9c:7d:a3:83:97:b2  reachable   13  yes no      et-11/0/20.3000
fe80::e54:d1                 9c:7d:a3:83:96:d2  reachable   19  yes no      et-12/0/26.3000
fe80::e55:d1                 f0:2f:a7:38:28:82  reachable   18  yes no      et-12/0/25.3000
fe80::e56:d1                 9c:7d:a3:83:94:c2  reachable   6   yes no      et-12/0/23.3000
fe80::e57:d1                 f0:2f:a7:38:29:f2  reachable   34  yes no      et-12/0/22.3000
fe80::e58:d1                 f0:2f:a7:38:28:02  reachable   31  yes no      et-12/0/20.3000
fe80::e59:d1                 f0:2f:a7:38:2c:b2  reachable   21  yes no      et-12/0/19.3000
fe80::e60:d1                 9c:7d:a3:83:97:72  reachable   8   yes no      et-11/0/19.3000
fe80::e61:d1                 f0:2f:a7:38:2c:32  reachable   43  yes no      et-12/0/18.3000
fe80::e62:d1                 f0:2f:a7:38:28:52  reachable   15  yes no      et-3/0/13.3000
fe80::e63:d1                 9c:7d:a3:83:98:52  reachable   14  yes no      et-2/0/17.3000
fe80::e64:d1                 9c:7d:a3:83:98:22  reachable   33  yes no      et-10/0/6.3000
fe80::e65:d1                 f0:2f:a7:38:2c:12  reachable   16  yes no      et-10/0/5.3000
fe80::e66:d1                 f0:2f:a7:38:2c:52  reachable   11  yes no      et-4/0/13.3000
fe80::e67:d1                 f0:2f:a7:38:28:d2  reachable   22  yes no      et-4/0/12.3000
fe80::e68:d1                 f0:2f:a7:38:2c:a2  reachable   26  yes no      et-10/0/4.3000
fe80::e69:d1                 9c:7d:a3:83:97:62  reachable   31  yes no      et-8/0/5.3000
fe80::e70:d1                 f0:2f:a7:38:2c:d2  reachable   28  yes no      et-12/0/10.3000
fe80::e71:d1                 f0:2f:a7:38:27:f2  reachable   5   yes no      et-12/0/9.3000
fe80::e72:d1                 9c:7d:a3:83:96:82  reachable   3   yes no      et-8/0/4.3000
fe80::e73:d1                 9c:7d:a3:83:95:72  reachable   28  yes no      et-12/0/8.3000
fe80::e74:d1                 9c:7d:a3:83:97:e2  reachable   7   yes no      et-8/0/3.3000
fe80::e77:d1                 9c:7d:a3:83:95:c2  delay       1   yes no      et-8/0/23.3000
fe80::e78:d1                 9c:7d:a3:83:97:82  reachable   1   yes no      et-6/0/12.3000
fe80::e79:d1                 9c:7d:a3:83:96:32  reachable   16  yes no      et-6/0/13.3000
fe80::e80:d1                 9c:7d:a3:83:96:52  reachable   12  yes no      et-6/0/14.3000
fe80::e81:d1                 9c:7d:a3:83:96:12  reachable   17  yes no      et-6/0/16.3000
fe80::e82:d1                 9c:7d:a3:83:95:82  reachable   12  yes no      et-6/0/17.3000
fe80::e83:d1                 9c:7d:a3:83:94:b2  reachable   12  yes no      et-7/0/12.3000
fe80::e84:d1                 9c:7d:a3:83:95:b2  reachable   13  yes no      et-7/0/13.3000
fe80::e85:d1                 f0:2f:a7:38:2d:12  reachable   11  yes no      et-7/0/14.3000
fe80::e86:d1                 f0:2f:a7:38:2c:e2  reachable   13  yes no      et-7/0/15.3000
fe80::e87:d1                 f0:2f:a7:38:2c:72  reachable   9   yes no      et-7/0/16.3000
fe80::e88:d1                 f0:2f:a7:38:28:b2  reachable   27  yes no      et-7/0/17.3000
fe80::e89:d1                 9c:7d:a3:83:97:f2  reachable   5   yes no      et-5/0/13.3000
fe80::e90:d1                 f0:2f:a7:38:2a:32  reachable   33  yes no      et-5/0/14.3000
fe80::e91:d1                 f0:2f:a7:38:2c:42  reachable   11  yes no      et-5/0/15.3000
fe80::e93:d1                 48:7b:6b:3e:8b:82  reachable   13  yes no      et-11/0/29.3000
fe80::e96:d1                 f0:2f:a7:38:27:a2  reachable   38  yes no      et-12/0/5.3000
fe80::e99:d1                 f0:2f:a7:38:2b:f2  reachable   5   yes no      et-8/0/16.3000
fe80::ea1:d1                 68:cc:6e:a8:b8:71  reachable   5   yes no      ae101.3000 
fe80::ea1:d1                 68:cc:6e:a8:b8:71  reachable   10  yes no      ae101.3666 
fe80::ea2:d1                 2c:21:31:18:0f:00  reachable   21  no  no      ae102.3000 
fe80::ea2:d1                 2c:21:31:18:0f:00  stale       1193 no no      ae102.3666 
fe80::e101:d1                f0:2f:a7:38:29:52  reachable   23  yes no      et-9/0/19.3000
fe80::e102:d1                f0:2f:a7:38:28:62  reachable   26  yes no      et-9/0/20.3000
fe80::e103:d1                f0:2f:a7:38:2b:52  reachable   27  yes no      et-9/0/22.3000
fe80::e104:d1                f0:2f:a7:38:29:62  reachable   18  yes no      et-9/0/23.3000
fe80::e106:d1                f0:2f:a7:38:2b:12  reachable   3   yes no      et-9/0/27.3000
fe80::e109:d1                f0:2f:a7:38:2a:62  reachable   37  yes no      et-8/0/14.3000
fe80::e110:d1                9c:7d:a3:83:95:42  reachable   21  yes no      et-11/0/22.3000
fe80::e111:d1                f0:2f:a7:38:2a:12  reachable   4   yes no      et-12/0/1.3000
fe80::e112:d1                f0:2f:a7:38:2c:92  reachable   23  yes no      et-12/0/0.3000
fe80::e113:d1                f0:2f:a7:38:29:b2  reachable   16  yes no      et-12/0/29.3000
fe80::e114:d1                f0:2f:a7:38:2b:c2  reachable   36  yes no      et-12/0/28.3000
fe80::e115:d1                9c:7d:a3:83:96:02  reachable   27  yes no      et-0/0/16.3000
fe80::e116:d1                f0:2f:a7:38:2b:e2  reachable   20  yes no      et-0/0/15.3000
fe80::e117:d1                f0:2f:a7:38:2a:42  reachable   18  yes no      et-0/0/14.3000
fe80::e118:d1                f0:2f:a7:38:27:82  reachable   7   yes no      et-11/0/4.3000
fe80::e119:d1                f0:2f:a7:38:29:82  reachable   30  yes no      et-11/0/5.3000
fe80::e120:d1                f0:2f:a7:38:28:92  reachable   21  yes no      et-11/0/6.3000
fe80::e121:d1                9c:7d:a3:83:98:62  reachable   24  yes no      et-9/0/0.3000
fe80::e122:d1                f0:2f:a7:38:2b:b2  reachable   15  yes no      et-9/0/1.3000
fe80::e124:d1                9c:7d:a3:83:94:f2  delay       3   yes no      et-11/0/23.3000
fe80::e125:d1                9c:7d:a3:83:95:02  reachable   14  yes no      et-11/0/24.3000
fe80::e126:d1                9c:7d:a3:83:97:c2  reachable   18  yes no      et-11/0/26.3000
fe80::e127:d1                f0:2f:a7:38:28:f2  reachable   10  yes no      et-11/0/27.3000
fe80::e128:d1                f0:2f:a7:38:28:42  reachable   25  yes no      et-11/0/28.3000
fe80::e129:d1                f0:2f:a7:38:2b:22  reachable   8   yes no      et-11/0/0.3000
fe80::e131:d1                f0:2f:a7:38:28:12  reachable   18  yes no      et-11/0/2.3000
fe80::e132:d1                9c:7d:a3:83:95:92  reachable   11  yes no      et-3/0/14.3000
fe80::e133:d1                f0:2f:a7:38:28:c2  reachable   29  yes no      et-3/0/15.3000
fe80::e134:d1                f0:2f:a7:38:2b:42  reachable   9   yes no      et-3/0/16.3000
fe80::e136:d1                9c:7d:a3:83:95:e2  reachable   9   yes no      et-1/0/13.3000
fe80::e138:d1                f0:2f:a7:38:29:12  reachable   23  yes no      et-1/0/16.3000
fe80::e139:d1                f0:2f:a7:38:2c:c2  reachable   2   yes no      et-1/0/17.3000
fe80::e140:d1                f0:2f:a7:38:27:c2  reachable   21  yes no      et-0/0/12.3000
fe80::e141:d1                9c:7d:a3:83:95:22  reachable   29  yes no      et-12/0/21.3000
fe80::e142:d1                9c:7d:a3:83:95:32  reachable   40  yes no      et-11/0/11.3000
fe80::e143:d1                9c:7d:a3:83:95:52  reachable   24  yes no      et-10/0/27.3000
fe80::e144:d1                f0:2f:a7:38:27:d2  stale       1200 yes no     et-10/0/28.3000
fe80::e145:d1                18:de:d7:a6:78:12  reachable   4   yes no      et-10/0/29.3000
fe80::e146:d1                88:3f:d3:2b:6a:02  reachable   25  yes no      et-10/0/0.3000
fe80::e147:d1                88:3f:d3:2b:6c:72  reachable   33  yes no      et-10/0/1.3000
fe80::e148:d1                88:3f:d3:2b:6a:e2  reachable   16  yes no      et-10/0/2.3000
fe80::e149:d1                88:3f:d3:2b:6c:52  reachable   33  yes no      et-10/0/3.3000
fe80::e150:d1                48:7b:6b:3e:8b:92  reachable   2   yes no      et-11/0/18.3000
fe80::e151:d1                f0:2f:a7:38:2c:22  reachable   21  yes no      et-8/0/12.3000
fe80::e152:d1                9c:7d:a3:83:94:e2  reachable   16  yes no      et-9/0/17.3000
fe80::e153:d1                9c:7d:a3:83:95:12  reachable   33  yes no      et-9/0/16.3000
fe80::e155:d1                f0:2f:a7:38:29:22  reachable   35  yes no      et-9/0/13.3000
fe80::e156:d1                f0:2f:a7:38:27:b2  reachable   24  yes no      et-9/0/26.3000
fe80::e157:d1                88:3f:d3:2b:6b:22  reachable   7   yes no      et-8/0/27.3000
fe80::e158:d1                88:3f:d3:2b:6b:12  reachable   20  yes no      et-8/0/28.3000
fe80::e159:d1                88:3f:d3:2b:6b:62  reachable   12  yes no      et-8/0/29.3000
fe80::e160:d1                88:3f:d3:2b:6b:f2  reachable   16  yes no      et-8/0/0.3000
fe80::e161:d1                48:7b:6b:3e:8b:72  reachable   14  yes no      et-8/0/1.3000
fe80::e162:d1                9c:7d:a3:83:95:a2  reachable   17  yes no      et-8/0/2.3000
fe80::e163:d1                bc:62:0e:4c:21:92  reachable   25  yes no      et-1/0/15.3000
fe80::e164:d1                9c:7d:a3:83:96:92  reachable   15  yes no      et-9/0/12.3000
fe80::e165:d1                f0:2f:a7:38:29:32  reachable   34  yes no      et-11/0/16.3000
fe80::e166:d1                f0:2f:a7:38:2a:02  reachable   8   yes no      et-11/0/15.3000
fe80::e167:d1                f0:2f:a7:38:2a:52  reachable   12  yes no      et-11/0/14.3000
fe80::e168:d1                48:7b:6b:3e:8b:a2  reachable   25  yes no      et-12/0/11.3000
fe80::e169:d1                9c:7d:a3:83:97:02  reachable   22  yes no      et-3/0/12.3000
fe80::e170:d1                2c:9d:1e:0a:69:02  reachable   3   yes no      et-8/0/11.3000
fe80::e171:d1                88:3f:d3:2b:6a:42  reachable   2   yes no      et-12/0/24.3000
fe80::e173:d1                88:3f:d3:2b:6c:02  reachable   15  yes no      et-10/0/20.3000
fe80::e200:d1                ec:0d:9a:fb:83:10  reachable   1   yes no      et-9/0/28.3000
fe80::e201:d1                ec:0d:9a:fb:7a:90  reachable   8   yes no      et-9/0/5.3000
fe80::e202:d1                ec:0d:9a:fb:7d:10  reachable   24  yes no      et-9/0/2.3000
fe80::e203:d1                ec:0d:9a:fb:7d:90  reachable   31  yes no      et-9/0/24.3000
fe80::e204:d1                ec:0d:9a:fb:76:90  reachable   21  yes no      et-9/0/18.3000
fe80::ee0d:9aff:fefb:8310    ec:0d:9a:fb:83:10  stale       1167 yes no     et-9/0/28.3000

{master}
    """
    cmd = "show ipv6 neighbors"
    host = "vla1-1d1"
    version = """
Hostname: vla1-1d1
Model: qfx10016
Junos: 15.1X53-D67.5
JUNOS OS Kernel 64-bit  [20171218.adb25b3_builder_stable_10]
JUNOS OS libs [20171218.adb25b3_builder_stable_10]
JUNOS OS runtime [20171218.adb25b3_builder_stable_10]
JUNOS OS time zone information [20171218.adb25b3_builder_stable_10]
JUNOS OS libs compat32 [20171218.adb25b3_builder_stable_10]
JUNOS OS 32-bit compatibility [20171218.adb25b3_builder_stable_10]
JUNOS py extensions [20180619.213418_builder_junos_151_x53_d67]
JUNOS py base [20180619.213418_builder_junos_151_x53_d67]
JUNOS OS vmguest [20171218.adb25b3_builder_stable_10]
JUNOS OS crypto [20171218.adb25b3_builder_stable_10]
JUNOS network stack and utilities [20180619.213418_builder_junos_151_x53_d67]
JUNOS libs compat32 [20180619.213418_builder_junos_151_x53_d67]
JUNOS runtime [20180619.213418_builder_junos_151_x53_d67]
JUNOS qfx runtime [20180619.213418_builder_junos_151_x53_d67]
JUNOS qfx platform support [20180619.213418_builder_junos_151_x53_d67]
JUNOS modules [20180619.213418_builder_junos_151_x53_d67]
JUNOS qfx modules [20180619.213418_builder_junos_151_x53_d67]
JUNOS libs [20180619.213418_builder_junos_151_x53_d67]
JUNOS Data Plane Crypto Support [20180619.213418_builder_junos_151_x53_d67]
JUNOS daemons [20180619.213418_builder_junos_151_x53_d67]
JUNOS qfx daemons [20180619.213418_builder_junos_151_x53_d67]
JUNOS Voice Services Container package [20180619.213418_builder_junos_151_x53_d67]
JUNOS Services SSL [20180619.213418_builder_junos_151_x53_d67]
JUNOS Services Stateful Firewall [20180619.213418_builder_junos_151_x53_d67]
JUNOS Services RPM [20180619.213418_builder_junos_151_x53_d67]
JUNOS Services PTSP Container package [20180619.213418_builder_junos_151_x53_d67]
JUNOS Services NAT [20180619.213418_builder_junos_151_x53_d67]
JUNOS Services Mobile Subscriber Service Container package [20180619.213418_builder_junos_151_x53_d67]
JUNOS Services MobileNext Software package [20180619.213418_builder_junos_151_x53_d67]
JUNOS Services LL-PDF Container package [20180619.213418_builder_junos_151_x53_d67]
JUNOS Services Jflow Container package [20180619.213418_builder_junos_151_x53_d67]
JUNOS Services IPSec [20180619.213418_builder_junos_151_x53_d67]
JUNOS IDP Services [20180619.213418_builder_junos_151_x53_d67]
JUNOS Services HTTP Content Management package [20180619.213418_builder_junos_151_x53_d67]
JUNOS Services Crypto [20180619.213418_builder_junos_151_x53_d67]
JUNOS Services Captive Portal and Content Delivery Container package [20180619.213418_builder_junos_151_x53_d67]
JUNOS Border Gateway Function package [20180619.213418_builder_junos_151_x53_d67]
JUNOS AppId Services [20180619.213418_builder_junos_151_x53_d67]
JUNOS Services Application Level Gateways [20180619.213418_builder_junos_151_x53_d67]
JUNOS Services AACL Container package [20180619.213418_builder_junos_151_x53_d67]
JUNOS SDN Software Suite [20180619.213418_builder_junos_151_x53_d67]
JUNOS Packet Forwarding Engine Support (DC-PFE) [20180619.213418_builder_junos_151_x53_d67]
JUNOS Packet Forwarding Engine Support (M/T Common) [20180619.213418_builder_junos_151_x53_d67]
JUNOS Online Documentation [20180619.213418_builder_junos_151_x53_d67]
JUNOS FIPS mode utilities [20180619.213418_builder_junos_151_x53_d67]
JUNOS Host Software [3.14.52-rt50-WR7.0.0.9_ovp:3.0.2]
JUNOS Host qfx-10-m platform package [15.1X53-D67.5]
JUNOS Host qfx-10-m base package [15.1X53-D67.5]
JUNOS Host qfx-10-m data-plane package [15.1X53-D67.5]
JUNOS Host qfx-10-m fabric package [15.1X53-D67.5]
JUNOS Host qfx-10-m control-plane package [15.1X53-D67.5]

{master}
    """
    result = [{'interface': 'et-2/0/16.3000',
               'ip': 'fe80::e10:d1',
               'mac': 'f0:2f:a7:38:29:92'},
              {'interface': 'et-2/0/15.3000',
               'ip': 'fe80::e11:d1',
               'mac': '9c:7d:a3:83:95:d2'},
              {'interface': 'et-2/0/14.3000',
               'ip': 'fe80::e12:d1',
               'mac': 'f0:2f:a7:38:2a:72'},
              {'interface': 'et-2/0/13.3000',
               'ip': 'fe80::e13:d1',
               'mac': '9c:7d:a3:83:96:72'},
              {'interface': 'et-2/0/12.3000',
               'ip': 'fe80::e14:d1',
               'mac': '9c:7d:a3:83:96:c2'},
              {'interface': 'et-4/0/17.3000',
               'ip': 'fe80::e15:d1',
               'mac': 'f0:2f:a7:38:28:72'},
              {'interface': 'et-4/0/16.3000',
               'ip': 'fe80::e16:d1',
               'mac': 'f0:2f:a7:38:28:32'},
              {'interface': 'et-4/0/15.3000',
               'ip': 'fe80::e17:d1',
               'mac': '9c:7d:a3:83:97:32'},
              {'interface': 'et-4/0/14.3000',
               'ip': 'fe80::e18:d1',
               'mac': 'f0:2f:a7:38:29:c2'},
              {'interface': 'et-8/0/10.3000',
               'ip': 'fe80::e19:d1',
               'mac': 'f0:2f:a7:38:2c:f2'},
              {'interface': 'et-8/0/9.3000',
               'ip': 'fe80::e20:d1',
               'mac': 'f0:2f:a7:38:2b:82'},
              {'interface': 'et-8/0/7.3000',
               'ip': 'fe80::e21:d1',
               'mac': 'f0:2f:a7:38:29:d2'},
              {'interface': 'et-8/0/6.3000',
               'ip': 'fe80::e22:d1',
               'mac': '9c:7d:a3:83:97:42'},
              {'interface': 'et-10/0/11.3000',
               'ip': 'fe80::e23:d1',
               'mac': 'f0:2f:a7:38:2b:62'},
              {'interface': 'et-10/0/10.3000',
               'ip': 'fe80::e24:d1',
               'mac': '9c:7d:a3:83:96:22'},
              {'interface': 'et-8/0/8.3000',
               'ip': 'fe80::e25:d1',
               'mac': '9c:7d:a3:83:95:f2'},
              {'interface': 'et-8/0/21.3000',
               'ip': 'fe80::e26:d1',
               'mac': 'f0:2f:a7:38:2b:92'},
              {'interface': 'et-8/0/20.3000',
               'ip': 'fe80::e27:d1',
               'mac': 'f0:2f:a7:38:2a:f2'},
              {'interface': 'et-8/0/19.3000',
               'ip': 'fe80::e28:d1',
               'mac': 'f0:2f:a7:38:2a:d2'},
              {'interface': 'et-9/0/11.3000',
               'ip': 'fe80::e30:d1',
               'mac': '9c:7d:a3:83:96:a2'},
              {'interface': 'et-9/0/10.3000',
               'ip': 'fe80::e31:d1',
               'mac': 'f0:2f:a7:38:28:22'},
              {'interface': 'et-9/0/9.3000',
               'ip': 'fe80::e32:d1',
               'mac': '9c:7d:a3:83:98:42'},
              {'interface': 'et-9/0/8.3000',
               'ip': 'fe80::e33:d1',
               'mac': 'f0:2f:a7:38:2a:b2'},
              {'interface': 'et-9/0/6.3000',
               'ip': 'fe80::e34:d1',
               'mac': 'f0:2f:a7:38:2a:e2'},
              {'interface': 'et-9/0/4.3000',
               'ip': 'fe80::e36:d1',
               'mac': 'f0:2f:a7:38:2b:a2'},
              {'interface': 'et-10/0/9.3000',
               'ip': 'fe80::e37:d1',
               'mac': '9c:7d:a3:83:97:a2'},
              {'interface': 'et-10/0/8.3000',
               'ip': 'fe80::e38:d1',
               'mac': '9c:7d:a3:83:97:d2'},
              {'interface': 'et-10/0/7.3000',
               'ip': 'fe80::e39:d1',
               'mac': '9c:7d:a3:83:98:02'},
              {'interface': 'et-10/0/26.3000',
               'ip': 'fe80::e40:d1',
               'mac': 'f0:2f:a7:38:2c:82'},
              {'interface': 'et-10/0/25.3000',
               'ip': 'fe80::e41:d1',
               'mac': '9c:7d:a3:83:96:42'},
              {'interface': 'et-10/0/22.3000',
               'ip': 'fe80::e44:d1',
               'mac': '9c:7d:a3:83:97:22'},
              {'interface': 'et-10/0/21.3000',
               'ip': 'fe80::e45:d1',
               'mac': '9c:7d:a3:83:96:b2'},
              {'interface': 'et-10/0/18.3000',
               'ip': 'fe80::e46:d1',
               'mac': 'f0:2f:a7:38:2a:92'},
              {'interface': 'et-11/0/10.3000',
               'ip': 'fe80::e47:d1',
               'mac': 'f0:2f:a7:38:2d:02'},
              {'interface': 'et-11/0/8.3000',
               'ip': 'fe80::e48:d1',
               'mac': 'f0:2f:a7:38:28:e2'},
              {'interface': 'et-11/0/9.3000',
               'ip': 'fe80::e49:d1',
               'mac': 'f0:2f:a7:38:29:02'},
              {'interface': 'et-11/0/21.3000',
               'ip': 'fe80::e50:d1',
               'mac': '9c:7d:a3:83:98:12'},
              {'interface': 'et-12/0/2.3000',
               'ip': 'fe80::e51:d1',
               'mac': '9c:7d:a3:83:96:f2'},
              {'interface': 'et-12/0/27.3000',
               'ip': 'fe80::e52:d1',
               'mac': '9c:7d:a3:83:94:d2'},
              {'interface': 'et-11/0/20.3000',
               'ip': 'fe80::e53:d1',
               'mac': '9c:7d:a3:83:97:b2'},
              {'interface': 'et-12/0/26.3000',
               'ip': 'fe80::e54:d1',
               'mac': '9c:7d:a3:83:96:d2'},
              {'interface': 'et-12/0/25.3000',
               'ip': 'fe80::e55:d1',
               'mac': 'f0:2f:a7:38:28:82'},
              {'interface': 'et-12/0/23.3000',
               'ip': 'fe80::e56:d1',
               'mac': '9c:7d:a3:83:94:c2'},
              {'interface': 'et-12/0/22.3000',
               'ip': 'fe80::e57:d1',
               'mac': 'f0:2f:a7:38:29:f2'},
              {'interface': 'et-12/0/20.3000',
               'ip': 'fe80::e58:d1',
               'mac': 'f0:2f:a7:38:28:02'},
              {'interface': 'et-12/0/19.3000',
               'ip': 'fe80::e59:d1',
               'mac': 'f0:2f:a7:38:2c:b2'},
              {'interface': 'et-11/0/19.3000',
               'ip': 'fe80::e60:d1',
               'mac': '9c:7d:a3:83:97:72'},
              {'interface': 'et-12/0/18.3000',
               'ip': 'fe80::e61:d1',
               'mac': 'f0:2f:a7:38:2c:32'},
              {'interface': 'et-3/0/13.3000',
               'ip': 'fe80::e62:d1',
               'mac': 'f0:2f:a7:38:28:52'},
              {'interface': 'et-2/0/17.3000',
               'ip': 'fe80::e63:d1',
               'mac': '9c:7d:a3:83:98:52'},
              {'interface': 'et-10/0/6.3000',
               'ip': 'fe80::e64:d1',
               'mac': '9c:7d:a3:83:98:22'},
              {'interface': 'et-10/0/5.3000',
               'ip': 'fe80::e65:d1',
               'mac': 'f0:2f:a7:38:2c:12'},
              {'interface': 'et-4/0/13.3000',
               'ip': 'fe80::e66:d1',
               'mac': 'f0:2f:a7:38:2c:52'},
              {'interface': 'et-4/0/12.3000',
               'ip': 'fe80::e67:d1',
               'mac': 'f0:2f:a7:38:28:d2'},
              {'interface': 'et-10/0/4.3000',
               'ip': 'fe80::e68:d1',
               'mac': 'f0:2f:a7:38:2c:a2'},
              {'interface': 'et-8/0/5.3000',
               'ip': 'fe80::e69:d1',
               'mac': '9c:7d:a3:83:97:62'},
              {'interface': 'et-12/0/10.3000',
               'ip': 'fe80::e70:d1',
               'mac': 'f0:2f:a7:38:2c:d2'},
              {'interface': 'et-12/0/9.3000',
               'ip': 'fe80::e71:d1',
               'mac': 'f0:2f:a7:38:27:f2'},
              {'interface': 'et-8/0/4.3000',
               'ip': 'fe80::e72:d1',
               'mac': '9c:7d:a3:83:96:82'},
              {'interface': 'et-12/0/8.3000',
               'ip': 'fe80::e73:d1',
               'mac': '9c:7d:a3:83:95:72'},
              {'interface': 'et-8/0/3.3000',
               'ip': 'fe80::e74:d1',
               'mac': '9c:7d:a3:83:97:e2'},
              {'interface': 'et-8/0/23.3000',
               'ip': 'fe80::e77:d1',
               'mac': '9c:7d:a3:83:95:c2'},
              {'interface': 'et-6/0/12.3000',
               'ip': 'fe80::e78:d1',
               'mac': '9c:7d:a3:83:97:82'},
              {'interface': 'et-6/0/13.3000',
               'ip': 'fe80::e79:d1',
               'mac': '9c:7d:a3:83:96:32'},
              {'interface': 'et-6/0/14.3000',
               'ip': 'fe80::e80:d1',
               'mac': '9c:7d:a3:83:96:52'},
              {'interface': 'et-6/0/16.3000',
               'ip': 'fe80::e81:d1',
               'mac': '9c:7d:a3:83:96:12'},
              {'interface': 'et-6/0/17.3000',
               'ip': 'fe80::e82:d1',
               'mac': '9c:7d:a3:83:95:82'},
              {'interface': 'et-7/0/12.3000',
               'ip': 'fe80::e83:d1',
               'mac': '9c:7d:a3:83:94:b2'},
              {'interface': 'et-7/0/13.3000',
               'ip': 'fe80::e84:d1',
               'mac': '9c:7d:a3:83:95:b2'},
              {'interface': 'et-7/0/14.3000',
               'ip': 'fe80::e85:d1',
               'mac': 'f0:2f:a7:38:2d:12'},
              {'interface': 'et-7/0/15.3000',
               'ip': 'fe80::e86:d1',
               'mac': 'f0:2f:a7:38:2c:e2'},
              {'interface': 'et-7/0/16.3000',
               'ip': 'fe80::e87:d1',
               'mac': 'f0:2f:a7:38:2c:72'},
              {'interface': 'et-7/0/17.3000',
               'ip': 'fe80::e88:d1',
               'mac': 'f0:2f:a7:38:28:b2'},
              {'interface': 'et-5/0/13.3000',
               'ip': 'fe80::e89:d1',
               'mac': '9c:7d:a3:83:97:f2'},
              {'interface': 'et-5/0/14.3000',
               'ip': 'fe80::e90:d1',
               'mac': 'f0:2f:a7:38:2a:32'},
              {'interface': 'et-5/0/15.3000',
               'ip': 'fe80::e91:d1',
               'mac': 'f0:2f:a7:38:2c:42'},
              {'interface': 'et-11/0/29.3000',
               'ip': 'fe80::e93:d1',
               'mac': '48:7b:6b:3e:8b:82'},
              {'interface': 'et-12/0/5.3000',
               'ip': 'fe80::e96:d1',
               'mac': 'f0:2f:a7:38:27:a2'},
              {'interface': 'et-8/0/16.3000',
               'ip': 'fe80::e99:d1',
               'mac': 'f0:2f:a7:38:2b:f2'},
              {'interface': 'ae101.3000', 'ip': 'fe80::ea1:d1', 'mac': '68:cc:6e:a8:b8:71'},
              {'interface': 'ae101.3666', 'ip': 'fe80::ea1:d1', 'mac': '68:cc:6e:a8:b8:71'},
              {'interface': 'ae102.3000', 'ip': 'fe80::ea2:d1', 'mac': '2c:21:31:18:0f:00'},
              {'interface': 'ae102.3666', 'ip': 'fe80::ea2:d1', 'mac': '2c:21:31:18:0f:00'},
              {'interface': 'et-9/0/19.3000',
               'ip': 'fe80::e101:d1',
               'mac': 'f0:2f:a7:38:29:52'},
              {'interface': 'et-9/0/20.3000',
               'ip': 'fe80::e102:d1',
               'mac': 'f0:2f:a7:38:28:62'},
              {'interface': 'et-9/0/22.3000',
               'ip': 'fe80::e103:d1',
               'mac': 'f0:2f:a7:38:2b:52'},
              {'interface': 'et-9/0/23.3000',
               'ip': 'fe80::e104:d1',
               'mac': 'f0:2f:a7:38:29:62'},
              {'interface': 'et-9/0/27.3000',
               'ip': 'fe80::e106:d1',
               'mac': 'f0:2f:a7:38:2b:12'},
              {'interface': 'et-8/0/14.3000',
               'ip': 'fe80::e109:d1',
               'mac': 'f0:2f:a7:38:2a:62'},
              {'interface': 'et-11/0/22.3000',
               'ip': 'fe80::e110:d1',
               'mac': '9c:7d:a3:83:95:42'},
              {'interface': 'et-12/0/1.3000',
               'ip': 'fe80::e111:d1',
               'mac': 'f0:2f:a7:38:2a:12'},
              {'interface': 'et-12/0/0.3000',
               'ip': 'fe80::e112:d1',
               'mac': 'f0:2f:a7:38:2c:92'},
              {'interface': 'et-12/0/29.3000',
               'ip': 'fe80::e113:d1',
               'mac': 'f0:2f:a7:38:29:b2'},
              {'interface': 'et-12/0/28.3000',
               'ip': 'fe80::e114:d1',
               'mac': 'f0:2f:a7:38:2b:c2'},
              {'interface': 'et-0/0/16.3000',
               'ip': 'fe80::e115:d1',
               'mac': '9c:7d:a3:83:96:02'},
              {'interface': 'et-0/0/15.3000',
               'ip': 'fe80::e116:d1',
               'mac': 'f0:2f:a7:38:2b:e2'},
              {'interface': 'et-0/0/14.3000',
               'ip': 'fe80::e117:d1',
               'mac': 'f0:2f:a7:38:2a:42'},
              {'interface': 'et-11/0/4.3000',
               'ip': 'fe80::e118:d1',
               'mac': 'f0:2f:a7:38:27:82'},
              {'interface': 'et-11/0/5.3000',
               'ip': 'fe80::e119:d1',
               'mac': 'f0:2f:a7:38:29:82'},
              {'interface': 'et-11/0/6.3000',
               'ip': 'fe80::e120:d1',
               'mac': 'f0:2f:a7:38:28:92'},
              {'interface': 'et-9/0/0.3000',
               'ip': 'fe80::e121:d1',
               'mac': '9c:7d:a3:83:98:62'},
              {'interface': 'et-9/0/1.3000',
               'ip': 'fe80::e122:d1',
               'mac': 'f0:2f:a7:38:2b:b2'},
              {'interface': 'et-11/0/23.3000',
               'ip': 'fe80::e124:d1',
               'mac': '9c:7d:a3:83:94:f2'},
              {'interface': 'et-11/0/24.3000',
               'ip': 'fe80::e125:d1',
               'mac': '9c:7d:a3:83:95:02'},
              {'interface': 'et-11/0/26.3000',
               'ip': 'fe80::e126:d1',
               'mac': '9c:7d:a3:83:97:c2'},
              {'interface': 'et-11/0/27.3000',
               'ip': 'fe80::e127:d1',
               'mac': 'f0:2f:a7:38:28:f2'},
              {'interface': 'et-11/0/28.3000',
               'ip': 'fe80::e128:d1',
               'mac': 'f0:2f:a7:38:28:42'},
              {'interface': 'et-11/0/0.3000',
               'ip': 'fe80::e129:d1',
               'mac': 'f0:2f:a7:38:2b:22'},
              {'interface': 'et-11/0/2.3000',
               'ip': 'fe80::e131:d1',
               'mac': 'f0:2f:a7:38:28:12'},
              {'interface': 'et-3/0/14.3000',
               'ip': 'fe80::e132:d1',
               'mac': '9c:7d:a3:83:95:92'},
              {'interface': 'et-3/0/15.3000',
               'ip': 'fe80::e133:d1',
               'mac': 'f0:2f:a7:38:28:c2'},
              {'interface': 'et-3/0/16.3000',
               'ip': 'fe80::e134:d1',
               'mac': 'f0:2f:a7:38:2b:42'},
              {'interface': 'et-1/0/13.3000',
               'ip': 'fe80::e136:d1',
               'mac': '9c:7d:a3:83:95:e2'},
              {'interface': 'et-1/0/16.3000',
               'ip': 'fe80::e138:d1',
               'mac': 'f0:2f:a7:38:29:12'},
              {'interface': 'et-1/0/17.3000',
               'ip': 'fe80::e139:d1',
               'mac': 'f0:2f:a7:38:2c:c2'},
              {'interface': 'et-0/0/12.3000',
               'ip': 'fe80::e140:d1',
               'mac': 'f0:2f:a7:38:27:c2'},
              {'interface': 'et-12/0/21.3000',
               'ip': 'fe80::e141:d1',
               'mac': '9c:7d:a3:83:95:22'},
              {'interface': 'et-11/0/11.3000',
               'ip': 'fe80::e142:d1',
               'mac': '9c:7d:a3:83:95:32'},
              {'interface': 'et-10/0/27.3000',
               'ip': 'fe80::e143:d1',
               'mac': '9c:7d:a3:83:95:52'},
              {'interface': 'et-10/0/28.3000',
               'ip': 'fe80::e144:d1',
               'mac': 'f0:2f:a7:38:27:d2'},
              {'interface': 'et-10/0/29.3000',
               'ip': 'fe80::e145:d1',
               'mac': '18:de:d7:a6:78:12'},
              {'interface': 'et-10/0/0.3000',
               'ip': 'fe80::e146:d1',
               'mac': '88:3f:d3:2b:6a:02'},
              {'interface': 'et-10/0/1.3000',
               'ip': 'fe80::e147:d1',
               'mac': '88:3f:d3:2b:6c:72'},
              {'interface': 'et-10/0/2.3000',
               'ip': 'fe80::e148:d1',
               'mac': '88:3f:d3:2b:6a:e2'},
              {'interface': 'et-10/0/3.3000',
               'ip': 'fe80::e149:d1',
               'mac': '88:3f:d3:2b:6c:52'},
              {'interface': 'et-11/0/18.3000',
               'ip': 'fe80::e150:d1',
               'mac': '48:7b:6b:3e:8b:92'},
              {'interface': 'et-8/0/12.3000',
               'ip': 'fe80::e151:d1',
               'mac': 'f0:2f:a7:38:2c:22'},
              {'interface': 'et-9/0/17.3000',
               'ip': 'fe80::e152:d1',
               'mac': '9c:7d:a3:83:94:e2'},
              {'interface': 'et-9/0/16.3000',
               'ip': 'fe80::e153:d1',
               'mac': '9c:7d:a3:83:95:12'},
              {'interface': 'et-9/0/13.3000',
               'ip': 'fe80::e155:d1',
               'mac': 'f0:2f:a7:38:29:22'},
              {'interface': 'et-9/0/26.3000',
               'ip': 'fe80::e156:d1',
               'mac': 'f0:2f:a7:38:27:b2'},
              {'interface': 'et-8/0/27.3000',
               'ip': 'fe80::e157:d1',
               'mac': '88:3f:d3:2b:6b:22'},
              {'interface': 'et-8/0/28.3000',
               'ip': 'fe80::e158:d1',
               'mac': '88:3f:d3:2b:6b:12'},
              {'interface': 'et-8/0/29.3000',
               'ip': 'fe80::e159:d1',
               'mac': '88:3f:d3:2b:6b:62'},
              {'interface': 'et-8/0/0.3000',
               'ip': 'fe80::e160:d1',
               'mac': '88:3f:d3:2b:6b:f2'},
              {'interface': 'et-8/0/1.3000',
               'ip': 'fe80::e161:d1',
               'mac': '48:7b:6b:3e:8b:72'},
              {'interface': 'et-8/0/2.3000',
               'ip': 'fe80::e162:d1',
               'mac': '9c:7d:a3:83:95:a2'},
              {'interface': 'et-1/0/15.3000',
               'ip': 'fe80::e163:d1',
               'mac': 'bc:62:0e:4c:21:92'},
              {'interface': 'et-9/0/12.3000',
               'ip': 'fe80::e164:d1',
               'mac': '9c:7d:a3:83:96:92'},
              {'interface': 'et-11/0/16.3000',
               'ip': 'fe80::e165:d1',
               'mac': 'f0:2f:a7:38:29:32'},
              {'interface': 'et-11/0/15.3000',
               'ip': 'fe80::e166:d1',
               'mac': 'f0:2f:a7:38:2a:02'},
              {'interface': 'et-11/0/14.3000',
               'ip': 'fe80::e167:d1',
               'mac': 'f0:2f:a7:38:2a:52'},
              {'interface': 'et-12/0/11.3000',
               'ip': 'fe80::e168:d1',
               'mac': '48:7b:6b:3e:8b:a2'},
              {'interface': 'et-3/0/12.3000',
               'ip': 'fe80::e169:d1',
               'mac': '9c:7d:a3:83:97:02'},
              {'interface': 'et-8/0/11.3000',
               'ip': 'fe80::e170:d1',
               'mac': '2c:9d:1e:0a:69:02'},
              {'interface': 'et-12/0/24.3000',
               'ip': 'fe80::e171:d1',
               'mac': '88:3f:d3:2b:6a:42'},
              {'interface': 'et-10/0/20.3000',
               'ip': 'fe80::e173:d1',
               'mac': '88:3f:d3:2b:6c:02'},
              {'interface': 'et-9/0/28.3000',
               'ip': 'fe80::e200:d1',
               'mac': 'ec:0d:9a:fb:83:10'},
              {'interface': 'et-9/0/5.3000',
               'ip': 'fe80::e201:d1',
               'mac': 'ec:0d:9a:fb:7a:90'},
              {'interface': 'et-9/0/2.3000',
               'ip': 'fe80::e202:d1',
               'mac': 'ec:0d:9a:fb:7d:10'},
              {'interface': 'et-9/0/24.3000',
               'ip': 'fe80::e203:d1',
               'mac': 'ec:0d:9a:fb:7d:90'},
              {'interface': 'et-9/0/18.3000',
               'ip': 'fe80::e204:d1',
               'mac': 'ec:0d:9a:fb:76:90'},
              {'interface': 'et-9/0/28.3000',
               'ip': 'fe80::ee0d:9aff:fefb:8310',
               'mac': 'ec:0d:9a:fb:83:10'}]
