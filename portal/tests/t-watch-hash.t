#!/usr/bin/perl

use Test::More;
use lib::abs qw(../lib);
use_ok("WatchHash");
use_ok('MordaX::Req');
use_ok("Rapid::ReqWatch");

use_ok('MordaX::Logit');

MordaX::Logit::setup(1);
#MordaX::Logit::dmp('test');
ok(MordaX::Logit::enable_dumpit());

my %hash = (old => 1);
tie(%hash, "WatchHash");

is($hash{old}, undef, "Zerro on start");
ok($hash{'ok'} = 1, "SET");
ok($hash{'ok'}, "GET");

my %h2 = ('example' => 1,);

tie(%h2, "WatchHash", \%h2, "R2");

ok($h2{example}, "Get of erly setted");

#ok( \%h2->type() , "Type");

done_testing();

