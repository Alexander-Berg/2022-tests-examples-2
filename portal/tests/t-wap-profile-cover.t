#!/usr/bin/perl

use strict;
use warnings;

use lib::abs qw(. ../lib);
use Data::Dumper;

use Test::More;

my $WAPS = q{
20005   http://wap1.huawei.com/uaprof/HuaweiMediaPadWCDMA_ICS.xml
20222   http://www.htcmms.com.tw/Android/Common/Legend/ua-profile.xml
20424   x22http://nds1.nds.nokia.com/uaprof/NN8-00r310-3G.xmlx22
20450   http://www.htcmms.com.tw/Android/Common/PG58/ua-profile.xml
20915   x22http://nds1.nds.nokia.com/uaprof/Nokia5530c-2r100-2G.xmlx22
21241   http://gsm.lge.com/html/gsm/P970-M3-D2.xml
21340   x22http://wap.samsungmobile.com/uaprof/GT-S8500_3G.rdfx22
21677   x22http://nds1.nds.nokia.com/uaprof/300r100.xmlx22
22088   http://uaprofile.asus.com/uaprof/ASUS-TF300TG.xml
23566   http://218.249.47.94/Xianghe/MTK_Athens15_UAProfile.xml
23691   x22http://nds1.nds.nokia.com/uaprof/Nokia5230r100-3G.xml x22
24667   http://support.acer.com/UAprofile/Acer_A500_IML74K_Profile.xml
24864   x22http://nds1.nds.nokia.com/uaprof/Nokia302r100.xmlx22
26638   http://support.acer.com/UAprofile/Acer_A501_IML74K_Profile.xml
29076   http://support.acer.com/UAprofile/Acer_A501_Profile.xml
30355   http://wap.samsungmobile.com/uaprof/GT-P1000.xml
34877   x22http://nds1.nds.nokia.com/uaprof/305r100.xmlx22
35355   http://www.htcmms.com.tw/Android/Common/Wildfire/ua-profile.xml
35754   x22http://nds1.nds.nokia.com/uaprof/NokiaC2-03r100.xmlx22
36002   http://wap.samsungmobile.com/uaprof/GT-S5660.xml
36289   http://wap.samsungmobile.com/uaprof/GT-P7300.xml
37621   x22http://nds1.nds.nokia.com/uaprof/311r100.xmlx22
42715   http://www.htcmms.com.tw/Android/Common/PG88/ua-profile.xml
44942   http://wap.samsungmobile.com/uaprof/GT-I9100.xml
46163   http://wap.samsungmobile.com/uaprof/GT-I9001.xml
53262   x22http://nds1.nds.nokia.com/uaprof/202r100.xmlx22
63500   http://www.htcmms.com.tw/Android/Common/PG76/ua-profile.xml
66394   http://www.htcmms.com.tw/Android/Common/Bravo/HTC_Desire_A8181.xml
78266   x22http://nds1.nds.nokia.com/uaprof/Nokia200r100.xmlx22
78572   http://www.htcmms.com.tw/Android/Common/PG32/ua-profile.xml
83146   x22http://nds1.nds.nokia.com/uaprof/NokiaX2-02r100.xmlx22
83382   http://www.htcmms.com.tw/Android/Common/DesireHD/ua-profile.xml
121424  http://wap.samsungmobile.com/uaprof/GT-P7500.xml
125474  x22http://wap.samsungmobile.com/uaprof/GT-S5230MR.rdfx22
9682    http://www.htcmms.com.tw/Android/Common/Hero/ua-profile.xml
9754    http://www.htcmms.com.tw/Android/Common/PK76/ua-profile.xml
9825    x22http://wap.samsungmobile.com/uaprof/GT-S5610_2G.rdfx22
10229   http://wap.samsungmobile.com/uaprof/GT-I9103.xml
10254   x22http://nds1.nds.nokia.com/uaprof/Nokia5800d-1r100-3G.xml x22
10364   http://support.acer.com/UAprofile/Acer_A101_Profile.xml
10536   http://support.acer.com/UAprofile/Acer_A200_Profile.xml
10641   x22http://nds1.nds.nokia.com/uaprof/NC7-00r200.xmlx22
10667   http://www.htcmms.com.tw/Android/Common/PJ401/ua-profile.xml
10773   http://wap.sonyericsson.com/UAprof/ST25iR601.xml
10835   http://wap.sonyericsson.com/UAprof/MT11iR402.xml
10996   x22http://nds1.nds.nokia.com/uaprof/NN8-00r300-3G.xmlx22
11328   x22http://wap.samsungmobile.com/uaprof/GT-S8500.rdfx22
11535   x22http://nds1.nds.nokia.com/uaprof/NokiaC2-05r100.xmlx22
11902   x22http://wap.samsungmobile.com/uaprof/GT-S8530_3G.rdfx22
12343   x22http://nds1.nds.nokia.com/uaprof/NC3-01.5r100.xmlx22
12650   x22http://wap.samsungmobile.com/uaprof/GT-S5233T.rdfx22
12838   http://www.htcmms.com.tw/Android/Common/PG5813/ua-profile.xml
12891   x22http://wap.samsungmobile.com/uaprof/GT-S5230.rdfx22
13032   http://wap.sonyericsson.com/UAprof/E15iR202.xml
13074   x22http://nds1.nds.nokia.com/uaprof/NC5-00r100.xmlx22
13136   http://support.acer.com/UAprofile/Acer_A511_IML74K_Profile.xml
13191   http://wap.sonyericsson.com/UAprof/K700cR201.xml
14227   x22http://nds1.nds.nokia.com/uaprof/NokiaC2-06r100.xmlx22
14234   x22http://nds1.nds.nokia.com/uaprof/NN8-00r200-3G.xmlx22
14680   x22http://wap.samsungmobile.com/uaprof/GT-S5610_3G.rdfx22
14810   x22http://nds1.nds.nokia.com/uaprof/NokiaC6-00r100.xmlx22
14966   http://wap.sonyericsson.com/UAprof/LT26iR611.xml
15022   x22http://wap.samsungmobile.com/uaprof/GT-C3011.xmlx22
15076   http://wap.sonyericsson.com/UAprof/ST18iR402.xml
15430   x22http://nds1.nds.nokia.com/uaprof/306r100.xmlx22
15830   x22http://wap.samsungmobile.com/uaprof/GT-C6712.rdfx22
15903   x22http://wap.samsungmobile.com/uaprof/GT-C3300K.xmlx22
15962   x22http://www.htcmms.com.tw/gen/HTC_HD2_T8585-1.0.xmlx22
16044   http://wap.sonyericsson.com/UAprof/WT19iR402.xml
16655   http://www.htcmms.com.tw/Android/Common/PJ461/ua-profile.xml
17294   x22http://wap.samsungmobile.com/uaprof/GT-S5260.rdfx22
17598   http://wap.sonyericsson.com/UAprof/LT18iR402.xml
17656   http://gsm.lge.com/html/gsm/P500-M6-D1.xml
18590   x22http://wap.samsungmobile.com/uaprof/GT-S3600i.xmlx22
18610   x22http://wap.samsungmobile.com/uaprof/E2121B.xmlx22
19419   x22http://nds1.nds.nokia.com/uaprof/NE72-1r100.xmlx22
19906   x22http://wap.samsungmobile.com/uaprof/GT-C3300i.xmlx22
19980   x22http://nds1.nds.nokia.com/uaprof/NE52-1r100.xmlx22
};

