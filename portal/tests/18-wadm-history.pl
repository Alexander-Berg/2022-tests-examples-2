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

use Data::Dumper;

my $input = FakeInput->new();

ok(
    $input->set_args({
            change_from  => '2010-05-10',
            change_until => '2010-05-20',
        }
      )
);

subtest 'interval extractor' => sub {
    plan tests => 4;
    my $i2 = WADM::HistoryController::extract_time_intervals([
            {op_login => 'a', 'change_dt' => '2010-12-30 18:00:11'},
            {op_login => 'b', 'change_dt' => '2010-12-30 00:00:11'},
            {op_login => 'a', 'change_dt' => '2010-01-01 00:30:11'},
            {op_login => 'a', 'change_dt' => '2010-01-01 00:02:01'},
            {op_login => 'a', 'change_dt' => '2010-01-01 00:00:11'},
        ]
    );
    ok($i2->{'a'});
    is($#{$i2->{a}}, 2);
    ok($i2->{'b'});
    is($#{$i2->{b}}, 0);

    #warn Data::Dumper::Dumper( $i2 );

};

my ($h_count, $h_data) = WADM::History::load(
    change_from  => '2010-06-22',
    change_until => '2010-06-22',
    type         => {'EDIT' => 1},

    limit => 10,
);

isnt($h_count, 0, 'Test Extraction have data');
diag(" Loaded: $h_count, from HDB");
#warn Data::Dumper::Dumper( $h_data );

my $intervals = WADM::HistoryController::extract_time_intervals($h_data);
ok($intervals);
ok(keys %$intervals);
my ($login) = keys %$intervals;
diag(" working with intervals of login: $login ");

isnt($#{$intervals->{$login}}, -1, $login . ' has time intervals in history ');

#warn Data::Dumper::Dumper( $intervals );

my $PD = {};
ok(WADM::HistoryController::HandleChartsData($input, $input, $PD), ' Cahrts Data ');

ok($PD->{x_points});
ok($PD->{y_vals});
#ok( keys %{ $PD->{y_vals} }, 'sevaral logins found' );

#warn Data::Dumper::Dumper( $PD->{x_points} );

my ($v_count, $v_data) = WADM::History::load(
    change_from  => '2010-06-25',
    change_until => '2010-06-25',
    'op_login'   => 'veral',
#    type            => {'EDIT' => 1},

    limit => 10,
);

my $v_intervals = WADM::HistoryController::extract_time_intervals($v_data);
warn Data::Dumper::Dumper($v_intervals);

ok(
    $input->set_args({
            date     => '2010-06-25',
            op_login => 'veral',
#            change_from =>'2010-05-10',
#            change_until=>'2010-05-20',
        }
      )
);
ok(WADM::HistoryController::ChartBarData($input, $input, $PD), ' Cahrts Data ');

#warn Data::Dumper::Dumper($PD);

# Real test
#https://wadm-dev29.wdevx.yandex-team.ru/history-charts-data/?mode=bar&date=2010-12-14&op_login=koala&type=undefined
$input->set_args({
        mode     => q{bar},
        date     => q{2010-12-14},
        op_login => q{koala},
    }
);
my $koala = WADM::HistoryController::ChartBarData($input, $input, $PD);
ok($koala, ' Cahrts Data ');
isnt(scalar keys %{$PD->{x_points}}, 0, "Has X Points");
isnt(scalar keys %{$PD->{y_points}}, 0, "Has Y Points");
isnt((scalar grep { $_ > 0 } values %{$PD->{Y_points}}), 0, "Has Y Points data");

my ($k_count, $k_data) = WADM::History::load(
    change_from  => '2010-12-14',
    change_until => '2010-12-14',
    'op_login'   => 'koala',
#    type            => {'EDIT' => 1},
    limit => 100000
);
ok($k_count, 'koala data presents');
diag("count: " . $k_count);
my $k_intervals = WADM::HistoryController::extract_time_intervals($k_data)->{koala};
isnt(scalar @$k_intervals, 0, 'has intervals');
#warn Dumper( $k_intervals );

