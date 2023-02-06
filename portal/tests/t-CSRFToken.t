use strict; use warnings;
use Test::Most;
use Data::Dumper;
use lib::abs qw( . ../lib);
die_on_fail();

use_ok('CSRFToken');
use_ok("MordaX::Req");

no warnings 'redefine', 'once';
*CSRFToken::logit = sub { note 'Redefined logit function tells: ', join(', ', @_) };
use warnings 'redefine', 'once';

my $key       = 'zxhCGbvp01cEvQCw';
my $yandexuid = '6447714881391768016';
my $uid       = 0;                       # Пользователь не авторизован

#fake req
my $req = MordaX::Req->new();
$req->{yandexuid} = $yandexuid;
$req->{AuthOBJ}   = {};

my $token = 'CSRFToken'->new($req, key => $key);
is ref $token, 'CSRFToken';

is $token->key,       $key;
is $token->uid,       $uid;
is $token->type,      'sha256';
is $token->yandexuid, $yandexuid;
ok $token->lifetime > 0;
is $token->timestamp, time();

# генерируем для заданного ts
my $ts = '1438861750';
$token->timestamp($ts);
is $token->timestamp, $ts;
my $etalon_hmac = '2a06e9d76097cac1d2fc731b88ef635238d57adfac739244f83086f11def93cd:1438861750';

{
    my $hmac = $token->generate();
    ok length($hmac) > 0;
    is $hmac, $etalon_hmac;
    note $hmac;
}

{
    my $hmac = 'CSRFToken'->new($req, key => $key, timestamp => $ts)->generate();
    ok length($hmac) > 0;
    is $hmac, $etalon_hmac;
}

{
    my $hmac = 'CSRFToken'->new($req, key => $key)->generate();
    ok length($hmac) > 0;
    note 'hmac ', $hmac;
    note 'time ', time;

    my $is_valid = 'CSRFToken'->new($req, key => $key)->is_valid($hmac);
    ok $is_valid;

    $is_valid = 'CSRFToken'->new($req, key => $key)->is_valid($hmac . 'garbage');
    ok !$is_valid;
}

{
    my $token = 'CSRFToken'->new($req, key => $key);
    my $lifetime = $token->lifetime;
    note $lifetime;
    my $timestamp = time - $lifetime + 10;

    #check valid token
    $token->timestamp($timestamp);
    my $hmac = $token->generate();
    note time;
    note $hmac;
    my $is_valid = 'CSRFToken'->new($req, key => $key)->is_valid($hmac);
    ok $is_valid;

    #check expired token
    $timestamp = time - $lifetime - 1;
    $token->timestamp($timestamp);
    $hmac = $token->generate();
    note time;
    note $hmac;
    $is_valid = 'CSRFToken'->new($req, key => $key)->is_valid($hmac);
    ok !$is_valid;
}

{
    delete $req->{yandexuid};
    my $hmac = 'CSRFToken'->new($req, key => $key)->generate();
    ok !$hmac;
}

{
    my $hmac = '453f5140aa219b524a6939674fc48ba135867cecaf26b09a13f42c1cc2733570:' . time;
    my $is_valid = 'CSRFToken'->new($req, key => $key)->is_valid($hmac);
    ok !$is_valid;
}
{
    my $uid = 111222333;
    $req->{AuthOBJ}->{UID} = $uid;
    my $token = 'CSRFToken'->new($req, key => $key);
    is $token->uid, $uid;

}
done_testing();

exit(0);
