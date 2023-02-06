#!/usr/bin/perl

use common::sense;
use Test::More;

use lib::abs qw(../lib ../scripts .);

require 'export_olymp.pl';

my $country_medal_json = load_json(lib::abs::path("./data/olymp_country_medals.json"));
ok($country_medal_json);
my $last_medal_json = load_json(lib::abs::path("./data/olymp_last_medals.json"));
ok($last_medal_json);

my $last_medals = export_olymp::v2_last_medals_from_json($last_medal_json);
ok($last_medals);

my $top_countries = export_olymp::v2_top_countries_from_json($country_medal_json);
ok($top_countries);

done_testing();

sub load_json {
    my $file = shift;
    my $json = shift;
    local $/ = undef;
    if (open(IN_JSON, $file)) {
        $json = <IN_JSON>;
    } else {
        logit('interr', "cannot open file:" . $json);
    }
}

