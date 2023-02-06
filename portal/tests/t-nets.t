#!/usr/bin/perl

use warnings;
use lib::abs qw(../lib);
use Test::More;


use MordaX::Nets;

ok( MordaX::Nets::yandex_network( '5.45.226.80' ) );
ok( MordaX::Nets::yandex_network( '2a02:6b8:0:862::80') );
ok( !MordaX::Nets::yandex_network( '5.45.226.81' ) );

done_testing();

