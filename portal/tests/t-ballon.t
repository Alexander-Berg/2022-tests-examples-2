#!/usr/bin/perl

=h1 ISSUES

    HOME-7662 + HOME-8078 - new balloon tt2 inteface - citySuggest -> {}
    home-7951 initial

=cut

use strict;
use warnings;

use lib::abs qw(. ../t/testlib);

use MordaTest;
use testlib::TestRequest qw(r);
use Test::Most 'no_plan';
die_on_fail();
use testlib::GeoHelper;

use MordaX;
use MordaX::Config;

use MordaX::Logit qw(dmp logit);
MordaX::Logit::enable_dumpit();

my $geo = testlib::GeoHelper->new();
ok($geo,          "testlib::GeoHelper Active");
ok($geo->ip(225), "testlib::GeoHelper provides ip");

#done_testing();
#diag(" Ballon test damaged by lib.geo, \n test damadged \n test damaged \n test damadged");
#exit 0;

subtest "No YandexUID" => sub {
    my $req      = r(get => {});
    my $page     = {};
    my $pagedata = $req->{'pagedata'};
    MordaX::init_geo_balloon($req, $page);

    #default morda content is BIG
    ok($req->{'yandexuid'}, "yandex uid setted");

    is($req->{'MordaContent'},         'big', "MordaContent");
    is($pagedata->{'ShowGeoBaloonN1'}, undef, "no mobile balloon");
    is($req->{'roll_yabs_gballoon'},   undef, "No yabs flag");

    done_testing();
};

my %default_req_param = (
    get     => {},
    cookies => {
        yandexuid => '666941071298288078',
    },
);

my $detection_city = {
    region            => 213,
    pure_region       => 213,
    region_by_ip      => 213,
    pure_region_by_ip => 213,
};
subtest "No Balloon for city" => sub {
    my $req = r(%default_req_param);
    #hack detector
    $req->{'GeoDetection'} = Storable::dclone($detection_city);
    my $page     = {};
    my $pagedata = $req->{'pagedata'};

    MordaX::init_geo_balloon($req, $page);

    is($pagedata->{'ShowGeoBaloonN1'}, undef, "no mobile balloon");
    is($req->{'roll_yabs_gballoon'},   undef, "no yabs flag");
    is($pagedata->{'citySuggest'},     undef, "no city suggest");

    done_testing();
};

#225 1 213
my $detection_region = {
    region            => 213,
    pure_region       => 213,
    region_by_ip      => 1,
    pure_region_by_ip => 1,
    #suspected_region    => 213,
    precision       => 3,
    precision_by_ip => 3,
};
my $detection_country = {
    region            => 213,
    pure_region       => 213,
    region_by_ip      => 225,
    pure_region_by_ip => 225,
    precision         => 4,
    precision_by_ip   => 4,
};

SKIP: {
    skip 'Sugest field in geobase damadjed by movesjan@', 2;
    subtest "Balloon for district, no suspected" => sub {
        my $req = r(%default_req_param);
        #hack detector
        $req->{'GeoDetection'} = Storable::dclone($detection_region);
        my $page     = {};
        my $pagedata = $req->{'pagedata'};
        MordaX::init_geo_balloon($req, $page);
        is($req->{'AlienVisitior'}, undef, 'Non alien');

        #TODO move mobile for outher test;
        #ok( $pagedata->{'ShowGeoBaloonN1'}      , "ok mobile balloon");
        is($pagedata->{'ShowGeoBaloonN1'}, undef, "no mobile balloon");
        ok($req->{'roll_yabs_gballoon'}, "yabs flag");
        my $sr = $pagedata->{'GeoBaloonSuggests'};
        ok($sr, "Suggest region");
        if ($sr) {
            is(scalar @$sr, 4, "suggested 4 regions for district");
        }

        my $tts = $pagedata->{citySuggest};
        ok($tts, "new sity Suggest");
        if ($tts) {
            ok($tts->{cityName});
            ok($tts->{cityGid});
            ok($tts->{cityNameLocative});
            ok($tts->{namePre});
            is($tts->{type}, 'thisCity');
            ok($tts->{'otherCities'}, "Other Sities present")
        }
        done_testing();
    };
    subtest "Balloon for country" => sub {
        my $req = r(%default_req_param);
        #hack detector
        $req->{'GeoDetection'} = Storable::dclone($detection_country);
        my $page     = {};
        my $pagedata = $req->{'pagedata'};
        MordaX::init_geo_balloon($req, $page);

        #ok( $pagedata->{'ShowGeoBaloonN1'}      , "ok mobile balloon");
        is($pagedata->{'ShowGeoBaloonN1'}, undef, "no mobile balloon");
        ok($req->{'roll_yabs_gballoon'}, "yabs flag");
        my $sr = $pagedata->{'GeoBaloonSuggests'};
        ok($sr, "Suggest region");
        if ($sr) {
            is(scalar @$sr, 10, "suggested 10 regions for country");
        }
        my $tts = $pagedata->{citySuggest};
        ok($tts, "new sity Suggest");

        done_testing();
    };
}
my $detection_country2 = {
    region            => 213,
    pure_region       => 213,
    region_by_ip      => 225,
    pure_region_by_ip => 225,
    precision         => 4,
    precision_by_ip   => 4,
    suspected_region  => 2,
};

