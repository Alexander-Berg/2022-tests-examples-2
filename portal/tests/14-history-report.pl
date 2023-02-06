#!/usr/bin/perl

use Test::More qw(no_plan);

use common;
use strict;
use warnings;

use POSIX;
#--------------------------
#we  just testing mail mode
#----------

use WADM::Mailer;
#WADM::Mailer;

#load widget
#
require WADM::Index;
#use WBOX::Model::Widget;
#use WADM::Monitoring;
use WADM::History;

my $result = WADM::History::report(
    change_from  => '2010-06-01',
    change_until => '2010-06-03',
);

ok($result);
ok($result->{lines});
ok($result->{dates});

$result = WADM::History::report(
    change_from  => '2010-06-01',
    change_until => '2010-06-03',
    mode         => 'agregated',
);

ok($result);
$result = WADM::History::report(
    change_from  => '2010-06-01',
    change_until => '2010-06-03',
    mode         => 'agregated',
    unic         => 'week',
);
ok($result);
$result = WADM::History::report(
    change_from  => '2010-06-01',
    change_until => '2010-06-03',
    mode         => 'agregated',
    unic         => 'day',
);
ok($result);
$result = WADM::History::report(
    change_from  => '2010-06-01',
    change_until => '2010-06-03',
    mode         => 'agregated',
    unic         => 'day',
    showgroup    => 'week',
);
ok($result);

use Data::Dumper;

#print Dumper($result);

$result = WADM::History::get_active_users(
    change_from  => '2010-06-01',
    change_until => '2010-06-29',
);
ok($result, 'Active users returns somthing');
is(ref($result), 'ARRAY');
ok(scalar(@$result), 'Has Active users');
print Dumper($result);

