package MordaX::Experiment::AB::Tree::Relational::NUM::LE::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro;

use base qw(MordaX::Experiment::AB::Tree::Relational::NUM::Test);

sub class {'MordaX::Experiment::AB::Tree::Relational::NUM::LE'}

sub expected_double_op {'<='}

sub evaluate_ok { (
        [123,        123],
        [0,          00],
        ['00000001', 1],
        [0xff,       255],
        [5,          12],
        [13,         100],
        [-5,         -2],
      ); }

sub evaluate_not_ok { (
        ['string', 'string'],
        ['',       undef],
        [0,        undef],
        [undef,    undef],
        ['Inf',    0],
        ['NaN',    0],
        ['Inf',    'Inf'],
        ['NaN',    'NaN'],
        [12,       5],
        [100,      13],
        [-2,       -5],
      ); }

1;

