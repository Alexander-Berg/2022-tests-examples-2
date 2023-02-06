package MordaX::Experiment::AB::Tree::Equality::STR::EQ::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro;

use base qw(MordaX::Experiment::AB::Tree::Equality::STR::Test);

sub class {'MordaX::Experiment::AB::Tree::Equality::STR::EQ'}

sub expected_double_op {'eq'}

sub evaluate_ok { (
        ['123',    '123'],
        ['0',      00],
        ['',       ''],
        ['string', 'string'],
      ); }

sub evaluate_not_ok { (
        ['213', '321'],
        ['',    undef],
        [undef, undef],
        [' ',   ''],
        ['one', 'other']
      ); }

1;

