package MP::LRU::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro;

use base qw(Test::Class);

use MP::Logit qw(dmp);

use Test::More;

use Scalar::Util qw(weaken);

sub requier : Test(startup => no_plan) {
    my ($self) = @_;
    use_ok('MP::LRU');
    return;
}

sub creation : Tests {
    my $cache = MP::LRU->new(5);
    isa_ok($cache, 'MP::LRU');
    is($cache->count,     0);
    is($cache->count_max, 5);
    is_deeply([$cache->keys],            []);
    is_deeply([$cache->keys_unsorted],   []);
    is_deeply([$cache->values],          []);
    is_deeply([$cache->values_unsorted], []);
    return;
}

sub public_interface : Tests {
    my $max_count = 5;
    my $cache = MP::LRU->new($max_count);

    for my $i (1 .. 10) {
        my $key   = $i;
        my $value = $i * 2;
        ok(not($cache->in($key)), "false: \$cache->in($key)");
        my $ret = $cache->add($key, $value);
        is($ret, $value, "\$cache->add($key, $value) == $value");
        ok($cache->in($key), "true: \$cache->in($key)");
        is($cache->get($key), $value, "\$cache->get($key) == $value");
        ok($cache->count <= $max_count, "true: \$cache->count <= $max_count");
    }

    my @expected_keys = reverse(6 .. 10);
    my @expected_values = map { $_ * 2 } @expected_keys;
    is_deeply(
        [$cache->keys],
        \@expected_keys,
        'test sorted by usage keys',
    );
    is_deeply(
        [sort $cache->keys_unsorted],
        [sort @expected_keys],
        'test unsorted keys',
    );

    is_deeply(
        [$cache->values],
        \@expected_values,
        'test sorted by usage values',
    );
    is_deeply(
        [sort $cache->values_unsorted],
        [sort @expected_values],
        'test unsorted values',
    );

    is($cache->get(8), 16, '$cache->get(8) == 16');
    is($cache->add(7, 70), 70, '$cache->add(7, 70) == 70');
    is($cache->remove(10),    20, '$cache->remove(10) == 20');
    is($cache->remove_last(), 12, '$cache->remove_last() == 12');
    @expected_keys = (7, 8, 9);
    @expected_values = map { $_ * 2 } @expected_keys;
    $expected_values[0] = 70;
    is_deeply(
        [$cache->keys],
        \@expected_keys,
        'test sorted by usage keys after manipulations',
    );
    is_deeply(
        [sort $cache->keys_unsorted],
        [sort @expected_keys],
        'test unsorted keys after manipulations',
    );
    is_deeply(
        [$cache->values],
        \@expected_values,
        'test sorted by usage values after manipulations',
    );
    is_deeply(
        [sort $cache->values_unsorted],
        [sort @expected_values],
        'test unsorted values after manipulations',
    );

    return;
}

sub tie_interface : Tests {
    my $max_count = 5;
    my %cache;
    tie %cache, 'MP::LRU', 5;
    for my $i (1 .. 10) {
        my $key   = $i;
        my $value = $i * 2;
        ok(not(exists $cache{$key}), "false: exists \$cache{$key}");
        my $ret = $cache{$key} = $value;
        is($ret, $value, "\$cache{$key} = $value == $value");
        ok(exists $cache{$key}, "true: exists \$cache{$key}");
        is($cache{$key}, $value, "\$cache{$key} == $value");
        ok(scalar(%cache) <= $max_count, "true: scalar(%cache) <= $max_count");
    }

    my @expected_keys = reverse(6 .. 10);
    my @expected_values = map { $_ * 2 } @expected_keys;
    is_deeply([keys %cache], \@expected_keys, 'test keys');
    is_deeply([keys %cache], \@expected_keys, 'test keys 2nd run');
    is_deeply([values %cache], \@expected_values, 'test values');
    @expected_values = reverse @expected_values;
    is_deeply([values %cache], \@expected_values, 'test values 2nd run');

    is($cache{8}, 16, '$cache{8} == 16');
    is($cache{7} = 70, 70, '($cache{7} = 70) == 70');
    is(delete $cache{10}, 20, 'delete $cache{10} == 20');
    @expected_keys = (7, 8, 9, 6);
    @expected_values = map { $_ * 2 } @expected_keys;
    $expected_values[0] = 70;
    is_deeply([keys %cache], \@expected_keys, 'test keys');
    is_deeply([keys %cache], \@expected_keys, 'test keys 2nd run');
    is_deeply([values %cache], \@expected_values, 'test values');
    @expected_values = reverse @expected_values;
    is_deeply([values %cache], \@expected_values, 'test values 2nd run');

    undef %cache;
    is_deeply([keys %cache], [], 'keys after cleanup');
    is_deeply([values %cache], [], 'values after cleanup');
    is(scalar(%cache), 0, 'scalar context after cleanup');
    return;
}

sub memory_leak_test : Tests {
    my $cache = MP::LRU->new(5);
    $cache->add($_, $_) for (1 .. 5);
    my @values = values %{ $cache->[MP::LRU::LRU_MAP()] };
    $cache->get($_) for (reverse(1 .. 5));
    weaken($_) for @values;
    $cache->add($_ * 10, $_ * 10) for (1 .. 5);
    is_deeply(\@values, [undef, undef, undef, undef, undef]);
    return;
}

1;
