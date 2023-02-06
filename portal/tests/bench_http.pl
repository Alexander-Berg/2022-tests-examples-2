#!/usr/bin/perl

use lib::abs qw(../lib ../scripts);
use rules;
use Benchmark;
use MordaX::HTTP;
use http_tiny;

my $debug = 0;

sub mordax_http_get ($;$) {
    my ($url, $change) = @_;
    my $http = MordaX::HTTP->new({});
    $http->{$_} = $change->{$_} for keys %$change;
    $http->add(
        alias   => 'test',
        url     => $url,
        timeout => 1,
        slow    => 1,
        can_v6  => 1,
    );
    return $http->result_req_info('test');
}

for my $url (
    #'http://morda-mocks.wdevx.yandex.ru/api/v1/mocks/list?ids=5ce3c056dcbace8ca55fc629',
    'https://ya.ru',
    #'http://v8d6.wdevx.yandex.ru/portal/stories_report',
    #'https://mirror.yandex.ru/ubuntu/dists/bionic/main/binary-amd64/Packages.xz',
    'https://v8d11.wdevx.yandex.ru/nytprof/1mb', # 1mb file
    'https://v8d11.wdevx.yandex.ru/nytprof/1b', # echo 1 > nytprof/1b
  )
{
    warn $url;
    Benchmark::cmpthese(
        10, {
            'MordaX::HTTP default' => sub {
                my $req_info = mordax_http_get($url);
                warn join ' ', $req_info->{success}, length $req_info->{response_content} if $debug;
            },

            # lib/MordaX/HTTP.pm: my $usleep = $self->{usleep}
            #(
            #    map {
            #        my $t = $_;
            #        "MordaX::HTTP $t" => sub {
            #            my $req_info = mordax_http_get($url, {usleep => $t});
            #            warn join ' ', $req_info->{success}, length $req_info->{response_content} if $debug;
            #          }
            #    } qw(00001 00050 00100 00500 01000 01500 02000 03000 04000 06000 10000 20000 40000)
            #),

            #(
            #    map {
            #        my $t = $_;
            #        "MordaX::HTTP buf $t" => sub {
            #            my $req_info = mordax_http_get($url, {buffersize => $t});
            #            warn join ' ', $req_info->{success}, length $req_info->{response_content} if $debug;
            #          }
            #    } qw(16000 100000 500000)
            #),

            (
                map {
                    my $t = $_;
                 map {
                    my $buf = $_;
                    "MordaX::HTTP b=$buf t=$t" => sub {
                        my $req_info = mordax_http_get($url, {buffersize => $buf, poke_usleep => $t});
                        warn join ' ', $req_info->{success}, length $req_info->{response_content} if $debug;
                      }
                 } qw(001000 016000 050000 100000 200000 300000 400000 500000)
                } qw(00001 00050 00100 00500 01000 01500 02000 03000 04000 06000 10000 20000 40000)
            ),

            'http_tiny' => sub {
                my $o = http_tiny::http_get($url)->{content};
                warn length $o if $debug;
            },
            'wget' => sub {
                my $o = `wget -q --output-document=- '$url'`;
                warn length $o if $debug;
            },
            'curl' => sub {
                my $o = `curl --silent '$url'`;
                warn length $o if $debug;
            },
        },
        'all'
    );
}
