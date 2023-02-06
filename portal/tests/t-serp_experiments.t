#!/usr/bin/perl

use strict;
use warnings;
use Test::More;
use JSON qw();
use lib::abs qw( . ../lib ../scripts );
use Data::Dumper;
#$Data::Dumper::Maxdepth = 2;
$Data::Dumper::Useqq = 1;

use GetData;
use Test::MockModule;
use MordaX::Experiment::SERPCond;

my $module = Test::MockModule->new('GetData');
$module->mock('error', sub { shift; diag @_ });

=pod
use XML::Simple;
# собираем все кондишены, которые есть
my $test_path = lib::abs::path('.').'/serp.json';
diag $test_path;

my $conditions = {};
my $statuses = {};
my $json_text = do {
   open(my $json_fh, "<:encoding(UTF-8)", $test_path)
      or die("Can't open \$test_path\": $!\n");
   local $/;
   <$json_fh>
};

my $json = JSON->new;
my $data = $json->decode($json_text);
for my $exp (@$data) {
    my $params = $json->decode($exp->{'params'})->[0];
    my $condition = $params->{'CONDITION'};
    next unless $condition;
    push @{$conditions->{$condition}}, $exp->{'testid'};
    
    my $status = $exp->{'status'};
    $statuses->{$status}++;
}
print Dumper [sort keys %$conditions];
print Dumper [sort keys %$statuses];
exit(0);
=cut

# ================================ MAIN ====================================
my $helper = GetData->new();

# =
for my $samplecondition (@{get_conditions()}) {
    $samplecondition = MordaX::Experiment::SERPCond::condition_normalize($samplecondition);
    ok(MordaX::Experiment::SERPCond::condition_validate($helper, $samplecondition)) or diag 'CHECKED FOR ', $samplecondition;
}

# =
my $cond     = get_conditions_for_code();
my $cgi_cond = {};
for my $samplecondition (keys %$cond) {
    my $code = MordaX::Experiment::SERPCond::condition_turn_to_code($samplecondition);
    is($code, $cond->{$samplecondition}) or diag $samplecondition, ' => ', $code;
    $cgi_cond->{$code}++ if $code =~ /cgi/;
}

# =
my $req = {};

#cgi('noreask', '==', 1)
is(MordaX::Experiment::SERPCond::cgi('noreask', '==', 1), 0);
is(MordaX::Experiment::SERPCond::cgi('noreask', '>=', 1), 0);

$req->{'Getargshash'} = {noreask => 1};
MordaX::Experiment::SERPCond::initserpexpquery($req);
is(MordaX::Experiment::SERPCond::cgi('noreask', '==', 1), 1);
is(MordaX::Experiment::SERPCond::cgi('noreask', '<=', 500300), 1);
is(MordaX::Experiment::SERPCond::cgi('noreask', '<', 500300), 1);
is(MordaX::Experiment::SERPCond::cgi('noreask', '>', 500300), 0);
is(MordaX::Experiment::SERPCond::cgi('noreask', '>=', 500300), 0);

#cgi('numdoc', '==', 50)
$req->{'Getargshash'} = {numdoc => 20};
MordaX::Experiment::SERPCond::initserpexpquery($req);
is(MordaX::Experiment::SERPCond::cgi('numdoc', '==', 50), 0);

$req->{'Getargshash'} = {numdoc => 50};
MordaX::Experiment::SERPCond::initserpexpquery($req);
is(MordaX::Experiment::SERPCond::cgi('numdoc', '==', 50), 1);

$req->{'Getargshash'} = {numdoc => 50};
MordaX::Experiment::SERPCond::initserpexpquery($req);
is(MordaX::Experiment::SERPCond::cgi('numdoc', '==', 50), 1);

#cgi('p', '==', 2)
$req->{'Getargshash'} = {p => 'qwe'};
MordaX::Experiment::SERPCond::initserpexpquery($req);
is(MordaX::Experiment::SERPCond::cgi('p', '==', 2), 0);

$req->{'Getargshash'} = {};
is(MordaX::Experiment::SERPCond::cgi('p', '==', 1), 0);
is(MordaX::Experiment::SERPCond::cgi('p', '!=', 1), 0);
is(MordaX::Experiment::SERPCond::cgi('p', '<',  1), 0);
is(MordaX::Experiment::SERPCond::cgi('p', '>',  1), 0);
is(MordaX::Experiment::SERPCond::cgi('p', '>=', 1), 0);
is(MordaX::Experiment::SERPCond::cgi('p', '<=', 1), 0);
is(MordaX::Experiment::SERPCond::cgi('p', 'eq', 'qwe'), 0);
is(MordaX::Experiment::SERPCond::cgi('p', 'ge', 'qwe'), 0);
is(MordaX::Experiment::SERPCond::cgi('p', 'gt', 'qwe'),  0);
is(MordaX::Experiment::SERPCond::cgi('p', 'lt', 'zqwe'), 0);

