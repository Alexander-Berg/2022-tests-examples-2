#!/usr/bin/perl

use strict;
use warnings;
no warnings qw(uninitialized);
#use Test::More tests => 8;
use Test::More qw(no_plan);
#use Test::Output;

use Time::HiRes qw(gettimeofday tv_interval);
use lib::abs qw(../lib);
use Data::Dumper;
use Net::Netmask;
use constant IP => '93.158.134.11';
use constant ALARM_TIMEOUT => 20;

use_ok("Geo::ConfigParser");

# main auto test for geodatafile

my $geobaseconf = $ARGV[0] || lib::abs::path("../etc/geobase.conf");
ok($geobaseconf, "Geobaseconf: $geobaseconf");
my $config = Geo::ConfigParser::parse($geobaseconf);
ok($config);
unless ($config) {
    die("Config $geobaseconf not found");
}
my $geodata_file = $config->{data_file};

ok(-f $geodata_file, 'file found: ' . $geodata_file);
ok($_ = -s $geodata_file, "file size [$_]");

use_ok 'geobase5';
our $geobase;
our $region = geobase5::region->new();
ok($region, 'Region object inited');

#LOAD
my $geobase_load_errors = undef;
my $geobase_loaded_fast = 0;
my $cmd                 = qq{perl -e 'use geobase5; geobase5::lookup->new("$geobaseconf");' 2>&1};
eval {
    local $SIG{ALRM} = sub { die "ALARMed" };
    alarm ALARM_TIMEOUT;
    $geobase_load_errors = `$cmd`;
    alarm 0;
    $geobase_loaded_fast = 1;

    #combined_is( sub { $geobase =  geobase5::lookup->new($geodata_file); }, ''          , 'geobase do not fail in stderr');
    #$geobase =  geobase5::lookup->new($geodata_file);
};
alarm 0;
warn "run: $cmd" if !is($@, '', "no eval error");
is($geobase_load_errors, '', 'no warns or errors');
ok($geobase_loaded_fast, sprintf('geobase loaded in %d seconds', ALARM_TIMEOUT));
if ($geobase_load_errors or !$geobase_loaded_fast) {
    diag('Epic fail of load geobase in 10 seconds');
    exit 199;
}

eval {
    $geobase = geobase5::lookup->new($geobaseconf);
};
is($@, '', "no eval error");

ok($geobase, "load base ok");
unless ($geobase) {
    diag('Epic fail of load geobase in 10 seconds');
    exit 200;
}
$geobase->set_new_geolocation_used(1);

#SEARCH BY IP
my $geobase_ip_resolve_start = [gettimeofday];
#stderr_is( sub { $_ = $geobase->region_id(IP) }, '', 'no SDDERR BLA BLA');
#stdout_is( sub { $_ = $geobase->region_id(IP) }, '', 'no STDOUT BLA BLA');
$_ = $geobase->region_id(IP);
ok $_ , "geo [$_]";
cmp_ok(tv_interval($geobase_ip_resolve_start), '<', 0.1, 'serch region by ip less then 10 milliseconds,');

#SEARCH BY GID
my $geobase_geo_name_start = [gettimeofday];
$geobase->region_by_id(213, $region);
#stderr_is( sub { $geobase->region_by_id( 213 , $region) }, ''                       , 'no STDERR Blablabla');
ok($region->name(), 'Get Moscow name');
cmp_ok(tv_interval($geobase_geo_name_start), '<', 0.1, 'region name by gid less then 10 milliseconds,');

#SEARCH by BAD IP
ok !($_ = $geobase->region_id('ggg')), "geo [$_]";

# Yandex networks could be mapped to real geolocation, must be skipped
my $yandex_network1 = Net::Netmask->new('172.24.0.0/13');
my $yandex_network2 = Net::Netmask->new('10.208.0.0/12');

for my $block (qw{172.16.0.0/12 192.168.0.0/16 10.0.0.0/8}) {
    ok 1, "Checking subnet $block";
    my $net  = Net::Netmask->new($block);
    my $size = $net->size();
    for (my $i = 0; $i < $size; $i += 256) {
        for (-2, 1, 127) {
            my $ip = $net->nth($i + $_);
            #skip Yandex networks
            next if $yandex_network1->match($ip);
            next if $yandex_network2->match($ip);
            my $r = $geobase->region_id($ip);
            if ( $r and $r != 10000 ) {
                fail("geobase5 internal IP "
                      . $ip
                      . " assigned to region: "
                      . $r
                  );
            }
        }
    }
}

{
    my $geolocation = geobase5::geolocation->new();
    my $data = geobase5::geolocation_search_data->new();
    $data->set_ip(IP);

    local $SIG{ALRM} = sub { die 'timeout' };
    alarm 1;
    my $result;
    eval {
        $result = $geobase->pinpoint_geolocation($data, '', '', $geolocation);
        alarm 0;
    };
    alarm 0;

    is($@, '', 'pinpoint_geolocation - no eval error');
    is($result, 1, 'pinpoint_geolocation')
}
