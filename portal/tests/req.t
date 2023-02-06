#!/usr/bin/perl

use lib::abs qw(. ../lib);
use common::sense;

use Test::More;
use MordaX::Logit;
use MordaX::Config;
$MordaX::Config::DevInstance = 1;

use_ok("MordaX::Req");
ok(MordaX::Req->new());
my $r1 = MordaX::Req->new();
ok($r1,           'REquest created without params');
ok($r1->{'time'}, 'time present');

my $r2 = MordaX::Req->new(req => {'x' => {'y' => 'z'}});
is($r2->{x}->{y}, 'z', 'clone works');

my $r3 = MordaX::Req->new('time' => 1390098201);
is($r3->{time}, 1390098201, "TIme ok");

done_testing();

