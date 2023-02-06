# 1471520455.log - это лог из грепки
#cat 1471520455.log | perl -p -e '$_ =~ s/^.*request=([^\t]+).*user_agent=([^\t]+).*/$1 $2/' > /tmp/api_ua.txt

use lib::abs qw( . ../lib );
use MP::Logit qw(logit dmp);
use rules;
use LWP::UserAgent;
use MP::Utils;
use Test::Most;
die_on_fail();

my $file = '/tmp/api_ua.txt';

my $ua = LWP::UserAgent->new();
my $host_prod = 'http://yandex.ru';
my $host_dev = 'http://www-v21d4.wdevx.yandex.ru';
my $host_dev_et = 'http://www-v21d3.wdevx.yandex.ru';

open my $F, '<', '/tmp/api_ua.txt';
while (<$F>) {
    chomp $_;
    my ($url, $usag) = split(" ", $_, 2);
    $url = '/portal/api/search/1/application?geo_by_settings=155';

    note 'prod ',$host_prod.$url;
    my $res_prod = MP::Utils::parse_json($ua->get($host_prod.$url)->decoded_content);

    note 'dev ', $host_dev.$url, ' ',$usag;
    my $request = HTTP::Request->new();
    $request->method('GET');
    $request->uri($host_dev.$url);
    $request->header('User-Agent' => $usag);
    my $res_dev = MP::Utils::parse_json($ua->request($request)->decoded_content);

    note 'et ', $host_dev_et.$url;
    my $res_dev_et = MP::Utils::parse_json($ua->get($host_dev_et.$url)->decoded_content);

    note 'dev_noh ', $host_dev.$url;
    my $res_dev_nohe = MP::Utils::parse_json($ua->get($host_dev.$url)->decoded_content);
    compare($res_prod, $res_dev, $res_dev_et, $res_dev_nohe);

}

sub compare {
    my ($p, $d, $e, $n) = @_;
    is_deeply [sort keys %$p], [sort keys %$d], 'p d OK';
    is_deeply [sort keys %$d], [sort keys %$e], 'd e OK';
    is_deeply [sort keys %$e], [sort keys %$n], 'e n OK';
}
done_testing();
