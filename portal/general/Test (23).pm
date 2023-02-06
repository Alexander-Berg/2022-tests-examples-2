package Handler::ForApphost::Api::Test;

use rules;

use Test::Most;
use base qw(Test::Class);

use MP::Logit qw(logit dmp);

use Handler::ForApphost::Api;

sub test___get_data_weather : Test(3) {
    my ($self) = @_;

    no warnings qw(redefine);
    local *_get_data_weather = \&Handler::ForApphost::Api::_get_data_weather;
    local *get_items = sub {
        return {
            market => {
                zen_id => 'zen_market',
                zen_id_promo => 'zen_market_promo'
            },
        };
    };
    local *MordaX::Block::Assist::Utils::is_geoblock_available_pp = sub {1};
    local *MordaX::Block::Assist::Utils::is_geoblock_shortcuts_promo = sub {1};

    my $exp = {
        geoblock_lite => {
            geo => {
                geoid => 213,
            }
        }
    };
    my $req = MordaX::Req->new();
    my $result = _get_data_weather($req);
    is_deeply($result, $exp, 'get_data_weather _get_weather_geoblock_lite');


    *MordaX::Block::Assist::Utils::is_geoblock_shortcuts_promo = sub {0};
    local *MordaX::Block::Assist::Utils::is_geoblock_shortcuts = sub {1};

    $exp = {
        shortcuts => {
            geo => {
                geoid => 213,
            }
        }
    };
    $req = MordaX::Req->new();
    $result = _get_data_weather($req);
    is_deeply($result, $exp, 'get_data_weather _get_weather_shortcuts');


    *MordaX::Block::Assist::Utils::is_geoblock_shortcuts = sub {0};

    $req = MordaX::Req->new();
    $result = _get_data_weather($req);
    is($result, undef, 'get_data_weather undef');
}


1;