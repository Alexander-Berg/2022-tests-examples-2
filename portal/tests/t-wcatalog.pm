#!/usr/bin/perl

use lib::abs qw(../lib);
use Test::More;

#use_ok('InitBase');
#use_ok('InitUtils');
use_ok('Geo');
use_ok('MordaX::Block::CatalogCache');
MordaX::Logit::enable_dumpit();

subtest "Geobase" => sub {
    ok(Geo::geo(213, 'name'), 'Moscow has name');
    done_testing();
};

subtest "GeoHash Moscow 213" => sub {
    my $h = MordaX::Block::CatalogCache::get_wcatalog_geo_hash(213);

    is($h->{city},     undef,);
    is($h->{district}, undef,);
    is($h->{country},  undef);
    done_testing();
};

=x Vnukovo and Troits - Поселение городского типа, и поэтому мы его игнорирую
subtest "GeoHash SubMoscow Vnukovo 10720" => sub {
    my $h = MordaX::Block::CatalogCache::get_wcatalog_geo_hash( 10720 );

    is( $h->{city},         undef,  );
    is( $h->{subcity},      11720,  );

    is( $h->{district},     1,      );
    is( $h->{country},      undef   );
    done_testing();
};
=cut

subtest "GeoHash SubMoscow Moscoswkiy 103817" => sub {
    my $h = MordaX::Block::CatalogCache::get_wcatalog_geo_hash(103817);

    is($h->{city},    undef,);
    is($h->{subcity}, 103817,);

    is($h->{district}, 1,);
    is($h->{country},  undef);
    done_testing();
};
subtest "GeoHash SubMoscow Moskow Region" => sub {
    my $h = MordaX::Block::CatalogCache::get_wcatalog_geo_hash(37120);

    is($h->{city},    37120,);
    is($h->{subcity}, undef,);

    is($h->{district}, 1,);
    is($h->{country},  undef);
    done_testing();
};

subtest "GeoHash SPB" => sub {
    my $h = MordaX::Block::CatalogCache::get_wcatalog_geo_hash(2);
    is($h->{city},    2,);
    is($h->{subcity}, undef,);

    is($h->{district}, undef,);
    is($h->{country},  225);
};
subtest "GeoHash Petergof(SPB subcity)" => sub {
    my $h = MordaX::Block::CatalogCache::get_wcatalog_geo_hash(98546);
    is($h->{city},    2,);
    is($h->{subcity}, 98546,);

    is($h->{district}, undef,);
    is($h->{country},  225);
};
subtest "GeoHash Viborg" => sub {
    my $h = MordaX::Block::CatalogCache::get_wcatalog_geo_hash(969);
    is($h->{city},    969,);
    is($h->{subcity}, undef,);

    is($h->{district}, 10174,);
    is($h->{country},  225);
};

done_testing();
