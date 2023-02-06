#!/usr/bin/env perl

=head1 NAME

t-rapid.t - тест быстроморды

=head1 DESCRIPTION

    Требует запущенный fastcgi и веб-сервер.
    Должны быть разрешены запросы по http.

=cut

use Test::Most;
use common::sense;
use lib::abs qw( . ../lib );
use 5.010;

#use_ok('InitBase');
use MordaX::Logit qw(dmp);
use MP::Utils qw(is_hash is_hash_size);
use Test::Deep;

use MP::UserAgent;
use HTTP::Cookies;
use MordaX::HTTP;
die_on_fail();

require(lib::abs::path('../tools/instance'));
my $inst = instance();
ok($inst);

my $host = "www-$inst.wdevx.yandex.ru";
my $rapid = "https://$host/instant/all?";
my $oldjson = "https://$host/?json=1&";

my $http  = MordaX::HTTP->new( {} );
ok($http, "HTTP online");
ok($rapid, "Fetchinf $rapid and $oldjson");

my $cookies = HTTP::Cookies->new();
#$cookies->set_cookie(1.1, 'yandexuid',
my $yandexuid = '4632667731411099774';

#$ua->cookie_jar($cookies);
our ($old, $new);

my $testcount = 0;
do {
    $old = get_json($oldjson);
    $new = get_json($rapid);
    if( !$testcount ){
        subtest "OLD NEW RESPONCE" => sub {
            ok($old && is_hash($old), 'old json responce');
            ok($new && is_hash($new), 'rapid all json responce');
            ok( $old->{JSTimestamp} , 'OLD JSTimestamp');
            ok( $new->{JSTimestamp} , 'NEW JSTimestamp');
            fail( 'upps')  if ! ($old->{JSTimestamp} && $new->{JSTimestamp} );
        };
    }

    $testcount++;
} while ($old->{'JSTimestamp'} ne $new->{'JSTimestamp'} and $testcount < 10);

exit 1 unless $new;

ok( !$new->{common}, "Common block not present");
for(qw/
        HomePageNoArgs
        statRoot
        statRootAttrs
        staticVersion
    /){
    ok( $new->{$_} , $_ . " is obligatory " );
}

subtest 'CMP OLD->NEW' => sub {
    my $skip = {
        map {$_ => 1} (qw/
            Banner_debug
            Geo
            NcRnd
            Getargs
            Gohome
            raw_Getargs
            CountSetHome

            Direct
            HideThisWidget
            NoParallelSearches
            ReportPixel
            Requestid
            Safegetargs
            ShowID
            SmartExample
            SetHomeStripe
            SetHomeIOS
            SetHome
            TemplatePrimordial
            yu
            yandexuid_hash
            Layout
            JSMda
            HomePageEmptyStub
            HomePage
            TargetingInfo
            geolocation_promo
            interests

            common
            statRoot
            statRootAttrs
            Teaser
        /)
    };

    is( $old->{Yandexuid}, $yandexuid, "OLD YANDEX UID OK");
    is( $old->{Yandexuid}, $new->{Yandexuid}, "yandexuid same, NEWOK");
    is( $old->{sk}, $new->{sk} , 'sk same');
    is( $old->{Newyandexuid}, undef, );
    is( $old->{history_api_url}, undef, 'OLD: history api' );
    is( $new->{history_api_url}, undef, 'NEW: history api clean url: NONe');

    ok( $new->{blocks} , "Blocks in new");
    ok( scalar( @{$new->{blocks}} ) > 1 , "Blocks presetns" );

    $old->{'Services'}->{'hash'} = ignore();
    $old->{'Miniservices'}->{'direct'} = ignore();
    $old->{'WrongDateAlert'}->{'show_url'} = ignore();
    $old->{'WrongDateFatal'}->{'show_url'} = ignore();
    #$old->{'Afisha'}->{concert} = ignore();


    #блок promo с рандомайзеров. сравнивать напрямую их нельзя
    if (is_hash($old->{'Afisha'}->{'promo'})) {
        ok(is_hash($new->{'Afisha'}->{'promo'}), 'promo exists');
        if (is_hash_size($old->{'Afisha'}->{'promo'})) {
            ok(is_hash_size($new->{'Afisha'}->{'promo'}), 'promo not empty');
        }
        else {
            ok(!is_hash_size($new->{'Afisha'}->{'promo'}), 'promo empty');
        }
    }
    else {
        ok( !($new->{'Afisha'}->{'promo'}), 'promo not exists');
    }
    for( $new, $old ){
        delete $_->{'Afisha'}->{'promo'};
        delete $_->{'Afisha'}->{'premiere'};
        delete $_->{'TV'}->{'announces'};
        delete $_->{'Afisha'}->{'concert'};
    }

    #блок GeoDetection для быстроморды содержит доп. свойства degrade geolib
    delete $new->{'GeoDetection'}->{'degrade'};
    delete $new->{'GeoDetection'}->{'geolib'};

    #интерфейс GeoDetection сильно отличается
    is($new->{'GeoDetection'}->{'lon'}, $old->{'GeoDetection'}->{'lon'}, 'geo lon');
    is($new->{'GeoDetection'}->{'lat'}, $old->{'GeoDetection'}->{'lat'}, 'geo lat');
    #delete $new->{'GeoDetection'};
    #delete $old->{'GeoDetection'};

    #SetupURL SetupURLRegion отличаются
    delete $new->{'SetupURL'};
    delete $old->{'SetupURL'};
    delete $new->{'SetupURLRegion'};
    delete $old->{'SetupURLRegion'};

    #на плоской морде есть Themes->promos, на быстрой - нет
    delete $old->{'Themes'}->{'promos'};

    #на быстроморде нет yu_v2
    delete $old->{'yu_v2'};

    for( qw/Banner_stripe GeoDetection Getargshash ClientCounters/){
        dmp($_, $old->{$_}, $new->{$_});
        delete $old->{$_};
        delete $new->{$_};
    }

    $old->{exp}->{skin_touch} = ignore();
    foreach my $o (sort keys %{ $old }) {
        next if $skip->{ $o };
        next if $o =~ /^raw_/;
        next if $o =~ /^TenPercent/;

        cmp_deeply($new->{ $o }, $old->{ $o }, "CMP: $o");
    }
    done_testing();
};
subtest 'is in NEW' => sub {
    foreach (qw/ShowID NcRnd Gohome Requestid ReportPixel/) {
        ok($new->{ $_ }, "PRESENTS: $_");
    }

    like($new->{'HomePage'}, qr/clid=\d{3,}/, 'New HomePage with clid, ( clid->go_home)');
    like($old->{'HomePage'}, qr/clid=\d{3,}/, 'Old HomePage with clid');

    done_testing();
};
#SmartExample
#Geo
done_testing();

sub get_json {
    my $url = shift;

    $http->add(
        alias => 'x',
        url => $url,
        timeout => 1,
        headers => [
            {
                name => 'Cookie',
                value => "yandexuid=$yandexuid; mda=1; yandex_gid=213",
            },
            {
                name => 'RandomSeed',
                value => 12233,
            },
            {
                name => 'User-Agent',
                value => 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 YaBrowser/16.6.0.8125 Safari/537.36',
            }
        ],
        verbose => 0,

    );
    my $content = $http->result('x');
    my $data = MP::Utils::parse_json($content);
    return $data;
}
