#!/usr/bin/perl

use common::sense;
use Test::More;
use lib::abs qw(. ../lib ../t/testlib);

use testlib::TestRequest qw(r);
#use InitUtils;
use MordaTest;
use MordaX::Nets;
use MordaX::Logit qw(logit dmp);

my $r = testlib::TestRequest->fast_cgi_r(ip => '178.154.238.89', url => "https://www.yandex.ru/banner");
my $req = MordaX::Req->new();
my $input = MordaX::Input->new(r => $r, req => $req);

ok($MordaX::Nets::nets->in('_MARKETNETS_', $req->{'RemoteIp_Obj'}), 'MARKETNETS');

ok($req->{post_banner_allow});
is($req->{UriChain}->[0], 'banner');

done_testing();
