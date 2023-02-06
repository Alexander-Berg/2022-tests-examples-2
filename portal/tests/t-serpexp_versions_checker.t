#!/usr/bin/perl
use Data::Dumper;
use Test::Most;
use lib::abs qw( . ../lib);
use rules;
#die_on_fail();

use MordaX::Experiment::SERPCond;

sub device {
    return MordaX::Experiment::SERPCond::device(@_);
}

$MordaX::Experiment::SERPCond::Req->{BrowserDesc}{'BrowserVersion'} = "1.0";
ok !device('BrowserVersion', 'eq', "2");
ok device('BrowserVersion', 'lt', "2");
ok !device('BrowserVersion', 'gt', "2");
ok device('BrowserVersion', 'le', "2");
ok !device('BrowserVersion', 'ge', "2");
ok device('BrowserVersion', 'ne', "2");

$MordaX::Experiment::SERPCond::Req->{BrowserDesc}{'BrowserVersion'} = "2.0";
ok !device('BrowserVersion', 'eq', "10");
ok device('BrowserVersion', 'lt', "10");
ok !device('BrowserVersion', 'gt', "10");
ok device('BrowserVersion', 'le', "10");
ok !device('BrowserVersion', 'ge', "10");
ok device('BrowserVersion', 'ne', "10");

$MordaX::Experiment::SERPCond::Req->{BrowserDesc}{'BrowserVersion'} = "10.0";
ok device('BrowserVersion', 'eq', "10");
ok !device('BrowserVersion', 'lt', "10");
ok !device('BrowserVersion', 'gt', "10");
ok device('BrowserVersion', 'le', "10");
ok device('BrowserVersion', 'ge', "10");
ok !device('BrowserVersion', 'ne', "10");

$MordaX::Experiment::SERPCond::Req->{BrowserDesc}{'BrowserVersion'} = "15.2";
ok !device('BrowserVersion', 'eq', "14.9");
ok !device('BrowserVersion', 'lt', "14.9");
ok device('BrowserVersion', 'gt', "14.9");
ok !device('BrowserVersion', 'le', "14.9");
ok device('BrowserVersion', 'ge', "14.9");
ok device('BrowserVersion', 'ne', "14.9");

my $device = {
    "BrowserEngine"        => "Trident",     #+
    "BrowserEngineVersion" => "4.0",         #+
    "BrowserName"          => "MSIE",
    "OSFamily"             => "Windows",
    "OSName"               => "Windows 7",
    "OSVersion"            => "6.1",
    "isBrowser"            => 1,
    "isMobile"             => 0,
    "localStorageSupport"  => 1,
    "postMessageSupport"   => 1,
};

$MordaX::Experiment::SERPCond::Req->{BrowserDesc} = $device;
ok device('BrowserEngine', 'eq', "Trident");
ok !device('BrowserEngine', 'ne', "Trident");
ok !device('BrowserEngine', 'eq', "Gecko");
ok device('BrowserEngine', 'ne', "Gecko");

ok device('BrowserEngineVersion', 'eq', "4");
ok device('BrowserEngineVersion', 'lt', "5");
ok !device('BrowserEngineVersion', 'gt', "5");
ok device('BrowserEngineVersion', 'le', "8.0");
ok device('BrowserEngineVersion', 'ge', "3.5.2");
ok device('BrowserEngineVersion', 'ne', "14.9");

ok device('BrowserName', 'eq', "MSIE");
ok !device('BrowserName', 'ne', "MSIE");
ok !device('BrowserName', 'eq', "Opera");
ok device('BrowserName', 'ne', "Opera");

ok device('OSName', 'eq', "Windows 7");
ok !device('OSName', 'ne', "Windows 7");
ok !device('OSName', 'eq', "Linux");
ok device('OSName', 'ne', "Linux");

ok device('OSVersion', 'eq', "6.1");
ok !device('OSVersion', 'eq', "6");
ok !device('OSVersion', 'eq', "6.3");
ok !device('OSVersion', 'lt', "6.1");
ok !device('OSVersion', 'gt', "10.0");
ok device('OSVersion', 'le', "8.0");
ok device('OSVersion', 'ge', "3.5.2");
ok device('OSVersion', 'ne', "14.9");
done_testing();
