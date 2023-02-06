package MordaX::Experiment::AB::Tree::Primary::String::Test;
use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro;

use base qw(MordaX::Experiment::AB::Tree::Primary::Test);

use Test::More;

sub class {'MordaX::Experiment::AB::Tree::Primary::String'}

sub new_tests_setup : Test(startup) {
    my $tests = shift->next::method(@_);
    push @$tests, (
        {
            name     => 'one arg undef',
            args     => [undef],
            errors   => 0,
            expected => [undef, undef],
        },
        {
            name     => 'one arg 0',
            args     => [0],
            errors   => 0,
            expected => [0, undef],
        },
    );
    return $tests;
}

sub test_as_string_one_node : Tests {
    my ($self) = @_;
    is($self->class->new(undef)->as_string, 'undef',  'as_string undef');
    is($self->class->new("0")->as_string,   q('0'),   'as_string 0');
    is($self->class->new("str")->as_string, q('str'), 'as_string "str"',);
    is($self->class->new(q('"''"))->as_string,
        q('\'"\'\'"'),
        'as_string q(\'"\'\'")',
    );
    return $self;
}

sub test_evaluate : Tests {
    my ($self) = @_;
    is($self->class->new(undef)->evaluate, undef, 'evaluate undef');
    is($self->class->new(0)->evaluate,     0,     'evaluate 0');
    is($self->class->new("str")->evaluate, 'str', 'evaluate "str"');
    is(
        $self->class->new(q('"''"))->evaluate,
        q('"''"),
        'evaluate q(\'"\'\'")',
    );
    return $self;
}

1;
