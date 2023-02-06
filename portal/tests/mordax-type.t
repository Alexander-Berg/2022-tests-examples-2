#!/usr/bin/perl

package mordax_logit;

use lib::abs qw(. ../lib);
use common::sense;

use utf8;
use Test::More;
use Test::Deep;

use MP::Logit qw(logit dmp);

use_ok('MordaX::Type');

use testlib::TestRequest;

my $r_api   = testlib::TestRequest::fast_cgi_r({url => '/api/search/1'});
my $r_rapid = testlib::TestRequest::fast_cgi_r({url => '/instant/all'});

ok($r_api);
ok($r_rapid);

my $req = MordaX::Req->new();
ok($req);
#dmp( $req );
ok($req->morda_type());

#dmp( $req );
is($req->morda_type(), $req->morda_type());

is(MordaX::Type->new(), undef, 'req is required');

done_testing();

