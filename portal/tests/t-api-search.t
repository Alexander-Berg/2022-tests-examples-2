#!/usr/bin/perl

use Test::More;
use utf8;
use common::sense;
use lib::abs qw( . ../lib );
use 5.010;

binmode(STDERR,':utf8');

#use_ok('InitBase');
use MP::Logit qw(dmp);
use MP::Utils qw(is_hash);
use Test::Deep;

use MP::UserAgent;
use URI;


require_ok(lib::abs::path('../tools/instance'));
my $inst = instance();
my $ua   = MP::UserAgent->new();


my $host    = "www-$inst.wdevx.yandex.ru";

subtest "country" => sub {
    my $spb = get('geo' => 2 , 'country' => 'by', lang => 'ru' );
    like( $spb->{block}->[0]->{data}->{geo}->{name}, qr/Санкт-Петербург/, "SPB");


    my $minsk = get('country' => 'by' ); 

    like( $minsk->{block}->[0]->{data}->{geo}->{name}, qr/Минск/, "Minsk for By");
 
    done_testing();
};



sub get {
    my %query = @_;
    my $URI = URI->new('http://' . $host ."/portal/api/search/1/");
    $URI->query_form( %query );

    dmp( $URI->as_string() );

    my $request = $ua->get($URI->as_string);
    if ($request->is_success()) {
        my $data = MP::Utils::parse_json($request->content());
        return $data;
    }
}
done_testing(); 
