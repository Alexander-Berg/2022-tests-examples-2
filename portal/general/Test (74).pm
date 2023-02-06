package MordaX::Experiment::AB::Tree::Primary::Internal::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro;

use base qw(MordaX::Experiment::AB::Tree::Primary::Test);

use Test::More;
use MTH;

sub class {'MordaX::Experiment::AB::Tree::Primary::Internal'}

sub test_evaluate : Tests {
    my ($self) = @_;
    for my $internal (0, 1) {
        my $test_name = ($internal ? 'true: ' : 'false: ')
          . $self->class . '->new("internal")'
          . '->evaluate(' . explain_args({ YandexInternal => $internal })
          . ')';
        my $tree = $self->class->new("internal");
        my $req = { YandexInternal => $internal };
        is($tree->evaluate($req), $internal, $test_name);
    }
    return $self;
}

1;
