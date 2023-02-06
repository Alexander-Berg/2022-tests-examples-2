#!/usr/bin/perl
use lib::abs qw(. ../lib);
use common::sense;
use Test::More qw(no_plan);
use MordaX::Logit;
use URI::Escape;
use utf8;
MordaX::Logit::enable_dumpit();

use_ok("MordaX::Utils");

my $t = q{
1697360315.yb.::::4                                                     none
1697360315.yb.:1234                                                     none
1697360315.yb.:1234:::4                                                 none

1697360315.yb.1_7_1364_22194                                            installed

1697360315.yb.1_7_1364_22194::1379000315                                installed yabr30
1697360315.yb.1_7_1364_22194::1382000315                                installed

1697360315.yb.1_7_1364_22194:::1379000315                               installed yabr30
1697360315.yb.1_7_1364_22194:::1382000315                               installed

1697360315.yb.1_7_1364_22194:::::1379000315                             removed
1697360315.yb.1_7_1364_22194:::::1382000315                             removed

1697360315.yb.1_7_1364_22194::1379000315:1379000315                     installed yabr30
1697360315.yb.1_7_1364_22194::1379000315:1382000315                     installed
1697360315.yb.1_7_1364_22194::1382000315:1379000315                     installed
1697360315.yb.1_7_1364_22194::1382000315:1379000315                     installed !yabr30

1697360315.yb.1_7_1364_22194::1379000315:::1382000315                   removed
1697360315.yb.1_7_1364_22194::1382000315:::1379000315                   installed
1697360315.yb.1_7_1364_22194::1379000315:::1379000314                   installed yabr30

1697360315.yb.1_7_1364_22194:::1379000315::1382000315                   removed
1697360315.yb.1_7_1364_22194:::1382000315::1379000315                   installed
1697360315.yb.1_7_1364_22194:::1379000315::1379000314                   installed yabr30

1697360315.yb.1_7_1364_22194::1379000315:1379000315::1382000315         removed
1697360315.yb.1_7_1364_22194::1382000315:1379000315::1379000315         installed
1697360315.yb.1_7_1364_22194::1379000315:1382000315::1379000315         installed
1697360315.yb.1_7_1364_22194::1379000315:1379000315::1379000314         installed yabr30

1697360315.yb.1_7_1364_22194::1382000315:1379000315::1379000315         installed !yabr30
1697360315.yb.1_7_1364_22194::1379000315:1382000315::1379000315         installed !yabr30

1_7_1364_22194::1382000315:1379000315 !yabr30
1_7_1364_22194::1382000315:1379000315::1379000315 !yabr30

1697360315.yb.1_7_1364_22194::lqlqlqlq:lololololoo:cooool:ggggggg       installed
1697360315.yb.qq_zz_lolo_ggg::lqlqlqlq:lololololoo:cooool:ggggggg       !removed
};

my $req = {'time' => 1382020313};

for (split /\n+/, $t) {
    next unless $_;
    my ($c, @flags) = split /\s+/;
    $c =~ s/^\d+\.yb\.//;
#dmp @flags,
    my $r = MordaX::Utils::yb_parse($req, $c);

    if ($flags[0] ~~ 'none') {
        ok(!$r->{$_}, "!flag[$_]=[$r->{$_}] yb[$c]") for qw(installed removed yabr30);
    } else {
        ok($r->{$_}, "flag[$_]=[$r->{$_}] yb[$c]") || dmp($r) for grep { !/^!/ } @flags;
        ok(!$r->{$_}, "!flag[$_]=[$r->{$_}] yb[$c]") || dmp($r) for map { s/^!//; $_ } grep {/^!/} @flags;
    }

}

dmp MordaX::Utils::yb_parse($req, $_) for qw (1_7_1364_22194::1382000315:1379000315 1_7_1364_22194::1382000315:1379000315::1379000315);
