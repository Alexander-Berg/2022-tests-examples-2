#!/usr/bin/perl

=h1 ISSUES

HOME-7989
HOME-7824

=cut

use strict;
use warnings;

use lib::abs qw(.);

use MordaTest;
use testlib::TestRequest qw(r);

use Test::More;
require HelloWorld;
require Handler::Gpsave;

use Data::Dumper;
use MordaX::Logit qw(logit dumpit);

*gpsave_data = *Handler::Gpsave::gpsave_data;

use testlib::GeoHelper;

my $gh = testlib::GeoHelper->new();

ok($gh, 'testlib::GeoHelper');
#fisrt request;
$MordaX::Errorlog::setuplogging{debug} = 0;

subtest "A1" => sub {
    my $r = request(get => {add => 1233});
    #warn Dumper( {'main' => '' }, $r );

    my $response = gpsave_data($r);
    plan tests => 3;

    ok($response);
    ok($response->{error});
    is($response->{gpauto}, undef);
};

#second request;
subtest "A2" => sub {
    my $r0 = request(
        cookies => {
            yandexuid => '666941071298288078',
          }
    );

    my $r = request(
        get => {
            sk        => MordaX::Utils::sk_gen($r0),
            lat       => 55.980875,
            lon       => 37.17938,
            precision => 10,
            device    => 1,
        },
        cookies => {
            yandexuid => '666941071298288078',
        },
        ip => $gh->ip(35),    #krasondar!!
    );

    subtest "test request" => sub {
        #plan tests => 9;
        #is($r->{RemoteIp}, '::ffff:62.183.64.27', 'IP');
        ok($r->{time}, "time in request");
        ok($r->{Getargshash});
        ok($r->{Getargshash}->{sk}, 'yu in get args');

        is($r->{Domain},    'yandex.ru',        'yandex.ru');
        is($r->{yandexuid}, 666941071298288078, 'yandex uid');
        is($r->{yu},        'b9423d792cd1da4fb5147958e050b314');

        is($r->{GeoDetection}->{region}, 35, 'krasnodar');

        #dumpit( $r->{GeoDetection} ) ;

        done_testing();

    };
    subtest "test response" => sub {
        my $resp = gpsave_data($r);

        #plan tests => 9;
        ok($resp);
        is($resp->{error}, undef, 'no error');
        ok($resp->{gpauto}, 'Have gpauto');
        #diag($resp->{gpauto});
        {
            local $TODO = "wait 216 -> 213";
            is($resp->{region}, 216, "zelenograd");
        }
        is($resp->{format},   'json', "json format by default");
        is($resp->{language}, 'ru',   'ru language for .ru');

        is($r->{'YCookies'}->value('gpauto'), $resp->{gpauto}, "gp auto setted");
        is($resp->{region_changed},           1,               'region changed');
        is($resp->{should_reload},            1,               'should reload');

        ok($r->ycookies()->value('gpauto'), 'gpauto setted');

        my $detection2 = Geo::get_geo_code_by_request($r);
        #diag( "GPAUTO:" . $r->ycookies()->value('gpauto') );
        #diag( "YS :" .$r->ycookies()->{ys} );
        #dumpit( $detection2 ,
        #    $r->ycookies()
        #) ;

        done_testing();

    };
    done_testing();
};
subtest "A3" => sub {
    my $r0 = request(
        cookies => {
            yandexuid => '666941071298288078',
        },
    );
    my $req = request(
        get => {
            sk        => MordaX::Utils::sk_gen($r0),
            lat       => 55.980875,
            lon       => 37.17938,
            precision => 10,
            device    => 1,
            lang      => 'tr',
        },
        ip      => $gh->ip(213),
        cookies => {
            yandexuid => '666941071298288078',
        },
    );
    my $resp = gpsave_data($req);

    is($resp->{language}, 'tr', 'turkich language for interface');
    {
        local $TODO = "wait for 216 instead of 213";
        like($resp->{region_name}, qr/^Zeleno/, 'Zelenorgad in translit');
    }
    done_testing();
};
subtest "A3, with yandex gid" => sub {
    my $r0 = request(
        cookies => {
            yandexuid => '666941071298288078',
        },
    );

    my $req = request(
        get => {
            sk        => MordaX::Utils::sk_gen($r0),
            lat       => 55.980875,
            lon       => 37.17938,
            precision => 10,
            device    => 1,
            status    => 0,
            lang      => 'tr',
        },
        ip      => $gh->ip(213),
        cookies => {
            yandexuid  => '666941071298288078',
            yandex_gid => 2,
        },
    );
    my $resp = gpsave_data($req);
    plan tests => 4;
    {
        local $TODO = "wait for 216 instead of 213";
        like($resp->{region_name}, qr/^Zeleno/, 'Zelenorgad in translit');
        is($resp->{region}, 216, 'region Zelenograd');
    }
    is($resp->{region_changed}, 1, 'region changed');
    is($resp->{should_reload},  0, 'should reload');

};
subtest "B1" => sub {
    #bad request
    my $req = request(
        get => {
            yu  => 'b9423d792cd1da4fb5147958e050b314',
            lat => 55.980875,
#               lon         => 37.17938,
            precision => 10,
            device    => 1,
            status    => 3,
        },
        ip      => $gh->ip(213),
        cookies => {
            yandexuid => '666941071298288078',
        },
    );
    my $resp = gpsave_data($req);

    is($resp->{in}->{device}, '93', 'status pased');
    ok($resp->{in}->{lat});
    #ok($resp->{in}->{lon});
    isnt($resp->{in}->{lat}, 55.980875, 'Lat not for Zelik');
    #ok($resp->{gpauto}, "gpauto stetted");
    is($resp->{region}, '213', 'Default is moscow');

    is($resp->{region_changed}, 0, 'region changed');
    is($resp->{should_reload},  0, 'should reload');
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
