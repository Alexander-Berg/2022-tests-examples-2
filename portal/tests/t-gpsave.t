#!/usr/bin/perl

=h1 ISSUES

    home-7824

=cut

use utf8;

use strict;
use warnings;
use 5.010;

use lib::abs qw(. ../lib ../t/testlib);
use Test::Most;
die_on_fail();

use MP::Logit qw(dmp logit);

dmp("привет мир", ["где этот дабл энкодинг"]);

use MordaTest;
use testlib::TestRequest qw(r);

require HelloWorld;
require Handler::Gpsave;
use testlib::GeoHelper;
my $gh = testlib::GeoHelper->new();
ok($gh, "testlib::GeoHelper online");
my $cookies = {
    yandexuid => '666941071298288078',
};
my $r_base = r(
    cookies => {
        %$cookies,
      }
);
my $sk = MordaX::Utils::sk_gen($r_base);

ok($sk, "SK generated: $sk");

#fisrt request;
$MordaX::Errorlog::setuplogging{debug} = 0;
*gpsave_data = *Handler::Gpsave::gpsave_data;

sub gpsave {
    my (%args) = @_;

    $args{cookies}->{yandexuid} = $cookies->{yandexuid};

    $args{get}->{sk} //= $sk;
    $args{ip} //= $gh->ip($args{geobyip} || 213);
    my $r = r(%args);
    my $resp = gpsave_data($r, $args{mobile});
    return {req => $r, resp => $resp};
}

sub has_cookie {
    my ($resp, $name, $test_name) = @_;
    my $set = build_cookies($resp);
    Test::More->builder->ok((scalar grep { $_ =~ /^$name=/ } @$set), $test_name || ("set cookie: $name"));
}

sub has_no_cookie {
    my ($resp, $name, $test_name) = @_;
    my $set = build_cookies($resp);
    my @rest = grep { $_ =~ /^$name=/ } @$set;
    if (scalar @rest) {
        dmp(\@rest)
    }
    Test::More->builder->is_eq((scalar @rest), 0, $test_name || "no set cookie: $name");
}

sub no_cookies {
    my ($r, $test_name) = @_;
    my $set = build_cookies($r);

    Test::More->builder->is_eq(scalar @$set, 0, $test_name);
}

sub build_cookies {
    my $r = shift;
    my $h = HTTP::Headers->new();

    MordaX::Output::set_cookies_into_header($r->{req}, $r->{resp}->{cookies}, $h);
    #dmp( $h );
    return $h->{'set-cookie'} || [];
}

subtest "secret key error" => sub {
    my $r = request(get => {add => 1233});
    #warn Dumper( {'main' => '' }, $r );

    my $response = gpsave_data($r);

    ok($response,);
    ok($response->{error});

    is($response->{error}, "yu_check_failed", "YU error");
    is($response->{gpauto}, undef);

    my $r_sk = request(get => {sk => 12132});
    my $resp_sk = gpsave_data($r_sk);
    is($resp_sk->{error}, "sk_check_failed", "SK error");
    done_testing();
};
subtest "sk error via meta function" => sub {
    my $m1 = gpsave(get => {sk => 12132});
    is($m1->{resp}->{error}, 'sk_check_failed');
    #is($m1->{cookies}, undef, "no cookies");
    no_cookies($m1);
    is($m1->{resp}->{mobile}, 0, "No mobile");
    done_testing();
};

subtest "Testing Ivalid Input" => sub {

    my $rep1 = gpsave(get => {precision => 10,}, geobyip => 216);
    #dmp( $rep1 );
    #say STDERR $rep1->{im_in_region};
    #say STDERR "Я тоже";
    #dmp( "А Я нет" , $rep1->{im_in_region} , [ $rep1->{im_in_region} ] );

    is($rep1->{resp}->{error}, undef, "lat lon no error, ");
    no_cookies($rep1);

    my $r2 = r(
        get => {
            sk     => $sk,
            lat    => 55.980875,
            lon    => 37.17938,
            device => 0,
        },
        cookies => {
            %$cookies,
        },
        ip => $gh->ip(213),
    );

    my $rep2 = gpsave_data($r2);

    is($rep2->{error}, "bad_precision", "accuracy error");
    is(@{$rep2->{cookies}}, 0, "No cookies to set");

};

