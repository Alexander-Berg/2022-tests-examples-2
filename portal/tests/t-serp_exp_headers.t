#!/usr/bin/perl
use strict;
use Test::Most;
use Test::More;

use MIME::Base64;
use lib::abs qw(../lib);
use MordaX::Experiment::SERPCond;
use MordaX::Req;
die_on_fail;

use_ok('LWP::UserAgent');

my $ua = LWP::UserAgent->new;
#$ua->add_handler("request_send",  sub { shift->dump; return });

$ua->timeout(10);
$ua->ssl_opts(verify_hostname => 0, SSL_verify_mode => 0x00);

$ua->default_header('X-Yandex-ExpConfigVersion' => '3616');
$ua->default_header('X-Yandex-ExpBoxes'         => '9191,0,41;12391,0,53;9791,0,17;11461,0,97;11747,0,58');
$ua->default_header('X-Yandex-ExpFlags'         => '');

require(lib::abs::path('../tools/instance'));
my $inst = instance();

my $response = $ua->get("https://www-$inst.wdevx.yandex.ru/?forcecounters=1");
if ($response->is_success) {
    ok $response->decoded_content;
}
else {
    die $response->status_line;
}
my $req = MordaX::Req->new();
# no data
my $res = MordaX::Experiment::SERPCond::_parse_flags_raw($req, {string => undef});
ok !$res;

# no base, no json, warning
$res = MordaX::Experiment::SERPCond::_parse_flags_raw($req, {string => '123'});
ok !$res;

# not json; warning
$res = MordaX::Experiment::SERPCond::_parse_flags_raw($req, {string => encode_base64('123')});
ok !$res;

# not array, no warning
$res = MordaX::Experiment::SERPCond::_parse_flags_raw($req, {string => encode_base64('{"HANDLER": "REPORT", "CONTEXT": {"REPORT": {"flags": ["experimental_geobase=1:control"], "testid": ["11111"]}}}')});
ok !$res;

# no HASH, no warning
$res = MordaX::Experiment::SERPCond::_parse_flags_raw($req, {string => encode_base64('["HANDLER", "REPORT"]')});
ok !$res;

# no CONTEXT, skip
$res = MordaX::Experiment::SERPCond::_parse_flags_raw($req, {string => encode_base64('[{"HANDLER": "REPORT", "CONDITION": "desktop"}]')});
ok !$res;

# no REPORT, skip
$res = MordaX::Experiment::SERPCond::_parse_flags_raw($req, {string => encode_base64('[{"HANDLER": "REPORT", "CONDITION": "desktop", "CONTEXT": {"MAIN": {}}}]')});
ok !$res;

# no flags, skip
$res = MordaX::Experiment::SERPCond::_parse_flags_raw($req, {string => encode_base64('[{"HANDLER": "REPORT", "CONDITION": "desktop", "CONTEXT": {"REPORT": {"testid": ["13977"]}, "MAIN": {}}}]')});
ok !$res;

# no testid, skip
$res = MordaX::Experiment::SERPCond::_parse_flags_raw($req, {string => encode_base64('[{"HANDLER": "REPORT", "CONDITION": "desktop", "CONTEXT": {"REPORT": {"flags": ["yxnews_all_rubrics_rank_extra=exp4"]}, "MAIN": {}}}]')});
ok !$res;

# flags are not array, skip
$res = MordaX::Experiment::SERPCond::_parse_flags_raw($req, {string => encode_base64('[{"HANDLER": "REPORT", "CONDITION": "desktop", "CONTEXT": {"REPORT": {"flags": "yxnews_all_rubrics_rank_extra=exp4", "testid": "13977"}, "MAIN": {}}}]')});
ok !$res;

#OK
$res = MordaX::Experiment::SERPCond::_parse_flags_raw($req, {string => encode_base64('[{"HANDLER": "MORDA", "CONDITION": "desktop", "CONTEXT": {"MORDA": {"flags": ["yxnews_all_rubrics_rank_extra=exp4"], "testid": ["13977"]}, "MAIN": {}}}]')});
my $must = {
    13977 => {
        'yxnews_all_rubrics_rank_extra' => 'exp4',
      }
};
is_deeply $res, $must;

done_testing();

