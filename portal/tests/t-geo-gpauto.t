#!/usr/bin/perl

use Test::More;
use lib::abs qw( . ../lib );
use 5.010;

#use_ok('InitBase');
use MordaX::Logit qw(dumpit dmp logit);
MordaX::Logit::enable_dumpit();

use_ok('Geo');
use_ok('testlib::GeoHelper');

my $geo = testlib::GeoHelper->new();
diag('this lib test of use GPAUTO ycookie');

my $ip213 = $geo->ip(213);
my $core  = {
    ip   => $ip213,
    'yp' => (time() + 100) . '.gpauto.44_944251449699415:34_10204596817494:300:1:' . time() . '',
};
# non yandex gid call
my $r = Geo::get_geo_code_core(%$core);
#dmp( $r );
is($r->{region}, 146, 'A: Simferopol by GpAuto');
#AFTER LAAS region by ip is usless
#is( $r->{region_by_ip}      , 213   , "A: Mosow by IP");
is($r->{suspected_region}, -1, 'A: no Suspected region');
my $r_gid = Geo::get_geo_code_core(%$core, gid => 47);
is($r_gid->{region}, 47, 'B: Novgorod by  by GID');
#is( $r_gid->{region_by_ip}      , 213   , "B: Mosow by IP");

TODO: {
    #local $TODO = "expecting new geobase";
    #is( $r_gid->{suspected_region}  , -1    , 'B: no Suspected region' );

    is($r_gid->{suspected_region}, 146, 'B: no Suspected region');
}

my $r_bad = Geo::get_geo_code_core(
    ip   => $ip213,
    gid  => 47,
    'yp' => (time() + 100) . '.gpauto.44_944251449699415:34_10204596817494:300:1:' . time() . '#2147483647.ygo.213:47',
);
is($r_bad->{region}, 47, 'C: Novgorod by  by GID');
#is( $r_bad->{region_by_ip}      , 213   , "C: Mosow by IP");
TODO: {
    local $TODO = "expecting no susspected region by ip (LAAS-21)" if ($Geo::laas);
    is($r_bad->{suspected_region}, -1, 'C: Simferopol is Suspected by GP AUTO');
}

done_testing();

