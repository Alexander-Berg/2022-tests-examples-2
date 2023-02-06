#!/usr/bin/perl

use Test::More;
use lib::abs qw{../lib};
use_ok(qw/EP::Logger/);

$EP::Logger::setup{filesavelog} = lib::abs::path("../log/file.log.test");

my $h= EP::Logger::openfile( $EP::Logger::setup{filesavelog} );
ok( $h);
ok( syswrite( $h, "test\n", 5) , 'syswrite');

ok( EP::Logger::file('ok' => 1 ) );

done_testing();
