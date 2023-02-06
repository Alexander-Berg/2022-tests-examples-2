#!/usr/bin/perl

use strict;
use warnings;

use Test::More qw(no_plan);

use common;
use JSON::XS;
use Data::Dumper;

use WADM::History;
use WADM::Conf;

my $file = WADM::Conf->get('HistoryMaster');
ok(WADM::Conf->get('Devel'));
ok(WADM::Conf->get('Templates'));
ok($file, 'history master db in config');
my $dbh = WADM::History::_master_dbh();
ok($dbh);

#my $sth = $dbh->prepare('select name from version limit 1');
#$sth->execute();
#my ( $version )= $sth->fetchrow_array();
#$sth->finish();

#like($version, qr{wadm} );

my $hid = WADM::History::_db_log_action('test', -1, 'TEST:ACTION', 12, {hello => q{world}});
isnt($hid, undef);
print "# HID: $hid\n";
ok(my $list = WADM::History::_db_log_load(id => $hid));
is(scalar @$list, 1, 'returned 1 record');
#warn Dumper( $list );
is($list->[0]->{changes}->{hello}, q{world}, 'World recieved');
isnt(WADM::History::_db_log_action('test', -1, 'TEST:ACTION', 12), undef);

