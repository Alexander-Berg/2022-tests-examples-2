#!/usr/bin/perl
use strict; use warnings;
use feature qw/say/;
use LWP::UserAgent;
use JSON::XS;
use Data::Dumper;
use Test::Most;
use lib::abs;
#die_on_fail();

my $ua = new LWP::UserAgent;

require(lib::abs::path('../tools/instance'));
my $inst = instance();


my $page_android = $ua->get("http://www-$inst.wdevx.yandex.ru/portal/api/search/1/?app_platform=android")->content;
$page_android = JSON::XS->new->decode($page_android);

my $page_apad = $ua->get("http://www-$inst.wdevx.yandex.ru/portal/api/search/1/?app_platform=apad")->content;
$page_apad = JSON::XS->new->decode($page_apad);
{
    is $page_android->{'block'}->[1]->{data}->{list}->[0]->{url},
      'intent://213#Intent;S.browser_fallback_url=https%3A%2F%2Fpogoda.yandex.ru%2Fmoscow;package=ru.yandex.weatherplugin;end;';
    is $page_android->{'block'}->[1]->{data}->{list}->[4]->{url},
      '//yandex.ru/video/touch/';
    is $page_android->{'block'}->[1]->{data}->{list}->[5]->{url},
      'intent://#Intent;S.browser_fallback_url=http%3A%2F%2Fm.market.yandex.ru%2F;package=ru.yandex.market;end;';
    is $page_android->{'block'}->[1]->{data}->{more}->{list}->[3]->{url},
      'intent://#Intent;S.browser_fallback_url=https%3A%2F%2Fm.money.yandex.ru%2F;package=ru.yandex.money;end;';
    is $page_android->{'block'}->[1]->{data}->{more}->{list}->[8]->{url},
      'intent://#Intent;S.browser_fallback_url=https%3A%2F%2Fm.news.yandex.ru%2F;package=ru.yandex.news;end;';
    is $page_android->{'block'}->[1]->{data}->{more}->{list}->[12]->{url},
      'intent://#Intent;S.browser_fallback_url=https%3A%2F%2Fm.slovari.yandex.ru%2F;package=ru.yandex.translate;end;';
    is $page_android->{'block'}->[1]->{data}->{more}->{list}->[13]->{url},
      'intent://#Intent;S.browser_fallback_url=https%3A%2F%2Fm.taxi.yandex.ru;package=ru.yandex.taxi;end;';
    is $page_android->{'block'}->[1]->{data}->{more}->{list}->[14]->{url},
      "https://m.tv.yandex.ru/";
    is $page_android->{'block'}->[1]->{data}->{traffic}->{apps}->{maps}->{url},
      "https://maps.yandex.ru/moscow_traffic";
    is $page_android->{'block'}->[1]->{data}->{traffic}->{url},
      "https://maps.yandex.ru/moscow_traffic";
    is $page_android->{'block'}->[2]->{data}->{tab}->[0]->{url},
      "https://m.news.yandex.ru/index.html?appsearch_header=1";
    is $page_android->{'block'}->[2]->{data}->{tab}->[1]->{url},
      "https://m.news.yandex.ru/Moscow?appsearch_header=1";
    is $page_android->{'block'}->[2]->{data}->{url},
      "https://m.news.yandex.ru/?lang=ru&appsearch_header=1";
    is substr($page_android->{'block'}->[4]->{data}->{events}->[0]->{url}, 0, 26),
      "https://m.afisha.yandex.ru";
    is $page_android->{'block'}->[4]->{data}->{url},
      "https://m.afisha.yandex.ru/msk/";
    is $page_android->{'block'}->[5]->{data}->{list}->[0]->{url},
      "intent://#Intent;S.browser_fallback_url=https%3A%2F%2Ftaxi.yandex.ru%2F%3Ffrom%3Dmtaxi_geoblock_msk;package=ru.yandex.taxi;end;";
    is $page_android->{'block'}->[5]->{data}->{list}->[2]->{url},
      "//t.rasp.yandex.ru/stations/plane?city=213";
    is $page_android->{'block'}->[5]->{data}->{list}->[4]->{url},
      "intent://#Intent;S.browser_fallback_url=https%3A%2F%2Ft.rasp.yandex.ru%2Fsuburban-directions%3Fcity%3D213;package=ru.yandex.rasp;end;";
    is $page_android->{'block'}->[5]->{data}->{list}->[5]->{url},
      "//t.rasp.yandex.ru/stations/train?city=213";
    is substr($page_android->{'block'}->[7]->{data}->{tab}->[0]->{program}->[0]->{url}, 0, 26),
      "https://m.tv.yandex.ru/213";
    is $page_android->{'block'}->[7]->{data}->{tab}->[0]->{url},
      "https://m.tv.yandex.ru/213/";
    is $page_android->{'block'}->[7]->{data}->{tab}->[1]->{url},
      "https://m.tv.yandex.ru/213/channels/146";
    is $page_android->{'block'}->[7]->{data}->{url},
      "https://m.tv.yandex.ru/213/";
}

