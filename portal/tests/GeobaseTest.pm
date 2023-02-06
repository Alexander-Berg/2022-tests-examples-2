#!/usr/bin/perl

package GeobaseTest;
use lib::abs qw(. ../lib ../t/testlib);

use common::sense;

use lib::abs qw(.);

#use Test::More;
use MordaTest;

sub reg_by_ip {
    my $ip = shift;
    my $res = Geo::get_geo_code_core(ip => $ip);
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
        my $res = Geo::get_geo_code_core(ip => $ip_str);
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
        my $res = Geo::get_geo_code_core(ip => $ip_str);
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
    #print "$v6\n";
    return $v6;
}

1;
