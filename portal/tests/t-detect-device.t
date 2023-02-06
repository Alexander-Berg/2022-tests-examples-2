#!/usr/bin/perl

use strict;
use warnings;

use lib::abs qw(. ../t/testlib);

use Test::More;

use MordaTest;
#use testlib::TestRequest qw(r);
use MordaX::Logit qw(dumpit);
use MordaX::Conf;

use_ok('uatraits');

use_ok("MordaX::Req");
use_ok("MordaX::Input");

#MordaX::Conf->get('UseUatraits');
#MordaX::Conf->new()->set('UseUatraits', 1);

#ok( MordaX::Conf->get('UseUatraits') , "use uatriats");

use_ok('MordaX::DetectDevice');

my $detector = MordaX::DetectDevice->new();

ok($detector->detect(headers => {'User-Agent' => 'Opera'}), 'some Opera detect works');
ok($detector->get_browser());

#dumpit( $detector->get_browser() );
subtest "FF3.0" => sub {
    my $req = MordaX::Req->new();
    $req->{'UserHeaders'}->{'User-Agent'} = 'Mozilla/5.0 (X11; U; Linux armv5tejl; en; rv:1.9.0.19) Gecko/2010072023 Firefox/3.0.6 (Debian-3.0.6-3)';

    $detector->detect(
        'headers' => $req->{'UserHeaders'},
    );
    $detector->set_req_flags($req);

    #dumpit( $req, $req->{BrowserDesc} );

    ok($req->{BrowserDesc}->{BrowserName}, 'name');

    my $input = {};    #MordaX::Input->new();
    bless($input, "MordaX::Input");

    #$input->{Request} = $req;
    #$input->fillin_browser();

    ok($req->{FireFox});
    is($req->{FireFoxVersion}, 3);
    like($req->{FireFoxVersionFull}, qr/^3\.0/);

    done_testing();

};
subtest "MSIE 9.0" => sub {
    my $ua  = 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)';
    my $req = MordaX::Req->new();
    $req->{'UserHeaders'}{'User-Agent'} = $ua;
    $detector->detect(
        'headers' => $req->{'UserHeaders'},
    );
    $detector->set_req_flags($req);

    ok($req->{BrowserDesc}->{BrowserName}, 'name');

    my $input = {};    #MordaX::Input->new();
    bless($input, "MordaX::Input");
    $input->{Request} = $req;
    #$input->fillin_browser();
    ok($req->{isMSIE},  "IE!!");
    ok($req->{isMSIE9}, "IE9");
    is($req->{MSIE}, "9", "IE9!!");
    done_testing();
};

subtest "ANDROID " => sub {
    my $ua = 'Mozilla/5.0 (Linux; U; Android 3.1; ru-ru; GT-P7500 Build/HMJ37) AppleWebKit/534.13 (KHTML, like Gecko) Version/4.0 Safari/534.13';
    my $req = MordaX::Req->new();
    $req->{'UserHeaders'}{'User-Agent'} = $ua;
    $detector->detect(
        'headers' => $req->{'UserHeaders'},
    );
    $detector->set_req_flags($req);

    #ok( $req->{BrowserDesc}->{BrowserName} , 'name');

    my $input = {};    #MordaX::Input->new();
    bless($input, "MordaX::Input");
    $input->{Request} = $req;
    is($req->{'isAndroid'}, 1, 'android ok');
    is($req->{'AndroidVersion'}, '3', 'android version ok');
    is($req->{'AndroidVersionFull'}, '3.1', 'android full version ok');
    #$input->fillin_browser();
    #ok( $req->{UserDevice} , 'UserDevice presets');
    #ok( length( $req->{UserDevice}->{name} || ''  ) < 15, 'name is short' );
    #ok( $req->{UserDevice}->{device_id}, 'device id ok');
    #ok($mordax::Memd, 'memd online');

    my $apps = MordaX::Block::Application->new(req => $req);

    done_testing();

};

done_testing();

