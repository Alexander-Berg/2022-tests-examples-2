#!/usr/bin/perl


use Test::More;

use lib::abs qw( . ../scripts/ );
use common;
use strict;
use warnings;

#require 'widgets_job.pl';

use Jobs::search_catalog;
use MordaX::Utils;
use MordaX::Logit qw(dumpit);
use MordaX::Config;
$MordaX::Config::DevInstance = 1;


ok(1, ' i m online');

my $r = Jobs::search_catalog::get_rubrics();

ok( $r );
ok( is_hash( $r ), 'rubrics is hash' );

my $cr = Jobs::search_catalog::compile_rubrics( $r );

ok( is_hash( $cr ), 'rubrics compiled');

my $widget_tags = {
    32 => 1,
    6  => 1,
};

my $widget_rubrics = Jobs::search_catalog::detect_rubrics( $cr , $widget_tags );
ok( $widget_rubrics->{41}, 'Cars');
ok( $widget_rubrics->{42}, 'Cars news');
ok( $widget_rubrics->{77}, 'news about cars');

my $w_car_news = get(27491);
ok( $w_car_news );
ok( $w_car_news->tags()->[0] );
my $w_tags = Jobs::search_catalog::get_widget_hash_tags( $w_car_news);
ok( $w_tags );
ok( $w_tags->{32}, 'tag a1');
ok( $w_tags->{6},  'tag a1');
ok( $w_tags->{2}, 'tag news');

my $w_rubrics = Jobs::search_catalog::detect_rubrics( $cr , $w_tags );

#print Data::Dumper::Dumper( $w_rubrics );

my $w_rubrics2 = Jobs::search_catalog::widget_rubrics( $w_car_news, $cr );

#print Data::Dumper::Dumper( $w_rubrics2 );


subtest "distributed list" => sub {
    use_ok ('WBOX::Model::Widget');
    my $wc = WBOX::Model::Widget->new( { in_catalog => 1 , rating => 101, id => '1' } );
    my $wr = WBOX::Model::Widget->new( { in_catalog => 1 , in_regional  => 1, rating => 202, id => 2 } );

    ok( $wc );
    ok( $wr );
    ok( $wc->id() );
    is( $wr->id(), 2 );

    $wc->rating_multy( { all => {rating => 101 } , ru => { rating => 111 }, by => { rating => 121 } }); 
    $wr->rating_multy( { all => {rating => 202 } , ru => { rating => 212 }, by => { rating => 222 } }); 
    
    

    $wc->catflag( 'inside' );
    $wr->catflag( 'inside' );
    $wr->regflag( 'inside' );



    ok( $wc->in_catalog(), );
    ok( $wr->in_catalog(), );
    ok( $wr->in_regional() );

    is( $wc->get_rating() , 101 );
    is( $wr->get_rating( 'by' ) , 222 , 'by rating');


    #add to processed
    for my $w ( $wc, $wr ){
        $Jobs::search_catalog::processed_widgets->{ $w->id() } = $w;
        $w->set_languages ( { ru => 1, be => 1 });
        ok( $w->languages()->{ru} , 'RU lang ok');
        ok( $w->languages()->{be} , 'be lang ok');

    }
    is( $wc, Jobs::search_catalog::widget( $wc->id() ), 'widget works');


    my $list = Jobs::search_catalog::_language_distributed_list( [ [1 , 500 ], [2 , 500 ] ]);
    #dumpit( $list );    
    ok( $list );
    ok( $list->{be} , 'has By');
    ok( $list->{ru} , 'has RU');
    is( $list->{ru}->[0], 'C2', "C2");
    is( $list->{ru}->[2], 'C1', "C1");

    $list = Jobs::search_catalog::_language_distributed_list( [ [1 , 500 ], [2 , 500 ] ], 'catalog_bonus' => 1);
    is( $list->{ru}->[0], 'C1', "C1");
    is( $list->{ru}->[2], 'C2', "C2");
    is( $list->{ru}->[3], -19798, "C2 lowered rating" );


    #dumpit( $list );    

    $list = Jobs::search_catalog::_language_distributed_list( [ [1 , 500 ], [2 , 500 ] ], 'boost_const' => 1000, 'region' => 'by');
    is( $list->{ru}->[0], 'C2', "C2");
    is( $list->{ru}->[1], 1222 , "C2 by boosted rating" );
    is( $list->{ru}->[2], 'C1', "C1");
    is( $list->{ru}->[3], 1121, "C1 by boosted rating" );
    #dumpit( $list );    

    done_testing(); 
        
};

done_testing();

