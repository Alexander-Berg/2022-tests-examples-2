#!/usr/bin/perl

use common::sense;
use Test::More;
use lib::abs qw(../lib);
use MP::Utils;
use MP::Logit qw(dmp);

use MordaX::Data_get;

use Benchmark qw(:all);

use_ok("MordaX::Req");
use_ok("MordaX::Input");
use_ok("MordaX::Block::Stream");

use MordaX::Cache;


MordaX::Block::Stream::init_once();
MordaX::Data_load::load_static_exports(
    'options',
    MordaX::Block::Stream::static_exports()
);
MordaX::Block::Stream::init_data();

*MordaX::Experiment::Filter::filter = sub { 1 };
*MordaX::Block::Stream::is_stream_allowed_for_user_region = sub { 1 };

sub r(){
    my $req= MordaX::Req->new();
    $req->{Domain} = 'yandex.ru';
    $req->{MordaZone} = 'ru';
    $req->{Locale} = $req->{Language_lc} = 'ru';
    $req->{MordaContent}  = 'big';
    $req->{GeoByDomainIp} = 213;
    MordaX::Input::input_geoinfo( undef, $req, {geo => 213 } );
    $req;
}

my $req = r();
ok( $req );
my $wl = MordaX::Block::Stream::get_stream_whitelist_channels( $req );
ok( $wl->[0] , 'WHITE');


my $online = MordaX::Block::Stream::get_online_channels_cached( $req );
ok( MP::Utils::is_hash_size( $online), "Some online");

timethese( 1000, {
    nomemd => sub {
        my $req = r();
        MordaX::Block::Stream::get_any_channels( $req );
    },
    memd => sub {
        MordaX::Cache->cleanup();
        my $req = r();
        MordaX::Block::Stream::get_any_channels( $req );
    },
    memd_cached => sub {
        MordaX::Cache->cleanup();
        my $req = r();
        MordaX::Block::Stream::get_any_channels( $req , {big =>1 });
    },

});


done_testing();
