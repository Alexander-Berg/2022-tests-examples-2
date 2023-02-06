package MordaX::Experiment::AB::Tree::Equality::STR::NE::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro;

use base qw(MordaX::Experiment::AB::Tree::Equality::STR::Test);

sub class {'MordaX::Experiment::AB::Tree::Equality::STR::NE'}

sub expected_double_op {'ne'}

sub evaluate_ok { (
        ['213', '321'],
        [' ',   ''],
        ['one', 'other']
      ); }

sub evaluate_not_ok { (
        ['123',    '123'],
        ['0',      00],
        ['',       ''],
        ['string', 'string'],
        ['',       undef],
        [undef,    undef],
      ); }

1;

