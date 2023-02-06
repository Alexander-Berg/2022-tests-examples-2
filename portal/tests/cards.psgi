#!/usr/bin/perl

#
use common::sense;
use strict;
use warnings;
#no utf8;
use Time::HiRes qw( usleep );
use JSON::XS;
#
sub resp {
    my ( $code, $ref ) = @_;

    return [ 
        $code,
        [ 'Content-Type' => 'text/plain' ], 
        [ JSON::XS->new->utf8->encode( $ref || {error => 'nodata'} ) ],
    ];
}
my $app = sub {
    my $env = shift;
    my $msleep = 0;
    my $uri = $env->{REQUEST_URI};
    my $q   = $env->{QUERY_STRING};
    my $card_id;
    my $user_id;

    if( $q=~/getCardsByUid\//){
         return resp(200, {
            cards => [ {
                    view_count => 1,
                    text  => 'приывет',
                    card_id => 1,
                }, 
                {
                    view_count => 3,
                    text  => 'hi hi hi!',
                    card_id => 2,
                },
                { 'send_id' => 111, 'card_id' =>  0, 'text'=>  'Congratulations!', 'view_count'=> 2, 'from_email'=> 'mabubuka@yandex.ru' },
            ]
        });
    }
    if( $q=~/getCardByHash\//){
         return resp(200, {
            cards => [ 
                  { 'send_id' => 111, 'card_id' =>  0, 'text'=>  'Congratulations!', 'view_count'=> 2, 'from_email'=> 'mabubuka@yandex.ru'}
            ]
        });
    }

   if( $q=~/sendCard\//) {
       return resp(200, {'result' => 'ok'} );
   } 
   if( $q=~/markCardAsRead/ ) {
       return resp(200, {'result' => 'ok'} );
   }
   
   if( $q=~/viewCountIncrement\//){
       return resp(200, {'result' => 'ok'} );
   }

    
    return resp(404, {error => 'uri not parsed:'. $uri . '+' . $q ,} ); 
}

