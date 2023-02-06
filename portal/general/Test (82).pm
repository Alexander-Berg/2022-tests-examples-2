package MordaX::Experiment::AB::Tree::Primary::Tld::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro;

use base qw(MordaX::Experiment::AB::Tree::Primary::Test);

use Test::More;
use MTH;

sub class {'MordaX::Experiment::AB::Tree::Primary::Tld'}

sub not_need_one_arg_new_test {1}

sub new_tests_setup : Test(startup) {
    my $tests = shift->next::method(@_);
    push @$tests, (
        {
            name     => 'one arg "RU"',
            args     => ['RU'],
            errors   => 0,
            expected => ['ru', undef],
        },
        {
            name     => 'one arg "ua"',
            args     => ['ua'],
            errors   => 0,
            expected => ['ua', undef],
        },
    );
    return $tests;
}

sub test_as_string_one_node : Tests {
    my ($self) = @_;
    is($self->class->new("RU")->as_string, 'tld:ru', 'as_string "RU"');
    is($self->class->new("ua")->as_string, 'tld:ua', 'as_string "ua"');
    return $self;
}

sub test_evaluate : Tests {
    my ($self) = @_;
    my @tests = (
        { tree_tld => 'RU',         req_mordazone => 'ru',     result => 1 },
        { tree_tld => 'all',        req_mordazone => 'ru',     result => 1 },
        { tree_tld => 'all',        req_mordazone => 'com.tr', result => 1 },
        { tree_tld => 'ru',         req_mordazone => 'ru',     result => 1 },
        { tree_tld => 'ee',         req_mordazone => 'ee',     result => 1 },
        { tree_tld => 'all-com.tr', req_mordazone => 'by',     result => 1 },
        { tree_tld => 'all-com.tr', req_mordazone => 'com.tr', result => 0 },
        { tree_tld => 'comtr',      req_mordazone => 'com.tr', result => 1 },
        { tree_tld => 'kub',        req_mordazone => 'ru',     result => 1 },
        { tree_tld => 'kub',        req_mordazone => 'by',     result => 1 },
        { tree_tld => 'kub',        req_mordazone => 'ua',     result => 1 },
        { tree_tld => 'kub',        req_mordazone => 'kz',     result => 1 },
        { tree_tld => 'kub',        req_mordazone => 'uz',     result => 0 },
        { tree_tld => 'kubr-ua',    req_mordazone => 'ru',     result => 1 },
        { tree_tld => 'kubr-ua',    req_mordazone => 'by',     result => 1 },
        { tree_tld => 'kubr-ua',    req_mordazone => 'kz',     result => 1 },
        { tree_tld => 'kubr-ua',    req_mordazone => 'ua',     result => 0 },
        { tree_tld => 'kubru',      req_mordazone => 'kz',     result => 1 },
        { tree_tld => 'kubru',      req_mordazone => 'ua',     result => 1 },
        { tree_tld => 'kubru',      req_mordazone => 'by',     result => 1 },
        { tree_tld => 'kubru',      req_mordazone => 'ru',     result => 1 },
        { tree_tld => 'kubru',      req_mordazone => 'uz',     result => 1 },
        { tree_tld => 'kubru',      req_mordazone => 'com.tr', result => 0 },
        { tree_tld => 'kubru',      req_mordazone => 'ee',     result => 0 },
        { tree_tld => 'comtr',      req_mordazone => 'ru',     result => 0 },
    );
    for my $test (@tests) {
        my $req = { MordaZone => $test->{req_mordazone} };
        my $test_name = ($test->{result} ? 'true: ' : 'false: ')
          . $self->class . '->new(' . explain_args($test->{tree_tld}) . ')'
          . '->evaluate(' . explain_args($req) . ')';
        my $tree = $self->class->new($test->{tree_tld});
        is($tree->evaluate($req), $test->{result}, $test_name);
    }
    return $self;
}

1;