#second request;
subtest "A2" => sub {

    my $r = request(
        get => {
            sk        => $sk,
            lat       => 55.980875,
            lon       => 37.17938,
            precision => 10,
            device    => 0,
        },
        cookies => {
            %$cookies,
        },
        ip => $gh->ip(35),    #'62.183.64.27', #region 35
    );

    subtest "test requst" => sub {
        ok($r->{RemoteIp}, 'IP');
        ok($r->{time},     "time in request");
        ok($r->{Getargshash});
        ok($r->{Getargshash}->{sk}, 'sk in get args');
        ok($r->{sk_param},          'sk passed with get');

        is($r->{Domain},    'yandex.ru',        'yandex.ru');
        is($r->{yandexuid}, 666941071298288078, 'yandex uid');
        #is( $r->{yu}, 'b9423d792cd1da4fb5147958e050b314' );
        done_testing();

    };
    subtest "test response" => sub {
        my $resp = gpsave_data($r);

        ok($resp);
        is($resp->{error}, undef, 'no error');
        ok($resp->{gpauto}, 'Have gpauto');
        diag($resp->{gpauto});
        {
            local $TODO = "Waiting for RegionEdge update";
            is($resp->{region}, 216, "zelenograd");
        }
        is($resp->{format},   'json', "json format by default");
        is($resp->{language}, 'ru',   'ru language for .ru');

        ok($r->{'YCookies'}, 'have YCookies');
        is($r->{'YCookies'}->value('gpauto'), $resp->{gpauto}, "gp auto setted");
        is($resp->{region_changed},           1,               'region changed');
        is($resp->{should_reload},            1,               'should reload');
        is($resp->{poor_precision},           0,               'good precision');

        done_testing();

    };
    done_testing();
};
subtest "A3" => sub {
    my $req = request(
        get => {
            sk        => $sk,
            lat       => 55.980875,
            lon       => 37.17938,
            precision => 10,
            device    => 0,
            lang      => 'tr',
        },
        cookies => {
            %$cookies,
        },
        ip => $gh->ip(213),    #'178.167.0.199',
                               #works with 2 and 1 , but not with 213
    );
    my $resp = gpsave_data($req);

    plan tests => 2;
    is($resp->{language}, 'tr', 'turkey language for interface');
    local $TODO = "Waiting reigon edges update";
    like($resp->{region_name}, qr/^Zeleno/, 'Zelenorgad in translit');
};
subtest "A3, with yandex gid" => sub {
    my $req = request(
        get => {
            yu        => 'b9423d792cd1da4fb5147958e050b314',
            lat       => 55.980875,
            lon       => 37.17938,
            precision => 10,
            device    => 0,
            status    => 0,
            lang      => 'ru',
        },
        cookies => {
            %$cookies,
            yandex_gid => 2,
        },
        #ip => $gh->ip(1),
        ip => $gh->ip(213),
    );
    my $resp = gpsave_data($req);
    plan tests => 8;
    #dumpit( $resp );
  SKIP: {
        #local $TODO = "do it !!";
        skip 'not ready', 2;
        is($resp->{language}, 'ru', 'for incorrec language will be returned RU');
        ok($resp->{region_preposition}, 'preposition');
    }

    ok($resp->{region_locative}, ' locative');
    ok($resp->{region_dative},   ' dative');

    {
        local $TODO = "Waiting for Region Edges update";
        like($resp->{region_name}, qr/^Зелено/, 'Zelenorgad in translit');
        is($resp->{region}, 216, 'region Zelenograd');
    }
    is($resp->{region_changed}, 1, 'region changed');
    is($resp->{should_reload},  0, 'should reload');

};
subtest "B1" => sub {
    #bad request
    my $req = request(
        get => {
            #yu          => 'b9423d792cd1da4fb5147958e050b314',
            yu  => '666941071298288078',
            lat => 55.980875,
#               lon         => 37.17938,
            precision => 10,
            device    => 1,
            status    => 3,
        },
        cookies => {
            yandexuid => '666941071298288078',
        },
    );
    my $resp = gpsave_data($req);

    ok($req->{yandexuid}, 'Grabx yande uid from cookie to request');
    ok($req->{yu});
    ok($req->{yu_param});
    is($resp->{error}, undef, ' No Error, so yu is yandexuid passed ');

    is($resp->{in}->{device}, '93', 'status pased');
    ok($resp->{in}->{lat});
    #ok( $resp->{in}->{lon} );
    isnt($resp->{in}->{lat}, 55.980875, 'Lat not for Zelik');
    #ok( $resp->{gpauto}, "gpauto stetted");
    is($resp->{region}, '213', 'Default is moscow');

    is($resp->{region_changed}, 0, 'region changed');
    is($resp->{should_reload},  0, 'should reload');
    done_testing();
};

