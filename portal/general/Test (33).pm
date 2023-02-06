package MordaX::Block::Assist::Helper::Weather::Test;

use rules;

use Test::Most;
use base qw(Test::Class);

use MP::Logit qw(logit dmp);

use MordaX::Block::Assist::Helper::Weather;


sub testget_weather_informer_type_319 : Test(4) {
    my $self = shift;
    *test_func = \&MordaX::Block::Assist::Helper::Weather::get_weather_informer_type;

    no warnings qw(redefine experimental::smartmatch);
    my $req = {
        Getargshash => {
            dp => 3.39,
        },
        UserDevice => {
            screenx => 1080,
        },
    };
    # informer_width = 1080 / 3.39 = 318.6

    ok(test_func($req, 5) eq MordaX::Block::Assist::Helper::Weather::WEATHER_TINY);
    ok(test_func($req, 15) eq MordaX::Block::Assist::Helper::Weather::WEATHER_TINY);
    ok(test_func($req, -5) eq MordaX::Block::Assist::Helper::Weather::WEATHER_TINY);
    ok(test_func($req, -15) eq MordaX::Block::Assist::Helper::Weather::WEATHER_NONE);
}

sub testget_weather_informer_type_339 : Test(4) {
    my $self = shift;
    *test_func = \&MordaX::Block::Assist::Helper::Weather::get_weather_informer_type;

    no warnings qw(redefine experimental::smartmatch);
    my $req = {
        Getargshash => {
            dp => 3.19,
        },
        UserDevice => {
            screenx => 1080,
        },
    };
    # informer_width = 1080 / 3.19 = 338.6

    ok(test_func($req, 5) eq MordaX::Block::Assist::Helper::Weather::WEATHER_TINY);
    ok(test_func($req, 15) eq MordaX::Block::Assist::Helper::Weather::WEATHER_TINY);
    ok(test_func($req, -5) eq MordaX::Block::Assist::Helper::Weather::WEATHER_TINY);
    ok(test_func($req, -15) eq MordaX::Block::Assist::Helper::Weather::WEATHER_TINY);
}

sub testget_weather_informer_type_359 : Test(4) {
    my $self = shift;
    *test_func = \&MordaX::Block::Assist::Helper::Weather::get_weather_informer_type;

    no warnings qw(redefine experimental::smartmatch);
    my $req = {
        Getargshash => {
            dp => 3.01,
        },
        UserDevice => {
            screenx => 1080,
        },
    };
    # informer_width = 1080 / 3.01 = 358.8

    ok(test_func($req, 5) eq MordaX::Block::Assist::Helper::Weather::WEATHER_SMALL);
    ok(test_func($req, 15) eq MordaX::Block::Assist::Helper::Weather::WEATHER_SMALL);
    ok(test_func($req, -5) eq MordaX::Block::Assist::Helper::Weather::WEATHER_SMALL);
    ok(test_func($req, -15) eq MordaX::Block::Assist::Helper::Weather::WEATHER_TINY);
}

sub testget_weather_informer_type_393 : Test(4) {
    my $self = shift;
    *test_func = \&MordaX::Block::Assist::Helper::Weather::get_weather_informer_type;

    no warnings qw(redefine experimental::smartmatch);
    my $req = {
        Getargshash => {
            dp => 2.75,
        },
        UserDevice => {
            screenx => 1080,
        },
    };
    # informer_width = 1080 / 2.75 = 392.7

    ok(test_func($req, 5) eq MordaX::Block::Assist::Helper::Weather::WEATHER_REGULAR);
    ok(test_func($req, 15) eq MordaX::Block::Assist::Helper::Weather::WEATHER_REGULAR);
    ok(test_func($req, -5) eq MordaX::Block::Assist::Helper::Weather::WEATHER_REGULAR);
    ok(test_func($req, -15) eq MordaX::Block::Assist::Helper::Weather::WEATHER_SMALL);
}

sub testget_weather_informer_type_400 : Test(4) {
    my $self = shift;
    *test_func = \&MordaX::Block::Assist::Helper::Weather::get_weather_informer_type;

    no warnings qw(redefine experimental::smartmatch);
    my $req = {
        Getargshash => {
            dp => 2.7,
        },
        UserDevice => {
            screenx => 1080,
        },
    };
    # informer_width = 1080 / 2.7 = 400

    ok(test_func($req, 5) eq MordaX::Block::Assist::Helper::Weather::WEATHER_REGULAR);
    ok(test_func($req, 15) eq MordaX::Block::Assist::Helper::Weather::WEATHER_REGULAR);
    ok(test_func($req, -5) eq MordaX::Block::Assist::Helper::Weather::WEATHER_REGULAR);
    ok(test_func($req, -15) eq MordaX::Block::Assist::Helper::Weather::WEATHER_REGULAR);
}

1;
