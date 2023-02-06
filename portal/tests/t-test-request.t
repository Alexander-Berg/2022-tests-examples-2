#!/usr/bin/perl

use common::sense;
use Test::More;
use lib::abs qw(../lib ../t/testlib .);

use MordaTest;
use testlib::TestRequest qw();
use MordaX::Logit qw(dmp logit);
use MordaX::Input;
use Storable qw(dclone);

sub req {
    my $req = testlib::TestRequest->request(@_);
    return $req,
}
subtest 'Headers' => sub {
    my $req = req('headers' => {
            'User-Agent'    => 'xcom',
            'Custom-Header' => 'y',
    });
    is($req->{UserAgent}, 'xcom');
    ok($req->{UserHeaders});
    #dmp($req->{UserHeaders} );
    is($req->{UserHeaders}->{'CUSTOM-HEADER'}, 'y');
};

subtest "Cookies" => sub {
    my $req = req('cookies' => {
            yandexuid  => '1234567891234567890',
            yandex_gid => 1,
    });

    ok($req->cookies());
    is($req->cookies()->{yandex_gid}, 1);
    is($req->{yandexuid},             '1234567891234567890');
    is($req->{yandexuid_generated}, undef, 'non generated');

    my $r = testlib::TestRequest::r(
        cookies => {
            yp         => time + 1000 . ".sometime.1",
            yandex_gid => 216,
        },
    );
    ok($r);
    ok($r->ycookies());
    ok($r->ycookies()->value('sometime'));

};

subtest "URL" => sub {
    my $req = req(url => "/hello");
    is($req->{Uri},      "/hello");
    is($req->{HostName}, 'www.yandex.ru');
    is($req->{https},    undef);

    $req = req(url => "https://www.yandex.com");
    is($req->{HostName}, 'www.yandex.com');
    is($req->{https},    1);

    $req = req(url => 'http://yandex.ru/xcom/xcom2');
    is($req->{HostName},      'yandex.ru');
    is($req->{Uri},           "/xcom/xcom2");
    is($req->{UriChain}->[0], 'xcom');
    is($req->{UriChain}->[1], 'xcom2');

    $req = req(url => 'https://yandex.com.tr/?edit=1');
    is($req->{HostName},            'yandex.com.tr');
    is($req->{Getargshash}->{edit}, 1);
    #is( $req->{EditMode} , 1 );

    $req = req(url => 'yandex.com.tr/bjk');
    is($req->{HostName},     'yandex.com.tr');
    is($req->{MordaZone},    'com.tr');
    is($req->{MordaContent}, 'comtr');       #not requester problems
    is($req->{Uri},          '/bjk');

    $req = req(url => 'www.yandex.com.tr/bjk');
    is($req->{HostName},      'www.yandex.com.tr');
    is($req->{MordaZone},     'com.tr');
    is($req->{MordaContent},  'comtr');           #not requester problems
    is($req->{Uri},           '/bjk');
    is($req->{'UriChain'}[0], 'bjk');

    $req = req(url => 'ru.start3.mozilla.com');
    is($req->{HostName},       'ru.start3.mozilla.com');
    is($req->{foreign_domain}, 1);
    is($req->{MordaContent},   'firefox');

};
subtest "host" => sub {
    my $host = 'a.xom';
    my $r = testlib::TestRequest->fast_cgi_r(host => $host, url => '/');
    is($r->hostname(), 'a.xom');

    my $req = req(host => 'beta.com', url => '/bjk');

};

done_testing();