$req->{'Getargshash'} = {p => 'qwe'};
MordaX::Experiment::SERPCond::initserpexpquery($req);
is(MordaX::Experiment::SERPCond::cgi('p', 'eq', 'qwe'), 1);
is(MordaX::Experiment::SERPCond::cgi('p', 'eq', 'aaa'), 0);

is(MordaX::Experiment::SERPCond::cgi('p', 'ge', 'qwe'), 1);
is(MordaX::Experiment::SERPCond::cgi('p', 'ge', 'aqwe'), 1);
is(MordaX::Experiment::SERPCond::cgi('p', 'ge', 'zqwe'), 0);

is(MordaX::Experiment::SERPCond::cgi('p', 'gt', 'qwe'),  0);
is(MordaX::Experiment::SERPCond::cgi('p', 'gt', 'aqwe'), 1);
is(MordaX::Experiment::SERPCond::cgi('p', 'gt', 'zqwe'), 0);

is(MordaX::Experiment::SERPCond::cgi('p', 'lt', 'qwe'),  0);
is(MordaX::Experiment::SERPCond::cgi('p', 'lt', 'aqwe'), 0);
is(MordaX::Experiment::SERPCond::cgi('p', 'lt', 'zqwe'), 1);

$req->{'Getargshash'} = {p => 2};
MordaX::Experiment::SERPCond::initserpexpquery($req);
is(MordaX::Experiment::SERPCond::cgi('p', '==', 2), 1);

#cgi('text', 'eq', '123')
$req->{'Getargshash'} = {text => 111};
MordaX::Experiment::SERPCond::initserpexpquery($req);
is(MordaX::Experiment::SERPCond::cgi('text', 'eq', '123'), 0);

$req->{'Getargshash'} = {text => 123};
MordaX::Experiment::SERPCond::initserpexpquery($req);
is(MordaX::Experiment::SERPCond::cgi('text', 'eq', '123'), 1);

$req->{'Getargshash'} = {text => 'abc'};
MordaX::Experiment::SERPCond::initserpexpquery($req);
is(MordaX::Experiment::SERPCond::cgi('text', 'eq', 'abc'), 1);

# ! cgi('relatedVideo')
is(!MordaX::Experiment::SERPCond::cgi('relatedVideo'), 1);

$req->{'Getargshash'} = {relatedVideo => 0};
MordaX::Experiment::SERPCond::initserpexpquery($req);
is(MordaX::Experiment::SERPCond::cgi('relatedVideo'), 1);

$req->{'Getargshash'} = {relatedVideo => 1};
MordaX::Experiment::SERPCond::initserpexpquery($req);
is(MordaX::Experiment::SERPCond::cgi('relatedVideo'), 1);

#cgi('clid', '==', 2073169)
is(MordaX::Experiment::SERPCond::cgi('clid', '==', 2073169), 0);

$req->{'Getargshash'} = {clid => 1};
MordaX::Experiment::SERPCond::initserpexpquery($req);
is(MordaX::Experiment::SERPCond::cgi('clid', '==', 2073169), 0);

$req->{'Getargshash'} = {clid => 2073169};
MordaX::Experiment::SERPCond::initserpexpquery($req);
is(MordaX::Experiment::SERPCond::cgi('clid', '==', 2073169), 1);

#cgi('clid', '!=', 1955452)
is(MordaX::Experiment::SERPCond::cgi('clid', '!=', 1955452), 1);

$req->{'Getargshash'} = {clid => 2073169};
MordaX::Experiment::SERPCond::initserpexpquery($req);
is(MordaX::Experiment::SERPCond::cgi('clid', '!=', 1955452), 1);

$req->{'Getargshash'} = {clid => 1955452};
MordaX::Experiment::SERPCond::initserpexpquery($req);
is(MordaX::Experiment::SERPCond::cgi('clid', '!=', 1955452), 0);

done_testing();

