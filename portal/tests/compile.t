#!/usr/bin/env perl

use Test::Compile 1.3.0;
use Test::Most;
die_on_fail();
use lib::abs qw(../lib);

my $test = Test::Compile->new();
my $skip = {
    'lib/MordaX/Cache/Mmap.pm' => 1,
};

for my $file ($test->all_pm_files('lib/MordaX')) {
    note "Skip $file", next if $skip->{$file};
    ok($test->pm_file_compiles($file), $file);
}

done_testing();
