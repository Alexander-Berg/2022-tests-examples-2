#!/usr/bin/perl
use common::sense;

use lib::abs qw{../lib};
use Test::More;

use MordaX::Utils;

my @good = qw{
  ://

  http://ya.ru
  https://ya.ru
  http://www.ya.ru
  https://www.ya.ru
  http://ololo.www.ya.ru
  https://ololo.www.ya.ru

  http://www.yandex.ru
  https://www.yandex.ru
  http://yandex.ru
  https://yandex.ru
  http://qwe.qwe.yandex.ru
  https://qwe.qwe.yandex.ru

  http://www.yandex.ua
  https://www.yandex.ua
  http://yandex.ua
  https://yandex.ua
  http://qwe.qwe.yandex.ua
  https://qwe.qwe.yandex.ua

  http://www.yandex.by
  https://www.yandex.by
  http://yandex.by
  https://yandex.by
  http://qwe.qwe.yandex.by
  https://qwe.qwe.yandex.by

  http://www.yandex.kz
  https://www.yandex.kz
  http://yandex.kz
  https://yandex.kz
  http://qwe.qwe.yandex.kz
  https://qwe.qwe.yandex.kz

  http://www.yandex.com
  https://www.yandex.com
  http://yandex.com
  https://yandex.com
  http://qwe.qwe.yandex.com
  https://qwe.qwe.yandex.com

  http://www.yandex.com.tr
  https://www.yandex.com.tr
  http://yandex.com.tr
  https://yandex.com.tr
  http://qwe.qwe.yandex.com.tr
  https://qwe.qwe.yandex.com.tr

  https://home-blinovskov.soft.msup.dev.yandex.ua
};

my @bad = qw{
  http://wwwyandex.net
  https://wwwyandex.net
  http://wwwyandex.ru
  https://wwwyandex.ru
  http://wwwyandex.ua
  https://wwwyandex.ua
  http://wwwyandex.by
  https://wwwyandex.by
  http://wwwyandex.kz
  https://wwwyandex.kz
  http://wwwyandex.com
  https://wwwyandex.com
  http://wwwyandex.com.tr
  https://wwwyandex.com.tr
  http://www.yandex.qwe.com
  https://www.yandex.qwe.com
  http://www.yandex.zzz.com
  https://www.yandex.ru.com
  http://foooo.bar
  https://foooo.bar
};
push @bad, '';
push @bad, undef;

for my $origin (@good) {
    ok MordaX::Utils::is_yandex_origin($origin), "[$origin] yandex";
}
for my $origin (@bad) {
    ok !MordaX::Utils::is_yandex_origin($origin), "[$origin] not yandex";
}
done_testing();

1;
