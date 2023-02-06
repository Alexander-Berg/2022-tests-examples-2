package Test::Smoo::Host;
use parent 'Test::Class';

use Test::Most;

use Smoo::Host;

sub canonize : Tests() {
    my %fixture = (
        "clop-2-wdevx.haze.yandex.net" => "clop-2-wdevx",
        "s1.wfront.yandex.ru"          => "s1.wfront",
        "pstatic-mng2.yandex.net"      => "pstatic-mng2",
        "m6.pxiva.yandex.net"          => "m6.pxiva",
        "scripter.haze.yandex.ru"      => "scripter",
        "v99.wdevx.yandex.net"         => "v99.wdevx",
    );

    while (my($in, $out) = each %fixture) {
        is Smoo::Host::canonize($in), $out, "check fqdn canonization";
    }
}

1;
