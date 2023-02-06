#!/usr/bin/perl

use strict;
use warnings;

use lib::abs qw(. ../lib );
use Data::Dumper;

use Test::More;

use_ok('uatraits');
my $dump = 0;
my $dir  = $ARGV[0] || lib::abs::path('../auto/uatraits/');

ok( -d $dir, "Data directory found: $dir" );
if( !-d $dir ){
    exit 1;
}

subtest "OldAPI" => sub {

    my $browser_file = $dir . '/browser.xml';
    my $decoder      = uatraits->new($browser_file);
    my $headers      = {
        'User-Agent' => 'Mozilla/5.0 (X11; U; Linux armv5tejl; en; rv:1.9.0.19) Gecko/2010072023 Firefox/3.0.6 (Debian-3.0.6-3)',
    };
    my $res = $decoder->detect($headers->{'User-Agent'});
    ok($res);
    ok($res->{isBrowser});
    diag(Dumper($res)) if $dump;
    done_testing();
};
subtest "NewAPI" => sub {
    my $browser_file = $dir . '/browser.xml';
    my $decoder      = uatraits->new($browser_file);
    my $headers      = {
        'User-Agent' => 'Mozilla/5.0 (X11; U; Linux armv5tejl; en; rv:1.9.0.19) Gecko/2010072023 Firefox/3.0.6 (Debian-3.0.6-3)',
    };
    my $res = $decoder->detect_by_headers($headers);

    ok($res);
    is($res->{BrowserName}, q{Firefox});
    diag(Dumper($res)) if $dump;
    done_testing();
};

our $decoder;
subtest "NewApi + wap detector" => sub {
    my $browser_file = $dir . q{/browser.xml};
    my $profile_file = $dir . q{/profiles.xml};
    our $decoder = uatraits->new($browser_file, $profile_file);

    ok($decoder);

    my $headers = {
        'User-Agent'    => 'Mozilla/5.0 (X11; U; Linux armv5tejl; en; rv:1.9.0.19) Gecko/2010072023 Firefox/3.0.6 (Debian-3.0.6-3)',
        'X-Wap-Profile' => 'http://nds1.nds.nokia.com/uaprof/N6020r100.xml',
        'X-Operamini-Phone-Ua' => 'Mozilla/5.0 (SymbianOS/9.4; Series60/5.0 NokiaN97-1/10.0.012; Profile/MIDP-2.1 Configuration/CLDC-1.1; en-us) AppleWebKit/525 (KHTML, like Gecko) WicKed/7.1.12344',
    };

    my $res = $decoder->detect_by_headers($headers);
    ok($res);
    #is( $res->{BrowserName}, q{Firefox} );
    ok($res->{ScreenSize});
    ok($res->{DeviceVendor});
    diag(Dumper($res)) if $dump;
    done_testing();
};

subtest "X-Wap Profile in quotes" => sub {
    ok($decoder);
    my $headers1 = {
        'User-Agent'    => 'Mozilla/5.0 (X11; U; Linux armv5tejl; en; rv:1.9.0.19) Gecko/2010072023 Firefox/3.0.6 (Debian-3.0.6-3)',
        'X-Wap-Profile' => "http://nds1.nds.nokia.com/uaprof/N6020r100.xml",
        #'X-Wap-Profile' => 'http://wap.samsungmobile.com/uaprof/GT-I9100.xml',
        #'X-Operamini-Phone-Ua' => 'Mozilla/5.0 (SymbianOS/9.4; Series60/5.0 NokiaN97-1/10.0.012; Profile/MIDP-2.1 Configuration/CLDC-1.1; en-us) AppleWebKit/525 (KHTML, like Gecko) WicKed/7.1.12344',
    };
    my $res1 = $decoder->detect_by_headers($headers1);
    ok($res1);
    #diag(Dumper($res1));
    my $headers2 = {
        'User-Agent'    => 'Mozilla/5.0 (X11; U; Linux armv5tejl; en; rv:1.9.0.19) Gecko/2010072023 Firefox/3.0.6 (Debian-3.0.6-3)',
        'X-Wap-Profile' => "\x22http://nds1.nds.nokia.com/uaprof/N6020r100.xml\x22",
        #'X-Operamini-Phone-Ua' => 'Mozilla/5.0 (SymbianOS/9.4; Series60/5.0 NokiaN97-1/10.0.012; Profile/MIDP-2.1 Configuration/CLDC-1.1; en-us) AppleWebKit/525 (KHTML, like Gecko) WicKed/7.1.12344',
    };
    my $res2 = $decoder->detect_by_headers($headers2);
    ok($res2);
    #diag(Dumper($res2));
};