subtest "Accuracy Test 1m-10k" => sub {
    my %ll215 = (lat => 56.748032050802614, lon => 37.15418528222419,);
    my $a1 = gpsave(get => {%ll215, precision => 1,}, geobyip => 225);
    #dmp( $a1->{resp}, $a1->{req} );
    has_cookie($a1, 'yp');
    is($a1->{resp}->{no_gpauto},      undef);
    is($a1->{resp}->{region},         215);
    is($a1->{resp}->{poor_precision}, 0, " 1m ok");

    my $a100 = gpsave(get => {%ll215, precision => 100,}, geobyip => 225);
    has_cookie($a100, 'yp');
    is($a100->{resp}->{no_gpauto},      undef);
    is($a100->{resp}->{region},         215);
    is($a100->{resp}->{poor_precision}, 0, " 100m ok");

    my $a999 = gpsave(get => {%ll215, precision => 999,}, geobyip => 225);
    has_cookie($a999, 'yp');
    is($a999->{resp}->{no_gpauto},      undef);
    is($a999->{resp}->{region},         215);
    is($a999->{resp}->{poor_precision}, 0, " 999m ok");

    my $a2k = gpsave(get => {%ll215, precision => 1999,}, geobyip => 225);
    has_cookie($a2k, 'yp');
    is($a2k->{resp}->{no_gpauto},      undef);
    is($a2k->{resp}->{region},         215);
    is($a2k->{resp}->{poor_precision}, 0, " 2k- ok");

    my $a3k = gpsave(get => {%ll215, precision => 2999,}, geobyip => 225);
    has_cookie($a3k, 'yp');
    is($a3k->{resp}->{no_gpauto},      undef);
    is($a3k->{resp}->{region},         215);
    is($a3k->{resp}->{poor_precision}, 0, " 3k- ok");

    local $TODO = "Laas ignore accuracy :(";
    $a3k = gpsave(get => {%ll215, precision => 3003,}, geobyip => 225);
    #dmp( $a1->{resp}, $a1->{req} );
    has_cookie($a3k, 'yp');
    is($a3k->{resp}->{no_gpauto},      undef);
    is($a3k->{resp}->{region},         213);
    is($a3k->{resp}->{poor_precision}, 1, "4k poor");

    my $a4k = gpsave(get => {%ll215, precision => 3999,}, geobyip => 225);
    #dmp( $a1->{resp}, $a1->{req} );
    has_cookie($a4k, 'yp');
    is($a4k->{resp}->{no_gpauto},      undef);
    is($a4k->{resp}->{region},         213);
    is($a4k->{resp}->{poor_precision}, 1, "4k poor");

    my $a5k = gpsave(get => {%ll215, precision => 4999,}, geobyip => 225);
    #dmp( $a1->{resp}, $a1->{req} );
    has_cookie($a5k, 'yp');
    is($a5k->{resp}->{no_gpauto},      undef);
    is($a5k->{resp}->{region},         213);
    is($a5k->{resp}->{poor_precision}, 1, "5k poor");

    my $a10k = gpsave(get => {%ll215, precision => 10000,}, geobyip => 225);
    #dmp( $a1->{resp}, $a1->{req} );
    has_cookie($a10k, 'yp');
    is($a10k->{resp}->{no_gpauto},      undef);
    is($a10k->{resp}->{region},         213);
    is($a10k->{resp}->{poor_precision}, 1, "10k poor");

    done_testing();

};
subtest "Accuracy with former gpautocookies" => sub {

    my %ll215 = (lat => 56.748032050802614, lon => 37.15418528222419,);
    my $old = (time + 10000) . ".gpauto.56_840775982402484:35_94121673:20:0:" . (time - 1000);    #harkiv

    sub test {
        my ($ok, $r) = @_;
        my $tb = Test::More->builder;

        $tb->is_eq($r->{resp}->{should_reload}, 1, 'should reload');
        $tb->is_eq($r->{resp}->{region},         $ok ? 215 : 14, "region");
        $tb->is_eq($r->{resp}->{poor_precision}, $ok ? 0   : 1,  "poor presicion");
    }

    my $r0 = r(cookies => {yp => $old});
    #dmp( $r0 );
    ok($r0->ycookies()->value('gpauto'), 'Gpauto in cookies');
    #dmp( $r0->{GeoDetection} );
    my $g1 = gpsave(get => {%ll215, precision => 1,}, cookies => {yp => $old}, geobyip => 1);

    test(1, $g1);

    my $g2000 = gpsave(get => {%ll215, precision => 2000,}, cookies => {yp => $old}, geobyip => 1);
    test(1, $g2000);

    #my $g3000    = gpsave( get => { %ll215, precision => 3000, }, cookies => { yp => $old }, geobyip => 1 );
    #test( 1, $g3000 );

    my $g3003 = gpsave(get => {%ll215, precision => 3003,}, cookies => {yp => $old}, geobyip => 1);
    test(0, $g3003);

    my $g5000 = gpsave(get => {%ll215, precision => 5000,}, cookies => {yp => $old}, geobyip => 1);
    test(0, $g5000);

    my $g10000 = gpsave(get => {%ll215, precision => 10000,}, cookies => {yp => $old}, geobyip => 1);
    test(0, $g10000);

};

