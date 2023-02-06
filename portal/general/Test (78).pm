package MordaX::Experiment::AB::Tree::Primary::Number::Test;
use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro;

use base qw(MordaX::Experiment::AB::Tree::Primary::Test);

use Test::More;

sub class {'MordaX::Experiment::AB::Tree::Primary::Number'}

sub not_need_one_arg_new_test {1}

sub new_tests_setup : Test(startup) {
    my $tests = shift->next::method(@_);
    push @$tests, (
        {
            name     => 'one arg 0',
            args     => [0],
            errors   => 0,
            expected => [0, undef],
        },
        {
            name     => 'one arg 100',
            args     => [100],
            errors   => 0,
            expected => [100, undef],
        },
        {
            name     => 'one arg -5',
            args     => [-5],
            errors   => 0,
            expected => [-5, undef],
        },
        {
            name     => 'one arg "000002.22220000"',
            args     => ["000002.22220000"],
            errors   => 0,
            expected => [2.2222, undef],
        },
    );
    return $tests;
}

sub test_as_string_one_node : Tests {
    my ($self) = @_;
    is($self->class->new(0)->as_string,   0,    'as_string 0');
    is($self->class->new(100)->as_string, 100,  'as_string 100');
    is($self->class->new(-5)->as_string,  '-5', 'as_string -5');
    is(
        $self->class->new("000002.22220000")->as_string,
        2.2222,
        'as_string "000002.22220000"',
    );
    return $self;
}

sub test_evaluate : Tests {
    my ($self) = @_;
    is($self->class->new(0)->evaluate,   0,    'evaluate 0');
    is($self->class->new(100)->evaluate, 100,  'evaluate 100');
    is($self->class->new(-5)->evaluate,  '-5', 'evaluate -5');
    is(
        $self->class->new("000002.22220000")->evaluate,
        2.2222,
        'evaluate "000002.22220000"',
    );
    return $self;
}

1;