sub get_conditions {
    my $conditions = [
#          "(device.OSFamily eq 'Android' &&  device.OSVersion ge ‘4.0’ &&  device.BrowserName eq 'Chrome') || device.OSFamily eq ‘WindowsPhone'",
#          "(device.OSFamily eq 'Android' &&  device.OSVersion ge ‘4.0’ && BrowserName=Chrome) || device.OSFamily eq ‘WindowsPhone'",
        '108',
        '31',
        '32',
        '33',
        '34',
        '6',
        '79',
        '80',
#          'WEB.ShortBeak.MiddleIns_short_beak > 0',
        'cgi.noreask == 1',
        'cgi.numdoc == 50',
        'cgi.p == 2',
        'cgi.text eq \'123\'',
        'desktop',
        'desktop &&  relev.cm2>0.3',
        'desktop && !cgi.relatedVideo',
#          'desktop && ((cgi.clid==1989187||cgi.clid==1989188||cgi.clid==1989189||cgi.clid==1989190||cgi.clid==1989191||cgi.clid==1989192||cgi.clid==1989193||cgi.clid==1989194||cgi.clid==1989195||cgi.clid==1989196||cgi.clid==1989197||cgi.clid==1989198||cgi.clid==1989199||cgi.clid==1989200||cgi.clid==1989201||cgi.clid==1989202||cgi.clid==1989204||cgi.clid==1989205||cgi.clid==1989206||cgi.clid==1989207||cgi.clid==1989208||cgi.clid==1989209||cgi.clid==1989210||cgi.clid==1989211||cgi.clid==2161802)',
        'desktop && (cgi.clid==1948795||cgi.clid==1989274||cgi.clid==1989273||cgi.clid==1979777||cgi.clid==1989190||cgi.clid==1979776||cgi.clid==2101079||cgi.clid==1979737||cgi.clid==1989191||cgi.clid==1989199||cgi.clid==1989283)',
        'desktop && (cgi.clid==1989187||cgi.clid==1989188||cgi.clid==1989189||cgi.clid==1989190||cgi.clid==1989191||cgi.clid==1989192||cgi.clid==1989193||cgi.clid==1989194||cgi.clid==1989195||cgi.clid==1989196||cgi.clid==1989197||cgi.clid==1989198||cgi.clid==1989199||cgi.clid==1989200||cgi.clid==1989201||cgi.clid==1989202||cgi.clid==1989204||cgi.clid==1989205||cgi.clid==1989206||cgi.clid==1989207||cgi.clid==1989208||cgi.clid==1989209||cgi.clid==1989210||cgi.clid==1989211||cgi.clid==2161802)',
        'desktop && (cgi.clid==2073169 || cgi.clid==2073170 || cgi.clid==2073171 || cgi.clid==2073172 || cgi.clid==2073173 || cgi.clid==073174 || cgi.clid==073175 || cgi.clid==073176)',
        'desktop && (cgi.clid==2073169 || cgi.clid==2073170 || cgi.clid==2073171 || cgi.clid==2073172 || cgi.clid==2073173 || cgi.clid==2073174 || cgi.clid==2073175 || cgi.clid==2073176)',
        'desktop && (device.BrowserName eq \'Opera\' || device.BrowserName eq \'Safari\')',
        'desktop && (device.BrowserName ne \'Firefox\')',
        'desktop && (device.OSFamily eq \'MacOS\')',
        'desktop && (device.OSFamily eq \'iOS\')',
        'desktop && (i18n:ru)',
        'desktop && (relev.il==1 || relev.Cpo>35000)',
        'desktop && (relev.il==1 || relev.po>35000)',
        'desktop && cgi.clid!=1955452',
        'desktop && cgi.clid==1955452',
        'desktop && i18n:RU',
        'desktop && i18n:ru',
        'desktop && relev.Cpo>=35000',
        'desktop && relev.il==1',
        'desktop && relev.il==1 || relev.Cpo>35000',
        'desktop && relev.il==1 || relev.po>35000',
        'desktop && relev.il==1||relev.Cpo>35000',
        'desktop && relev.il==1||relev.po>35000',
        'desktop && relev.po<300',
        'desktop && relev.po<92',
        'desktop && relev.po>=300',
        'desktop && relev.po>=35000',
        'desktop && relev.po>=92',
        q{internal && cgi.app_platform eq 'ANDROID' && cgi.app_version >= 5030000 && cgi.os_version ge '5.0' && device.BrowserBaseVersion gt '33'},
        q{internal && cgi.app_platform eq 'ANDROID' && cgi.app_version>=5030000 && cgi.os_version ge '5.0' && device.BrowserBaseVersion gt '33'},
        q{internal && cgi.app_platform eq 'ANDROID' && cgi.app_version > 5030000 && cgi.os_version ge '5.0' && device.BrowserBaseVersion gt '33'},
#          'desktop&&((flags.its_location eq "sas")||(flags.its_location eq "msk"))',
#          'desktop&&(flags.its_location eq "man") ',
#          'desktop&&(flags.its_location eq "sas")',
#          'desktop&&(flags.its_location eq "zelo")',
        'desktop&&relev.cm2>0.3',
        'device.BrowserEngine eq \'Trident\'',
        'device.OSFamily eq "iOS" && device.DeviceName eq "iPad"',
        'device.OSFamily eq \'Android\' || device.OSFamily eq \'WindowsPhone\' || device.OSFamily eq \'iOS\'',
        'device.OSFamily eq \'WindowsPhone\'',
        'device.OSFamily eq \'iOS\' || device.OSFamily eq \'Android\'',
        'device.OSVersion ge \'4.2\'',
        'device.isTablet',
        'device.isTablet eq \'1\'',
        'device.isTablet eq \'1\' && ((device.OSFamily eq \'iOS\' && device.OSVersion ge \'6.0\') || (device.OSFamily eq \'Android\'  && device.OSVersion ge \'4.0\'))',
        'device.isTablet eq \'1\' && (device.OSFamily eq \'iOS\' || device.OSFamily eq \'Android\')',
        'device.isTouch eq \'1\'',
#          'flags.bs_debug == 1',
#          'flags.disable_serp3 eq \'DA\'',
#          'flags.enable_https',
        'i18n:be',
        'i18n:en',
        'i18n:kk',
        'i18n:ru',
        'i18n:tr',
        'i18n:tt',
        'i18n:uk',
        'internal',
        'ipv6',
        'mobile',
#          "mobile && (device.OSFamily eq ‘WindowsPhone')",
        'mobile == smart',
        'mobile == touch',
        'relev.Cpo>=35000',
        'relev.cm2>0.3',
        'relev.il==1',
#          'relev.il==1 | | relev.Cpo>35000',
        'relev.il==1 || relev.Cpo>35000',
        'relev.il==1 || relev.cpo>35000',
        'relev.il==1 || relev.po>35000',
#          'relev.il==1| |relev.Cpo>35000',
#          'relev.il==1| |relev.cpo>35000',
        'relev.il==1||relev.Cpo>35000',
        'relev.il==1||relev.cpo>35000',
        'relev.po>=35000',
        'relev.po>=35000 || relev.il==1',
        'report:www',
        'report:www-touch',
        'serp-version:1',
        'serp-version:2',
        'serp-version:3',
        'smart',
        'snip.uil eq \'ru\'',
        q{(flags.its_location eq "man")},
        'tablet',
        'tld:by',
        'tld:com',
#          'tld:com.tr',
        'tld:kz',
        'tld:ru',
        'tld:ua',
        'touch',
        'touch && !( (device.BrowserName eq \'MobileSafari\' && device.BrowserVersion ge \'6.0\') || (device.BrowserName eq \'UCBrowser\' && device.BrowserVersion ge \'9.0\') || (device.BrowserName eq \'OperaMobile\' && device.BrowserVersion ge \'14.0\') || (device.BrowserName eq \'ChromeMobile\' && device.BrowserVersion ge \'17.0\') || (device.BrowserName eq \'Chromium\' && device.BrowserVersion ge \'17.0\') || (device.BrowserName eq \'YandexBrowser\'))'
    ];
}