subtest "Balloon for country, with suspected" => sub {
    my $req = r(%default_req_param);
    #hack detector
    $req->{'GeoDetection'} = Storable::dclone($detection_country2);
    is(Geo::geo(213, 'type'), 6, "213, moscow type, ok");
    is(Geo::geo(225, 'type'), 3, "225, russia type, ok");
    diag("MordaContent:" . $req->{MordaContent});
    my $page     = {};
    MordaX::init_geo_balloon($req, $page);

    is($req->{'pagedata'}->{'ShowGeoBaloonN1'}, undef, "no mobile balloon");
    ok($req->{'roll_yabs_gballoon'}, "yabs flag");

    is($req->{'pagedata'}->{'GeoBaloonSuggests'}, undef, "No Suggest regions list");

    my $tts = $req->{'pagedata'}->{citySuggest};
    ok($tts, "new suggest ok");
    if ($tts) {
        ok($tts->{cityName});
        is($tts->{cityGid}, 2, 'supected gid ok');
        ok($tts->{cityNameLocative});
        ok($tts->{namePre});
        is($tts->{type}, 'otherCity');
        is($tts->{thisGid}, 213, 'base region is moscow');
        is($tts->{'otherCities'}, undef, "Other Sities not present")
    }
    done_testing();

};

$detection_country = {
    region            => 213,
    pure_region       => 213,
    region_by_ip      => 225,
    pure_region_by_ip => 225,
    precision         => 4,
    precision_by_ip   => 4,
};
SKIP: {
    skip 'Suject region damaged by movejan@', 1;
    subtest "Balloon for Country with good yago" => sub {

        my $req = r(%default_req_param);
        #hack detector
        $req->{'GeoDetection'} = Storable::dclone($detection_country);
        diag "ygo for this region 225:213";
        $req->{YCookies}->setyp('ygo', '225:213');

        my $page     = {};
        my $pagedata = $req->{'pagedata'};
        MordaX::init_geo_balloon($req, $page);
        ok($req->{'YCookies'}->value('ygo'), "ygo setted");
        is($pagedata->{'ShowGeoBaloonN1'}, undef, "no mobile balloon");
        is($req->{'roll_yabs_gballoon'},   undef, "No yabs flag");
        my $tts = $pagedata->{citySuggest};
        is($tts, undef, "no new suggest ");

        #---------------------------------------
        diag "ygo for this other region 225:2";

        $req = r(%default_req_param);
        $req->{'GeoDetection'} = Storable::dclone($detection_country);
        $req->{YCookies}->setyp('ygo', '225:2');

        $page     = {};
        $pagedata = $req->{'pagedata'};
        MordaX::init_geo_balloon($req, $page);
        is($pagedata->{'ShowGeoBaloonN1'}, undef, "no mobile balloon");
        is($req->{'roll_yabs_gballoon'},   1,     "yabs flag");
        $tts = $pagedata->{citySuggest};
        ok($tts, "new suggest ok");
        if ($tts) {
            ok($tts->{cityName});
            is($tts->{cityGid}, 213, 'supected gid ok');
            ok($tts->{cityNameLocative});
            ok($tts->{namePre});
            is($tts->{type},    'thisCity');
            is($tts->{thisGid}, undef);
        }
        done_testing();

    };

}

