#!/usr/bin/perl

use lib::abs qw(. ../scripts);

use Test::More;
use common; # qw(read_data_file);
use strict;
use warnings;

use MordaX::Logit qw(logit dumpit);

use_ok('Jobs::st_loader');


# NEW
# FORMAT 1
ok( read_data_file('mr.clicks.2011-09-01.41090.txt') , 'read_data_file ok');

#HACK1

Jobs::st_loader::HACK_map_reduce_SET_raw_data( read_data_file('mr.clicks.2011-09-01.41090.txt') );
my $clicks_1 = Jobs::st_loader::clicks( '2011-09-01', format => 1 );
ok( $clicks_1 , ' format 1 ok');
ok( $clicks_1->{41090}, '41090 ok');
    test_in_click_data( $clicks_1->{41090} , ' new edge format 1');
    

my $clicks_2 = Jobs::st_loader::clicks( '2011-09-01', format => 2 );
ok( $clicks_2 , 'format 2 presents');
is( $clicks_2->{date}, '2011-09-01', 'date ok');
    test_in_click_data( $clicks_2->{clicks}->{41090}->{all} , ' ALL new edge format 2');

#HACK 2 almoust now days 

Jobs::st_loader::HACK_map_reduce_SET_raw_data( read_data_file('mr.clicks.2011-09-28.41090.txt') );
$clicks_2 = Jobs::st_loader::clicks( '2011-09-28', format => 2 );
    test_in_click_data( $clicks_2->{clicks}->{41090}->{all} , ' ALL new edge format 2');


#HACK 2 new regional clicks
Jobs::st_loader::HACK_map_reduce_SET_raw_data( read_data_file('mr.clicks.2.2011-09-12.40190.txt') );
$clicks_2 = Jobs::st_loader::clicks( '2011-09-12', format => 2 );
#dumpit( $clicks_2 );
test_in_click_data( $clicks_2->{clicks}->{41090}->{all} , 'ALL new edge format 2');
test_in_click_data( $clicks_2->{clicks}->{41090}->{ru} , 'RU new edge format 2');
test_in_click_data( $clicks_2->{clicks}->{41090}->{ua} , 'UA new edge format 2');

#HITS
Jobs::st_loader::HACK_map_reduce_SET_raw_data( read_data_file('mr.hits.v3.2011-09-28.41090.txt') );
my $hits_1 = Jobs::st_loader::hits('2011-09-28', format => 1 );
ok( $hits_1->{shows}->{41090}, ' old shows');
ok( $hits_1->{patterns}->{41090}, ' old patterns');
ok( $hits_1->{visitors}->{41090}, ' old visitors');
ok( $hits_1->{visitors}->{_mail}, ' old style mail visitors');

my $hits_2 = Jobs::st_loader::hits('2011-09-28', format => 2 );

is( $hits_2->{date}, '2011-09-28', 'date');
is( $hits_2->{range}, 'daily', 'daily');
test_in_hit_data( $hits_2->{hits}->{41090}->{all} , ' hist for all ');
test_in_hit_data( $hits_2->{hits}->{41090}->{kz} , ' hist for kz ');
ok( $hits_2->{mail_reference}, 'mail reference ok');


Jobs::st_loader::HACK_map_reduce_CLEAR_raw_data();

$hits_2 = Jobs::st_loader::hits('2011-09-19', format => 2, range => 'weekly' );
ok( $hits_2);
is( $hits_2->{range}, 'weekly', 'weekly responce');
test_in_hit_data( $hits_2->{hits}->{_mail}->{ua} , 'mail hits for ua ');
#ok( $hits_2->{hits}->{_mail}->{ua} , 'mail ok')




done_testing();


sub test_in_click_data {
    my $data = shift;
    my $name = shift;
    for my $type ( qw(all title anchors iset iset) ){
        ok( $data->{$type}, $type . ' clicks for :' . $name );
    }
    #dumpit( $data ) ;
}
sub test_in_hit_data {
    my $data = shift;
    my $name = shift;
    for my $type ( qw(visitors patterns shows) ){
        ok( $data->{$type}, $type . ' hits for ' . $name );
    }
}

