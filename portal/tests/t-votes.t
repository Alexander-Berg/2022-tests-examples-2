#!/usr/bin/perl

use utf8;
use common::sense;
use lib::abs(qw{../lib ../scripts .});

use Test::More;
use MordaX::Logit qw(dmp logit);
use Encode;
use 5.010;

diag('Test broken');
plan skip_all => 'Test broken';
exit 0;

#use InitBase;
#use Geo;
require 'votes.pl';

ok($Geo::geobase, "Geobase inited");
ok(geo(213, 'name'), "Moscow has name");
ok((geo(213, 'parents'))[0], "Moscow has non zerro parents");

is(search_for_cik_urls(), undef);

subtest "UrlParse PRE" => sub {
    #! load data
    my $file = lib::abs::path("./data/votes_link_list-1.html");
    open(my $H, $file) || die "link list '$file' not loaded";
    my $data = join('', (<$H>));
    ok($data, "Data loaded: $file");

    my $cp1251 = $data;

    my $utf8 = $data; Encode::from_to($utf8, 'cp1251', 'utf8');

    my $urlsA = search_for_cik_urls($cp1251);
    ok($urlsA,              "HASH");
    ok($urlsA->{preshort},  "preShort ok");
    ok($urlsA->{predetail}, "preDetail ok");

    my $urlsB = search_for_cik_urls($utf8);

    ok($urlsB,              "HASH");
    ok($urlsB->{preshort},  "preShort ok");
    ok($urlsB->{predetail}, "preDetail ok");

    done_testing();
};
subtest "UrlParse LAST" => sub {
    #! load data
    my $file = lib::abs::path("./data/votes_link_list-2.html");
    open(my $H, $file) || die "link list '$file' not loaded";
    my $data = join('', (<$H>));
    ok($data, "Data loaded: $file");

    my $cp1251 = $data;

    my $utf8 = $data; Encode::from_to($utf8, 'cp1251', 'utf8');

    my $urlsA = search_for_cik_urls($cp1251);
    ok($urlsA,               "HASH");
    ok($urlsA->{lastshort},  "lastShort ok");
    ok($urlsA->{lastdetail}, "lastDetail ok");

    my $urlsB = search_for_cik_urls($utf8);

    ok($urlsB,               "HASH");
    ok($urlsB->{lastshort},  "lastShort ok");
    ok($urlsB->{lastdetail}, "lastDetail ok");

    done_testing();
};

subtest 'Votes Parce HTML' => sub {
    my $file = lib::abs::path("./data/votes_moscow2003.html");
    open(my $H, $file) || die "link list '$file' not loaded";
    my $data = join('', (<$H>));
    close($H);
    ok($data, "Data loaded: $file");
    #------------------------------------
    my $res = parse_cik_html(
        {id => 'moscow2003',
            geos       => '213',
            candidates => [
                {id => 'plain',    name => "Лужков М А", search => "Лужков"},
                {id => 'lif',      name => "Лифанов",     search => "лифанов"},
                {id => 'sterliad', name => "Стерлигов", search => "Стерлиго"},
                {id => 'swan',     name => "Лебедев",     search => "Лебедев"},
              ]},
        $data
    );

    #dmp( $res );
    ok($res->{ts},         "Timestamp");
    ok($res->{candidates}, "Candidates Yes");
    ok($res->{ok},         "Self test ok");

};

subtest 'Votes Parce Amur' => sub {
    my $file = lib::abs::path("./data/votes_amur.html");
    open(my $H, $file) || die "link list '$file' not loaded";
    my $data = join('', (<$H>));
    close($H);
    ok($data, "Data loaded: $file");
    #------------------------------------
    my $desc = {id => 'amur',
        geos       => '76',
        candidates => [
            {id => 'a', name => "Лужков М А", search => "Бульбенко"},
            {id => 'b', name => "Лифанов",     search => "Коваль"},
            {id => 'c', name => "Стерлигов", search => "Пинчук"},
            {id => 'd', name => "Лебедев",     search => "Руссиянов"},
            {id => 'e', name => "Лебедев",     search => "Черенков"},
            {id => 'f', name => "Лебедев",     search => "Михайлова"},
        ]};
    my $res = parse_cik_html($desc, $data);

    #dmp( $res );
    ok($res->{ts},         "Timestamp");
    ok($res->{candidates}, "Candidates Yes");
    ok($res->{ok},         "Self test ok");
    is($res->{warnings}, undef);

    $file = lib::abs::path("./data/votes_amur2.html");
    open($H, $file) || die "link list '$file' not loaded";
    $data = join('', (<$H>));
    close($H);

    my $res = parse_cik_html($desc, $data);
    ok($res->{ts},         "Timestamp");
    ok($res->{candidates}, "Candidates Yes");
    ok($res->{ok},         "Self test ok");
    ok($res->{warnings},   "warnings presents");

};

subtest "Votes Parse online habhab" => sub {
    my $file = lib::abs::path("./data/votes_habhab_online.html");
    open(my $H, $file) || die "link list '$file' not loaded";
    my $data = join('', (<$H>));
    close($H);
    my $desc = {id => 'habhab',
        geos       => '76',
        candidates => [
            {id => 'a', search => "Афанасьев"},
            {id => 'b', search => "Лысенко"},
            {id => 'c', search => "Перевезенцев"},
            {id => 'd', search => "Разуванов"},
            {id => 'e', search => "Савочкин"},
            {id => 'f', search => "Соколов"},
        ]};
    my $res = parse_cik_html($desc, $data);

    #dmp( $res );
    ok($res->{ts},         "Timestamp");
    ok($res->{candidates}, "Candidates Yes");
    ok($res->{ok},         "Self test ok");
    is($res->{warnings}, undef);

};

subtest "Votes EKB" => sub {

    my $file = lib::abs::path("./data/votes_ekb.html");
    open(my $H, $file) || die "link list '$file' not loaded";
    my $data = join('', (<$H>));
    close($H);
    my $desc = {id => 'habhab',
        geos       => '76',
        candidates => [
            {id => 'a',  search => "артюх"},
            {id => 'b',  search => "бакова"},
            {id => 'c',  search => "Бурков Александр Владимирович"},
            {id => 'd',  search => "Бурков Александр Леонидович"},
            {id => 'e',  search => "Бурков Антон Леонидович"},
            {id => 'f',  search => "карелин"},
            {id => 'a1', search => "носков"},
            {id => 'b1', search => "ройзман"},
            {id => 'c1', search => "рузаков"},
            {id => 'd1', search => "рявкин"},
            {id => 'f1', search => "силин"},
        ]};
    my $res = parse_cik_html($desc, $data);

    #dmp( $res );
    ok($res->{ts},         "Timestamp");
    ok($res->{candidates}, "Candidates Yes");
    ok($res->{ok},         "Self test ok");
    is($res->{warnings}, undef);

};

done_testing();
