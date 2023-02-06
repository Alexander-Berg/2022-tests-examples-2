#!/usr/bin/perl

use Test::More qw(no_plan);
use Data::Dumper;
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

use WADM::Stats;

my $data = WADM::Stats::get_widget_list();
#print Dumper( $data );
ok($data,);

my $r_data = WADM::Stats::get_region_list();
ok($r_data);

subtest "SORTER" => sub {
    plan tests => 13;
    my $sorter = Sorter->new();
    ok($sorter, "Sorter inited");

    my $input = FakeInput->new();
    ok($input);
    my $s = Sorter->new(input => $input, default => ['users', 'desc', 'users_ww', 'desc']);
    ok($s);
    ok($s->{sort});
    is($s->{sort}->[0], 'users');

    $input = FakeInput->new();
    $input->set_args({'sort' => 'widgets.desc,errors.asc;job.desc'});
    $s = Sorter->new('input' => $input);
    ok($s);
    ok($s->{sort});
    is($s->{sort}->[0], 'widgets');
    is($s->{sort}->[2], 'errors');
    is($s->{sort}->[4], 'job');
    ok($s->{get_param});
    like($s->{get_param}, qr/sort=/);

    my $order_by = $s->get_sort_by_map({job => 'ws.job', 'errors' => 'e.e'});
    is($order_by, 'ORDER BY e.e asc, ws.job desc');
    #warn Dumper( $s->{sort} );

#    ok( $sorter->{sort})
};
subtest "PAGER" => sub {
    plan tests => 15;
    my $p = Pager->new();
    ok($p, 'default pager');
    ok(defined $p->{offset});
    ok($p->{limit});
    $p = Pager->new(input => FakeInput->new());
    is($p->{offset}, 0);
    is($p->{limit},  20);
    $p->count(101);
    is($p->{items}, 101);
    is($p->{pages}, 6, 'correct cail');

    my $i = FakeInput->new();
    $i->set_args({page => 2, 'sort' => 'xyz.desc'});
    $p = Pager->new(input => $i);
    ok($p);
    isnt($p->{offset}, 0);

    $p = Pager->new(limit => 5);
    ok($p);
    is($p->{limit}, 5);

    $i = FakeInput->new();
    $i->set_args({xx_page => 3, 'sort' => 'xyz.desc'});

    $p = Pager->new(input => $i, prefix => 'xx_');
    ok($p);
    is($p->{page},   3);
    is($p->{limit},  20);
    is($p->{offset}, 60);

};

subtest "REGIONSORT" => sub {
    plan tests => 3;
    my $sort = [
        users     => 'desc',
        users_ww  => 'desc',
        users_all => 'desc',
        hits      => 'asc',
        hits_ww   => 'asc',
    ];
    my $sorter = Sorter->new(default => $sort);
    pass('getting sort request');
    my $data = WADM::Stats::get_region_list(sorter => $sorter);
    ok($data);
    ok(@$data)

};

subtest "WIDGET of REGION " => sub {
    plan tests => 5;
    my $pager = Pager->new();
    my $data = WADM::Stats::get_widget_list(filter => {region => 1}, pager => $pager);
    ok($data);
    isnt(@$data, 0, 'data presents ');
    isnt($pager->{items}, 0);
    isnt($pager->{pages}, 0);

    $data = WADM::Stats::get_widget_list(filter => {region => 100010001000});
    is(@$data, 0, 'no data on bad region');
};

subtest "WIDGET DATA" => sub {
    plan tests => 2;
    is(scalar @{WADM::Stats::get_widget_data(widget_id => undef)}, 0, 'no data for zerro');
    isnt(scalar @{WADM::Stats::get_widget_data(widget_id => 12217)}, 0, ' data for 12217');
};

subtest "SUB REGION LIST " => sub {
    plan tests => 6;
    my $data = WADM::Stats::get_subregion_list(region => 187);
    ok($data);
    is((scalar @$data), 10);
    $data = WADM::Stats::get_subregion_list(region => 1);
    is((scalar @$data), 10);
#    is( $data->[0]->{geo_id}, 127, "first is self" );
    my $pager = Pager->new(limit => 5);
    $data = WADM::Stats::get_subregion_list(region => 225, pager => $pager);
    ok($data);
    is(scalar @$data, 5);
    ok($pager->{items})

};

subtest "rUBRICS " => sub {
    my $data = WADM::Stats::get_rubrics_data();
    ok($data);
    is((scalar @$data), 10);
    my $pager = Pager->new(limit => 5);
    ok($pager->{limit});
    $data = WADM::Stats::get_rubrics_data(pager => $pager);
    ok($data);
    is(scalar @$data, 5);
#    ok( $pager->{items} );
    done_testing();
};

subtest "W_WEEKLY" => sub {
    use WADM::StatsData;
    my $data = WADM::StatsData::get_widget_weekly_data(date => '2010-10-04');
    ok($data);
    done_testing();
};

subtest "CSVOUT" => sub {

    my $data = [{a => 1, b => 2, c => 3}];
    ok(WADM::Stats::r200CVS(undef, data => $data));
    ok(WADM::Stats::r200CVS(undef, data => $data, headers => [['a' => 'ab'], ['b' => 'bb'], ['c' => 'cb']]));
    done_testing();

  }

