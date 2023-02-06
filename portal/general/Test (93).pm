package MordaX::Experiment::AB::Tree::Relational::STR::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro 'c3';

use base qw(MordaX::Experiment::AB::Tree::Relational::Test);

use Test::More;

sub class {'MordaX::Experiment::AB::Tree::Relational::STR'}

sub isa_test {
    my ($self, $instance) = (shift, @_);
    $self->next::method(@_);
    if (ref $self ne __PACKAGE__) {
        isa_ok($instance, 'MordaX::Experiment::AB::Tree::Relational::STR');
    }
    return $self;
}

1;
