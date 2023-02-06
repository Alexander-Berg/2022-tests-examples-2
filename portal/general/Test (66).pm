package MordaX::Experiment::AB::Tree::Logical::OR::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro;

use base qw(MordaX::Experiment::AB::Tree::Logical::Test);

use Test::More;

sub class {'MordaX::Experiment::AB::Tree::Logical::OR'}

sub expected_double_op {'||'}

sub test_evaluate : Tests {
    my ($self) = @_;
    my $true   = $self->true_node;
    my $false  = $self->false_node;
    is($self->class->new($false, $false)->evaluate, 0, 'false: 0 || 0');
    is($self->class->new($true,  $false)->evaluate, 1, 'true: 1 || 0');
    is($self->class->new($false, $true)->evaluate,  1, 'true: 0 || 1');
    is($self->class->new($true,  $true)->evaluate,  1, 'true: 1 || 1');
    return $self;
}

1;

