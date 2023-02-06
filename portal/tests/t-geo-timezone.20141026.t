#!/usr/bin/perl
use strict;
use 5.010;

use Test::More qw(no_plan);

use lib::abs qw( . ../lib );

#use_ok('InitBase');
use MordaX::Logit;
use MP::Time;
#use MP::Utils;
use_ok('Geo');
#MP::Utils::use_try 'MordaX::Utils';

#use Geo;
#use MordaX::Utils;

ok($Geo::geobase, "Geobase inited");

my $before = 1414270000;
my $after  = 1414290588;

my $times = [qw(1414267200 1414274390 1414274400 1414274410)];

#
#my $boom_lt     = MP::Time::ts_to_ltime(1414274400 - 1,             'Europe/Moscow');
#dmp
my $boom_lt_m1d = MP::Time::ts_to_ltime(1414274400 - 86400, 'Europe/Moscow');

#dmp
#my $boom_lt_m1s = {%$boom_lt_m1d, mday => $boom_lt_m1d->{mday}, sec  => 59, min=> $boom_lt_m1d->{min}-1 };
#my $boom_lt_m1s = {%$boom_lt_m1d, mday => $boom_lt_m1d->{mday}, sec  => 59, min=> $boom_lt_m1d->{min}-1 };
my $boom_lt_m1s = MP::Time::ts_to_ltime(1414274400 - 1, 'Europe/Moscow');
#dmp
my $boom_lt = {%$boom_lt_m1d, mday => $boom_lt_m1d->{mday} + 1};
#dmp
my $boom_lt_p1s = {%$boom_lt, sec => $boom_lt->{sec} + 1};

my $lts = [$boom_lt_m1s, $boom_lt, $boom_lt_p1s,];

#dmp $lts;
#dmp MP::Time::ltime_to_iso dmp MordaX::Utils::ts_to_ts dmp $_ for @$lts;
#dmp MP::Time::ltime_to_iso(MP::Time::ltime_to_iso($_)) for @$lts;
#dmp MP::Time::ltime_to_iso($_) for @$lts;
#exit;

my $data = q{
213	Europe/Moscow	3600
10857	Europe/Kaliningrad	3600		Калининградская область
11010	Europe/Moscow	3600
10174		3600
959		3600
11148		0
11131		0
11111		3600
10231		3600
10233		3600
11282		0
#21949		7200	1414252800
#11403		7200	1414245600
11443		3600
100348		3600
11450		3600
11398		0
10251		0
181		3600
157		0
};

for (grep {$_} split /\n+/, $data) {
    next if /^#/;
    my ($gid, $tz, $jump, $boom, $name) = split /\t/;
    $name ||= geo($gid, 'name');
    my $tzbase = geo($gid, 'timezone');
    is $tz, $tzbase, "gid=$gid name=$name tz=$tz tzbase=$tzbase jump=$jump" if $tz;

    $tz ||= $tzbase;
    #dmp $gid, $tz, geo($gid, 'timezone'), $jump, $name;
#dmp geo($gid, 'timezone');

#dmp MP::Time::ts_to_ltime $before, $now;
#dmp MP::Time::ts_to_iso $before, $now;
#dmp MP::Time::ts_to_iso $after, $now;
    #for my $t (@$times) {
    #    dmp 'times ', $t, MP::Time::ts_to_iso($t, $tz);
    #}

    my $t_m1s = MP::Time::ltime_to_ts($boom_lt_m1s, $tz);
    my $t_p1s = MP::Time::ltime_to_ts($boom_lt_p1s, $tz);
    $boom ||= $t_m1s + 1;

#dmp $boom, MP::Time::ts_to_iso($boom-1, $tz);
    is MP::Time::ts_to_iso($boom - 1, $tz), '2014-10-26T01:59:59', "boom: gid=$gid name=$name tz=$tz boom=$boom";
    isnt MP::Time::ts_to_iso($boom + 1, $tz), '2014-10-26T02:00:01', "boom+1 jump: gid=$gid name=$name tz=$tz boom=$boom" if $jump;
    is MP::Time::ts_to_iso($boom + 1, $tz), '2014-10-26T02:00:01', "boom+1: gid=$gid name=$name tz=$tz boom=$boom" if !$jump;

    is $boom - 1, $t_m1s, "double boom datetime " . ($boom - 1) . " $t_m1s";
    #dmp $t_m1s, $t_p1s, $t_p1s - $t_m1s;
    if (defined $jump) {
        if (!is $t_p1s - $t_m1s, $jump + 2, "jump: gid=$gid name=$name tz=$tz jump=$jump") {
#dmp 'boomlt-1', $t_m1s;
            for my $lt (@$lts) {
                my $t = MP::Time::ltime_to_ts($lt, $tz);
                dmp 'boomlt', $t, MP::Time::ts_to_iso($t, $tz), 'msk=', MP::Time::ts_to_iso($t, 'Europe/Moscow');
            }
            for my $t ($boom - 1, $boom, $boom + 1) {
                #my $t = MP::Time::ltime_to_ts($lt, $tz);
                dmp 'boom  ', $t, MP::Time::ts_to_iso($t, $tz), 'msk=', MP::Time::ts_to_iso($t, 'Europe/Moscow');
            }

            #for my $i (0..30) {
            #    my $t = 1414270800-15*3600+1 + $i*3600;
            #    dmp 'day', $t, MP::Time::ts_to_iso($t, $tz), $tz;
            #}

            for my $i (0 .. 70) {
                my $t = $t_p1s - $i * 5 * 60 - 2;
                #dmp 'day', $t, MP::Time::ts_to_iso($t, $tz), $tz;
            }

        }
    }
    #check child tz == my tz
    #for my $cid (grep {$_} map { $_, @{geo($_, 'children') || []} } map { $_, @{geo($_, 'children') || []} } map { $_, @{geo($_, 'children') || []} } @{geo($gid, 'children') || []}) {
    #    my $ctz = geo($cid, 'timezone') || Geo::timezone($cid);
    #    is $ctz, $tz, "tzchild: $cid name=" . geo($cid, 'name') . " parent=$gid";
    #}

}

my $boomtr = 1414285200;
is MP::Time::ts_to_iso($boomtr - 1, 'Europe/Istanbul'), '2014-10-26T03:59:59', "turkey -1";
# MP::Time::ts_to_iso($boomtr, 'Europe/Istanbul');
is MP::Time::ts_to_iso($boomtr + 1, 'Europe/Istanbul'), '2014-10-26T03:00:01', "turkey -1";
