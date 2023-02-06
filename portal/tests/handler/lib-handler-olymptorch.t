#!/usr/bin/env perl

#use strict; use warnings;
use feature qw/say/;
#use Test::LectroTest trials => 100; 
use Test::LectroTest; 
use Test::LectroTest::Generator qw(:common :combinators);
 
#use Test::Most;
use JSON;

my $gen_digits = String( length=>[0,], charset=>"0-9" ); 

my $gen_digits_1_3 = String(length => [2, 2], charset => "1-7");
my $gen_digits_2_8 = String(length => [2, 8], charset => "0-9");
my $gen_pref       = Elements( "", "-" );
my $gen_ll         = Paste(
                        $gen_pref,
                        Paste($gen_digits_1_3,
                        $gen_digits_2_8,
                        glue => ".")
                    );
my $gen_zero = Int(range => [0, 0]);

#Property {
#    ##[ geoid <- $gen_digits ]##
#    exists lookup( $geoid )->{ok};
#}, name => "Ok 1" ;

#Property {
#    ##[ lat <- $gen_digits, lon <- $gen_digits ]##
#    lookup( undef, $lat, $lon )->{ok} == 0;
#}, name => "Ok 2" ;
#
Property {
    ##[ lat <- $gen_ll, lon <- $gen_ll ]##
    lookup( undef, $lat, $lon )->{ok} == 1;
}, name => "Ok 2" ;


my $CMD = <<END;
curl -s "https://www-v21d3.wdevx.yandex.ru/portal/olymptorch/add?geoid=%s&lat=%s&lon=%s" -k \
END

sub lookup {
    my ($geoid, $lat, $lon) = @_;
    (my $cmd = $CMD) =~ s/\n//g;
    $lat //= '';
    $lon //= '';
    $cmd = sprintf($cmd, $geoid, $lat, $lon);
    say $cmd;
    my $res = `$cmd`;
    $res = decode_json($res);
    return $res;
}

#done_testing;

