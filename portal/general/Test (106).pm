package MordaX::RF::Test;

use rules;

use Test::Most;
use MordaX::Logit;
use base qw(Test::Class);

use MordaX::RF;

sub startup : Test(startup) {}
sub setup : Test(setup) {}

sub test_get_show_urls : Test(1) {
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

    my $expected = {
        market => $show_url,
        kinopoisk => $show_url
    };

    is_deeply(get_show_url($self, $self), $expected);
}

1;
