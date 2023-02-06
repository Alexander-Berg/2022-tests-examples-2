#!/usr/bin/perl

use 5.010;
use common::sense;
use Test::More;
use lib::abs qw(../lib);
use lib "/opt/www/morda/lib/";
use MordaX::Logit qw(dmp);

use XML::XPathEngine;
$XML::XPathEngine::DEBUG = 0;

use_ok(qw/Grabber/);
my $g = Grabber->new(

    #url     => '',
    #content => '',
    file    => lib::abs::path("./data/bash_old.main.html"),
    encoding=> 'cp1251',
);

my $start = $g->{x}->{_body};
sub prn_tags {
    my ( $tag , $i )=@_;
    next unless ref($tag);
    $i //=0;
    print "  "x$i . $tag->{_tag} ."\n";
    for my $item ( $tag->content_list() ){
        prn_tags($item, $i+1 );
    }

}
prn_tags( $start );
#dmp( $g->{x}->{_body} );


#dmp($g->{x}->findnodes('/html/body/table[4]/tr[3]/td')->[0]->content() );

#exit (1);

my $l = LinkGrabber->new(
    encoding => 'cp1251',
    type => 'file',
    path => lib::abs::path("data/"),
    pages => {
        main    => {
            #pre_results => '/html//tr[12]/td/nobr/a/@href',
            pre_results     => '/html//tr[12]/td/nobr/a/@href',
            fin_results     => 
            [
                '/html//tr[14]/td/nobr/a/@href' ,
                '/html//tr[11]/td/nobr/a/@href',
            ],
            #any         => '/html/body/table[4]/tr[3]/td/table[3]/tbody/tr',
            #any         => '/html/body/table[4]/tr[3]/td',
            #'first'     => '/html/body/table[6]/tbody/tr[3]/td/table[3]/tbody/tr[3]/td/nobr/a/@href',
            #'first14'    => '/html/body//tr[14]/td/nobr/a/@href',
            #'first15'    => '/html/body//tr[15]/td/nobr/a/@href',
        },
    },
    urls => {
        main => {map { "/".$_ => 1 } (
                #"bash_old.main.html",
            "msk_old.main.html",
        )},
    },

);
$l->grab();
ok( keys %{ $l->links('fin_results') } , "Results links Presents!"); 

done_testing();


