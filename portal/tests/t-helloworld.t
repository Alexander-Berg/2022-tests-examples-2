#!/usr/bin/env perl
use common::sense;
use Test::Most 'no_plan';
# die_on_fail();
use Data::Dumper;
 
use lib::abs qw(../lib . testlib);
use IO::Scalar;
use JSON::XS qw/decode_json/;

use testlib::TestRequest;
#use InitMorda;
use HelloWorld;

#при запросе с yandex.com.tr на домен yandex.ru handleYandexuid
# должен возвращать куки yandexuid
subtest 'handleYandexuid' => sub {
    do {
        my $req = testlib::TestRequest::r();
        $req->{'HTTPReferer'} = 'http://yandex.com.tr';
        tie *STDOUT, 'IO::Scalar', \my $stdout;
        my $res = HelloWorld::handleYandexuid($req);
        untie *STDOUT;
        
        ok($res, 'true return value');
        like($stdout, qr{^Content-Type: application/json; charset=UTF-8}m, 'Content-Type: application/json; charset=UTF-8');
        
        my ($body) = $stdout =~ /.*?(?:\n\n|\r\n\r\n)(.*)/s;
        my $body_decoded = eval {
            decode_json($body);
        };
        $@ ? fail("decode body: $body") : pass('decode body');
        $body_decoded->{'yandexuid'} ? pass('has yandexuid') : fail('no yandexuid');
        like($body_decoded->{'yandexuid'}, qr/^[1-9][0-9]{6,8}[0-9]{10}$/, 'correct yandexuid format');
    };
};

subtest 'handleYCookieSetter gif' => sub {
    #установить yu cookie через gif. копирование yandexuid с yandex.ru в yp->yu на .com.tr
    do {
        my $yandexuid = '12345671234567890';
        my $req = testlib::TestRequest::r('get' => {
            'gif' => 1,
            'yu' => $yandexuid,
        });

        tie *STDOUT, 'IO::Scalar', \my $stdout;
        my $res = HelloWorld::handleYCookieSetter($req);
        untie *STDOUT;

        ok($res, 'true return value');

        like($stdout, qr{^Content-Type: image/gif}m, 'Content-Type: image/gif');

        check_common_cookies($stdout, $yandexuid);
    };
};

subtest 'handleYCookieSetter js' => sub {
    #установить cookie через js
    do {
        my $yandexuid = '12345671234567890';
        my $req = testlib::TestRequest::r('get' => {
            'js' => 1,
            'yu' => $yandexuid,
        });

        tie *STDOUT, 'IO::Scalar', \my $stdout;
        my $res = HelloWorld::handleYCookieSetter($req);
        untie *STDOUT;
        
        ok($res, 'true return value');
        
        like($stdout, qr{^Content-Type: text/javascript;}m, 'Content-Type: text/javascript');

        check_common_cookies($stdout, $yandexuid);
    };    
};

sub check_common_cookies {
    my ($stdout, $yandexuid) = @_;

    do {
        my $num = () = $stdout =~ m|^Set-Cookie: yp=\d{10}\.yu\.$yandexuid; Expires=[^;]+; Domain=\.yandex\.ru; Path=/|mg;
        is($num, 1, 'Set yp .yandex.ru once');
    };

    do {
        my $num = () = $stdout =~ m|^Set-Cookie: yp=; Expires=[^;]+; Path=/|mg;
        is($num, 1, 'Set yp no domain once');
    };
    
    do {
        my $num = () = $stdout =~ m|^Set-Cookie: yp=; Expires=[^;]+; Domain=\.www\.yandex\.ru; Path=/|mg;
        is($num, 1, 'Set yp .www.yandex.ru once');
    };    

    #Set-Cookie: yandexuid должна быть 1 раз
    do {
        my $num = () = $stdout =~ m|^Set-Cookie: yandexuid=[1-9]\d{6,8}\d{10}; Expires=[^;]+; Domain=\.yandex\.ru; Path=/|gm;
        is($num, 1, 'Set yandexuid .yandex.ru once');
    };
    
}

#ErrorLog::logsubreqtimes хочет записать subreqtimes. не надо ему этого тут
no warnings 'redefine';
package Pfile;
sub PWrite {};
