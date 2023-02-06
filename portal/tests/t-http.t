#!/usr/bin/perl

use common::sense;
use Test::More;
use lib::abs qw(../lib);
use MordaX::Logit qw(logit dumpit dmp);

use_ok('MordaX::HTTP');
use_ok('Starman');
use_ok('MordaX::Req');
use_ok("Rapid::Req");

# starting plackup!
my $port = 59922 + int(rand(100));

my $starman_pid = start_http_server($port, 'timeout.psgi');
ok($starman_pid, "server started");

unless ($starman_pid) {
    diag("no http server");
    exit(100),
}
for (my $i = 0; $i < 5; $i++) {
    unless (self_test_http_server($port)) {
        sleep 1;
    }
}
ok(self_test_http_server($port), "Starman ansvered");

subtest "Req->http" => sub {
    my $R1 = MordaX::Req->new();
    ok(MordaX::HTTP->new($R1));
    ok($R1->http());
    is($R1->http(), $R1->http());
    done_testing();
};
subtest "Rapid::Req->http" => sub {
    my $R1 = Rapid::Req->new();
    ok($R1->http());
    ok(MordaX::HTTP->new($R1));
    is($R1->http(), $R1->http());
    done_testing();
};

eval {
    #eval needed to kill started server!

    my $simple_req = MordaX::Req->new();
    my $http       = MordaX::HTTP->new($simple_req);

    ok($http, "HTTP created http://localhost:$port/");
    subtest "post" => sub {
        $http->add(
            alias     => 'post_form',
            url       => "http://localhost:$port/post",
            post      => 1,
            post_data => {
                param => "Я"
            },
        );
        my $content = $http->result("post_form");
        is($content, 'param=%D0%AF');
        $http->add(
            alias     => 'post_content',
            url       => "http://localhost:$port/post",
            post      => 1,
            post_data => "megacontent=xxx[%12]",          #in bytes
        );
        my $c = $http->result("post_content");
        is($c, "megacontent=xxx[%12]");

        done_testing();
    };

    subtest "put" => sub {
        $http->add(
            alias    => 'put_content',
            url      => "http://localhost:$port/post",
            put      => 1,
            put_data => "megacontent=xxx[%12]",          #in bytes
        );
        my $c = $http->result("put_content");
        is($c, "megacontent=xxx[%12]");
        done_testing();
    };

    subtest "header" => sub {
        $http->add(
            alias   => 'header',
            url     => "http://localhost:$port/header/my",
            headers => ["MY: Header"],
        );
        my $c = $http->result("header");
        #dmp( $c );
        is($c, "Header");
        done_testing();

    };
    return;

    subtest "SIMPLE GET" => sub {
        $http->add(
            'alias' => 'simple_get',
            'url'   => "http://localhost:$port/",
            timeout => 2,
        );
        my $data = $http->result('simple_get');
        like($data, qr/ok/, 'data recieved');
        done_testing();
    };

    subtest "OLDStyle GET, witch timeouted" => sub {
        $http->add(
            'alias' => 'simple_timeout',
            'url'   => "http://localhost:$port/200",
            timeout => 0.15,
            retries => 2,
        );
        my $data = $http->result('simple_timeout');
        is($data, undef, "data not receaved");
        done_testing();
    };
    subtest "Progressive GET with some timeouts" => sub {
        $http->add(
            'alias'       => 'progressive_get',
            'url'         => "http://localhost:$port/200",
            'progressive' => 1,
            'timeout'     => 0.08,
            'retries'     => 3,
        );
        my $data = $http->result('progressive_get');
        like($data, qr/ok/, "Response Getted!! Hurra!");

        done_testing();
    };

    subtest "3concurent Requests" => sub {
        $http->add(
            alias   => 'c3_1',
            url     => "http://localhost:$port/100",
            timeout => 0.35,
        );
        $http->add(
            alias       => 'c3_2',
            progressive => 1,
            url         => "http://localhost:$port/200",
            timeout     => 0.13,
            retries     => 1,
        );
        $http->add(
            alias       => 'c3_3',
            progressive => 1,
            url         => "http://localhost:$port/350",
            timeout     => 0.11,
            retries     => 1,
        );
        diag('reqs lanunched');

        #wait 100ms
        my $data1 = $http->result('c3_1');
        like($data1, qr/ok/, "Response in 100ms");
        diag('hacking c3_2');
        ok(!$http->{aliases}->{c3_1});
        ok($http->{aliases}->{c3_2}, 'alias ok');
        ok($http->{aliases}->{c3_3}, 'alias ok');

        is($http->{inprogress}, 2, 'requests in progress');

        my $c3_2_req_info = $http->{aliases}->{c3_2};
        $c3_2_req_info->{urlobj}->path("5");

        my $data2 = $http->result('c3_2');
        is($data2, 'ok msleep 5');

        is($http->{inprogress}, 2, 'requests in progress');

        my $data3 = $http->result('c3_3');
        is($data3, undef, 'third request failed');
        done_testing();
    };

    subtest "X-Yandex-Retry" => sub {

        $http->add(
            alias   => 'r_0',
            url     => "http://localhost:$port/100/rETRy/1",
            timeout => 0.3,
        );
        is($http->result('r_0'), 'ok msleep 100', 'msleep - ok');

        $http->add(
            alias   => 'r_1',
            url     => "http://localhost:$port/100/retry/1",
            timeout => 0.3,
        );
        is($http->result('r_1'), 'Retry: none', 'No Retry');
        $http->add(
            alias   => 'r_2',
            url     => "http://localhost:$port/100/retry/1",
            timeout => 0.15,
            retries => 1,
        );
        is($http->result('r_2'), 'Retry: 1', 'Retry: 1');
        sleep 2;
        $http->add(
            alias   => 'r_3',
            url     => "http://localhost:$port/10/retry/3",
            timeout => 0.08,
            retries => 4,

            progressive => 0,
        );

        is($http->result('r_3'), 'Retry: 3', 'Retry: 3');
        done_testing();
    };
    subtest "empty content on now 200 error" => sub {
        $http->add(
            alias   => '500error',
            url     => "http://localhost:$port/500/status",
            timeout => 1,
        );

        my $ri = $http->result_req_info('500error');
        ok($ri);
        #dmp( $ri );
        is($ri->{response_content}, undef, 'No content on non 200 status code');
        ok($ri->{error_text}, 'Has error');
        like($ri->{error_text}, qr/500/, 'status in error');
        is($ri->{status_code}, 500);

        $http->add(
            alias   => '505error',
            url     => "http://localhost:$port/505/status",
            timeout => 1,
        );
        $ri = $http->result_req_info('505error');
        ok($ri);
        #dmp( $ri );
        is($ri->{response_content}, undef, 'No content on non 200 status code');
        ok($ri->{error_text}, 'Has error');
        like($ri->{error_text}, qr/505/, 'status in error');
        is($ri->{status_code}, 505);

        $http->add(
            alias   => '200nonError',
            url     => "http://localhost:$port/100",
            timeout => 1,
        );
        $ri = $http->result_req_info('200nonError');

        is($ri->{status_code}, 200, 'stauts code for successfull');
        ok($ri->{response_content}, 'content on 200 status code');
        #dmp( $ri );
        done_testing();
    };

};
if ($@) {
    fail('eval failed: ' . $@);
}

#diag("sleeping");
#sleep 10;

stop_http_server($starman_pid);
done_testing();
exit(0);

sub start_http_server {
    my ($port, $psgi) = @_;
    my $timeout_psgi = lib::abs::path($psgi);
    ok(-f $timeout_psgi, "Psgi ok:" . $timeout_psgi);
    open(our $server_fh, '-|', "starman -p $port --workers 5 $timeout_psgi 2>&1");
    #diag('!starman! started');
    #diag('warning this test can be kill only by contl C');
    my $starman_pid;
    while (<$server_fh>) {
        if (/pid\((\d+)\)/) {
            $starman_pid = $1;
            last;
        }
        diag($_);
    }
    return $starman_pid;
}

sub stop_http_server {
    my $pid = shift;
    our $server_fh;
    system "kill $pid";
    close($server_fh);
    system "kill $pid";
    wait;
}

sub self_test_http_server {
    my $post = shift;
    use LWP;
    use LWP::UserAgent;
    my $ua = LWP::UserAgent->new();

    my $resp = $ua->get("http://localhost:$port/");
    return $resp->is_success() ? 1 : 0;
}
