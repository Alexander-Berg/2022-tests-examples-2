#!/usr/bin/perl

=h1 ISSUES

HOME-10182

=cut

use utf8;
use strict;
use warnings;

use lib::abs qw( ./ ../t/testlib );

use MordaTest;
use testlib::TestRequest qw(r);

use Test::More;
require HelloWorld;
require Handler::Gpsave;

use Data::Dumper;
use MordaX::Logit qw(logit dumpit);

$MordaX::Errorlog::setuplogging{debug} = 0;

*gpsave_data = *Handler::Gpsave::gpsave_data;

subtest "mobile mode & rewrite cookie" => sub {
    my $req = r(
        get => {
            yu        => 'b9423d792cd1da4fb5147958e050b314',
            lat       => 55.980875,
            lon       => 37.17938,
            precision => 10,
            device    => 1,
            mobile    => 1,
        },
        cookies => {
            yandexuid  => '666941071298288078',
            yandex_gid => '2',
        },
        ip => '62.183.64.27',    #KRASONDAR
    );
    # expecting 216 Zelik
    my $resp = gpsave_data($req);
    ok($resp->{mobile});
    {
        local $TODO = "wait fix Zelenograd instead of Mosckow";
        is($resp->{region}, '216'),
          is($resp->{im_in_region}, 'Я в Зеленограде');
    }

    ok($resp->{region_changed});
    ok($resp->{should_reload}, 'should reload!');
    ok($resp->{cookies});

    #dumpit( $resp );
    #dumpit( $req->{YCookie} );
    ok(scalar(grep {m/yandex_gid=/} @{$resp->{cookies}}), 'gid');

    ok($req->ycookies->yp_changed(), "YP changed");
    is($req->ycookies->yp('ygu'), 1, "YGU 1 in Yp");
    ok($req->ycookies->yp('gpauto'), "GPauto in Yp");

    #ok( scalar( grep {m/ygu\./} @{$resp->{cookies}} )            , 'ygu');
    #ok( scalar( grep {m/yp=.*gpauto\./} @{$resp->{cookies}} )         , 'gpauto persistent');

    done_testing();

};

subtest "mobile set without coordinates" => sub {
    my $req = r(
        get => {
            yu     => 'b9423d792cd1da4fb5147958e050b314',
            lat    => '55.980875',
            lon    => 'i37.17938',
            device => 1,
            status => 3,
            mobile => 1,
        },
        cookies => {
            yandexuid  => '666941071298288078',
            yandex_gid => '2',
        },
        ip => '62.183.64.27',
    );
    my $r = gpsave_data($req);
    is(scalar @{$r->{cookies}}, 0, 'no cookies to set');
    is($r->{region},            2, 'gid region');

    done_testing();
};

subtest "precision erorr" => sub {
    my $r = r(
        get => {
            yu  => 'b9423d792cd1da4fb5147958e050b314',
            lat => 55.980875,
            lon => 37.17938,
            #precision => 10,
            device => 1,
            mobile => 1,
        },
        cookies => {
            yandexuid  => '666941071298288078',
            yandex_gid => '2',
        },
        ip => '62.183.64.27',
    );
    my $resp = gpsave_data($r);
    ok($resp->{error});
    is($resp->{error}, 'bad_precision');

    done_testing();
};

done_testing();

