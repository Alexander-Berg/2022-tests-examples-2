#!/usr/bin/perl

use Test::More qw(no_plan);

use common;
use strict;
use warnings;

use lib::abs qw( ../scripts/ );

#use POSIX;
use WBOX::Model::Widget;

my $w = WBOX::Model::Widget->new();
ok($w);
is($w->is_changed(), 0, 'not changed');

is($w->no_rss(), 0);
$w->no_rss(0);
is($w->no_rss(), 0);
is($w->is_changed(), 0, 'not changed');
$w->no_rss(1);
is($w->no_rss(), 1);
is($w->is_changed(), 1, 'changed');
$w->{changed} = 0;
$w->no_rss(0);
is($w->no_rss(), 0);
is($w->is_changed(), 1, 'changed');
$w->{changed} = 0;

is($w->news_weight(), '', 'no NW reson');
$w->news_weight(undef);
is($w->news_weight(), '', 'no NW reson');
is($w->is_changed(),  0,  'not changed');
$w->news_weight('test');
is($w->news_weight(), 'test');
is($w->is_changed(), 1, 'changed');