{
    use MordaX::Experiment::Filter;
    my $goods_browser_code = sub {
        MordaX::Experiment::Filter::filter($_[0], 'good_browser');
    };

    my $good_headers = [
        'Mozilla/5.0 (Linux; Android 5.1; Nexus 5 Build/LMY47I) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 YaBrowser/15.4.2272.3608.00 Mobile Safari/537.36',
        'Mozilla/5.0 (iPad; CPU OS 8_1_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B466 Safari/600.1.4',
        'Mozilla/5.0 (iPad; CPU OS 7_1 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) Version/7.0 Mobile/11D167 Safari/9537.53',
        'Mozilla/5.0 (iPad; CPU OS 7_1_2 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) Version/7.0 Mobile/11D257 Safari/9537.53',
        'Mozilla/5.0 (iPad; CPU OS 8_1_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B466 Safari/600.1.4',
        'Mozilla/5.0 (Linux; Android 5.0.2; SGP321 Build/10.6.A.0.454) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.111 Safari/537.36',
        'Mozilla/5.0 (Linux; Android 5.0.2; SGP321 Build/10.6.A.0.454) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 YaBrowser/15.4.2272.3842.01 Safari/537.36',
        'Mozilla/5.0 (iPad; CPU OS 7_1_2 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) YaBrowser/15.7.2357.2697.11 Mobile/11D257 Safari/9537.53',
        'Mozilla/5.0 (iPad; CPU OS 7_1_2 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) CriOS/44.0.2403.65 Mobile/11D257 Safari/9537.53',
    ];
    for my $h (@$good_headers) {
        my $res = $decoder->detect_by_headers({'User-Agent' => $h});
        ok($res);
        ok $goods_browser_code->({BrowserDesc => $res}), 'Good' or diag $h;
    }

    my $bad_headers = [
        'Mozilla/5.0 (iPhone; CPU iPhone OS 6_1_3 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10B329 Safari/8536.25',
        'Opera/9.80 (iPhone; Opera Mini/7.0.5/35.4183; U; ru) Presto/2.8.119 Version/11.10',
        'Mozilla/5.0 (Linux; Android 4.1.2; GT-I9100 Build/JZO54K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 YaBrowser/14.4.1750.13427.00 Mobile Safari/537.36',
        'Opera/9.80 (Android; Opera Mini/7.5.35199/34.2089; U; ru) Presto/2.8.119 Version/11.10',
        'Mozilla/5.0 (iPad; CPU OS 5_1_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B206 Safari/7534.48.3',
        'Mozilla/5.0 (iPad; CPU OS 5_1_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/6.0 Mobile/9B206 Safari/7534.48.3 YaBrowser/2.1.1364.172',
        'Mozilla/5.0 (iPad; CPU OS 6_1_3 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/5.1 YaBrowser/13.9.1500.7516 Mobile/10B329 Safari/8536.25',
        'Mozilla/5.0 (iPad; CPU OS 6_1_3 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) CriOS/30.0.1599.16 Mobile/10B329 Safari/8536.25',
        'Mozilla/5.0 (Linux; U; Android 3.2; en-gb; GT-P7300 Build/HTJ85B) AppleWebKit/534.13 (KHTML, like Gecko) Version/4.0 Safari/534.13',
        'Opera/9.80 (Android 3.2; Linux; Opera Tablet/ADR-1210241511) Presto/2.11.355 Version/12.10',
        'Mozilla/5.0 (Linux; Android 4.4.2; Nexus 7 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 YaBrowser/14.4.1750.13427.00 Safari/537.36',
        'Mozilla/5.0 (Android; Tablet; rv:29.0) Gecko/29.0 Firefox/29.0',
        'Mozilla/5.0 (iPad; CPU OS 8_1_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) YaBrowser/14.12.2125.9580.11 Mobile/12B466 Safari/600.1.4',
    ];
    for my $h (@$bad_headers) {
        my $res = $decoder->detect_by_headers({'User-Agent' => $h});
        ok($res);
        #note explain $res;
        ok !$goods_browser_code->({BrowserDesc => $res}), 'Bad' or diag $h;
    }
}
done_testing();

