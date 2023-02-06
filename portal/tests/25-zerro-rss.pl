#!/usr/bin/perl

use Test::More qw(no_plan);

use common;
use strict;
use warnings;

require WADM::Index;
use WBOX::Model::Widget;
use WADM::Monitoring;

use Data::Dumper;

my $w1 = get(30603);
my $w2 = get(30604);

for ($w1, $w2) {
    $_->{__TYPE} = 'rss';
    $_->{__BORN} = 'rss';
}
$w1->defaultvalue('feed_id', 40223667);
$w2->defaultvalue('feed_id', 40223871);
$w1->rss_last_ts(0);

ok($w1->defaultvalue('feed_id'), 'feed id 1');
ok($w2->defaultvalue('feed_id'), 'feed id 2');

is(WADM::Monitoring::test_if_rss_new($w1, 'force'), 1, 'contentless widget ok but no feed');
is($w1->rss_last_ts(), '', 'last post setted');
$w2->rss_last_ts(0);

is($w2->rss_last_ts(), 0, 'last post ressted');

WADM::Monitoring::test_if_rss_new($w2, 'force', 'one post widget ok');
is($w2->rss_last_ts(), 1284112348, 'last post setted');

#set FEEDid

