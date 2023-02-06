#!/usr/bin/perl

use Test::More qw(no_plan);

use common;
use strict;
use warnings;

require WADM::Index;
use WBOX::Model::Widget;
use WBOX::Requester;
use WADM::Monitoring;
use WADM::History;
use POSIX;
use Digest::MD5 qw(md5_hex);
use Data::Dumper;

use WBOX::Storage;
use WBOX::Storage::Widgets;

my $ws = WBOX::Storage::Widgets->new();

ok($ws, "WS");

my $resp = $ws->list([13, 13, 99999, 13, 14]);

ok($resp);
is(ref($resp),      'ARRAY');
is(scalar @$resp,   4);
is(ref($resp->[0]), 'WBOX::Model::Widget');

#print @$resp ;
subtest "STRICT widget list responce" => sub {
    my $resp2 = $ws->list([13, 13, 99999, 13, 14], strict => 1);
    is(ref($resp2),    'ARRAY');
    is(scalar @$resp2, 5);
    is($resp2->[2],    undef);

    done_testing;
};

subtest "HASHED widget list response" => sub {
    my $resp3 = $ws->list([13, 13, 99999, 13, 14, 14], hashed => 1);
    is(ref($resp3), 'HASH');
    is(scalar @{$resp3->{99999}}, 0, "not found array size");
    is(scalar @{$resp3->{13}},    3, "found array size");
    is(scalar @{$resp3->{14}},    2, "found 14 widgets");

    done_testing();
};

subtest "list classses" => sub {

    my $resp = $ws->list_classes([13, 13, 99999, 13, 14, 14]);

    ok($resp);
    is(ref($resp), 'ARRAY');
    is(scalar @$resp, 2, "response classes size");
    is(ref($resp->[0]), 'WBOX::Model::Widget');

    my @list13 = grep { $_->id() == 13 } @$resp;
    is($#list13, 0, "one instance of 13");
    my @list14 = grep { $_->id() == 14 } @$resp;
    is($#list14, 0, "one instance of 14");

    my @ids = map { $_->id() } @$resp;

    diag("IDS: " . join(', ', @ids));

    done_testing();
};

subtest "listclasses with alias" => sub {
    my $resp = $ws->list_classes([qw/etrains/]);
    is(ref($resp), 'ARRAY');
    is(scalar @$resp, 1, "response classes size");
    is(ref($resp->[0]), 'WBOX::Model::Widget', 'Widget');

    done_testing();
};

subtest "ordered list with alias" => sub {
    my $resp = $ws->list([qw/13 14 99999 etrains 13/]);
    is(ref($resp),    'ARRAY');
    is(scalar @$resp, 4);
    ok($resp->[2], "etrains id");

    done_testing();

};
