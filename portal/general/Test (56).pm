package MordaX::Experiment::AB::Tree::Equality::NUM::NE::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro;

use base qw(MordaX::Experiment::AB::Tree::Equality::NUM::Test);

sub class {'MordaX::Experiment::AB::Tree::Equality::NUM::NE'}

sub expected_double_op {'!='}

sub evaluate_ok { (
        [-1, 1],
        [12, 14],
      ); }

sub evaluate_not_ok { (
        [123,        123],
        [0,          00],
        ['00000001', 1],
        [0xff,       255],
        ['string',   'string'],
        ['',         undef],
        [0,          undef],
        [undef,      undef],
        ['Inf',      0],
        ['NaN',      0],
        ['Inf',      'Inf'],
        ['NaN',      'NaN'],
      ); }

1;