my %mobile_req = (
    get     => {},
    cookies => {
        yandexuid => '666941071298288078',
    },
    headers => {
        host => "m" . $MordaX::Config::InstanceModifier . $MordaX::Config::Subdomain . ".yandex.ru",
    },
    interface => 'mobmorda',
);
my $mobile_detection = {
    region            => 213,
    pure_region       => 213,
    region_by_ip      => 225,
    pure_region_by_ip => 225,
    precision         => 4,
    precision_by_ip   => 4,
};

subtest "mobile for city" => sub {
    my $req = r(%mobile_req);
    #hack detector
    $req->{'GeoDetection'} = Storable::dclone($detection_city);
    my $page     = {};
    my $pagedata = $req->{'pagedata'};
    MordaX::init_geo_balloon($req, $page);
    is($pagedata->{'ShowGeoBaloonN1'}, undef, "no mobile balloon");
    is($req->{'roll_yabs_gballoon'},   undef, "no yabs flag");
    is($pagedata->{citySuggest},       undef, "no city suggest");

    done_testing();
};

subtest "mobile, standart suggest" => sub {
    my $req = r(%mobile_req);

    is($req->{MordaContent}, 'mob', 'MordaContentTYpe');
    $req->{'GeoDetection'} = Storable::dclone($mobile_detection);
    my $page     = {};
    my $pagedata = $req->{'pagedata'};
    MordaX::init_geo_balloon($req, $page);

    is($pagedata->{'ShowGeoBaloonN1'}, 1, "mobile balloon");

    my $tts = $pagedata->{citySuggest};
    ok($tts, "new suggest ok");
    if ($tts) {
        ok($tts->{cityName});
        is($tts->{cityGid}, 213, 'gid ok');
        ok($tts->{cityNameLocative});
        ok($tts->{namePre});
        is($tts->{type}, 'thisCity');
        is($tts->{'otherCities'}, undef, "Other Sities not present")
    }

    done_testing();
};
subtest "mobile, suspected suggest" => sub {
    my $req = r(%mobile_req);
    $req->{'GeoDetection'} = Storable::dclone($mobile_detection);
    $req->{'GeoDetection'}->{suspected_region} = 2;
    my $page     = {};
    my $pagedata = $req->{'pagedata'};
    MordaX::init_geo_balloon($req, $page);

    is($pagedata->{'ShowGeoBaloonN1'}, 1, "mobile balloon");
    my $tts = $pagedata->{citySuggest};
    ok($tts, "new suggest ok");
    if ($tts) {
        ok($tts->{cityName});
        is($tts->{cityGid}, 2,   'gid ok');
        is($tts->{thisGid}, 213, 'gid ok');
        ok($tts->{cityNameLocative});
        ok($tts->{namePre});
        is($tts->{type}, 'otherCity');
        is($tts->{'otherCities'}, undef, "Other Sities not present")
    }

    done_testing();
};
subtest "mobile, ygo ok" => sub {
    my $req = r(%mobile_req);
    $req->{'GeoDetection'} = Storable::dclone($mobile_detection);
    my $page     = {};
    my $pagedata = $req->{'pagedata'};
    $req->{YCookies}->setyp('ygo', '225:213');

    MordaX::init_geo_balloon($req, $page);

    is($pagedata->{'ShowGeoBaloonN1'}, undef, "no mobile balloon");
    my $tts = $pagedata->{citySuggest};
    is($tts, undef, "no new suggest");

    done_testing();
};
subtest "mobile, ygo fail" => sub {
    my $req = r(%mobile_req);
    $req->{'GeoDetection'} = Storable::dclone($mobile_detection);
    my $page     = {};
    my $pagedata = $req->{'pagedata'};
    $req->{YCookies}->setyp('ygo', '2:213');

    MordaX::init_geo_balloon($req, $page);

    is($pagedata->{'ShowGeoBaloonN1'}, 1, "mobile balloon");
    my $tts = $pagedata->{citySuggest};
    ok($tts, "new suggest ok");

    done_testing();
};

