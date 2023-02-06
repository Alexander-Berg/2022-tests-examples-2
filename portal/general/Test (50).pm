package MordaX::Block::Weather::Helper::Test;

use rules;

use Test::Most;
use MordaX::Block::Weather::Helper;
use MordaX::Logit;
use base qw(Test::Class);

use MordaX::Block::Zen::Init;

sub test_get_widget_icon_size : Test(8) {
    my $self = shift;

    my $req;

    #case 1
    $req->{Getargshash}{dp} = 0;
    my $size = MordaX::Block::Weather::Helper::get_widget_icon_size($req);
    is($size, 48, 'good');

    #case 2
    $req->{Getargshash}{dp} = 1.24;
    $size = MordaX::Block::Weather::Helper::get_widget_icon_size($req);
    is($size, 48, 'good');

    #case 3
    $req->{Getargshash}{dp} = 1.25;
    $size = MordaX::Block::Weather::Helper::get_widget_icon_size($req);
    is($size, 64, 'good');

    #case 4
    $req->{Getargshash}{dp} = 1.74;
    $size = MordaX::Block::Weather::Helper::get_widget_icon_size($req);
    is($size, 64, 'good');

    #case 5
    $req->{Getargshash}{dp} = 1.75;
    $size = MordaX::Block::Weather::Helper::get_widget_icon_size($req);
    is($size, 96, 'good');

    #case 6
    $req->{Getargshash}{dp} = 2.4;
    $size = MordaX::Block::Weather::Helper::get_widget_icon_size($req);
    is($size, 96, 'good');

    #case 7
    $req->{Getargshash}{dp} = 2.5;
    $size = MordaX::Block::Weather::Helper::get_widget_icon_size($req);
    is($size, 128, 'good');

    #case 8
    $req->{Getargshash}{dp} = 3;
    $size = MordaX::Block::Weather::Helper::get_widget_icon_size($req);
    is($size, 128, 'good');
}

sub test_lang_weather : Test(2) {
    my $self = shift;

    no warnings qw(redefine once);
    local *MordaX::Cache::get = sub {
        state $ret = {
            MordaX::Block::Weather::Helper::TRANSLATIONS_MEMD() . 'test' => { 'ru' => 'test' }
        };
        return $ret->{ $_[1] };
    };
    my $res = MordaX::Block::Weather::Helper::lang_weather({ Locale => 'ru' }, 'test');
    is $res, 'test', 'return from memd by lang';
    my $logit = [];
    local *MordaX::Block::Weather::Helper::logit = sub { push @$logit, [shift, shift] };
    MordaX::Block::Weather::Helper::lang_weather({ Locale => 'ru' }, 'no_key');
    ok((grep { $_->[0] eq 'warning' } @$logit), "logit 'warning' when no key at memd");
};

1;
