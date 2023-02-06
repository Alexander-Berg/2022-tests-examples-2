#!/usr/bin/perl

use Test::More qw(no_plan);

use common;
use strict;
use warnings;

require WADM::Index;
use WBOX::Model::Widget;
use WBOX::Requester;
use WADM::Monitoring;
use WADM::History;
use WADM::Utils;
use POSIX;
use Digest::MD5 qw(md5_hex);

my $wi35 = WADM::Index::widget_by_wid(35);

ok($wi35);

$wi35->set_languages({});
is($wi35->lang(), '');

$wi35->parce_languages();
is(join('', keys %{$wi35->languages()}), '', "parsed undef leads to ''");
$wi35->parce_languages(";");
is(join('', keys %{$wi35->languages()}), '', "parsed  ';' leads to ''");
is($wi35->lang(), '', 'parced to null lang');

$wi35->set_languages({ru => 1});
is($wi35->lang(), 'ru');
ok($wi35->languages()->{ru}, 'RU Setted');
$wi35->set_languages({ru => 1, en => 1});
is($wi35->lang(), 'en;ru', "setted in alfabetical order");
ok($wi35->languages()->{ru}, 'RU Setted');
ok($wi35->languages()->{en}, 'EN Setted');
$wi35->set_languages({en => 1});
is($wi35->lang(), 'en');

save($wi35);

my $w2 = get(35);
is($w2->lang(), 'en');
ok($w2->languages()->{en}, 'EN Setted');
$w2->set_languages({ru => 1, uk => 1});
is($w2->lang(), 'ru;uk');
save($w2);

$w2 = get(35);

is($w2->lang(), 'ru;uk');
ok($w2->languages()->{uk}, 'UKraine Setted');

#new
my $w = WBOX::Model::Widget->new();
is($w->lang(), 'ru', 'default is russian language');
ok($w->languages()->{ru}, 'has russian language');

