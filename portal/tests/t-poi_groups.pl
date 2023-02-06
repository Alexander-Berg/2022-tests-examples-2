#!/usr/bin/perl
use common::sense;
use Test::More;
use 5.010;
use lib::abs qw(../lib .);
#use InitBase;
use Geo qw(geo);
use Data::Dumper;
#use InitBase;
use MordaX::Data_load;
use_ok("MordaX::Block::Poi");
use_ok("Geo");
Geo::init();

#MordaX::Data_load::load_static_exports(qw/poi_groups/);
#my $blocks = MordaX::Data_get::get_static_data({}, 'poi_groups');
#print Dumper $blocks;
#die;
%MordaX::Data_load::static_exports = (map { $_ => 1 } qw/poi_groups/);
#shops breakfast dinner supper night drugstore gas atm
%MordaX::Data::storage = (
    poi_groups => {
        'index' => {map { $_ => 1 } qw/geo geos/},
        'indexed' => {
            '10000' => [
                {
                    'geos'     => '10000',
                    'id'       => 'shops',
                    'week_day' => '1,2,3,4,5',
                    'order'    => 1,
                },
                {
                    'geos'  => '10000',
                    'id'    => 'drugstore',
                    'order' => 3,
                },
                {
                    'geos'  => '10000',
                    'id'    => 'gas',
                    'order' => 4,
                },
                {
                    'geos'     => '10000',
                    'id'       => 'helloween',
                    'disabled' => 1,
                },
                {
                    'geos'    => '10000',
                    'id'      => 'breakfast',
                    'morning' => 1,
                    'order'   => 2,
                },
                {
                    'geos'  => '10000',
                    'id'    => 'dinner',
                    'day'   => 2,
                    'order' => 2,
                },
                {
                    'geos'    => '10000',
                    'id'      => 'supper',
                    'evening' => 3,
                    'order'   => 2,
                },
                {
                    'geos'  => '10000',
                    'id'    => 'night',
                    'night' => 4,
                    'order' => 2,
                },
            ],
            '213' => [
                {
                    'geos' => '213',
                    'id'   => 'bankomats',
                },
                {
                    'geos' => '213',
                    'id'   => 'drugstore',
                },
                {
                    'geos' => '213',
                    'id'   => 'flowers',
                    'till' => '2015-04-07 23:00',
                    'from' => '2015-03-01 00:00',
                },
            ],
            '976' => [
                {
                    'geos'     => '976',
                    'id'       => 'bankomats',
                    'disabled' => 1,
                },
            ],
            '14' => [
                {
                    'geos'     => '14',
                    'id'       => 'cinema',
                    'week_day' => '5,6,7',
                },
                {
                    'geos'     => '14',
                    'id'       => 'clubs',
                    'week_day' => '6,7',
                },
                {
                    'geos'     => '14',
                    'id'       => 'drugstore',
                    'week_day' => 'workday',
                },
            ],
        },
    },
);

my $poi = MordaX::Block::Poi->new();
is(ref $poi, 'MordaX::Block::Poi', 'Obj OK');

# тестирование выборки рубрик

# у региона есть свое описание
my $groups_213_a = $poi->_get_poi_groups_for_region({GeoByDomainIp => 213, LocalYYYYMMDDHHMMSS => '20150201111300'});
my $groups_213_b = ['bankomats', 'drugstore'];
is_deeply([sort map ($_->{id}, @$groups_213_a)], [sort @$groups_213_b], 'Groups 213 1 OK');

my $groups_213_a_d = $poi->_get_poi_groups_for_region({GeoByDomainIp => 213, LocalYYYYMMDDHHMMSS => '20150401111300'});
my $groups_213_b_d = ['bankomats', 'drugstore', 'flowers'];
is_deeply([sort map ($_->{id}, @$groups_213_a)], [sort @$groups_213_b], 'Groups 213 2 OK');

# у региона нет своего описания
my $wday       = 1;                                                                            # понедельник
my $groups_6_a = $poi->_get_poi_groups_for_region({GeoByDomainIp => 6, LocalWday => $wday});
my $groups_6_b = [qw/breakfast dinner drugstore gas night shops supper/];
is_deeply([sort map ($_->{id}, @$groups_6_a)], [sort @$groups_6_b], 'Groups 6 OK');

# у региона есть описание, но все отключено
my $groups_976_a = $poi->_get_poi_groups_for_region({GeoByDomainIp => 976});
my $groups_976_b = [];
is_deeply([sort map ($_->{id}, @$groups_976_a)], [sort @$groups_976_b], 'Groups 976 OK');

# у региона есть описание, фильтрация по дням недели
$wday = 0;                                                                                     # воскресенье
my $groups_14_a_0 = $poi->_get_poi_groups_for_region({GeoByDomainIp => 14, LocalWday => $wday});
my $groups_14_b_0 = ['cinema', 'clubs'];
is_deeply([sort map ($_->{id}, @$groups_14_a_0)], [sort @$groups_14_b_0], 'Groups 14 wday 0 OK');

