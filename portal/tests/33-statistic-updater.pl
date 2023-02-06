#!/usr/bin/perl

use Test::More qw(no_plan);

use common;
use strict;
use warnings;

use lib::abs qw( ../scripts/ );
require 'widgets_job.pl';

#use POSIX;

use Jobs::statistic_updater;
use starter;
starter::init_wadm();
#starter::init_wadm_tt();
#ok($main::wadm_tt_obj, 'WADM TT inited');
starter::init_wadm();

starter::init_wbox();
starter::init_reasons();
my $w = get(22009);

#testing auto add to catalog

ok($w);

sub Jobs::statistic_updater::update_stats {
    return 1;
}

sub Jobs::statistic_updater::calculate {
    return 1;
}

#$starter::context{lazy} = 1;
$w->actflag('active');
$w->catflag('outside');
$w->regflag('outside');
$w->{__USERS} = 10;
$w->warning_recalculate({});
$w->dont_work_recalculate({});
$w->bad_response(0);
$w->no_rss(0);
$w->stale_rss(0);
$w->virusflag(1);

# ok( starter::c('lazy') , 'lazy mode' );
diag("starting work");

ok((not WADM::Auto::has_bad_signs($w)), 'no bad signs');

Jobs::statistic_updater::process($w);
is(WADM::Auto::get_catalog_add_limit($w), 150,       'limit 300');
is($w->catflag(),                         'outside', 'not for catalog');

$w->{__USERS} = 320;
$Jobs::statistic_updater::processed_widgets = {};
Jobs::statistic_updater::process($w);
is($w->catflag(), 'canrequest', 'for catalog');

$w->regflag('inside');
is(WADM::Auto::get_catalog_add_limit($w), 500, 'limit 500');
$Jobs::statistic_updater::processed_widgets = {};
Jobs::statistic_updater::process($w);
is($w->catflag(), 'outside', 'not for catalog');

$w->{__USERS} = 620;
$Jobs::statistic_updater::processed_widgets = {};
Jobs::statistic_updater::process($w);
is($w->catflag(), 'canrequest', 'for catalog');

$w->virusflag(2);
ok($w->is_infected());
$Jobs::statistic_updater::processed_widgets = {};
Jobs::statistic_updater::process($w);
is($w->catflag(), 'outside', 'not for catalog');

subtest "DB" => sub {
    plan tests => 2;
    is(Jobs::st_common::has_db(), 0, ' No Db');
    Jobs::st_common::bind_db(Jobs::statistic_updater::stats_master_dbh());
    is(Jobs::st_common::has_db(), 1, ' has Db');
};

subtest "HAS DATA" => sub {

    is(Jobs::st_common::has_data(date => '2001-01-11', type => 'users'),  0, 'no data');
    is(Jobs::st_common::has_data(date => '2001-01-11', type => 'rating'), 0, 'no data');
    is(Jobs::st_common::has_data(date => '2010-01-11', type => 'wid_rating', wid => 19917), 0, 'has no data');
    is(Jobs::st_common::has_data(date => '2001-01-11', type => 'x-com'),  undef, 'bad type');
    is(Jobs::st_common::has_data(date => '2011-01-03', type => 'users'),  1,     'has data');
    is(Jobs::st_common::has_data(date => '2010-12-22', type => 'rating'), 1,     'has data');
    is(Jobs::st_common::has_data(date => '2010-12-22', type => 'wid_rating', wid => 19917), 1, 'has data');
    done_testing();
};

=temp
my $wid = 33527;
my $wp = get( $wid );

ok( (not WADM::Auto::has_bad_signs($wp) ), 'no bad signs');
is( WADM::Auto::get_catalog_add_limit( $wp )
                        , 150       , 'limit 300' );

diag(' Users: '. $wp->users() );                   
$wp->catflag('outside');
Jobs::statistic_updater::process( $wp );
$wp = get( $wid );
is( $wp->catflag(), 'canrequest', 'can request now');
=cut

