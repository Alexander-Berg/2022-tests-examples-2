#!/usr/bin/perl

use lib::abs qw(../lib);
use common::sense;
use Test::More;
use MordaX::Errorlog;
use POSIX;

*f = *MordaX::Errorlog::get_tskv_timestamp;

sub fh {
    my $s = f(@_);
    if ($s =~ /timestamp=([^t]*)\ttimezone=([^\t]*)/) {
        return {
            timestamp => $1,
            timezone  => $2,
        };
    }
    {};
}

$ENV{'TZ'} = "Europe/Moscow";
POSIX::tzset();

subtest "Direct Time" => sub {

    my $r0 = {'server_time' => 1429217998};
    my $r1 = {'server_time' => 1429217999};
    my $r2 = {'server_time' => 1429218000};
    my $r3 = {'server_time' => 1429218001};

    my $t0 = fh($r0);
    my $t1 = fh($r1);
    my $t2 = fh($r2);
    my $t3 = fh($r3);

    is($t0->{timezone},  '+0300');
    is($t0->{timestamp}, "2015-04-16 23:59:58");
    is($t1->{timezone},  '+0300');
    is($t1->{timestamp}, "2015-04-16 23:59:59");
    is($t2->{timezone},  '+0300');
    is($t2->{timestamp}, "2015-04-17 00:00:00");

    is($t3->{timezone},  '+0300');
    is($t3->{timestamp}, "2015-04-17 00:00:01");

    ok($r1->{server_tskv_timestamp});
    ok($r2->{server_tskv_timestamp});

#    dmp( $r1 , $r2 );
};

ok(f());
ok(fh()->{timestamp},);
ok(fh()->{timezone});

is(fh()->{timezone}, '+0300');

sub scan_for_tz_diff {
    my $expected_tz = shift;
    my $start       = time();
    my $boom        = {};
    for (my $d = 0; $d < 25 * 60; $d += 5) {
        my $tz = fh({server_time => $d * 60 + $start})->{timezone};
        if ($tz ne $expected_tz) {
            next if $boom->{$tz};
            diag("Ts: " . ($d + $start) . " > '$tz' vs expected '$expected_tz'");
            $boom->{$tz} = 1;
        } else {

        }
    }
    fail(" Get nonexpected timzone") if scalar keys %$boom;
}

scan_for_tz_diff('+0300');

$ENV{'TZ'} = "America/Caracas";
POSIX::tzset();
scan_for_tz_diff('-0430');

$ENV{'TZ'} = 'Asia/Jakarta';
POSIX::tzset();
scan_for_tz_diff('+0700');

done_testing();
