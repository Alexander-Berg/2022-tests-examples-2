package TimeTests;

use strict;
use warnings;
use utf8;
use v5.14;

use POSIX qw(strftime tzset uname);

use constant TS => qw(
  1017849295
  1049385295
  1080921295
  1112457295
  1143993295
  1175529295
  1207065295
  1238601295
  1270137295
  1301673295
  1333209295
  1364745295
  1396281295
  1427817295
  1459353295
  1470585295
  1473177295
  1475769295
  1478361295
  1480953295
  1483545295
  1486137295
  1488729295
  1490889295
  1491321295
  1493913295
  1496505295
  1499097295
  1501689295
  1504281295
  1506873295
  1509465295
  1512057295
  1514649295
  1517241295
  1519833295
  1520697295
  1520783695
  1520870095
  1520956495
  1521042895
  1521129295
  1521215695
  1521302095
  1521388495
  1521474895
  1521561295
  1521647695
  1521734095
  1521820495
  1521906895
  1521993295
  1522079695
  1522166095
  1522252495
  1522338895
  1522353295
  1522356895
  1522360495
  1522364095
  1522367695
  1522371295
  1522374895
  1522378495
  1522382095
  1522385695
  1522389295
  1522392895
  1522396495
  1522400095
  1522403695
  1522407295
  1522410895
  1522414495
  1522418095
  1522421695
  1522425295
  1522425295
  1522425295
  1522425295
  1522428895
  1522432495
  1522436095
  1522439695
  1522443295
  1522511695
  1522598095
  1522684495
  1522770895
  1522857295
  1525017295
  1527609295
  1530201295
  1532793295
  1535385295
  1553961295
  1585497295
  1617033295
  1648569295
  1680105295
  891705295
  923241295
  954777295
  986313295
);
use constant TZ => qw(
    UTC
    US/Alaska
    Europe/Minsk
    Europe/Moscow
    Europe/Kiev
    Australia/LHI
    Asia/Choibalsan
    America/Kentucky/Louisville
);
use constant LOCALTIME_ARR => qw(sec min hour mday mon year wday yday isdst);

our $tests = [];
# array of:
# [$tz, $ts, \%ltime, $iso, \@isoz]
# @isoz = [ [$tz, $isoz], ... ]

my $time = time;
for my $ts (TS) {
    for my $tz (TZ) {
        $ENV{'TZ'} = $tz;
        tzset();
        my %ltime;
        @ltime{ (LOCALTIME_ARR) } = localtime($ts);
        $ltime{'mon'}++;
        $ltime{'year'} += 1900;
        my $iso = strftime("%FT%T", localtime($ts));
        my @isoz;

        for (TZ) {
            $ENV{'TZ'} = $_;
            tzset();
            if ($_ ne 'UTC') {
                push @isoz, [$_, strftime("%FT%T%z", localtime($ts))];
            }
            else {
                push @isoz, [$_, strftime("%FT%TZ", localtime($ts))];
            }
        }

        push @$tests, [$tz, $ts, \%ltime, $iso, \@isoz];
    }
}

1;