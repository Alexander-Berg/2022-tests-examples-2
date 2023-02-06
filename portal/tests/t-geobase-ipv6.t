#!/usr/bin/perl

use common::sense;

use lib::abs qw{../lib . ../t/testlib};

use Test::More;
use MordaTest;
use Geo;
ok(1, 'ok');

subtest "255 ipv4" => sub {
    for (my $j = 0; $j < 100; $j++) {
        my $ip225 = get_ipv4(225);
        next unless $ip225;
        ok($ip225, "Russia IP found");
        is(reg_by_ip($ip225), 225, "reverse ok: $ip225");
        my $ff225 = ipv4_to_ipv6($ip225);
        is(reg_by_ip($ff225), 225, "reverse + ipv6 ok: $ff225");

        #if( reg_by_ip( $ff225 ) || 0 != 225 ){
        #is( reg_by_ip( $ff225 ), 225, "reverse + ipv6 ok: $ff225");
        #    print $ff225 . "\n";

        #}
    }

    done_testing();
};

my $ip10 = get_ipv4(10);
ok($ip10, "Orel IP found");
is(reg_by_ip($ip10),               10, "reverse  ok");
is(reg_by_ip(ipv4_to_ipv6($ip10)), 10, "reverse + ipv6 ok: " . ipv4_to_ipv6($ip10));

#:w
#my $x255 = get_ipv6( 225 );
#ok( $x255, "ipv6 russia found: $x255 ");

done_testing();

sub reg_by_ip {
    my $ip = shift;
    my $res = Geo::get_geo_code_core(ip => $ip, laas => 0);
    return undef unless $res->{ok};
    return undef unless $res->{precision_by_ip};
    return $res->{region_by_ip};
}

sub get_ipv4 {
    my $r = shift;

    for (my $i = 0; $i < 100000; $i++) {
        my @ip_p = ();
        for (1 .. 4) {
            push @ip_p, int(rand(253) + 1);
        }

        my $ip_str = join('.', @ip_p);
        my $res = Geo::get_geo_code_core(ip => $ip_str, laas => 0);
        #dumpit( $res );
        next unless $res;
        next unless $res->{ok};
        next unless $res->{precision_by_ip};
        my $rg = $res->{region_by_ip};

        return $ip_str if $r == $rg;
    }
    return undef;
}

sub get_ipv6 {
    my $r = shift;

    for (my $i = 0; $i < 1000000; $i++) {
        my @ip_p = ();
        for (1 .. 8) {
            push @ip_p, int(rand(256 * 256 - 2) + 1);
        }

        my $ip_str = join(':', map { sprintf("\%04x", $_) } @ip_p);
        #print $ip_str . "\n";
        my $res = Geo::get_geo_code_core(ip => $ip_str, laas => 0);
        #dumpit( $res );
        next unless $res;
        next unless $res->{ok};
        next unless $res->{precision_by_ip};
        my $rg = $res->{region_by_ip};

        return $ip_str if $r == $rg;
    }
    return undef;
}

sub ipv4_to_ipv6 {
    my $ip  = shift;
    my $hex = join(".", map { sprintf('%d', $_) } split(/\./, $ip));
    my $v6  = "::ffff:" . $hex;
    print "$v6\n";
    return $v6;
}

