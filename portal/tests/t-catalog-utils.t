#!/usr/bin/perl

=h1 ISSUES
home-7805
=cut

use strict;
use warnings;

use lib::abs qw( ../lib/ );
use Test::More qw(no_plan);

use MordaX::Block::CatalogCache;
use Data::Dumper;

my $merge = \&MordaX::Block::CatalogCache::merge_widget_queues;

ok($merge, "function found");

subtest "Simple merge" => sub {
    my ($w, $count) = &$merge(
        src => [
            {
                ru => [qw/R1  4000  R2 2000 R3 1000/],
                ua => [qw/R4  4500  R5 3500 /]
            },
        ],
    );
    is(scalar @$w, 5,    'Size ok');
    is($count,     5,    'count ok');
    is($w->[0],    'R4', 'first ok');
    is($w->[1],    'R1', 'ok');
    is($w->[2],    'R5', 'ok');
    is($w->[3],    'R2', 'forth ok');

    done_testing();
};

subtest "Double merge" => sub {
    my ($w, $count) = &$merge(
        src => [
            {
                ru => [qw/R1  4001  R2 2000 R3 1000/],
                ua => [qw/R4  4500  R5 3500 /]
            },
            {
                ru => [qw/C1  4000  C2 2000 C3 999/],
                ua => [qw/C4  4501  C5 3500 /]
            },
        ],
    );
    is(scalar @$w, 10,   'Size ok');
    is($count,     10,   'count ok');
    is($w->[0],    'C4', 'first ok');
    is($w->[1],    'R4', 'ok');
    is($w->[2],    'R1', 'ok');
    is($w->[3],    'C1', 'forth ok');
    is($w->[9],    'C3', 'last ok');

    done_testing();
};
subtest "language merge" => sub {
    my ($w, $count) = &$merge(
        rating_k => {
            lang => {
                ru => {m => 1.1},
                uk => {c => 101},
            },
        },
        src => [
            {
                ru => [qw/R1  10000 R2  5000 R3 1000/],
                uk => [qw/R11 10900 R12 5400 /],
                de => [qw/R21 10999 R22 1000 /],
            },
            {
                uk => [qw/C4  10800  C5 999 C6 0/]
            },
        ],
        debug => 0,
    );
    #diag(  Dumper($w) );
    is(scalar @$w, 10,    'Size ok');
    is($count,     10,    'count ok');
    is($w->[0],    'R11', 'first ok');
    is($w->[1],    'R1',  'seconf ok');
    is($w->[2],    'R21', 'ok');
    is($w->[4],    'R12', 'fifth ok');

    is($w->[8], 'R22', 'last ok');
    is($w->[9], 'C6',  'last ok');

    done_testing();
};

subtest "dublicate merge" => sub {
    my ($w, $count) = &$merge(
        rating_k => {
            lang => {
#                ru => { m => 1.1  },
#                uk => { c => 101  },
            },
        },
        src => [
            {
                ru => [qw/C4  10000    R2  5000    R3 1000/],
            },
            {
                uk => [qw/C4  10800    C5 999      C6 0/]
            },
        ],
        start => 2,
        limit => 2,

        debug => 0,
    );
    #diag(  Dumper($w) );
    is(scalar @$w, 2,    'Size ok');
    is($count,     5,    'count ok');
    is($w->[0],    'R3', 'first ok');
    is($w->[1],    'C5', 'seconf ok');

    done_testing();
};