my @profiles = grep {$_}
  map { s/x22/\x22/g; $_ }
  map { s/^\d*\s*//; s/\s*[\n\r]*$//; $_; }
  split(/\n/, $WAPS);

#print Dumper( \@profiles );

use_ok('MordaX::DetectDevice');
my $d = MordaX::DetectDevice->new();

my $cx  = 0;
my $gx  = 0;
my $gsx = 0;
my $gpx = 0;
for my $p (@profiles) {
    my $headers = {
        'User-Agent'    => 'Opera',
        'X-Wap-Profile' => $p,
    };
    $d->detect(headers => $headers);
    my $bro = $d->get_browser();
    my $pho = $d->get_phone();

    $cx++;
    my $ok = $bro->{'ScreenSize'} && $bro->{'ScreenWidth'} && $bro->{DeviceVendor};
    ok($ok, $p);
    $gx++ if ($ok);

    if ($ok) {
        #is( $bro->{DeviceVendor}, $pho->{vendor} , 'Vendor') if $pho->{vendor};
        if ($pho->{screenx}) {
            if ($bro->{ScreenSize} eq $pho->{screenx} . "x" . $pho->{'screeny'}) {
                $gpx++;
            } elsif ($bro->{ScreenSize} eq $pho->{screeny} . "x" . $pho->{'screenx'}) {
                $gpx++;
                diag(" Inverted Screen Size");
            } else {
                diag(" ScreenSize dont match: " . $bro->{ScreenSize} . " vs " . $pho->{screenx} . "x" . $pho->{screeny});
            }
        }

        #is( $bro->{ScreenSize}  , $pho->{screenx} ."x". $pho->{'screeny'} , 'ScreenSize') if $pho->{screenx} ;
        #diag( Dumper( $p, $bro, $pho ));
    }

    $headers->{'X-Wap-Profile'} =~ s/\x22//g;
    $d->detect(headers => $headers);
    $bro = $d->get_browser();

    my $ok2 = $bro->{'ScreenSize'} && $bro->{'ScreenWidth'} && $bro->{DeviceVendor};
    ok($ok2, "Striped:" . $p);
    $gsx++ if ($ok2);

    unless ($ok) {
        diag(Dumper($p, $bro));
    }

}

my $k  = $gx / $cx * 100;
my $ks = $gsx / $cx * 100;
diag("KPD        : " . int($k) . "%");
diag("KPDstripped: " . int($ks) . "%");

ok($k > 80, "KPD over 80%");
done_testing();