subtest "Full test: yandex, by ip only" => sub {
    my $req = r(
        cookies => {
            yandexuid => '666941071298288078',
        },
        ip => '95.108.172.116',
    );
    my $page     = {};
    my $pagedata = $req->{'pagedata'};
    MordaX::init_geo_balloon($req, $page);

    is($req->{'GeoDetection'}->{'pure_region_by_ip'}, 213, 'Yandex IP');    # after geobase 3.0.5 yandex region 9999 becomes 213
    diag("yandex precision: for 213(9999) " . $req->{'GeoDetection'}->{'precision'});

    is($pagedata->{'ShowGeoBaloonN1'}, undef, "no mobile balloon");
    is($req->{'roll_yabs_gballoon'},   undef, "No yabs flag");
    done_testing();
};

#-------------------------------------------------------------

subtest "Full test: msk + yandexgid" => sub {
    my $req = r(
        cookies => {
            yandexuid  => '666941071298288078',
            yandex_gid => 2,
            ys         => 'gpauto.44_03:50_05:100:1:1298999674',
            yp         => '2147483647.ygo.213:2'
        },
        ip => '94.100.191.202',    #msk
    );

    is($req->{MordaContent}, 'big', 'MordaContentTYpe');

    my $page     = {};
    my $pagedata = $req->{'pagedata'};
    MordaX::init_geo_balloon($req, $page);
    is($req->{'yandex_gid'},               2,     'yandex gid accepted');
    is($req->{'GeoDetection'}->{'region'}, 2,     'region by yandexgid');
    is($pagedata->{'ShowGeoBaloonN1'},     undef, "no mobile balloon");
    is($req->{'roll_yabs_gballoon'},       undef, "No yabs flag");
    done_testing();
};

subtest "Full test: msk + yandexgid + bad yago" => sub {

    my $req = r(
        cookies => {
            yandexuid  => '666941071298288078',
            yandex_gid => 2,
            ys         => 'gpauto.44_03:50_05:100:1:1298999674',
            yp         => '2147483647.ygo.2:2'
        },
        ip => '94.100.191.202',    #msk
    );

    is($req->{MordaContent}, 'big', 'MordaContentTYpe');

    my $page     = {};
    my $pagedata = $req->{'pagedata'};
    MordaX::init_geo_balloon($req, $page);

    diag("precision: for msk with bad gid+yago " . $req->{'GeoDetection'}->{'precision'});

    is($req->{'GeoDetection'}->{'region'}, 2,     'region by yandexgid');
    is(MordaX::Utils::ygo_ok($req),        undef, 'ygo failed');

    is($pagedata->{'ShowGeoBaloonN1'}, undef, "no mobile balloon");
    is($req->{'roll_yabs_gballoon'},   1,     "yabs flag");
    done_testing();
};

subtest "Full test: russua + yandexgid:moscow + bad yago, " => sub {

=h2 description
    Данный случай не является баллуном первого типка так как пользователь уже устновил GID
    но и не является баллуном второго типа так как Пользователь не покинул пределы россии.

=cut    

    my $req = r(
        cookies => {
            yandexuid  => '666941071298288078',
            yandex_gid => 213,
        },
        ip => $geo->ip('225'),    #russia
    );

    is($req->{MordaContent}, 'big', 'MordaContentTYpe');

    my $page     = {};
    my $pagedata = $req->{'pagedata'};
    MordaX::init_geo_balloon($req, $page);

    diag("precision: for msk with bad gid+yago " . $req->{'GeoDetection'}->{'precision'});

    is(MordaX::Utils::ygo_ok($req), undef, 'ygo failed');

    is($req->{'GeoDetection'}->{'region'},          213, 'region by yandexgid');
    is($req->{'GeoDetection'}->{'region_by_ip'},    225, 'region by ip');
    is($req->{'GeoDetection'}->{'precision'},       2,   'precision by yandexgid');
    is($req->{'GeoDetection'}->{'precision_by_ip'}, 4,   'precision  by ip');
    is($req->{'GeoDetection'}->{'gid_is_trusted'},  1,   'gid is trusted');

    is($pagedata->{'ShowGeoBaloonN1'}, undef, "no mobile balloon");
    is($req->{'roll_yabs_gballoon'},   undef, "no yabs flag");

    my $sr = $pagedata->{'GeoBaloonSuggests'};
    my $cs = $pagedata->{'citySuggest'};
    is($sr, undef, "no Suggest region");
    is($cs, undef, "no City Suggest");

=x old style testes
    is( $req->{'roll_yabs_gballoon'}                 , 1         , "yabs flag");
    my $sr  = $pagedata->{'GeoBaloonSuggests'}; 
    ok( $sr                              , "Suggest region");
    if( $sr ){
       is( scalar @$sr                 ,  10, "suggested 10 regions for country");
    }

    ok( $cs , "city suggest ready" );
    if( $cs ){
        is( $cs->{'cityGid'}        , 213           , 'Suggest Moscow first' );
        is( $cs->{'type'}           , 'thisCity'    , 'ballon type N1');
    }
=cut

    done_testing();
};

