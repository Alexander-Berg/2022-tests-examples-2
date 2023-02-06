use strict; use warnings;
no strict 'refs';
use Data::Dumper;
use lib::abs qw(../lib);
use DNS;
use Benchmark;
$\ = "\n";
$, = ' ';
my $names = [qw/
      ymback-export.yandex.net
      any.yandex.ru
      e1-rs1.wboxdb.yandex.net
      blackbox.yandex.net
      yabs.yandex.com.tr
      u1-ri1.wboxdb.yandex.net
      mail.yandex.kz
      u1-rs1.widb.yandex.net
      u1-rn1.widb.yandex.net
      suggest-internal.yandex.ru
      /];
my $timeout = 0.05;
my $retries = 2;
my $iter    = 100;
*{"DNS::logit"} = sub { print @_ };

my $start = Benchmark->new();
for (0 .. $iter) {
    print $_ unless $_ % 100;
    for my $name (@$names) {
        my $addr_hr = DNS::_resolve($name, $timeout, $retries);
    }
}
my $end = Benchmark->new();
my $diffs = timediff($end, $start);
print timestr($diffs);

