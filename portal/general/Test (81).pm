package MordaX::Experiment::AB::Tree::Primary::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro;

use base qw(MordaX::Experiment::AB::Tree::Node::Test);

use Test::More;

sub package {'MordaX::Experiment::AB::Tree::Primary'}

sub class {'MordaX::Experiment::AB::Tree::Primary'}

sub not_need_one_arg_new_test { 0 }

sub new_tests_setup : Test(startup) {
    my ($self) = @_;
    my $node1  = $self->simple_node(1);
    my $node2  = $self->simple_node(2);
    return $self->{new_tests} = [
        {
            name     => 'without args',
            args     => [],
            errors   => 1,
            expected => undef,
        },
        {
            name     => 'two args 1st not base class',
            args     => ['some_arg', $self->simple_node(1)],
            errors   => 1,
            expected => undef,
        },
        {
            name     => 'two args 2nd not base class',
            args     => [$self->simple_node(1), 'some_arg'],
            errors   => 1,
            expected => undef,
        },
        {
            name     => 'two correct args',
            args     => [$node1, $node2],
            errors   => 1,
            expected => undef,
        },
        {
            name     => 'three args',
            args     => [qw(too many args)],
            errors   => 1,
            expected => undef,
        },
        (
            $self->not_need_one_arg_new_test
            ? ()
            : (
                {
                    name     => 'one arg',
                    args     => ['some_arg'],
                    errors   => 0,
                    expected => ['some_arg', undef],
                },
              )
        ),
    ];
}

sub test_as_string_two_nodes : Tests {
    my ($self) = @_;
    ok("skip as_string_two_nodes for " . $self->class);
    return $self;
}

sub isa_test {
    my ($self, $instance) = (shift, @_);
    $self->next::method(@_);
    if (ref $self ne __PACKAGE__) {
        isa_ok($instance, 'MordaX::Experiment::AB::Tree::Primary');
    }
    return $self;
}

1;


