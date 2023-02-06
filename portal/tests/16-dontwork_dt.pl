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

use Data::Dumper;
#----------------------

my $wid;
$wid = 28;
#$wid = 35;

my $wi = get($wid);
is($wi->dont_work(0), 0);
$wi->dont_work_complex({});
$wi->dont_work_dt('');
#$WBOX::Requester::requester->{debug} = 2;
save($wi);

$wi = get($wid);

is($wi->dont_work(), 0, 'dont work dropped');
is($wi->force_delete(), 0);
is($wi->dont_work_dt(), '');

#is( $wi->src_failed_ts(), '' );

$wi->dont_work_add('test', 'auto test');
is($wi->force_delete(), 0);
ok($wi->dont_work_dt(), 'dont work');

#$wi->stale_rss( 1 );
#$wi->rss_last_ts( time - 3600 * 24 * 180 );

$wi->dont_work_dt('2010-06-07 12:45:23');

ok($wi->force_delete(), 'force to delete');

save($wi);

$wi = get($wid);
ok($wi->force_delete(), 'force to delete');
ok($wi->dont_work_dt(), 'dont work ' . $wi->dont_work_dt());
#ok( $wi->src_failed_ts(), ' src set' );

