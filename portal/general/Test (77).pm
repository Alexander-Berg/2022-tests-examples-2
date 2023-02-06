package MordaX::Experiment::AB::Tree::Primary::NOT::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro;

use base qw(MordaX::Experiment::AB::Tree::Primary::Test);

use Test::More;

sub class {'MordaX::Experiment::AB::Tree::Primary::NOT'}

sub test_as_string_one_node : Tests {
    my ($self) = @_;
    my $subnode = $self->simple_node("some");
    is($self->class->new($subnode)->as_string, '!(some)');
    return $self;
}

sub test_evaluate : Tests {
    my ($self) = @_;
    my $true   = $self->true_node;
    my $false  = $self->false_node;
    is($self->class->new($false)->evaluate, 1, 'true: !0');
    is($self->class->new($true)->evaluate,  0, 'false: !1');
    return $self;
}

1;