$wday = 1;
my $groups_14_a_1 = $poi->_get_poi_groups_for_region({GeoByDomainIp => 14, LocalWday => $wday});
my $groups_14_b_1 = ['drugstore'];
is_deeply([sort map ($_->{id}, @$groups_14_a_1)], [sort @$groups_14_b_1], 'Groups 14 wday 1 OK');

$wday = 5;                                                                                     # пятница
my $groups_14_a_6 = $poi->_get_poi_groups_for_region({GeoByDomainIp => 14, LocalWday => $wday});
my $groups_14_b_6 = ['cinema', 'drugstore'];
is_deeply([sort map ($_->{id}, @$groups_14_a_6)], [sort @$groups_14_b_6], 'Groups 14 wday 5 OK');

my $weights_6 = {
    breakfast => {m => 20 + 10 * 1, d => 20, e => 20, n => 20},
    dinner => {m => 20, d => 20 + 10 * 2, e => 20, n => 20},
    supper => {m => 20, d => 20, e => 20 + 10 * 3, n => 20},
    night     => {m => 20, d => 20, e => 20, n => 20 + 10 * 4},
    drugstore => {m => 20, d => 20, e => 20, n => 20},
    gas       => {m => 20, d => 20, e => 20, n => 20},
    shops => {m => 20 * 2, d => 20 * 2, e => 20 * 2, n => 20 * 2},
};
# тестирование весов
for my $gr (@$groups_6_a) {
    my $weight_m = $poi->_get_weight_for_poi_group({LocalHHMM => '0700'}, $gr);
    is($weight_m, $weights_6->{$gr->{id}}->{m}, 'Weight Morning 1 for ' . $gr->{id} . ' OK');

    my $weight_m = $poi->_get_weight_for_poi_group({LocalHHMM => '1000'}, $gr);
    is($weight_m, $weights_6->{$gr->{id}}->{m}, 'Weight Morning 2 for ' . $gr->{id} . ' OK');

    my $weight_d = $poi->_get_weight_for_poi_group({LocalHHMM => '1200'}, $gr);
    is($weight_d, $weights_6->{$gr->{id}}->{d}, 'Weight Day 1 for ' . $gr->{id} . ' OK');

    my $weight_d = $poi->_get_weight_for_poi_group({LocalHHMM => '1335'}, $gr);
    is($weight_d, $weights_6->{$gr->{id}}->{d}, 'Weight Day 2 for ' . $gr->{id} . ' OK');

    my $weight_e = $poi->_get_weight_for_poi_group({LocalHHMM => '1800'}, $gr);
    is($weight_e, $weights_6->{$gr->{id}}->{e}, 'Weight Evening 1 for ' . $gr->{id} . ' OK');

    my $weight_e = $poi->_get_weight_for_poi_group({LocalHHMM => '2030'}, $gr);
    is($weight_e, $weights_6->{$gr->{id}}->{e}, 'Weight Evening 2 for ' . $gr->{id} . ' OK');

    my $weight_n = $poi->_get_weight_for_poi_group({LocalHHMM => '2330'}, $gr);
    is($weight_n, $weights_6->{$gr->{id}}->{n}, 'Weight Night 1 for ' . $gr->{id} . ' OK');

    my $weight_n = $poi->_get_weight_for_poi_group({LocalHHMM => '2359'}, $gr);
    is($weight_n, $weights_6->{$gr->{id}}->{n}, 'Weight Night 2 for ' . $gr->{id} . ' OK');

    my $weight_n = $poi->_get_weight_for_poi_group({LocalHHMM => '0000'}, $gr);
    is($weight_n, $weights_6->{$gr->{id}}->{n}, 'Weight Night 3 for ' . $gr->{id} . ' OK');

    my $weight_n = $poi->_get_weight_for_poi_group({LocalHHMM => '0300'}, $gr);
    is($weight_n, $weights_6->{$gr->{id}}->{n}, 'Weight Night 4 for ' . $gr->{id} . ' OK');
}

# тестирование сортировки и фильтрации
my $req = {GeoByDomainIp => 6, LocalWday => 1, LocalHHMM => '0300'};
$groups_6_a = $poi->_get_poi_groups_for_region($req);
my $groups_6_ord_a = $poi->_order_poi_groups($req, $groups_6_a);

is(scalar @$groups_6_ord_a,    4,           'Groups OK');
is($groups_6_ord_a->[0]->{id}, 'night',     'Order Night OK');
is($groups_6_ord_a->[1]->{id}, 'shops',     'Order Shops OK');
is($groups_6_ord_a->[2]->{id}, 'drugstore', 'Order Drugstore OK');
is($groups_6_ord_a->[3]->{id}, 'gas',       'Order Gas OK');

my $gr = [{subgroups_list => 'food store, supermarket, univermag,megastore'}];
my $gr_f = $poi->_format_poi_groups($gr);
is_deeply($gr_f->[0]->{subgroups}, ['food store', 'supermarket', 'univermag', 'megastore'], 'Split 1 OK');

$gr = [{subgroups_list => '  club1  ,  club2 ;club3   ;   club4  '}];
$gr_f = $poi->_format_poi_groups($gr);
is_deeply($gr_f->[0]->{subgroups}, ['club1', 'club2', 'club3', 'club4'], 'Split 2 OK');

done_testing();
