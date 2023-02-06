#!/usr/bin/env perl
use Test::Most;
use Time::localtime;

use lib::abs qw(../scripts/);
use http_tiny;

subtest 'send yasm signal that perl_tests is running' => sub {
    # на выходные делаем ttl побольше, т.к. никто не делает пуллреквест
    my $ttl = 86400 * (localtime->wday() == 5 ? 3 : 1.5);
    my $request = [{
        name => 'morda_perl_tests_is_alive_tttt',
        tags => {itype => 'mordatests'},
        val => 1,
        ttl => $ttl,
    }];

    my $response = http_tiny::http_post_json('http://portal-yasm.wdevx.yandex.ru:11005', $request, {timeout => 1});
    ok($response->{success});
};

done_testing();
