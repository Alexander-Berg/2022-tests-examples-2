package MordaX::Experiment::AB::Tree::Primary::I18N::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro;

use base qw(MordaX::Experiment::AB::Tree::Primary::Test);

use Test::More;
use MTH;

sub class {'MordaX::Experiment::AB::Tree::Primary::I18N'}

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
            name     => 'one arg "uk"',
            args     => ['uk'],
            errors   => 0,
            expected => ['uk', undef],
        },
    );
    return $tests;
}

sub test_as_string_one_node : Tests {
    my ($self) = @_;
    is($self->class->new("RU")->as_string, 'i18n:ru', 'as_string "RU"');
    is($self->class->new("uk")->as_string, 'i18n:uk', 'as_string "uk"');
    return $self;
}

sub test_evaluate : Tests {
    my ($self) = @_;
    my @tests = (
        {
            req_locale => 'ru',
            tree_i18n  => 'RU',
            result     => 1,
        },
        {
            req_locale => 'RU',
            tree_i18n  => 'ru',
            result     => 1,
        },
        {
            req_locale => 'ru',
            tree_i18n  => 'ru',
            result     => 1,
        },
        {
            req_locale => 'ru',
            tree_i18n  => 'UK',
            result     => 0,
        },
        {
            req_locale => 'ru',
            tree_i18n  => 'uk',
            result     => 0,
        },
    );

    for my $test (@tests) {
        my $req = { Locale => $test->{req_locale} };
        my $test_name = ($test->{result} ? 'true: ' : 'false: ')
          . $self->class . '->new(' . explain_args($test->{tree_i18n}) . ')'
          . '->evaluate(' . explain_args($req) . ')';
        my $tree = $self->class->new($test->{tree_i18n});
        is($tree->evaluate($req), $test->{result}, $test_name);
    }
    return $self;
}

1;
