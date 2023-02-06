#!/usr/bin/perl

use common::sense;
use Test::More;
use lib::abs qw(../lib) ;
use MP::Logit qw(dmp);


use_ok('Conf');
#use Conf;


#dmp(\%INC);

ok( $mordax::Conf );
ok( $mordax::Config );

ok( $mordax::Conf->GetVal('instance'), "instance online");

done_testing();
