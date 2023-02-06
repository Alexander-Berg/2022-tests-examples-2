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
$wid = 27548;
#$wid = 35;

my $wi = get($wid);
is($wi->bad_response(0), '');
#$WBOX::Requester::requester->{debug} = 2;
save($wi);

$wi = get($wid);

is($wi->bad_response(), '', 'bad respose dropped');
#is( $wi->force_delete(), '' );
is($wi->bad_response_dt(), '');
#is( $wi->src_failed_ts(), '' );

$wi->bad_response(1);
#is( $wi->force_delete(),  );
ok($wi->bad_response_dt(), 'bad responce');
#ok( $wi->src_failed_ts(), ' src set' );

$wi->bad_response_dt('2010-06-06 12:45:23');
#$wi->src_failed_ts( time() - 3600 * 24 * 50 );

#ok( $wi->force_delete() , 'force to delete');
save($wi);

$wi = get($wid);
#ok( $wi->force_delete() , 'force to delete');
ok($wi->bad_response_dt(), 'bad responce ' . $wi->bad_response_dt());
#ok( $wi->src_failed_ts(), ' src set' );