{
    is $page_apad->{'block'}->[1]->{data}->{list}->[0]->{url},
      'intent://213#Intent;S.browser_fallback_url=https%3A%2F%2Fpogoda.yandex.ru%2Fmoscow;package=ru.yandex.weatherplugin;end;';
    is $page_apad->{'block'}->[1]->{data}->{list}->[4]->{url},
      '//yandex.ru/video';
    is $page_apad->{'block'}->[1]->{data}->{list}->[5]->{url},
      'intent://#Intent;S.browser_fallback_url=https%3A%2F%2Fmarket.yandex.ru%2F%3Fclid%3D505;package=ru.yandex.market;end;';
    is $page_apad->{'block'}->[1]->{data}->{more}->{list}->[3]->{url},
      'intent://#Intent;S.browser_fallback_url=https%3A%2F%2Fmoney.yandex.ru%2F;package=ru.yandex.money;end;';
    is $page_apad->{'block'}->[1]->{data}->{more}->{list}->[8]->{url},
      'intent://#Intent;S.browser_fallback_url=https%3A%2F%2Fnews.yandex.ru%2F;package=ru.yandex.news;end;';
    is $page_apad->{'block'}->[1]->{data}->{more}->{list}->[12]->{url},
      'intent://#Intent;S.browser_fallback_url=https%3A%2F%2Fslovari.yandex.ru%2F;package=ru.yandex.translate;end;';
    is $page_apad->{'block'}->[1]->{data}->{more}->{list}->[13]->{url},
      'intent://#Intent;S.browser_fallback_url=https%3A%2F%2Ftaxi.yandex.ru;package=ru.yandex.taxi;end;';
    is $page_apad->{'block'}->[1]->{data}->{more}->{list}->[14]->{url},
      "https://tv.yandex.ru/";
    is $page_apad->{'block'}->[1]->{data}->{traffic}->{apps}->{maps}->{url},
      "https://maps.yandex.ru/moscow_traffic";
    is $page_apad->{'block'}->[1]->{data}->{traffic}->{url},
      "https://maps.yandex.ru/moscow_traffic";
    is $page_apad->{'block'}->[2]->{data}->{tab}->[0]->{url},
      "https://news.yandex.ru/index.html?appsearch_header=1";
    is $page_apad->{'block'}->[2]->{data}->{tab}->[1]->{url},
      "https://news.yandex.ru/Moscow?appsearch_header=1";
    is $page_apad->{'block'}->[2]->{data}->{url},
      "https://news.yandex.ru/?lang=ru&appsearch_header=1";
    is substr($page_apad->{'block'}->[4]->{data}->{events}->[0]->{url}, 0, 24),
      "https://afisha.yandex.ru";
    is $page_apad->{'block'}->[4]->{data}->{url},
      "https://afisha.yandex.ru/msk/";
#    is $page_apad->{'block'}->[5]->{data}->{list}->[0]->{url},
#        "intent://#Intent;S.browser_fallback_url=https%3A%2F%2Ftaxi.yandex.ru%2F%3Ffrom%3Dmtaxi_geoblock_msk;package=ru.yandex.taxi;end;";
#    is $page_apad->{'block'}->[5]->{data}->{list}->[2]->{url},
#        "//rasp.yandex.ru/stations/plane?city=213";
#    is $page_apad->{'block'}->[5]->{data}->{list}->[4]->{url},
#        "intent://#Intent;S.browser_fallback_url=https%3A%2F%2Frasp.yandex.ru%2Fsuburban-directions%3Fcity%3D213;package=ru.yandex.rasp;end;";
#    is $page_apad->{'block'}->[5]->{data}->{list}->[5]->{url},
#        "//rasp.yandex.ru/stations/train?city=213";
    is substr($page_apad->{'block'}->[7]->{data}->{tab}->[0]->{program}->[0]->{url}, 0, 24),
      "https://tv.yandex.ru/213";
    is $page_apad->{'block'}->[7]->{data}->{tab}->[0]->{url},
      "https://tv.yandex.ru/213/";
    is $page_apad->{'block'}->[7]->{data}->{tab}->[1]->{url},
      "https://tv.yandex.ru/213/channels/146";
    is $page_apad->{'block'}->[7]->{data}->{url},
      "https://tv.yandex.ru/213/";
}

done_testing;
