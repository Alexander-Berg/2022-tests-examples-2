#!/usr/bin/perl
use common::sense;
use Test::More;
use 5.010;
use lib::abs qw(../lib .);
#use InitBase;
use Geo qw(geo);
use Data::Dumper;
#use InitBase;
use_ok("MordaX::Block::Poi");
use_ok("Geo");
Geo::init();
use MordaX::Data_load;
#MordaX::Data_load::load_static_exports(qw/poi_favourite/);
#my $blocks = MordaX::Data_get::get_static_data({}, 'poi_favourite');
#print Dumper $blocks;
#die;
%MordaX::Data_load::static_exports = (map { $_ => 1 } qw/poi_favourite/);
#shops breakfast dinner supper night drugstore gas atm
%MordaX::Data::storage = (
    poi_favourite => {
        'index' => {map { $_ => 1 } qw/geo geos/},
        'indexed' => {
            '10000' => [
                {
                    'id'         => 'shops',
                    'subgroup'   => 'megastore',
                    'week_day'   => 'workday',
                    'weight_def' => 10,
                    'morning'    => 1,
                },
                {
                    'id'         => 'shops',
                    'subgroup'   => 'mall',
                    'week_day'   => 'workday',
                    'weight_def' => 20,
                    'day'        => 2,
                },
                {
                    'id'         => 'flowers',
                    'subgroup'   => 'flowers',
                    'from'       => '2015-03-01 00:00',
                    'till'       => '2015-04-07 23:00',
                    'weight_def' => 30,
                    'evening'    => 3,
                    'night'      => 4,
                },
            ],
            '14' => [
                {
                    'id'         => 'shops',
                    'subgroup'   => 'ministore',
                    'weight_def' => 10,
                },
            ],
        },
    },
);

my $poi = MordaX::Block::Poi->new();
is(ref $poi, 'MordaX::Block::Poi', 'Obj OK');

# у региона нет описания

my $wday         = 1;                                                                                 # понедельник
my $groups_213_a = $poi->_get_poi_favourite_for_region({GeoByDomainIp => 213, LocalWday => $wday});
my $groups_213_b = ['megastore', 'mall'];
is_deeply([sort map ($_->{subgroup}, @$groups_213_a)], [sort @$groups_213_b], 'Groups 213 1 OK');

$wday = 6;                                                                                            # суббота
$groups_213_a = $poi->_get_poi_favourite_for_region({GeoByDomainIp => 213, LocalWday => $wday, LocalYYYYMMDDHHMMSS => '20150310111300'});
$groups_213_b = ['flowers'];
is_deeply([sort map ($_->{subgroup}, @$groups_213_a)], [sort @$groups_213_b], 'Groups 213 2 OK');

$groups_213_a = $poi->_get_poi_favourite_for_region({GeoByDomainIp => 213, LocalWday => $wday, LocalYYYYMMDDHHMMSS => '20150501111300'});
$groups_213_b = [];
is_deeply([sort map ($_->{subgroup}, @$groups_213_a)], [sort @$groups_213_b], 'Groups 213 3 OK');

# у региона есть свое описание
my $groups_14_a = $poi->_get_poi_favourite_for_region({GeoByDomainIp => 14});
my $groups_14_b = ['ministore'];
is_deeply([sort map ($_->{subgroup}, @$groups_14_a)], [sort @$groups_14_b], 'Groups 14 OK');

$wday = 5;    # пятница
$groups_213_a = $poi->_get_poi_favourite_for_region({GeoByDomainIp => 213, LocalWday => $wday, LocalYYYYMMDDHHMMSS => '20150310111300'});

my $weights_213 = {
    'megastore' => {m => 10 * 2 + 10 * 1, d => 10 * 2, e => 10 * 2, n => 10 * 2},
    'mall' => {m => 20 * 2, d => 20 * 2 + 10 * 2, e => 20 * 2, n => 20 * 2},
    'flowers' => {m => 30, d => 30, e => 30 + 10 * 3, n => 30 + 10 * 4},
};

for my $gr (@$groups_213_a) {
    my $weight_m = $poi->_get_weight_for_poi_favourite({LocalHHMM => '0700'}, $gr);
    is($weight_m, $weights_213->{$gr->{subgroup}}->{m}, 'Weight Morning 1 for ' . $gr->{subgroup} . ' OK');

    my $weight_m = $poi->_get_weight_for_poi_favourite({LocalHHMM => '1000'}, $gr);
    is($weight_m, $weights_213->{$gr->{subgroup}}->{m}, 'Weight Morning 2 for ' . $gr->{subgroup} . ' OK');

    my $weight_d = $poi->_get_weight_for_poi_favourite({LocalHHMM => '1200'}, $gr);
    is($weight_d, $weights_213->{$gr->{subgroup}}->{d}, 'Weight Day 1 for ' . $gr->{subgroup} . ' OK');

    my $weight_d = $poi->_get_weight_for_poi_favourite({LocalHHMM => '1335'}, $gr);
    is($weight_d, $weights_213->{$gr->{subgroup}}->{d}, 'Weight Day 2 for ' . $gr->{subgroup} . ' OK');

    my $weight_e = $poi->_get_weight_for_poi_favourite({LocalHHMM => '1800'}, $gr);
    is($weight_e, $weights_213->{$gr->{subgroup}}->{e}, 'Weight Evening 1 for ' . $gr->{subgroup} . ' OK');

    my $weight_e = $poi->_get_weight_for_poi_favourite({LocalHHMM => '2030'}, $gr);
    is($weight_e, $weights_213->{$gr->{subgroup}}->{e}, 'Weight Evening 2 for ' . $gr->{subgroup} . ' OK');

    my $weight_n = $poi->_get_weight_for_poi_favourite({LocalHHMM => '2330'}, $gr);
    is($weight_n, $weights_213->{$gr->{subgroup}}->{n}, 'Weight Night 1 for ' . $gr->{subgroup} . ' OK');

    my $weight_n = $poi->_get_weight_for_poi_favourite({LocalHHMM => '2359'}, $gr);
    is($weight_n, $weights_213->{$gr->{subgroup}}->{n}, 'Weight Night 2 for ' . $gr->{subgroup} . ' OK');

    my $weight_n = $poi->_get_weight_for_poi_favourite({LocalHHMM => '0000'}, $gr);
    is($weight_n, $weights_213->{$gr->{subgroup}}->{n}, 'Weight Night 3 for ' . $gr->{subgroup} . ' OK');

    my $weight_n = $poi->_get_weight_for_poi_favourite({LocalHHMM => '0300'}, $gr);
    is($weight_n, $weights_213->{$gr->{subgroup}}->{n}, 'Weight Night 4 for ' . $gr->{subgroup} . ' OK');
}

$wday = 5;    # пятница, день
my $req = {GeoByDomainIp => 213, LocalWday => $wday, LocalYYYYMMDDHHMMSS => '20150310111300', LocalHHMM => '1432'};
$groups_213_a = $poi->_get_poi_favourite_for_region($req);
$groups_213_a = $poi->_order_poi_favourite($req, $groups_213_a);
$groups_213_b = ['mall', 'flowers', 'megastore'];
is_deeply([map ($_->{subgroup}, @$groups_213_a)], [@$groups_213_b], 'Groups 213 Order OK');

done_testing();

