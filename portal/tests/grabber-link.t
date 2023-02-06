#!/usr/bin/perl

use 5.010;
use common::sense;
use Test::More;
use lib::abs qw(../lib);
use lib "/opt/www/morda/lib/";
use MordaX::Logit qw(dmp);

use_ok(qw/Grabber/);
my $g = Grabber->new(

    #url     => '',
    #content => '',
    file    => lib::abs::path("data/WP301?PT001F01=701"),
    encoding=> 'cp1251',
);


ok( $g , "$g object okey");

is( $g->grab_table( 
    #file    => lib::abs::path("data/WP301?PT001F01=701"),
    nodes => "/html/body/table[5]/tbody/tr/td[1]/b/a",
    #find => {
    #    'link' => '@href'
    #}
), undef, "Grab table don't work with out _row" );



my $l = LinkGrabber->new(
    encoding => 'cp1251',
    type => 'file',
    path => lib::abs::path("data/"),
    pages => {
        main    => {
            reg_points => '/html/body/table[5]/tbody/tr/td[1]/b/a/@href',
        },
        reg_points    => {
            reg_results => '/html/body/table[4]/tbody/tr/td[2]/a/@href',
        }
    },
    urls => {
        main => {map { "/".$_ => 1 } qw/WP301?PT001F01=701 wp301?PT001F01=700/ },
    },

);

$l->grab();
ok( keys %{ $l->links('reg_results') } , "Reg Results links Presents!"); 


subtest "LinkCoversion" => sub {
    my $c = \&LinkGrabber::make_link;
    is ( &$c( "http://yandex.ru" , "http://ya.ru" ), 'http://yandex.ru' );

    is ( &$c( "common" , "http://ya.ru" ), 'http://ya.ru/common' );
    is ( &$c( "common" , "http://ya.ru/xx" ), 'http://ya.ru/common' );
    is ( &$c( "common" , "http://ya.ru/xx/" ), 'http://ya.ru/xx/common' );
    is ( &$c( "common" , "http://ya.ru/xx" ), 'http://ya.ru/common' );
    is ( &$c( "/co" , "http://ya.ru/xx" ), 'http://ya.ru/co' );

    is ( &$c( "?xxx" , "http://ya.ru/xx?yyy" ), 'http://ya.ru/xx?xxx' );
    is ( &$c( "#zzz" , "http://ya.ru/xx?yyy" ), 'http://ya.ru/xx?yyy#zzz' );


    is ( &$c( "co" , "/xx" ), '/co' );
    is ( &$c( "co" , "/xx/xx" ), '/xx/co' );
    is ( &$c( "?yyy" , "/xx/xx" ), '/xx/xx?yyy' );
    is ( &$c( "#zzz" , "/xx/xx" ), '/xx/xx#zzz' );
    done_testing ();
};

for my $res_url ( keys %{ $l->links('reg_results') } ){
    my $gr = Grabber->new(
        type        => 'file',
        encoding   => 'cp1251',
        file        => lib::abs::path( "data$res_url" ), #FIXME
    );

    ok($gr, "Graaber over $res_url");

    my $region = $gr->grab(
        region => '/html/body/table[4]/tbody/tr[1]/td[2]/b',
        prc    => '/html/body/table[4]/tbody/tr[3]/td[2]/b',
        n      => '/html/body/table[4]/tbody/tr[4]/td[2]/b',
        _first => 1,
    );
    ok( $region->{region} );
    ok( $region->{n} );
    ok( $region->{prc} );

    my $candidates = $gr->grab(
        name => '/html/body/table[5]/tbody/tr/td[1]/b/a',
    );
    ok( $candidates->{name}->[5] , "6th candidate presetnts");


    my $data = $gr->grab_table(
        _row => '/html/body/table[5]/tbody/tr',
        name => 'td[1]/b/a',
        prc  => 'td[3]',
        n    => 'td[4]',
    );
    ok( $data->[4] );
    ok( $data->[2]->{name} );
    ok( $data->[3]->{prc} );
    done_testing();
};


subtest "Production UA Grabber" =>sub {
    my $l2 = LinkGrabber->new(
        encoding => 'cp1251',
        pages => {
            main    => {
                reg_points => '/html/body/table[5]/tbody/tr/td[1]/b/a/@href',
            },
            reg_points    => {
                reg_results => '/html/body/table[4]/tbody/tr/td[2]/a/@href',
            }
        },
        urls => {
            main => {
                q{http://www.cvk.gov.ua/pls/vp2010/wp301?PT001F01=700} => 1,
            }
        },
    );
    $l2->grab();

    my $reg_links = [keys %{ $l2->links('reg_results') } ];
    ok($reg_links->[0] );;

    my $data = [];
    for my $link ( @$reg_links ){
        my $g = Grabber->new(
            content => $l2->get_content( $link ),
        );
        my $region = $g->grab(
            region => '/html/body/table[4]/tbody/tr[1]/td[2]/b',
            prc    => '/html/body/table[4]/tbody/tr[3]/td[2]/b',
            n      => '/html/body/table[4]/tbody/tr[4]/td[2]/b',
            _first => 1,
        );
        my $candidates = $g->grab_table(
            _row => '/html/body/table[5]/tbody/tr',
            name => 'td[1]/b/a',
            prc  => 'td[3]',
            n    => 'td[4]',
        );
        push @$data, {region => $region , candidates => $candidates}
    }

    for my $r ( @$data ){
        say "$r->{region}->{region}, $r->{region}->{prc}%";
        for( my $i =1; $i< 3 ; $i++){
            my $c = $r->{candidates}->[$i];
            say "  > $c->{name} $c->{prc}\%";
        }
    }
    done_testing();

};



done_testing();
