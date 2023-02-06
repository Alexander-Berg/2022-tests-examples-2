#!/usr/bin/perl

use Test::More qw(no_plan);

use common;
use utils;
use strict;
use warnings;

#
use WADM::Utils;

#
#exclude_widget_from_programs

my $wid = 26839;    # int1ch's widget

my $w = WADM::Utils::get_widget($wid);
ok($w, 'widget loaded');

ok(clear_widget($w), 'widget cleared');

my $res;

subtest 'exclude bad params' => sub {
    plan tests => 3;
    is(undef, WADM::Utils::exclude_widget_from_programs(),   'Call with no params');
    is(undef, WADM::Utils::exclude_widget_from_programs($w), 'Call witot reason');
    is(undef, WADM::Utils::exclude_widget_from_programs($w, 'simple reason'), 'Call witot reason');
};

subtest 'exclude normal' => sub {
    plan tests => 2;
    my $res = WADM::Utils::exclude_widget_from_programs($w, 'test reason', 'test');
    ok($res, 'excluded');
    is($res->{count}, 0, 'zerro excluded');
};

#clear

