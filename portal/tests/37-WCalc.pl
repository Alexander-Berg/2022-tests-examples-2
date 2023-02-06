#!/usr/bin/perl

use Test::More qw(no_plan);
use Test::Exception;

use common;
use strict;
use warnings;

use lib::abs qw( ../scripts/ );
require 'widgets_job.pl';

use_ok('WADM::WCalc');
use_ok('WADM::StatsDBProvider');

my $c_obj = WADM::WCalc->new();
ok($c_obj, "Object inited ");

my $w = get(41090);
ok($w, 'widget ok');

dies_ok { $c_obj->get_ratings($w); } 'bad get_ratings call';
diag('all ok');

dies_ok { $c_obj->get_widget_vector() } 'bad vector call';
dies_ok { $c_obj->get_widget_vector($w) } 'bad vector call';
dies_ok { $c_obj->get_widget_vector(date => '2011-01-12') } 'bad vector call';

my $vector_old = $c_obj->get_widget_vector($w, date => '2010-01-01');

my $vector = $c_obj->get_widget_vector($w, date => '2011-01-01');
ok($vector, 'vector calculated');
is($w->id(),       41090, 'wid in widget');
is($vector->{wid}, 41090, 'wid in vector');

ok($vector->{shows});
ok($vector->{ctr});
ok($vector->{users});
ok($vector->{return});

my $rating;
lives_ok { $rating = $c_obj->get_ratings(widget => $w, date => '2011-01-01') } 'Ratings obtained';
ok($rating);
ok($rating->{rating});
ok($rating->{rating_formula});
ok($rating->{rating_actual});

my $update;
lives_ok { $update = WADM::WCalc->update_widget($w, date => 'yesterday') };
ok($update);
ok($update->{widget});
ok($update->{rating_all});

