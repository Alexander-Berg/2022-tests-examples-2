#!/usr/bin/perl

use common::sense;
use 5.10.0;

use lib::abs qw(.);

use GeobaseTest;
use MordaX::Logit qw(logit);

logit("debug", "scaning ipv4");

my $skip1 = {map { $_ => 1 } qw/0 127 192/};
my $cx = 0;

for (my $i1 = 5; $i1 < 225; $i1++) {
    next if $skip1->{$i1};

    for my $i2 (0 .. 225) {
        logit("debug", "processing: $i1.$i2");
        for my $i3 (0 .. 225) {
            for my $i4 (0 .. 225) {
                my $ip = join(".", $i1, $i2, $i3, $i4);
                my $reg4 = GeobaseTest::reg_by_ip($ip);
                next unless $reg4;
                #logit('debug', "test: $ip");
                my $ipv6 = GeobaseTest::ipv4_to_ipv6($ip);
                my $reg6 = GeobaseTest::reg_by_ip($ipv6);
                if (not defined $reg6) {
                    $cx++;
                    say "no: " . $ipv6;
                }
                elsif ($reg6 != $reg4) {
                    $cx++;
                    say "bad: " . $ipv6;
                }
            }
            exit if $cx >= 1000;
        }
    }
}
