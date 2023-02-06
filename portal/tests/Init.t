#!/usr/bin/perl

use common::sense;
use Test::More;
use lib::abs qw(../lib) ;
use MP::Logit qw(dmp);

use_ok("Init");
ok( $mordax::Conf->GetVal('BlackBox') );

done_testing();