sub get_conditions_for_code {
    return {
        108                             => 108,
        31                              => 31,
        32                              => 32,
        33                              => 33,
        34                              => 34,
        6                               => 6,
        79                              => 79,
        80                              => 80,
        "cgi.noreask >= 1"              => "cgi('noreask', '>=', 1)",
        "cgi.noreask <= 1"              => "cgi('noreask', '<=', 1)",
        "cgi.noreask > 1"               => "cgi('noreask', '>', 1)",
        "cgi.noreask < 1"               => "cgi('noreask', '<', 1)",
        "cgi.noreask == 1"              => "cgi('noreask', '==', 1)",
        "cgi.noreask != 1"              => "cgi('noreask', '!=', 1)",
        "cgi.noreask>=1"              => "cgi('noreask', '>=', 1)",
        "cgi.noreask<=1"              => "cgi('noreask', '<=', 1)",
        "cgi.noreask>1"               => "cgi('noreask', '>', 1)",
        "cgi.noreask<1"               => "cgi('noreask', '<', 1)",
        "cgi.noreask==1"              => "cgi('noreask', '==', 1)",
        "cgi.noreask!=1"              => "cgi('noreask', '!=', 1)",
        "cgi.numdoc == 50"              => "cgi('numdoc', '==', 50)",
        "cgi.numdoc == '50'"            => "cgi('numdoc', 'eq', '50')",
        'cgi.numdoc == "50"'            => "cgi('numdoc', 'eq', '50')",
        "cgi.numdoc == 'qwqw'"          => "cgi('numdoc', 'eq', 'qwqw')",
        "cgi.p == 2"                    => "cgi('p', '==', 2)",
        "cgi.text eq '123'"             => "cgi('text', 'eq', '123')",
        "desktop"                       => "desktop",
        "desktop && ! cgi.relatedVideo" => "desktop && ! cgi('relatedVideo')",
        "desktop && ( cgi.clid==2073169 || cgi.clid==2073170 )" => "desktop && ( cgi('clid', '==', 2073169) || cgi('clid', '==', 2073170) )",
        "desktop && ( device.BrowserName eq 'Opera' || device.BrowserName eq 'Safari' )" => "desktop && ( device('BrowserName', 'eq', 'Opera') || device('BrowserName', 'eq', 'Safari') )",
        "desktop && ( device.BrowserName ne 'Firefox' )" => "desktop && ( device('BrowserName', 'ne', 'Firefox') )",
        "desktop && ( device.OSFamily eq 'MacOS' )"      => "desktop && ( device('OSFamily', 'eq', 'MacOS') )",
        "desktop && ( device.OSFamily eq 'iOS' )"        => "desktop && ( device('OSFamily', 'eq', 'iOS') )",
        "desktop && ( i18n:ru )"                         => "desktop && ( i18n('ru') )",
        "desktop && ( relev.il==1 || relev.Cpo>35000 )"  => "desktop && ( relev('il', '==', 1) || relev('Cpo', '>', 35000) )",
        "desktop && ( relev.il==1 || relev.po>35000 )"   => "desktop && ( relev('il', '==', 1) || relev('po', '>', 35000) )",
        "desktop && cgi.clid!=1955452"                   => "desktop && cgi('clid', '!=', 1955452)",
        "desktop && cgi.clid==1955452"                   => "desktop && cgi('clid', '==', 1955452)",
        "desktop && i18n:RU"                             => "desktop && i18n('RU')",
        "desktop && i18n:ru"                             => "desktop && i18n('ru')",
        "desktop && relev.Cpo>=35000"                    => "desktop && relev('Cpo', '>=', 35000)",
        "desktop && relev.cm2>0.3"                       => "desktop && relev('cm2', '>', 0.3)",
        "desktop && relev.il==1"                         => "desktop && relev('il', '==', 1)",
        "desktop && relev.il==1 || relev.Cpo>35000"      => "desktop && relev('il', '==', 1) || relev('Cpo', '>', 35000)",
        "desktop && relev.il==1 || relev.po>35000"       => "desktop && relev('il', '==', 1) || relev('po', '>', 35000)",
        "desktop && relev.po<300"                        => "desktop && relev('po', '<', 300)",
        "desktop && relev.po<92"                         => "desktop && relev('po', '<', 92)",
        "desktop && relev.po>=300"                       => "desktop && relev('po', '>=', 300)",
        "desktop && relev.po>=35000"                     => "desktop && relev('po', '>=', 35000)",
        "desktop && relev.po>=92"                        => "desktop && relev('po', '>=', 92)",
        "device.BrowserEngine eq 'Trident'"              => "device('BrowserEngine', 'eq', 'Trident')",
        "device.OSFamily eq \"iOS\" && device.DeviceName eq \"iPad\"" => "device('OSFamily', 'eq', 'iOS') && device('DeviceName', 'eq', 'iPad')",
        "device.OSFamily eq 'Android' || device.OSFamily eq 'WindowsPhone' || device.OSFamily eq 'iOS'" => "device('OSFamily', 'eq', 'Android') || device('OSFamily', 'eq', 'WindowsPhone') || device('OSFamily', 'eq', 'iOS')",
        "device.OSFamily eq 'WindowsPhone'" => "device('OSFamily', 'eq', 'WindowsPhone')",
        "device.OSFamily eq 'iOS' || device.OSFamily eq 'Android'" => "device('OSFamily', 'eq', 'iOS') || device('OSFamily', 'eq', 'Android')",
        "device.OSVersion ge '4.2'" => "device('OSVersion', 'ge', '4.2')",
        "device.isTablet"           => "device('isTablet')",
        "device.isTablet eq '1'"    => "device('isTablet', 'eq', '1')",
        "device.isTablet eq '1' && ( ( device.OSFamily eq 'iOS' && device.OSVersion ge '6.0' ) || ( device.OSFamily eq 'Android' && device.OSVersion ge '4.0' ) )" => "device('isTablet', 'eq', '1') && ( ( device('OSFamily', 'eq', 'iOS') && device('OSVersion', 'ge', '6.0') ) || ( device('OSFamily', 'eq', 'Android') && device('OSVersion', 'ge', '4.0') ) )",
        "device.isTablet eq '1' && ( device.OSFamily eq 'iOS' || device.OSFamily eq 'Android' )" => "device('isTablet', 'eq', '1') && ( device('OSFamily', 'eq', 'iOS') || device('OSFamily', 'eq', 'Android') )",
        "device.isTouch eq '1'"          => "device('isTouch', 'eq', '1')",
        "i18n:be"                        => "i18n('be')",
        "i18n:en"                        => "i18n('en')",
        "i18n:kk"                        => "i18n('kk')",
        "i18n:ru"                        => "i18n('ru')",
        "i18n:tr"                        => "i18n('tr')",
        "i18n:tt"                        => "i18n('tt')",
        "i18n:uk"                        => "i18n('uk')",
        "internal"                       => "internal",
        "ipv6"                           => "ipv6",
        "mobile"                         => "mobile",
        "mobile == smart"                => "mobile == smart",
        "mobile == touch"                => "mobile == touch",
        "relev.Cpo>=35000"               => "relev('Cpo', '>=', 35000)",
        "relev.cm2>0.3"                  => "relev('cm2', '>', 0.3)",
        "relev.il==1"                    => "relev('il', '==', 1)",
        "relev.il==1 || relev.Cpo>35000" => "relev('il', '==', 1) || relev('Cpo', '>', 35000)",
        "relev.il==1 || relev.cpo>35000" => "relev('il', '==', 1) || relev('cpo', '>', 35000)",
        "relev.il==1 || relev.po>35000"  => "relev('il', '==', 1) || relev('po', '>', 35000)",
        "relev.po>=35000"                => "relev('po', '>=', 35000)",
        "relev.po>=35000 || relev.il==1" => "relev('po', '>=', 35000) || relev('il', '==', 1)",
        "report:www"                     => "report('www')",
        "report:www-touch"               => "report('www-touch')",
        "serp-version:1"                 => "serp_version('1')",
        "serp-version:2"                 => "serp_version('2')",
        "serp-version:3"                 => "serp_version('3')",
        "smart"                          => "smart",
        "snip.uil eq 'ru'"               => "snip('uil', 'eq', 'ru')",
        q{(flags.its_location eq "man")} => q{(flags('its_location', 'eq', 'man'))},
        "tablet"                         => "tablet",
        "tld:by"                         => "tld('by')",
        "tld:com"                        => "tld('com')",
        "tld:kz"                         => "tld('kz')",
        "tld:ru"                         => "tld('ru')",
        "tld:ua"                         => "tld('ua')",
        "touch"                          => "touch",
        "touch && ! ( ( device.BrowserName eq 'MobileSafari' && device.BrowserVersion ge '6.0' ) || ( device.BrowserName eq 'UCBrowser' && device.BrowserVersion ge '9.0' ) || ( device.BrowserName eq 'OperaMobile' && device.BrowserVersion ge '14.0' ) || ( device.BrowserName eq 'ChromeMobile' && device.BrowserVersion ge '17.0' ) || ( device.BrowserName eq 'Chromium' && device.BrowserVersion ge '17.0' ) || ( device.BrowserName eq 'YandexBrowser' ) )" => "touch && ! ( ( device('BrowserName', 'eq', 'MobileSafari') && device('BrowserVersion', 'ge', '6.0') ) || ( device('BrowserName', 'eq', 'UCBrowser') && device('BrowserVersion', 'ge', '9.0') ) || ( device('BrowserName', 'eq', 'OperaMobile') && device('BrowserVersion', 'ge', '14.0') ) || ( device('BrowserName', 'eq', 'ChromeMobile') && device('BrowserVersion', 'ge', '17.0') ) || ( device('BrowserName', 'eq', 'Chromium') && device('BrowserVersion', 'ge', '17.0') ) || ( device('BrowserName', 'eq', 'YandexBrowser') ) )"
    };
}

