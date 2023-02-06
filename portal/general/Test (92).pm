package MordaX::Experiment::AB::Tree::Relational::STR::LT::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro;

use base qw(MordaX::Experiment::AB::Tree::Relational::STR::Test);

sub class {'MordaX::Experiment::AB::Tree::Relational::STR::LT'}

sub expected_double_op {'lt'}

sub evaluate_ok { (
        ['az',  'za'],
        ['aa',  'zd'],
        [12,    2],
        ['one', 'other'],
      ); }

sub evaluate_not_ok { (
        ['',       undef],
        ['a',      undef],
        [undef,    ''],
        [undef,    'a'],
        [undef,    undef],
        ['za',     'az'],
        ['zd',     'aa'],
        [2,        12],
        ['other',  'one'],
        ['123',    '123'],
        ['0',      00],
        ['',       ''],
        ['string', 'string'],
      ); }

1;

