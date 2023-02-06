package MordaX::Block::Afisha_events::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro;

use base qw(Test::Class);

use Test::More;

use MordaX::Block::Afisha_events;
use MordaX::Lang;

my %MONTHS = (
    'month_accus.1'  => 'января',
    'month_accus.2'  => 'февраля',
    'month_accus.3'  => 'марта',
    'month_accus.4'  => 'апреля',
    'month_accus.5'  => 'мая',
    'month_accus.6'  => 'июня',
    'month_accus.7'  => 'июля',
    'month_accus.8'  => 'августа',
    'month_accus.9'  => 'сентября',
    'month_accus.10' => 'октября',
    'month_accus.11' => 'ноября',
    'month_accus.12' => 'декабря',
    'month_name.1'   => 'январь',
    'month_name.2'   => 'февраль',
    'month_name.3'   => 'март',
    'month_name.4'   => 'апрель',
    'month_name.5'   => 'май',
    'month_name.6'   => 'июнь',
    'month_name.7'   => 'июль',
    'month_name.8'   => 'август',
    'month_name.9'   => 'сентябрь',
    'month_name.10'  => 'октябрь',
    'month_name.11'  => 'ноябрь',
    'month_name.12'  => 'декабрь',
);

sub _make_dates_text : Tests(10) {
    my $self = shift;

    no warnings 'redefine';
    *MordaX::Lang::lang = sub { $MONTHS{$_[0]} };

    my @tests = (
        [[qw/2019-03-01/], '1 марта'],
        [[qw/2019-01-01 2019-01-02/], '1, 2 января'],
        [[qw/2019-04-01 2019-04-02 2019-04-05/], '1, 2, 5 апреля'],
        [[qw/2019-02-01 2019-05-10 2019-05-15/], '1 февраля, 10, 15 мая'],
        [[qw/2019-06-01 2019-07-01 2019-07-15/], '1 июня, 1, 15 июля'],
        [[qw/2019-08-01 2019-08-10 2019-09-15/], '1, 10 августа, 15 сентября'],
        [[qw/2019-10-01 2019-10-10 2019-10-15 2019-10-25/], 'октябрь'],
        [[qw/2019-11-01 2019-11-10 2019-12-15 2019-12-25/], 'ноябрь, декабрь'],
        [[qw/2019-06-01 2019-07-01 2019-08-15/], '1 июня, 1 июля'],
        [[qw/2019-06-01 2019-07-01 2019-08-15 2019-09-15/], 'июнь, июль'],
    );

    for (@tests) {
        is MordaX::Block::Afisha_events::_make_dates_text($_->[0]), $_->[1];
    }
}


1;

