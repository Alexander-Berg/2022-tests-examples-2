#!/usr/bin/perl

use Test::More qw(no_plan);

use common;
use strict;
use warnings;

use Data::Dumper;

use lib::abs('../scripts');
eval { require 'widgets_job.pl'; };

my $w = get(4474);
our $widget_domain = {};
ok($w, 'widget_loaded');
is($w->titleurl_domain(), 'autocentre.ua');
prepare_widget_host_list($w);

ok($widget_domain->{'autocentre.ua'}, 'Auto center loaded');

