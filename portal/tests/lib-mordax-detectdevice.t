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

use MordaX::DetectDevice;
use MordaX::Input;
use Rapid::Base;
use testlib::TestRequest;
use MP::Logit qw(logit dmp);
MordaX::DetectDevice::init_detect_device( $dir );
Rapid::Base::compile_require( errors => 0, no_fault => 1 );

ok( $MordaX::DetectDevice::dd , "DD object inited and placed as expecte");


my $agents = {
    q{Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10240} => {
        MordaContent => 'big',
        js_template => 'big.gramps',
    },
    q{Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 YaBrowser/15.6.2311.4209 Safari/537.36} => {
        MordaContent => 'big',
        js_template => 'big.gramps',
    },
    q{Mozilla/5.0 (Linux; U; Android 4.2.2; ru-ru; BPM7021 Build/JDQ39) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30} => {
        MordaContent => 'touch',
        js_template => 'touch.gramps',
    },
    q{Mozilla/5.0 (Linux; Android 5.1; LGLS991 Build/LMY47D) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 YaBrowser/15.6.2311.6088.00 Mobile Safari/537.36} => {
        MordaContent => 'touch',
        js_template => 'touch.gramps',
    },
    q{Opera/9.80 (J2ME/MIDP; Opera Mini/7.1.32052/35.5706; U; id) Presto/2.8.119 Version/11.10} => {
        MordaContent => 'mob',
        js_template => 'mob.*',
    },
    q{Opera/9.80 (Android 2.3.5; Linux; Opera Mobi/ADR-1309251116) Presto/2.11.355 Version/12.10} => {
        MordaContent => 'touch',
        js_template => 'touch.gramps',
    },
    q{Mozilla/5.0 (SMART-TV; Linux; Tizen 2.3) AppleWebkit/538.1 (KHTML, like Gecko) SamsungBrowser/1.0 TV Safari/538.1} => {
        MordaContent => 'tv',
        js_template => 'tv.*',
    },
    q{Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.2228.0 Safari/537.36} => {
        MordaContent => 'big',
        js_template => 'big.v15',
    },
    q{Mozilla/5.0 (iPad; CPU OS 15_0 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) CriOS/91.0.2490.85 Mobile/13B143 Safari/600.1.4 (000476)} => {
        MordaContent => 'big',
        js_template => 'big.v15',
    },
    q{Mozilla/5.0 (iPhone; CPU iPhone OS 10_0_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) YaBrowser/16.3.3.4 YaApp_iOS/2.32} => {
        MordaContent => 'touch',
        js_template => 'touch.gramps',
    },
    q{Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) YaBrowser/15.10.2454.3724.10 Mobile/13B143 Safari/600.1.4} => {
        MordaContent => 'touch',
        js_template => 'touch.gramps',
    },
    q{Mozilla/5.0 (Linux; Android 6.0.1; Redmi 4 Build/MMB29M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/56.0.2924.87 YaBrowser/17.6.1.11 (lite) Mobile Safari/537.36} => {
        MordaContent => 'touch',
        js_template => 'touch.*',
    },
};

#dmp( $Rapid::Base::reg );

subtest "UA + Rapid" => sub {

    MordaX::Experiment::Filter::add('ne_gramps', sub {1});

    for my $ua (keys %$agents ){
        diag( $ua );
        my $data = $agents->{$ua};
        my $req = MordaX::Req->new();
        my $r =  testlib::TestRequest::FcgiRequest->new( headers => { 'User-Agent' => $ua } );
        $MordaX::Input::JSTemplateEnabled = 'xxxxxx';

        Rapid::Base::run_with_reqs('input', 'device_morda_content', $r, $req);
        Rapid::Base::run_with_reqs('input', 'template', $r, $req);
        MordaX::Input::input_touch_gramps( $req );
        MordaX::Input::templater_select( $req );
        ok( $req->{BrowserDesc} );
        is( $req->{MordaContent} , $data->{MordaContent}, "Content:" . $req->{MordaContent} );
        is( $MordaX::Input::JSTemplateEnabled, $data->{js_template} , 'JS_template');
        #dmp( $r , $r->{_HEADERS}, $req );

        $MordaX::Input::JSTemplateEnabled = 'xxxxxx';
        my $req2 = testlib::TestRequest::Req->new(  headers => { 'User-Agent' => $ua });
        is( $req2->{MordaContent} , $data->{MordaContent}, "2Content:" . $req->{MordaContent} );
        is( $MordaX::Input::JSTemplateEnabled, $data->{js_template} , '2JS_template');

    }

};


done_testing();


