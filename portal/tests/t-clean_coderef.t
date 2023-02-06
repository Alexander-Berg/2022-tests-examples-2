#!/usr/bin/perl

use common::sense;
use Test::More;
use lib::abs qw(../lib .);

use MordaX::Logit qw(dmp logit);

use Test::Deep;
use_ok("MordaX::Utils");
use_ok("MordaX::Req");

my $clean = \&MordaX::Utils::complex_clean;
ok($clean);

my $t1 = &$clean({a => 1, b => {c => 2}, d => [4, 5], e => sub { }});
ok($t1);

cmp_deeply($t1,
    {a => 1, b => {c => 2}, d => [4, 5], e => undef}
    , "simple sub hash and array");

my $req = MordaX::Req->new();

#ok( MordaX::Utils::is_hash( $req ));
my $rc = &$clean($req);
ok($rc);
ok($rc->{time}, 'HashValues in opbject are ok');
is(ref($rc), 'HASH');
#dmp( $req,$rc );

done_testing();
