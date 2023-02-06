#!/usr/bin/perl

use strict;
use warnings;

use lib::abs qw(. ../t/testlib);
use MordaTest;
use MordaX::BlackBox;
use testlib::TestRequest qw(r);
use Test::More;

use MordaX::Logit qw(dmp);

use WBWI::Input;
use MordaX::Auth;

my $dmp = 0;

#my $bburl ="http://pass-test.yandex.ru/blackbox";
my $bburl = q{http://blackbox-mimino.yandex.net/blackbox};
my $session_id = q{3:1410260023.5.0.1410260023000:Gtm01Q:52.0|123167392.-1.0.1:47991|116341.507282.uH8icVSiEwFCe-2OKf9sDHmGsHk};
my ($req, $input, $r) = r(
    get     => {},
    cookies => {
        yandexuid  => '666941071298288078',
        Session_id => $session_id,
    },
);

$req->{'_STATBOX_ID_SUFFIX_'} = 'test'; # HOME-37938

ok($req,   "Request");
ok($input, "input");
ok($r,     "meta request");

my $wbwi_input = WBWI::Input->new($r);

ok($wbwi_input,                       "wbwidgets input ok");
ok($wbwi_input->cookie('Session_id'), 'session-id');
ok($wbwi_input->{'time'},             'time');
ok($wbwi_input->ip_from(),            'IP');

my $auth = MordaX::BlackBox::request(
    $req,
    'method'   => 'userinfo',
    'login'    => 'zhx',
    'bburl'    => $bburl,
    'dbfields' => [
        'accounts.login.uid',
        'subscription.login.2',    # needs for wadm (display authors email)
    ],
    'input' => $wbwi_input,
    'try'   => 1,
    # ip      => '213.180.217.26',
    #   'emails'    => 'getall',
);

ok($auth);
ok($auth->{uid}, 'request responce have uid');

subtest "BB UserInfo of Social User" => sub {
    #uid123167392
    my $rc = MordaX::BlackBox::request(
        $req,
        'method'   => 'userinfo',
        'uid'      => '123167392',
        'bburl'    => $bburl,
        'dbfields' => [
            # 'accounts.login.uid',
            'subscription.login.2',    # needs for wadm (display authors email)
            'subscription.login_rule.33',
        ],
        'input' => $wbwi_input,
        'try'   => 1,
        #'ip'    => '213.180.217.26',
    );

    dmp($rc) if $dmp;

    is($rc->{login}, '-', 'No login as -');    #
    done_testing();
};

subtest "BB UserInfo for DottedLogin" => sub {
# 1374587074.0.5.221607553.8
    my $rc = MordaX::BlackBox::request(
        $req,
        'method'   => 'userinfo',
        'uid'      => '221607553',
        'bburl'    => $bburl,
        'dbfields' => [
            # 'accounts.login.uid',
            'subscription.login.2',    # needs for wadm (display authors email)
            'subscription.login_rule.33',
        ],
        'input' => $wbwi_input,
        'try'   => 1,
        #'ip'    => '213.180.217.26',
    );

    is($rc->{login}, 'int.ch', 'mail login with dot');
    is($rc->{mail},  1,        'mail online');
    dmp($rc) if $dmp;
    done_testing();
};

subtest "BB UserInfo for light login lara.testx\@mail.ru" => sub {
    my $rc = MordaX::BlackBox::request(
        $req,
        'method'   => 'userinfo',
        'uid'      => '117690998',
        'bburl'    => $bburl,
        'dbfields' => [
            # 'accounts.login.uid',
            'subscription.login.2',    # needs for wadm (display authors email)
            'subscription.login_rule.33',
        ],
        'input' => $wbwi_input,
        'try'   => 1,
        #'ip'    => '213.180.217.26',
    );

    is($rc->{mail}, undef, 'NoMail');
    is($rc->{login}, 'lara.testx@mail.ru');
    dmp($rc) if $dmp;
    done_testing();
};

#  lara.testx@mail.ru // 111222
our $light_session = q{3:1493219740.5.0.1493219740631:pEjB515y9BkMBAAAuAYCKg:16.1|117690998.0.2.0:5|162726.457004.at4dYdlo8BtA133DtLl3trqwrs8};

subtest "MordaX::Auth check session" => sub {
    my ($req) = r();
    $req->{'_STATBOX_ID_SUFFIX_'} = 'test'; # HOME-37938
    my $auth = MordaX::Auth->new($req);
    my $rc   = $auth->check($req, {
        dont_use_tvm    => 1,
        sessionid       => $light_session,
    });
    dmp($rc, $auth->{INFO}) if $dmp;

    ok($rc->{uid});
    done_testing();
};

subtest "BB SessionInfo for light user login" => sub {
    local $TODO = 'Depricated via time dependent cookie value';
    my $rc = MordaX::BlackBox::request(
        $req,
        'method'    => 'sessionid',
        'sessionid' => $light_session,
        'from'     => 'morda',
        'ip'       => '::ffff:77.88.54.71',
        'host'     => 'yandex.ru',
        'bburl'    => $bburl,
        'dbfields' => [
            # 'accounts.login.uid',
            'subscription.login.2',
            'subscription.login_rule.33',
        ],
        'input' => $wbwi_input,
        'try'   => 1,
    );

    ok($rc->{uid});
    #is( $rc->{status}, 'VALID');
    dmp($rc) if $dmp;
    done_testing();
};

done_testing();

#print Data::Dumper::Dumper($rc);

