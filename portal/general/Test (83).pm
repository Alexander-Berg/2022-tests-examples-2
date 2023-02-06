package MordaX::Experiment::AB::Tree::Primary::Unsupported::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro;

use base qw(MordaX::Experiment::AB::Tree::Primary::Test);

use Test::More;

sub class {'MordaX::Experiment::AB::Tree::Primary::Unsupported'}

sub test_evaluate : Tests {
    my ($self) = @_;
    is($self->class->new('xxx')->evaluate, undef);
    return $self;
}

1;
