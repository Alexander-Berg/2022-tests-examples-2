#!/usr/bin/perl
use lib::abs qw(. ../lib);
use common::sense;
use Test::More;
use MordaX::Logit;
use MordaX::Utils;

my @plan = (
    ['http://www.ya.ru',          'lr', '20', 'http://www.ya.ru?lr=20'],
    ['http://www.ya.ru/?a=b',     'lr', '20', 'http://www.ya.ru/?a=b&lr=20'],
    ['http://www.ya.ru/?lr=',     'lr', '20', 'http://www.ya.ru/?lr=20'],
    ['http://www.ya.ru/?lr=0',    'lr', '20', 'http://www.ya.ru/?lr=20'],
    ['http://www.ya.ru/?lr=10',   'lr', '20', 'http://www.ya.ru/?lr=20'],
    ['https://www.ya.ru/?lr=1',   'lr', '20', 'https://www.ya.ru/?lr=20'],
    ['http://www.ya.ru#qwe',      'lr', '20', 'http://www.ya.ru?lr=20#qwe'],
    ['http://www.ya.ru?a=b#q&=w', 'lr', '20', 'http://www.ya.ru?a=b&lr=20#q&=w'],
);

for (@plan) {
    my $res = MordaX::Utils::add_getarg($_->[0], $_->[1], $_->[2]);
    ok($res eq $_->[3], $res . ' eq ' . $_->[3]);
}

done_testing();
