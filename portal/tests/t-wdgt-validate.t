#!/usr/bin/perl

use common::sense;
use Test::More;
use lib::abs qw( . ../lib );

use_ok('WDGT::Validate');

my $v = WDGT::Validate->new();

diag("Data::Validate::URI version:", $Data::Validate::URI::VERSION);
diag("Net::Domain::TLD version:, ",  $Net::Domain::TLD::VERSION);

subtest "SRC URL" => sub {

    ok($v->is_http_uri("http://www.yandex.ru"), "yandex.ok");

    ok($v->is_http_uri("https://www.yandex.ru"), "https yandex.ok");
    ok(!$v->is_http_uri("http://www.yandex"),    "yandex domain");

    ok($v->is_http_uri("http://президент.рф"), "cyrrylyc domain");

    ok($v->is_http_uri("http://xn--d1abbgf6aiiy.xn--p1ai/"), "punny domain");
    done_testing();
};

done_testing();