subtest "Full test: SUSPECTED" => sub {
    my $req = r(
        cookies => {
            yandexuid  => '666941071298288078',
            yandex_gid => 143,
#            ys        => 'gpauto.44_03:50_05:100:1:1298999674',
            yp => '2147483647.ygo.2:143'
        },
        ip => '94.100.191.202',    #msk
    );
    my $page     = {};
    my $pagedata = $req->{'pagedata'};
    MordaX::init_geo_balloon($req, $page);

    my $geo = $req->{GeoDetection};

    is($geo->{region},       143, "region");
    is($geo->{region_by_ip}, 213, "region");

    is($geo->{suspected_region}, 213, "suspected ok - Moscow");

    MordaX::init_geo_balloon($req, $page);
    is($req->{'roll_yabs_gballoon'}, 1, "yabs flag");
    my $tts = $pagedata->{citySuggest};
    ok($tts, "new suggest ok");
    if ($tts) {
        is($tts->{cityGid}, 213, 'gid ok');
        is($tts->{thisGid}, 143, 'gid ok');
    }

    done_testing();

};
subtest "SUSPECTED with WIFI" => sub {
    my $now = time;
    my $req = r(
        cookies => {
            yandexuid  => '666941071298288078',
            yandex_gid => 2,
            ys         => 'gpauto.55_7338542:37_5880274:20:0:' . $now,    #moscow red
            yp         => '2147483647.xsz.1600#2147483647.ygo.2:2',       #after geobase 3.0.5 9999 becomes 213
        },
        ip => '94.100.191.202',                                           #msk
                                                                          #ip => '4.0.0.3', #USA
    );
    my $page     = {};
    my $pagedata = $req->{'pagedata'};
    MordaX::init_geo_balloon($req, $page);
    my $geo = $req->{GeoDetection};
    is($geo->{region},           2,   "SPB");
    is($geo->{suspected_region}, 213, "suspected ok - Moscow");
    my $tts = $pagedata->{citySuggest};
    ok($tts, "new suggest ok");
    is($tts->{cityGid}, 213, 'gid ok');

    done_testing();

};

subtest "Mobile, Leaving Msk" => sub {
    my $req = r(
        cookies => {
            yandexuid  => '666941071298288078',
            yandex_gid => 2,
            yp         => '2147483647.xsz.1600#2147483647.ygo.213:2',
        },
        headers => {
            host => "m" . $MordaX::Config::InstanceModifier . $MordaX::Config::Subdomain . ".yandex.ru",
        },
        ip => '4.0.0.3',    #USA
    );
    my $page     = {};
    my $pagedata = $req->{'pagedata'};

    my $gd = $req->{GeoDetection};
    #dumpit( $gd );
    #$gd->{region} = 87;
    $gd->{region_by_ip}     = 84;
    $gd->{precision}        = $gd->{precision_by_ip} = 4;
    $gd->{suspected_region} = -1;
    MordaX::init_geo_balloon($req, $page);

    my $tts = $pagedata->{citySuggest};
    ok($tts, "city suggest");
    is($tts->{cityGid}, 2,            'gid ok');
    is($tts->{type},    q{leaveCity}, 'type');

    done_testing();
};

