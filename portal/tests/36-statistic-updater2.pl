#!/usr/bin/perl

use Test::More qw(no_plan);
use Test::Deep;

BEGIN {
    die "This test is broken";
    # Нужно заменить LWP::UserAgent на MP::UserAgent, иначе не будет работать IPv6
}

use common;
use strict;
use warnings;

use lib::abs qw( ../scripts/ );
require 'widgets_job.pl';

#use POSIX;

use Jobs::statistic_updater2;
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

use_ok 'Jobs::st_loader';
use_ok 'Jobs::statistic_updater2';

# hash SUM
my $x1 = {a => 1, b => 3, c => 4, e => 1};
my $x2 = {a => 1, b => 2, c => 6, d => 2};
Jobs::statistic_updater2::hash_sum($x1, $x2);
cmp_deeply(
    $x1,
    {a => 2, b => 5, c => 10, e => 1, d => 2},
    'Hash sum ok'
);

*ts_from_date = *Jobs::statistic_updater2::ts_from_date;
ok(ts_from_date('2010-11-09'),          'ts');
ok(ts_from_date('2010-11-09 12:23:11'), 'ts');
is(ts_from_date('2010-11-9'), undef, 'ts');
is(ts_from_date(undef),       undef, 'ts');

#ok
subtest "STATs db DATA Getter" => sub {
    plan tests => 4;
    use_ok("WADM::StatsData");

    my $w_7d = WADM::StatsData::get_widget_average_7day_stats(wid => 2621, date => '2010-12-20');
    ok($w_7d->{return});
    ok($w_7d->{ctr});
    my $w_7d2 = WADM::StatsData::get_widget_average_7day_stats(wid => 2621, date => '2001-12-20');
    is($w_7d2->{ctr}, 0, 'no stats -- no ctr');

    #done_testing();
};

subtest "LOADER" => sub {
    #
    use_ok 'Jobs::st_loader';
    ok(UNIVERSAL::isa(Jobs::st_loader::get_browser(), 'LWP::UserAgent'), 'UA');
    ok(Jobs::st_loader::map_reduce_request(table => "report/regular/stat-4654/2010-11-15"), 'MR responce');

    my $hits = Jobs::st_loader::hits('2010-10-12');
    ok($hits->{visitors}, 'all');
    cmp_ok($hits->{visitors}->{_mail}, '>', 10000, 'reference mail users');
    is($hits->{date}, '2010-10-12', 'data in hits');
    my $clicks = Jobs::st_loader::clicks('2010-10-12');
    ok($clicks);
    ok($clicks->{all});
    is($clicks->{date}, '2010-10-12', 'date in clicks');

    $Jobs::st_loader::all_clicks_data->{'2010-10-11'} = {
        date => '2010-10-11',
        hi   => 'world',
        all  => {
            1 => 100,
          }
    };

    is(Jobs::st_loader::clicks('2010-10-11')->{'hi'}, 'world', 'click chache ok');

#    ok
    done_testing();

};

#done_testing();

