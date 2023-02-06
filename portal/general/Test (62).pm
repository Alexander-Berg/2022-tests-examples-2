package MordaX::Experiment::AB::Tree::Equality::VER::EQ::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro;

use base qw(MordaX::Experiment::AB::Tree::Equality::VER::Test);

use Test::More;

use MTH;

sub class {'MordaX::Experiment::AB::Tree::Equality::VER::EQ'}

sub expected_double_op {'=='}

sub test_evaluate : Tests {
    my ($self) = @_;
    my @ok = (
        [qw(2.3  2.3)],
        [qw(1  1)],
        [qw(2  2.0)],
        [qw(2.2  2.2.0)],
        [qw(2  2.0.0.0.0)],
        [qw(7.5  7.5)],
        [qw(7.5b 7.5)],
    );
    my @not_ok = (
        [qw(7.4  7.5)],
        [qw(7.4.5  7.5.5)],
        [qw(4  7)],
        [undef, 0],
        [undef, undef],
    );
    for my $t (@ok) {
        my ($left, $right) = map { $self->simple_node($_) } @$t;
        my ($ls,   $rs)    = map { explain_args($_) } @$t;
        ok($self->class->new($left,  $right)->evaluate, "true: $ls == $rs");
        ok($self->class->new($right, $left)->evaluate,  "true: $rs == $ls");
    }
    for my $t (@not_ok) {
        my ($left, $right) = map { $self->simple_node($_) } @$t;
        my ($ls,   $rs)    = map { explain_args($_) } @$t;
        ok(not($self->class->new($left,  $right)->evaluate), "false: $ls == $rs");
        ok(not($self->class->new($right, $left)->evaluate),  "false: $rs == $ls");
    }
    return $self;
}

1;

