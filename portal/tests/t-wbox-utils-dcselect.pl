#!/usr/bin/perl
use strict;
use warnings;
use feature 'say';
use Data::Dumper;
use Test::More;
use lib::abs qw( . ../lib);
use WBOX::Utils;
use WBOX::Conf;

my $debug = $ARGV[0];

my ($database, $dc_settings) = WBOX::Conf->get('Widgets', 'DCSettings');

for my $dc (qw{ugr ams ugr3 myt fol iva iva2 sas ams_res}) {
    say "\033[7mDC ", $dc, "\033[0m";
    my $this_dc_cond = WBOX::Utils::_get_this_dc_cond($dc, $dc_settings);
    my $res = [];

    say 'read 1';
    my $res1_r = &sel_1($dc, $database, $this_dc_cond, 'read', undef);
    &say_res($res1_r);
    say '';

    say 'write 1';
    my $res1_w = &sel_1($dc, $database, $this_dc_cond, undef, 'write');
    &say_res($res1_w);
    say '';

    say 'read 2';
    my $res2_r = &sel_2($dc, $database, $this_dc_cond, 'read', undef);
    &say_res($res2_r);
    say '';

    say 'write 2';
    my $res2_w = &sel_2($dc, $database, $this_dc_cond, undef, 'write');
    &say_res($res2_w);
    say '';

    say 'read 3';
    my $res3_r = WBOX::Utils::_select_dcs($dc, $database, $this_dc_cond, 'GetWidgetsDBURL', undef);
    &say_res($res3_r);
    say '';

    say 'write 3';
    my $res3_w = WBOX::Utils::_select_dcs($dc, $database, $this_dc_cond, 'GetWidgetsDBURL', undef, 'write');
    &say_res($res3_w);
    say '';

#    is_deeply($res1_r, $res2_r, 'READ OK');
#    is_deeply($res1_w, $res2_w, 'WRITE OK');

    is_deeply($res1_r, $res3_r, 'READ OK');
    is_deeply($res1_w, $res3_w, 'WRITE OK');
    say '';
}
done_testing();

# ===================================================================
sub logit(@) {
    say @_ if $debug;
}

# ===================================================================
sub say_res($) {
    my $r = shift;
    for (@$r) {
        print $_->{dc}, '; ';
    }
    say '';
}

# ===================================================================
sub sel_1 {
    my ($dc, $database, $this_dc_cond, $read, $write) = @_;
    my @res;
    if ($write) {
        my (@our_dc_dbs, @prior_dc_dbs, @other_dc_dbs);
        for (@{$database->{'MasterArr'}}) {
            my $db_dc = $_->{'dc'};
            if ($this_dc_cond->{'write'}->{$db_dc}) {
                logit('debug', "Found master in prioriry DC($dc)");
                push @prior_dc_dbs, $_;
            } elsif ($dc eq $db_dc) {
                logit('debug', "Found master in our DC($dc)");
                push @our_dc_dbs, $_;
            } else {
                push @other_dc_dbs, $_;
            }
        }
        if (@prior_dc_dbs) {
            @res = @prior_dc_dbs;
        } elsif (@other_dc_dbs || @our_dc_dbs) {
            @res = (@our_dc_dbs, @other_dc_dbs);
        } else {
            logit('admin', "In GetShardURL: Master not configured");
            return undef;
        }
    } else {
        my (@our_dc_dbs, @prior_dc_dbs, @other_dc_dbs);
        for (@{$database->{'ReplicasArr'}}) {
            my $db_dc = $_->{'dc'};
            if ($this_dc_cond->{'read'}->{$db_dc}) {
                logit('debug', "Found slave in prioriry DC($dc)");
                push @prior_dc_dbs, $_;
            } elsif ($this_dc_cond->{'no_read'}->{$db_dc}) {
                logit('debug', "Skip noread slave for DC($dc)");
                next;
            } elsif ($dc eq $db_dc) {
                logit('debug', "Found slave in our DC($dc)");
                push @our_dc_dbs, $_;
            } else {
                push @other_dc_dbs, $_;
            }
        }
        if (@prior_dc_dbs) {
            @res = @prior_dc_dbs;
        } elsif (@other_dc_dbs || @our_dc_dbs) {
            @res = (@our_dc_dbs, @other_dc_dbs);
        } else {
            logit('admin', "In GetShardURL: Slave not configured");
            return undef;
        }
#        WBOX::Utils::shuffle_wbox_replics(\@res);
    }
    return \@res;
}

# ===================================================================
sub sel_2 {
    my ($dc, $database, $this_dc_cond, $read, $write) = @_;
    my @res;
    if ($write) {
        for (@{$database->{'MasterArr'}}) {
            my $db_dc = $_->{'dc'};
            if ($dc eq $db_dc) {
                logit('debug', "Found master in our DC($dc)");
                unshift @res, $_;
            } elsif ($this_dc_cond->{'write'}->{$db_dc}) {
                logit('debug', "Found master in prioriry DC($dc)");
                unshift @res, $_;
            } elsif ($this_dc_cond->{'no_write'}->{$db_dc}) {
                logit('debug', "Skip nowrite master for DC($dc)");
                next;
            } else {
                push @res, $_;
            }
        }
        unless (@res) {
            logit('admin', "In GetWidgetsDBURL: Master for Widgets not configured");
            return undef;
        }
    } else {
        for (@{$database->{'ReplicasArr'}}) {
            my $db_dc = $_->{'dc'};

            logit('debug', "$db_dc");
            if ($dc eq $db_dc) {
                logit('debug', "Found slave in our DC($dc)");
                unshift @res, $_;
            } elsif ($this_dc_cond->{'read'}->{$db_dc}) {
                logit('debug', "Found slave in prioriry DC($dc)");
                unshift @res, $_;
            } elsif ($this_dc_cond->{'no_read'}->{$db_dc}) {
                logit('debug', "Skip noread slave for DC($dc)");
                next;
            } else {
                logit('debug', "PUSH");
                push @res, $_;
            }
        }

#        WBOX::Utils::shuffle_wbox_replics(\@res);
    }
    return \@res;
}

