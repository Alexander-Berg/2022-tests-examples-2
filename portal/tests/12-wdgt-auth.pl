#!/usr/bin/perl
use utf8;
use strict;
use warnings;

use Test::More qw(no_plan);

use lib::abs qw(../../lib .);

#--------------------------
#we  just testing mail mode
#----------

use common;
use MordaX::Conf;
use MordaX::Auth;
use MP::Logit qw{dmp};

use FakeInput;

my $Input   = FakeInput->new();
my $bb_conf = MordaX::Conf->get('black_box');
my $req     = {};
$req->{'_STATBOX_ID_SUFFIX_'} = 'wadm.test'; # HOME-37938

ok($bb_conf, 'black box Online');
ok($Input,   'input inited');

my $auth = MordaX::Auth->new($req, 'dontauth' => 1,);
my $zhx_auth = $auth->UserInfo($req, {
    'login'             => 'zhx',
    allow_yandexteam    => 1,
    emails              => 'getyandex'
});

is($zhx_auth->{'uid'},   434095, 'Uid right');
is($zhx_auth->{'login'}, 'zhx',  'login right');

$zhx_auth = $auth->UserInfo($req, {
    'uid'               => 434095,
    allow_yandexteam    => 1,
    emails              => 'getall'
});
ok($zhx_auth, 'userinfo by uid');
is($zhx_auth->{login}, 'zhx', 'login ok');

is($zhx_auth->{uid}, 434095, 'uid confirmed');
ok($zhx_auth->{emails}, 'emails loaded');
is($zhx_auth->{email}, 'zhx@yandex.ru', 'yandex email located');

my @outer = grep{!$_->{'native'}} @{$zhx_auth->{emails}};
ok(@outer, 'outer email ok');

my $rc = $auth->UserInfo($req, {
    'uid'               => 1,
    allow_yandexteam    => 1,
    emails              => 'getyandex'
});
ok($rc, 'Request complited to NotExistent UID');



