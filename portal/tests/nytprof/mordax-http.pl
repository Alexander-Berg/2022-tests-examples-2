#!/usr/bin/env perl

# mkdir -p ../../nytprof && echo 1 > ../../nytprof/1b
# perl -d:NYTProf ./mordax-http.pl
# nytprofhtml --out ../../nytprof/mordax-http

use lib::abs qw(../../lib);
use rules;

use MordaX::HTTP;
use MP::Logit;

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

for (0..100) {
    my $req_info = mordax_http_get('https://v8d11.wdevx.yandex.ru/nytprof/1b');
    say $req_info->{per};
    #dmp $req_info->{curl_metrics};
}
for (0..10) {
    my $req_info = mordax_http_get('https://v8d11.wdevx.yandex.ru/nytprof/1mb');
    #dmp $req_info->{curl_metrics};
    say $req_info->{per};
}

