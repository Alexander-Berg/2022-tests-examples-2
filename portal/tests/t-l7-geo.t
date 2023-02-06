#!/usr/bin/perl

use strict;
use warnings;
no warnings qw(uninitialized);
use utf8;
use lib::abs qw{../lib ../t/testlib .};
use Test::More;
use Test::Deep;
#use MordaX::Utils qw(xclone);

use MP::Logit qw(logit dmp);
use testlib::GeoHelper;

use testlib::TestRequest qw(r);
use MordaTest;    #:(
use MordaX::Config;

$MordaX::Config::DevInstance = 1;

my $r = r(headers => {'X-Region-City-Id' => 2});
my $geo = $r->{GeoDetectionByLaas} || $r->{GeoDetection};
is($geo->{region},   2, 'region ok');
is($geo->{balancer}, 0, 'balancer branch');

sub L7_geo {
    my ($headers, $detection, $name) = @_;
    #diag("Start $name");
    my ($r, $input) = r(headers => $headers, time => 1437057799);
    #push @$store, $r, $input ;
    my $geo = $r->{GeoDetectionByLaas} || $r->{GeoDetection};

    #dmp( $geo, $detection );
    if (!cmp_deeply($geo, $detection, $name)) {
        dmp('Deep Error', $headers, $geo);
    }
    #return $geo;

}

L7_geo(
    {'X-Region-City-Id' => 2},
    {
        ok           => 1,
        laas         => 1,
        balancer     => 0,
        region       => 2,
        region_by_ip => 2,
        'lat'        => '59.938531',
        'lon'        => '30.313497',
    },
    'City Only',
);
L7_geo(
    {
        'X-Region-Precision' => 3,
        'X-Region-City-Id'   => 215,
        'X-Region-Id'        => 1,
    },
    {
        ok                => 1,
        laas              => 1,
        balancer          => 0,
        region            => 215,
        region_by_ip      => 215,
        pure_region       => 1,
        pure_region_by_ip => 1,
        precision         => 3,
        precision_by_ip   => 3,
        'lat'             => '56.733793',
        'lon'             => '37.155156',
    },
    'City + precision'
);

L7_geo(
    {
        'X-Region-Precision' => 3,
        'X-Region-City-Id'   => 215,
        'X-Region-Id'        => 1,
        'X-Region-Location'  => "100.3434, 123.23432",
    },
    {
        ok                => 1,
        laas              => 1,
        balancer          => 0,
        region            => 215,
        region_by_ip      => 215,
        pure_region       => 1,
        pure_region_by_ip => 1,
        precision         => 3,
        precision_by_ip   => 3,
        lat               => 100.3434,
        lon               => 123.23432,
    }
);
L7_geo(
    {
        'X-Region-Precision' => 3,
        'X-Region-City-Id'   => 215,
        'X-Region-Id'        => 1,
        'X-Region-Location'  => "100.3434, 123.23432, 300, 15",
        'Cookie'             => 'ys=gpauto.100_3434:123_23432:300:3:1437057799',
    },
    {
        ok                => 1,
        laas              => 1,
        balancer          => 0,
        region            => 215,
        region_by_ip      => 215,
        pure_region       => 1,
        pure_region_by_ip => 1,
        precision         => 3,
        precision_by_ip   => 3,
        lat               => 100.3434,
        lon               => 123.23432,
        'gpauto'          => {
            'acc'        => 300,
            'age'        => 1,
            'gpauto_age' => 1,
            'lat'        => '100.3434',
            'lib_ok'     => 1,
            'lon'        => '123.23432',
            'ok'         => 1
        },
    },
    'GpAuto Exactly as Headers'
);

L7_geo(
    {
        'X-Region-Precision' => 3,
        'X-Region-City-Id'   => 215,
        'X-Region-Id'        => 1,
        'X-Region-Location'  => "100.3434, 123.23432, 300, 15",
    },
    {
        ok                => 1,
        laas              => 1,
        balancer          => 0,
        region            => 215,
        region_by_ip      => 215,
        pure_region       => 1,
        pure_region_by_ip => 1,
        precision         => 3,
        precision_by_ip   => 3,
        lat               => 100.3434,
        lon               => 123.23432,
        'gpauto'          => {
            'acc'    => 300,
            'age'    => 15,
            'lat'    => '100.3434',
            'lib_ok' => 1,
            'lon'    => '123.23432',
            'ok'     => 1
        },
    },
    'GpAuto deffers from headers but still gpauto',
);

L7_geo(
    {
        'X-Region-Precision' => 3,
        'X-Region-City-Id'   => 215,
        'X-Region-Id'        => 1,
        'X-Region-Location'  => "100.3454, 123.23432, 300, 15",
        'Cookie'             => 'ys=gpauto.100_3434234:123_23432234:300:3:1437057799',
    },
    {
        ok                => 1,
        laas              => 1,
        balancer          => 0,
        region            => 215,
        region_by_ip      => 215,
        pure_region       => 1,
        pure_region_by_ip => 1,
        precision         => 3,
        precision_by_ip   => 3,
        lat               => 100.3454,
        lon               => 123.23432,
        'gpauto'          => {
            'acc'        => 300,
            'age'        => 1,
            'gpauto_age' => 1,
            'lat'        => '100.3434234',
            'lon'        => '123.23432234',
            'lib_ok'     => 0,
            'ok'         => 0
        },
    },
    'Different values in gpauto and headers'
);

done_testing();
