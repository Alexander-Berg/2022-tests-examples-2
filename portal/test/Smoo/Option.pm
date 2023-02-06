package Test::Smoo::Option;
use parent 'Test::Class';

use utf8;
use strict;
use warnings;

use Test::Most;
use Smoo::Option;

my $dbh;
sub start : Test(startup) {
    $dbh = Smoo::DB2::instance();
    $dbh->begin_work();
}

sub refresh : Test(setup) {
    _init_db();
}

sub _init_db {
    $dbh->do('DELETE FROM options');
    my $res;

    $res = $dbh->do(
        "INSERT INTO options SET name=?, value=?, description=?, enabled=?",
        undef,
        21, 'val21', 0, 0
    );
    $res = $dbh->do(
        "INSERT INTO options SET name=?, value=?, description=?, enabled=?",
        undef,
        25, 'val25', 0, 1
    );
    $res = $dbh->do(
        "INSERT INTO options SET name=?, value=?, description=?, enabled=?",
        undef,
        23, 'val23', 0, 0
    );
}

sub end : Test(shutdown) {
    $dbh->rollback();
}

sub list : Tests() {
    Smoo::Option::save(
        [
            [21, 31, 41, 0],
            [25, 32, 42, 1],
            [23, 33, 43, 0],
        ]
    );
    my $got      = Smoo::Option::list();
    my $expected = {
        ok  => 1,
        res => [
            [21, 31, 41, 0],
            [23, 33, 43, 0],
            [25, 32, 42, 1],
          ]
    };

    is_deeply($got, $expected) or explain { got => $got, expected => $expected };
}

sub load : Tests() {
    my $got      = Smoo::Option::_load();
    my $expected = {
        25 => 'val25',
    };
    is_deeply($got, $expected) or explain { got => $got, expected => $expected };
}

sub get_non_exists : Tests() {
    my $got      = Smoo::Option::get('23');
    my $expected = undef;
    is($got, $expected);
}

sub get_exists : Tests() {
    my $got      = Smoo::Option::get('25');
    my $expected = 'val25';
    is($got, $expected);
}

sub update_cache : Tests() {
    my $got      = Smoo::Option::get('25');
    my $expected = 'val25';
    is($got, $expected);

    $Smoo::Option::CACHE_TTL_SECONDS = 2;
    Smoo::Option::save(
        [
            [25, 'val26', 0, 1],
        ]
    );

    sleep 1;
    $got      = Smoo::Option::get('25');
    $expected = 'val25';
    is($got, $expected);

    sleep 2;
    $got      = Smoo::Option::get('25');
    $expected = 'val26';
    is($got, $expected);
}

1;
