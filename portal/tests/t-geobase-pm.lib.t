#!/usr/bin/perl

use strict;
use warnings;
use Test::More tests => 8;
use Data::Dumper;

our %Region;

my $geobase_file = '/opt/www/bases/geobase.pm';
if ($ARGV[0]) {
    $geobase_file = $ARGV[0];
}

ok(-f $geobase_file, 'file found');
require_ok($geobase_file);
ok(\%geobase::Region,            'Region Inited');
ok(scalar keys %geobase::Region, 'We have some data in Geobase');
#ok(\%Region                ,'Region Exported');
our $geobase = \%geobase::Region;

ok(test_selflink('parents'), 'Parents ok');
ok(test_selflink('path'),    'Path self link ok');
ok(test_selflink('chld'),    'Children ok');
ok(test_path(),              'Path ok');

sub test_selflink {
    my $type = shift;
#   'parents';
    while (my ($ID, $data) = each(%$geobase)) {
        if (scalar grep { $ID == $_ } @{$data->{$type}}) {
            warn "Id: $ID, Type: $type find link to itself\n";
            return undef;
        }
    }
    return 1;
}

sub test_path {
    while (my ($ID, $data) = each(%$geobase)) {
#        eval {
        my $path    = $data->{path};
        my $parents = $data->{parents};

        my $parent = ${$parents}[-1];
        if ($parent) {
            $parent = $geobase->{$parent};
            #сравнить 2 массива
            for (my $i = 0; $i < @$parents - 1; $i++) {
                if ($parent->{path}->[$i] != $path->[$i]) {
                    warn "Parents path differs for $ID\n";
                    return undef;
                }
                if (scalar @$parents != @{$parent->{parents}} + 1) {
                    warn "Parrents differs in size for $ID\n";
                }
                my %ids = map { $_ => 1 } @$parents;
                if (scalar grep { !$ids{$_} } @{$parent->{parents}}) {
                    warn "Parents deffirs in items for $ID\n";
                }
            }
            # убедиться что есть в дитях
            unless (scalar grep { $_ == $ID } @{$parent->{chld}}) {
                warn "$ID not in child of parent\n";
                return undef;
            }
            # убедится есть все дети
            if (scalar grep { not $geobase->{$_} } @{$data->{chld}}) {
                warn "Children of $ID not found:\n" . join(' ', grep { not $geobase->{$_} } @{$data->{chld}}) . "\n";
                return undef;
            }

        } else {
            if (scalar(@$path)) {
                warn "Path elements for Root\n";
                return undef;
            }
            if (scalar(@$parents)) {
                warn "Parent elements for Root\n";
                return undef;
            }
        }
#        };
#        if( $@ ){
#            warn "Error in $ID : $@\n";
#            warn Dumper ($data);
#            return undef;
#        }

    }
    return 1;
}
