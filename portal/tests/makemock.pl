#!/usr/bin/perl

use Test::More;
use lib::abs qw(../lib);
use MP::MakeMock;
use MP::MockData;

use_ok("MP::MakeMock");

sub test {
    my ($in) = @_;
    return [3, 2];
}

test("a");    #MOCKME

#MP::MockData::dmp();

done_testing(1);
