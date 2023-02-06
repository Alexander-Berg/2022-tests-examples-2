package MordaX::RF::ZenExtensions::Test;

use rules;

use Test::Most;
use MP::Logit;
use base qw(Test::Class);

use MordaX::RF::ZenExtensions;

sub startup : Test(startup) {}
sub setup : Test(setup) {}

sub test_change_ids_placeholders : Test(1) {
    my $self = shift;

    *change_ids = \&MordaX::RF::ZenExtensions::change_ids_placeholders;

    local *get_items = sub {
        return {
            market => {
                zen_id => 'zen_market',
                zen_id_promo => 'zen_market_promo'
            },
        };
    };

    my $in_data = [
        {zen_id => 'zen_market'},
        {zen_id => 'zen_kinopoisk'},
    ];
    change_ids($self, {}, $in_data);
    is_deeply($in_data, [{zen_id => 'zen_market_promo'}, {zen_id => 'zen_kinopoisk'}]);
}

1;
