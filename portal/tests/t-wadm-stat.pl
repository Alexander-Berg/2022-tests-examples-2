#!/usr/bin/perl
use strict;
use Test::More;
use lib::abs qw( . ../lib ../wadm/scripts);
use Data::Dumper;

use_ok('Jobs::st');
my $date  = '2015-02-10';
my $qdate = Jobs::st::convert_date($date);
is($qdate, '10.02.2015', 'Date OK');

my $query = "Morda/Totals/Geography?type=csv&max_distance=3&date_max=$qdate&date_min=$qdate";

my $browser = Jobs::st::get_browser();
ok($browser, 'Browser OK');
#$browser->add_handler("request_send",  sub { shift->dump; return });

$browser->default_header('Host' => 'stat-beta.yandex-team.ru');

my $response = $browser->get("https://213.180.205.33/" . $query . "&t=2");
ok($response->is_success, 'Response Auth OK');

my $body = $response->content;
ok($body, 'Body with Auth OK');

sub data {
    my $body = shift;
    $body =~ s/\r//gm;
    my @lines = split(/\n/, $body);
    @lines = splice(@lines, 0, 3);
    foreach my $line (@lines) {
        chomp($line);
        my @d = map { s/^"//; s/"$//; $_ } split(/;/, $line);
        print Encode::decode('cp1251', $d[0]);
    }
}
done_testing();