subtest "BIG, Sverlovsk REGION, with EBurg GID" => sub {
    my $req = r(
        cookies => {
            yandexuid  => '666941071298288078',
            yandex_gid => 54,
            yp         => '2147483647.xsz.1600#2147483647.ygo.213:54',
        },
        headers => {
        },
        ip => '78.107.34.64',    #SVERDLOVS REGION
    );
    my $page     = {};
    my $pagedata = $req->{'pagedata'};
    MordaX::init_geo_balloon($req, $page);

    my $cs = $pagedata->{citySuggest};
    is($cs, undef, "no city suggest");
    done_testing();
};
subtest "BIG, SPB REGION, with Moscow GID" => sub {
    #we moved to other region so, show ballon type "2"
    my $req = r(
        cookies => {
            yandexuid  => '666941071298288078',
            yandex_gid => 213,
            yp         => '2147483647.xsz.1600#2147483647.ygo.213:54',
        },
        headers => {
        },

        ip => $geo->ip(10174),    #SPB REGION
    );
    my $page     = {};
    my $pagedata = $req->{'pagedata'};
    MordaX::init_geo_balloon($req, $page);

    my $cs = $pagedata->{citySuggest};
    # FIXME: deprication changed ip binding 78.107.34.64. need ip of SVERDLOVS REGION
    ok($cs, "city suggest");
    #is( $cs , undef                        ,   "city suggest return");
    if ($cs) {
        is($cs->{cityGid}, 213,          'gid ok');
        is($cs->{type},    q{leaveCity}, 'type');
        #
        my $os = $cs->{otherCities};
        ok($os, "other cities present");
        if ($os) {
            is(scalar @$os, 2, "othher citis have some data( 2 items)");    #
        }
    }
    done_testing();
};

subtest "Double SPB_Rregion" => sub {
    my $req = r(
        cookies => {
            yandexuid => '666941071298288078',
        },
        headers => {
        },
        ip => $geo->ip(10174),    #SPB REGION
    );
    is($req->{MordaContent}, 'big', 'MordaContentTYpe');
    my $page     = {};
    my $pagedata = $req->{'pagedata'};
    MordaX::init_geo_balloon($req, $page);
    my $cs = $pagedata->{citySuggest};
    # FIXME: deprication changed ip binding 78.107.34.64. need ip of SVERDLOVS REGION
    ok($cs, "city suggest returns");
    #dmp( $cs );
    #is( $cs , undef                        ,   "city suggest");
    if ($cs) {
        is($cs->{cityGid}, 2,           'gid ok');
        is($cs->{type},    q{thisCity}, 'type');
        #
        my $os = $cs->{otherCities};
        ok($os, "other cities present");
        if ($os) {
            ok(scalar @$os, 'other citis have some data');
            my $eburg_count = scalar grep { $_ == 2 } @$os;
            is($eburg_count, 0, " no samara in other cities");

        }
    }

    done_testing();

};
subtest "Double Samara, mobie" => sub {
    my $req = r(
        cookies => {
            yandexuid => '666941071298288078',
        },
        headers => {
            host => "m" . $MordaX::Config::InstanceModifier . $MordaX::Config::Subdomain . ".yandex.ru",
        },
        ip => $geo->ip(10174),    #Samara REGION
    );
    is($req->{MordaContent}, 'mob', 'MordaContentTYpe');
    my $page     = {};
    my $pagedata = $req->{'pagedata'};
    MordaX::init_geo_balloon($req, $page);
    my $cs = $pagedata->{citySuggest};
    ok($cs, "city suggest");
    #is( $cs , undef                        ,   "city suggest");
    if ($cs) {
        is($cs->{cityGid}, 2,           'gid ok');
        is($cs->{type},    q{thisCity}, 'type');
    }

    done_testing();

};

SKIP: {
    #skip 'Sugest field in geobase damadjed by movesjan@', 1;
    subtest "10 items in city suggest for FarEast region" => sub {
        my $req = r(
            cookies => {
                yandexuid => '666941071298288078',
            },
            headers => {
            },
            ip => $geo->ip(73),    #SAMARA REGION
        );
        my $page     = {};
        my $pagedata = $req->{'pagedata'};
        MordaX::init_geo_balloon($req, $page);
        my $cs = $pagedata->{citySuggest};
        ok($cs, "city suggest");
        if ($cs) {
            my $os = $cs->{otherCities};
            ok($os, "other cities present");
            if ($os) {
                is(scalar @$os, 10, 'other citis have some data 10 items');
            }
        }
        done_testing();
    };
}
done_testing();

