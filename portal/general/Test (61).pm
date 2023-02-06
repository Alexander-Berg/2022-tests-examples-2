package MordaX::Experiment::AB::Tree::Equality::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro 'c3';

use base qw(
  MordaX::Experiment::AB::Tree::DoubleTest
  MordaX::Experiment::AB::Tree::Node::Test
);

use Test::More;
use MTH;

sub package {'MordaX::Experiment::AB::Tree::Equality'}

sub class {'MordaX::Experiment::AB::Tree::Equality'}

sub isa_test {
    my ($self, $instance) = (shift, @_);
    $self->next::method(@_);
    if (ref $self ne __PACKAGE__) {
        isa_ok($instance, 'MordaX::Experiment::AB::Tree::Equality');
    }
    return $self;
}

sub evaluate_ok { () }

sub evaluate_not_ok { () }

sub test_evaluate : Tests {
    my ($self) = @_;
    my $op = $self->class->_double_op();
    for my $t ($self->evaluate_ok()) {
        my ($lt, $rt) = map { $self->simple_node($_) } @$t;
        my ($ls, $rs) = map { explain_args($_) } @$t;
        is($self->class->new($lt, $rt)->evaluate, 1, "true: $ls $op $rs");
        is($self->class->new($rt, $lt)->evaluate, 1, "true: $rs $op $ls");
    }
    for my $t ($self->evaluate_not_ok()) {
        my ($lt, $rt) = map { $self->simple_node($_) } @$t;
        my ($ls, $rs) = map { explain_args($_) } @$t;
        is($self->class->new($lt, $rt)->evaluate, 0, "false: $ls $op $rs");
        is($self->class->new($rt, $lt)->evaluate, 0, "false: $rs $op $ls");
    }
    return $self;
}

1;
