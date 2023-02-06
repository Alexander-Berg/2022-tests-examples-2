#!/usr/bin/perl -w
use strict;
use utf8;
use lib::abs('../lib');

use Storable;

use MordaX::Cache;
use Data::Dumper;

binmode STDOUT, ':utf8';

my $hockey = MordaX::Cache->get('hockey2011');
if (defined($hockey)) {
    print Data::Dumper->Dump([$hockey], ['Hockey_data']) . "\n";
} else {
    print "Hockey data not found\n";
}

