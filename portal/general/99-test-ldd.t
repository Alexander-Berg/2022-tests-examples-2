#!/usr/bin/env perl

use strict;
use warnings;

use FindBin qw($RealBin);
use File::Basename qw(basename);
use File::Spec;
use File::Find qw(find);

use Test::More;

my $blib = File::Spec->catfile($RealBin, File::Spec->updir(), 'blib');

my $so;
find(
    sub { $so = $File::Find::name if basename($File::Find::name) eq 'Curl.so' },
    $blib
);

ok($so, "so found");

my %ldd;

open(my $fh, '-|', qw(ldd), $so)
  or die $!;
while (defined(local $_ = <$fh>)) {
    chomp;
    my ($l) = split;
    $l =~ s/so(?:\.[0-9]++)++$/so/g;
    $ldd{$l} = 1;
}
close($fh);

ok($ldd{'libcurl.so'},             "Has link with libcurl.so");
ok($ldd{'libssl.so'},              "Has link with libssl.so");
ok(not($ldd{'libcurl-gnutls.so'}), "Has NO link with libcurl-gnutls.so");

done_testing();
