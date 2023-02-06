#!/usr/bin/perl

use common::sense;
use Test::More;
use lib::abs qw(. ../lib ../t/testlib);

#use_ok("InitBase");
#use_ok("InitUtils");
use_ok('MordaTest');
use_ok('testlib::TestRequest');
use_ok('MordaX::Logit');

MordaX::Logit::enable_dumpit();
MordaX::Logit::logit('debug', "test");
dmp('test');

ok(testlib::TestRequest::r(), "r returns something");

done_testing();

