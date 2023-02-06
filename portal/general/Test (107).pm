package MordaX::RF::Web::Test;

use rules;

use Test::Most;
use MordaX::Logit;
use base qw(Test::Class);

use MordaX::RF::Web;
use MordaX::RF;

sub startup : Test(startup) {}
sub setup : Test(setup) {}

sub test_change_ids_placeholders : Test(1) {
    my $self = shift;

    *change_ids_placeholders = \&MordaX::RF::Web::change_ids_placeholders;

    no warnings qw(redefine);
    local *get_items = sub {
        return {
            market => {
                id => 'market',
                zen_promo => 'zen_market_promo'
            },
        };
    };

    my $in_data = {
        market => 'zen_market',
        kinopoisk => 'zen_kinopoisk',
    };
    change_ids_placeholders($self, {}, $in_data);
    is_deeply($in_data, {market => 'zen_market_promo', kinopoisk => 'zen_kinopoisk'});
}

sub test_get_show_url : Test(1) {
    my $self = shift;

    *get_show_url = \&MordaX::RF::get_show_urls;

    my $show_url = 'https://yabs.ru/show_url'; 

    no warnings qw(redefine);
    local *get_items = sub {
        return {
            market => {
                id => 'market',
                zen_promo => 'zen_market_promo',
                bk => 'bk'
            },
            kinopoisk => {
                id => 'kinopoisk',
                zen_promo => 'zen_kinopoisk',
                bk => 'bk'
            },
        };
    };

    local $self->{_BANNERS_} = $self;

    local *get_flag_show_url = sub {
        return $show_url;
    };

    my $exp = {
        market => $show_url,
        kinopoisk => $show_url
    };

    is_deeply(get_show_url($self, $self), $exp);
}

sub test_get_items : Test(1) {
    my $self = shift;

    no warnings qw(redefine);
    *test_get_items = \&MordaX::RF::Web::get_items;

    local *MordaX::Layout::instance = sub {
        return $self;
    };

    local *get_zen_id_web = sub {
        return {
            market => {
                block => 'market',
                zen_promo => 'zen_market_promo',
            },
            kinopoisk => {
                block => 'kinopoisk',
                zen_promo => 'zen_kinopoisk',
            },
            afisha => {
                block => 'afisha',
            },
        };
    };

    local *get_items = sub {
        return [
            {
                id => 'market',
                bk => 'bk_market',
            },
            {
                id => 'kinopoisk',
                bk => 'bk_kinopoisk',
            },
            {
                id => 'afisha',
            },
        ];
    };

    $self->{rf_after_bk} = {
        kinopoisk => 1,
    };

    my $exp = {
        market => {
            id => 'market',
            bk => 'bk_market',
            zen_promo => 'zen_market_promo',
        },
    };

    is_deeply(test_get_items($self, $self), $exp);
}

1;
