#!/usr/bin/perl

use utf8;
use 5.010;
use common::sense;
use Test::More;
use lib::abs qw(../lib);
use lib "/opt/www/morda/lib/";
use MordaX::Logit qw(logit dmp);

use XML::XPathEngine;
$XML::XPathEngine::DEBUG = 0;



my $url = "http://www.vybory.izbirkom.ru/region/izbirkom?action=show&vrn=27720001539308&region=77&prver=0&pronetvd=null";

use Grabber;

my $l = LinkGrabber->new(
    encoding => 'cp1251',
    pages => {
        main    => {
            'c' => '/html//tr[3]/td/table[3]/tbody/tr[3]/td/nobr/a/@href',
        },
        'c'  => {
            'c' => '/html/body/table[4]//tr[4]/td/table[4]//tr[3]/td/a/@href'
        }
    },
    urls => {
        main => {
             $url => 1, 
        },
    },

);
$l->grab();
my $urls = $l->links('c');
my $c_all ={};

for my $url ( keys %$urls ){
    my $content = $l->get_content( $url );
    my $g = Grabber->new( content => $content);

    my $d = $g->grab_table(
         _row    => ".//*[\@id='test']/tr",
        id    => 'td[1]',
        name  => 'td[2]',
        group => 'td[4]',
        n     => 'td[5]',
        reg   => 'td[7]',
    );

    #dmp($d);
    for my $c ( @$d ){
        #say $c->{reg};
        next if $c->{reg} ne 'зарегистрирован';
        $c_all->{ $c->{id} } = $c;
        for( values %$c ){
            s/^\s*(.*?)\s*$/$1/;
        }
    }
    # last;

}


use Text::CSV;
use Encode;
my $csv = Text::CSV->new ( { 
        binary => 1 ,
        sep_char            => ';',
        always_quote        => 0,
        quote_space         => 1,
        quote_null          => 1,  
    } );
 $csv->eol ("\r\n");

for( sort { $a->{n} <=> $b->{n} } values %$c_all ){
    $csv->print (*STDOUT, [ map { Encode::encode( 'cp1251', $_); } ($_->{id}, $_->{n}, $_->{name}, $_->{group}) ]);
}


