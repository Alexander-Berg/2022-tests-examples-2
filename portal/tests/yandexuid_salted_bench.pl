#!/usr/bin/perl

use lib::abs qw(../lib);
use MordaX::Experiment::AB::Helper qw(make_salted_slot);

use Benchmark qw(:all);

cmpthese(1000000, {
        'str' => sub {
            make_salted_slot(int(rand(1000)) . int(rand(1000)) . int(rand(1000)));
        },
        'unpack' => sub {
            my $slot = int(rand(1000)) . int(rand(1000)) . int(rand(1000));
            my $bin  = Digest::MD5::md5($slot, 'dsvyTDJDk2te96d');
            my $dec  = unpack("I1", $bin) % 1000;

        },
});
