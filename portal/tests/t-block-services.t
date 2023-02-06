#!/usr/bin/perl
use strict;
use warnings FATAL => 'all';
use Data::Dumper;
use Test::Most;
die_on_fail();
use lib::abs qw( . ../lib);

use_ok('MordaX::Block::Services');
use_ok("MordaX::Req");
my $tabs = 'services_tabs';
my $v12  = 'services_v12_2';

my $tests = [
    {
        req => {},
        res => $v12,
    },
    {
        req => {MordaZone => 'com.tr', MordaContent => 'mob'},
        res => $v12,
    },
    {
        req => {MordaZone => 'com.tr', MordaContent => 'touch'},
        res => $v12,
    },
    {
        req => {MordaContent => 'com', isMobile => 0},
        res => $tabs,
    },
    {
        req => {MordaContent => 'com', isMobile => 1},
        res => $v12,
    },
    {
        req => {MordaZone => 'com.tr', comtr_old => 1},
        res => $tabs,
    },
    {
        req => {MordaZone => 'ru'},
        res => $v12,
    },
];

{
    no warnings 'redefine';
    *MordaX::Experiment::AB::Flags::new = sub {return bless {}, $_[0]};
    use warnings 'redefine';
    for my $t (@$tests) {
        is(MordaX::Block::Services::SourceData($t->{req}), $t->{res}, 'OK')
            or explain $t;
    }
}
my $setup_rotation = {
    'default_nosign' => ['money', 'fotki', 'disk',],
    'default_sign' => ['master', 'fine', 'market', 'auto', 'taxi', 'brbr', 'acac', 'lklk'],
    'pinned' => ['rabota', 'realty',],
};

my $weights = {
    'master' => 1,
    'fine'   => 2,
    'market' => 3,
    'auto'   => 4,
    'taxi'   => 5,
    'brbr'   => undef,
    'acac'   => 0,
};

my $req = MordaX::Req->new(
    req => {Cookies => {}},
);

use Test::MockModule;
my $module = new Test::MockModule('MordaX::Block::Services');
$module->mock('_services_defaults_is_showed_item', sub { return 1; });

my $block = MordaX::Block::Services->new;
{
    my $set = $setup_rotation->{'default_sign'};
    my $mixed_signed = MordaX::Block::Services::_services_defaults_mix_one_group($req, {'data' => $set, 'weights' => $weights});
    ok(scalar @$mixed_signed >= 4, 'Count OK');
}
{
    my $mixed = MordaX::Block::Services::_services_defaults_mix($req, {'data' => $setup_rotation, 'weights' => $weights});
    # количество сервисов ограничено
    ok(scalar @{$mixed->{'default_sign'}} >= 4, 'Count OK'); # потому что 6=4+2 (уменьшаем на количество pinned)

    # порядок этих сервисов без изменений
    is_deeply($mixed->{'default_nosign'}, $setup_rotation->{'default_nosign'}, 'Order OK');
    is_deeply($mixed->{'pinned'},         $setup_rotation->{'pinned'},         'Order OK');

    my $counter_sequencies = {};
    my $counter_elements   = {};
    for (1 .. 1000) {
        my $mixed = MordaX::Block::Services::_services_defaults_mix($req, { data => $setup_rotation, weights => $weights });
        @{$mixed->{default_sign}} = splice @{$mixed->{default_sign}}, 0, 3;
        my $key = join '|', @{$mixed->{default_sign}};
        # считаем общее попадание элементов в выборку
        $counter_elements->{$_}++ for @{$mixed->{default_sign}};
        # считаем количество различных последовательностей
        $counter_sequencies->{$key}++;
    }
    note explain $counter_sequencies;
    ok(scalar keys %$counter_sequencies > 1, 'Mixer OK');

    note explain $counter_elements;
    ok($counter_elements->{'taxi'} > $counter_elements->{'auto'},   'Taxi OK');
    ok($counter_elements->{'auto'} > $counter_elements->{'market'}, 'Auto OK');
    ok($counter_elements->{'market'} > $counter_elements->{'fine'}, 'Market OK');
    ok($counter_elements->{'fine'} > $counter_elements->{'master'}, 'Fine OK');
    ok(!$counter_elements->{'acac'},                                'Acac OK');
    ok(!$counter_elements->{'brbr'},                                'Acac OK');
    ok(!$counter_elements->{'lklk'},                                'lklk not found OK');
}
done_testing();
