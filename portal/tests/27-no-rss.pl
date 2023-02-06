#!/usr/bin/perl

use Test::More qw(no_plan);

use common;
use strict;
use warnings;

use POSIX;
#--------------------------
#we  just testing mail mode
#----------

#WADM::Mailer;

#load widget
#
require WADM::Index;
use WBOX::Model::Widget;
use WADM::Monitoring;
use WADM::History;
use WADM::HistoryController;

use WADM::Auto;

#require MordaX::Errorlog;
#require InitMorda;
#use InitUtils;

my $w = get(32977);

$w->stale_rss_after(4);

is($w->stale_rss_after(), 4);

is($w->can_stale_rss(), 1);

$w->stale_rss_after(-1);

is($w->stale_rss_after(), -1);
is($w->can_stale_rss(),   0);

#is( $w->rss_last_ts(), 0 );
my $a = $w->autostatus() || {};
$a->{dontwork}->{norss} = 1;
$w->autostatus($a);
my $auto = WADM::Auto::get_new_autostatus($w);
is($auto->{dontwork}->{norss}, 1, 'dont work saved between auto statuss')

