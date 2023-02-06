package MordaX::Experiment::AB::Tree::Relational::VER::GT::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro;

use base qw(MordaX::Experiment::AB::Tree::Relational::VER::Test);

sub class {'MordaX::Experiment::AB::Tree::Relational::VER::GT'}

sub expected_double_op {'>'}

sub evaluate_ok { (
        [qw(6.1.3  6)],
        [qw(6.1.3c  6)],
        [qw(4..3 4)],
        [qw(2.3 1.2)],
      ); }

sub evaluate_not_ok { (
        [undef, 0],
        [undef, undef],
        [undef, 1],
        [1,     undef],
        [qw(6 6.1.3)],
        [qw(6 6.1.3c)],
        [qw(4 4..3)],
        [qw(1.2 2.3)],
        [qw(2.3  2.3)],
        [qw(1  1)],
        [qw(2  2.0)],
        [qw(2.2  2.2.0)],
        [qw(2  2.0.0.0.0)],
        [qw(7.5  7.5)],
        [qw(7.5b 7.5)],
      ); }

1;

