#!/usr/bin/env perl
use strict;
use warnings;

use lib::abs qw(../lib/ ../wbox/lib ../wdgt/lib);
use Data::Dumper;
use Test::Most qw(no_plan);
die_on_fail();
use langdetect;
use MordaX::FcgiRequest;
use MordaX::National;

use MordaX::LangDetect;

require '/opt/www/bases/geobase.pm';

ok(!MordaX::LangDetect::detect(), 'detect no params');

ok(keys %geobase::Region, 'geosize ' . scalar keys(%geobase::Region));

#выполняться будет до утра
# ok(open(my $alh, '<', lib::abs::path('') . '/bases/accept-language.txt'), 'open data');
# foreach my $accept_language (<$alh>) {
    # chomp $accept_language;
    # foreach my $hostname (qw(yandex.ru yandex.ua yandex.kz yandex.by)) {
        # foreach my $geo (sort keys %geobase::Region) {
            # foreach my $cookie (sort values %MordaX::National::LangCookieValues) {
                # my $req = {};
                # $req->{'SetupHash'}->{'39'}->[1] = $cookie;
                # $req->{'GeoByDomainIp'}          = $geo;
                # $req->{'MordaContent'}           = 'big';
                # my $r = MordaX::FcgiRequest->new();
                # $r->{'_HEADERS'}->header('Accept-Language' => $accept_language);
                # my %args = (
                    # 'request'         => $r,
                    # 'Accept-Language' => $accept_language,
                    # 'hostname'        => $hostname,
                    # 'default'         => 'ru',
                # );
                # my ($xs_detect) = MordaX::LangDetect::detect($req, %args);
                # ok($xs_detect, "xs $xs_detect = $accept_language : $hostname : $geo : $cookie");
            # }
        # }
    # }
# }
# close $alh;
