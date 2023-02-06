#!/usr/bin/env perl
use strict;
use warnings;

use Test::Most 'no_plan';

use lib::abs q(../lib);
use testlib::TestRequest;
use MordaX::Block::Teaser_service;

subtest 'TargetBlock' => sub {
    my $ret = MordaX::Block::Teaser_service::TargetBlock();
    is($ret, 'Teaser_service', 'Teaser_service');
};

subtest 'SourceData' => sub {
    do {
        my $ret = MordaX::Block::Teaser_service::SourceData();
        is($ret, 'teaser_service', 'teaser_service');
    };
    do {
        my $req = testlib::TestRequest->request();
        $req->{'MordaContent'} = 'touch';
        my $ret = MordaX::Block::Teaser_service::SourceData(undef, $req);
        is($ret, 'teaser_service_exp', 'teaser_service_exp');
    };
};

subtest 'init_once' => sub {
    MordaX::Block::Teaser_service::init_once();
    ok($MordaX::Block::Teaser_service::formats{'teaser_service'}, 'teaser_service defined');
    ok($MordaX::Block::Teaser_service::formats{'teaser_service_exp'}, 'teaser_service_exp defined');
};