subtest "Gpsave, MGPsave" => sub {

    my %get215 = (lat => 56.748032050802614, lon => 37.15418528222419, precision => 100, device => 2);

    my $big = gpsave(get => {%get215, mobile => 0}, cookies => {'yandex_gid' => 101754}, geobyip => 225,);

    ok(!$big->{resp}->{mobile}, "big call");

    is($big->{resp}->{should_reload},  0, "Big: no reload via yandexuid");
    is($big->{resp}->{region_changed}, 1, "Big: region changeed, should change mannually");
    has_no_cookie($big, 'yandex_gid');
    has_cookie($big, 'yp');

    my $mob = gpsave(get => {%get215, mobile => 1}, cookies => {'yandex_gid' => 101754}, geobyip => 225,);
    ok($mob->{resp}->{mobile}, "Mobile call");
    is($mob->{resp}->{should_reload},  1, "mob: reload , ignore yandex_gid");
    is($mob->{resp}->{region_changed}, 1, "mob: region changeed, should change mannually");
    has_cookie($mob, 'yandex_gid');
    has_cookie($mob, 'yp');

};

subtest "Ocean 10km precision" => sub {
    # http://www-dev24.wdevx.yandex.ru/gpsave?lat=59.212306168972&lon=39.910414748992&precision=25000&device=0&format=JSONP&callback=happyEnd&lang=ru&yu=6d6c4fa2328075b7d1f955f92ee5a0bc
    my $req = request(
        get => {
            yu        => 'b9423d792cd1da4fb5147958e050b314',
            lat       => 59.212306168972,
            lon       => 39.910414748992,
            precision => 25000,
            device    => 1,
            status    => 3,
        },
        cookies => {
            yandexuid  => '666941071298288078',
            yandex_gid => 54,
            yp         => '2147483647.xsz.1280:2147483647.ygo.11162:54',
        },
        ip => $gh->ip(11162),    #"217.66.146.70", #SEVEROZAPAD SPB REGION
    );

    my $resp = gpsave_data($req);
    #dmp( $resp );
    is($resp->{poor_precision}, 1,     'poor precision');
    is($resp->{distance},       undef, 'No distance for low precision');
    done_testing();

};

sub gpfresh {
    my $ts  = $_[1] || time;
    my $exp = $ts + 100000;
    my $yp  = $_[0];
    $yp =~ s/(\d+).gpauto\.(([^:]+:){4})\d+/$exp.gpauto.$2$ts/;
    return $yp;
}

subtest "Distance" => sub {
    my $great = gpsave(
        get => {
            precision => 2000,
            lat       => 55.928698985443916,
            lon       => 36.606928812500000
        },
        geobyip => 213,
        cookies => $cookies,
    );
    is($great->{resp}->{distance_great}, 1, "Great Distance ok");
    ok($great->{resp}->{distance}, 'distance by 2000m ok');

    my $move = gpsave(
        get => {
            lat       => 55.9826297237657,
            lon       => 36.450373636718545,
            precision => 600,
            sk        => $sk,
        },
        cookies => {
            yp => gpfresh('1436106664.gpauto.55_928698985443916:36.6069288125:50:3:1435933864'),
            %$cookies,
        },
        geobyid => 213,
    );

    is($move->{resp}->{distance},       11442);
    is($move->{resp}->{distance_great}, undef);

    #102560

    done_testing();
};

done_testing();
#-----------------------------------------------------------
#-------------------------------------- xxx
#-----------------------------------------------------------
sub request {
    r(@_);
    #testlib::TestRequest->request( @_ );
}
