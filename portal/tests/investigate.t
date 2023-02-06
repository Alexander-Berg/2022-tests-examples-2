#!/usr/bin/perl

use common::sense;
use Test::More;
use lib::abs qw(../lib ../t/testlib .);

use MordaTest;
use testlib::TestRequest qw();
use MordaX::Logit qw(dmp logit);

use MordaX::Input;
use_ok('MordaX::InputWatch');
use_ok('Rapid::ReqWatch');
diag("Summon! Summon! Summon! Investigate!!!");

my $headers = [
    {'User-Agent' => 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1)',},
    {'User-Agent' => 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)'},
    {'User-Agent' => 'Opera/9.80 (Windows NT 6.1; WOW64) Presto/2.12.388 Version/12.17'},
    {'User-Agent' => 'Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0; SAMSUNG; GT-S7530)'},
    {'User-Agent' => 'Mozilla/5.0 (compatible; MSIE 10.0; Windows Phone 8.0; Trident/6.0; IEMobile/10.0; ARM; Touch; NOKIA; Lumia 920)'},
    {'User-Agent' => 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.74 YaBrowser/15.4.2272.2343 Safari/537.36'},
    {'User-Agent' => 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:39.0) Gecko/20100101 Firefox/39.0'},
];
my $cookies = [
    {'yandex_gid' => '2'},
    {'yandex_gid' => '977'},
    {'yandexuid'  => '1000058641418478371', Session_id => 'noauth'},
    {'yandexuid'  => '1000058641418478370'},
    {'yp'         => '1418478371.ygo.1'},
    {'my'         => 'YywBATYBAQA='},
    {'my'         => 'YywBADYBAQA='},
    {'S'          => '12532'},
    {'S'          => '12532-233'},
    {'S'          => '12532.233'},
];
my $urls = [
    'www.yandex.com.tr',
    "www.yandex.com.tr/bjk",
    'www.yandex.ua',
    'www.yandex.by',
    'ru.start3.mozilla.com',
];
my $gets = [
    {'time' => '120000', date => '20140214'},
    {ip => '122.34.11.34'},
    {dumpvars        => 1,},
    {ncrnd           => 32423},
    {ncrnd           => 'am'},
    {LocalDayTimeDev => 17},
    {q               => ''},
    {q               => 'exmple'},
    {clid            => 12,},
    {clid            => "221313-233", clidrp => 'ru'},
    {clid            => 1232121, win => 23},
    {clid            => 1983172},                        #tizenSpecial
    {clidrp          => 'ua'},
    {edit            => 1,},
    {lang            => 'uk'},
    {save_lang       => 'ru'},
    {q               => ''},
];

my $skip = {
    map { $_ => 1 } qw/hello_world beta_host rapid intercept404 ipv6promo ClidSaved api_search no_device_detect/
};

my $todo = {
    map { $_ => 1 } qw/use_lang_for_chooser WP7Special Widgets Language_lc Locale comtr_old/
};
my $temp_todo = {
    map { $_ => 1431894696 } qw/Locale/,
};

diag("Generate Load");
for my $head (@$headers) {
    my $r = testlib::TestRequest->fast_cgi_r('headers' => $head);
    my $input = MordaX::Input->new(r => $r, watch => 'MordaX::InputWatch');
}
for my $cookie (@$cookies) {
    my $r = testlib::TestRequest->fast_cgi_r('cookies' => $cookie);
    my $input = MordaX::Input->new(r => $r, watch => 'MordaX::InputWatch');
}
for my $url (@$urls) {
    my $r = testlib::TestRequest->fast_cgi_r('url' => $url);
    my $input = MordaX::Input->new(r => $r, watch => 'MordaX::InputWatch');
}
for my $get (@$gets) {
    my $cookies = {yandexuid => '1000058641418478370'};
    my $mreq = MordaX::Req->new(req => $cookies);
    #$get->{sk} = MordaX::Token->new( $mreq )->generate( );
    my $r = testlib::TestRequest->fast_cgi_r('get' => $get, cookies => $cookies);
    my $input = MordaX::Input->new(r => $r, watch => 'MordaX::InputWatch');
}

my $vars = MordaX::InputWatch::calllog()->{'REQ'};
for my $name (keys %$vars) {
    next if $skip->{$name};
    my $from = {};
    for my $op (qw/set get/) {
        my $early;
        for my $point (keys %{$vars->{$name}->{$op}}) {
            my ($pack, $line) = split(/--/, $point);
            next if !$line;
            next if $line !~ /^\d+$/;
            $early //= $line;
            $early = $line if $line < $early;
        }
        $from->{$op} = $early;
    }
    if ($name eq 'yandexuid') {
        ok($from->{set}, "yandexuid set point");
        ok($from->{get}, "yandexuid get point");
    }

    #dmp( $from ) if $name eq 'isMSIE';
    if ($from->{get} and
        (!$from->{set}
            or ($from->{get} < $from->{set}))
      ) {
        local $TODO;
        $TODO = "$name need investigation" if ($todo->{$name});
        if ($temp_todo->{$name} and $temp_todo->{$name} > time()) {
            $TODO = "$name waits for " . localtime($temp_todo->{$name});
        }

        fail('input req: ' . $name);
        #dmp( $from );

        diag("$name: setted on line: " . $from->{set});
        diag("$name: getted on line: " . $from->{get});
    }
}

#ok( $req );
#dmp( $vars->{isMSIE} );
#dmp( $vars->{Locale} );
#dmp($r);

done_testing();
