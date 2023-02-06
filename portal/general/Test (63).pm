package MordaX::Experiment::AB::Tree::Equality::VER::NE::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro;

use base qw(MordaX::Experiment::AB::Tree::Equality::VER::Test);

sub class {'MordaX::Experiment::AB::Tree::Equality::VER::NE'}

sub expected_double_op {'!='}

sub evaluate_ok { (
        [qw(7.4  7.5)],
        [qw(7.4.5  7.5.5)],
        [qw(4  7)],
      ); }

sub evaluate_not_ok { (
        [undef, 0],
        [undef, undef],
        [qw(2.3  2.3)],
        [qw(1  1)],
        [qw(2  2.0)],
        [qw(2.2  2.2.0)],
        [qw(2  2.0.0.0.0)],
        [qw(7.5  7.5)],
        [qw(7.5b 7.5)],
      ); }

1;

