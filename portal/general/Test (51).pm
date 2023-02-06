package MordaX::Block::Zen::Init::Test;

use rules;

use Test::Most;
use MordaX::Logit;
use base qw(Test::Class);

use MordaX::Block::Zen::Init;

sub _startup : Test(startup) {
    my ($self) = @_;

    $self->{get_static_data} = {
        api_search_2 => {
            content => 'api_search_2',
            country_code => 'ru',
            domain => 'ru',
            geos => 10000
        },
        big => {
            content => 'big',
            country_code => 'ru',
            domain => 'ru',
            geos => 10000,
            yabro_promo_link => 'https://browser.yandex.ru/desktop/zen/?from=yamain_zen&banerid=0458000000'
        },
        touch => {
            content => 'touch',
            country_code => 'ru',
            domain => 'ru',
            geos => 10000,
        },
    };

}
sub _setup : Test(setup) {
    no warnings qw(redefine);
    *MordaX::Block::Zen::Init::_get_zen_params = sub {
        return {};
    };

    *MordaX::Block::Zen::Init::use_ssr_scheme = sub {
        return 1;
    };

    *MordaX::Block::Zen::Init::_get_params_for_static = sub {
        return {};
    };

    *MordaX::Block::Zen::Init::get_disabled_blocks = sub {
        return {};
    };

    *MordaX::Block::Zen::Init::_get_features = sub {
        return {};
    };

    *MordaX::Block::Zen::Init::_get_headers = sub {
        return {};
    };

    *MordaX::Block::Zen::Init::_get_debug_params = sub {
        return {};
    };
}

sub test_zen_params_api_search : Test(1) {
    my $self = shift;

    *zen_params = \&MordaX::Block::Zen::Init::zen_params;

    no warnings qw(redefine);
    local *MordaX::Type::is_api_search_2 = sub {
        return 1;
    };

    local *MordaX::Type::is_api_search = sub {
        return 1;
    };

    local *MordaX::Data_get::get_static_data = sub {
        my ($req, $name, %args) = @_;
        if ($name eq 'zen') {
            return $self->{get_static_data}{$args{content}};
        }
    };

    my $req = MordaX::Req->new();

    my $exp_data = {
        ok => 1,
        zen_type => 'app',
        zen_settings => $self->{get_static_data}{api_search_2}
    };

    is_deeply(zen_params($req, {}), $exp_data);
}

sub test_zen_params_big : Test(1) {
    my $self = shift;

    *zen_params = \&MordaX::Block::Zen::Init::zen_params;

    no warnings qw(redefine once);
    local *MordaX::Type::is_api_search_2 = sub {
        return 0;
    };

    local *MordaX::Block::Zen::Init::_get_zen_type = sub {
        return 'desktop';
    };

    local *MordaX::Type::is_big = sub {
        return 1;
    };

    local *MordaX::Data_get::get_static_data = sub {
        my ($req, $name, %args) = @_;
        if ($name eq 'zen') {
            return $self->{get_static_data}{$args{content}};
        }
    };

    local *MordaX::Experiment::AB::flags = sub {
        MordaX::Experiment::AB::Flags::instance($_[0], 'MUTE_WARNINGS');
    };

    my $req = MordaX::Req->new();
    $req->{MordaContent} = 'big';

    my $exp_data = {
        ok => 1,
        zen_type => 'desktop',
        zen_settings => $self->{get_static_data}{big},
        debug_params => {},
        disabled_blocks => {},
        features => {},
        headers => {},
        params => {},
        params_for_static => {},
        should_load_with_anti_adblock => undef,
        should_use_zen_adb_host => 0,
        zen_api_host => undef,
        zen_client_host => undef,
        zen_loader_host => undef,
        zen_server_host => undef,
    };

    is_deeply(zen_params($req, {}), $exp_data);
}

sub test_zen_params_touch : Test(1) {
    my $self = shift;

    *zen_params = \&MordaX::Block::Zen::Init::zen_params;

    no warnings qw(redefine once);
    local *MordaX::Type::is_api_search_2 = sub {
        return 0;
    };

    local *MordaX::Block::Zen::Init::_get_zen_type = sub {
        return 'mobile';
    };

    local *MordaX::Type::is_big = sub {
        return 0;
    };

    local *MordaX::Data_get::get_static_data = sub {
        my ($req, $name, %args) = @_;
        if ($name eq 'zen') {
            return $self->{get_static_data}{$args{content}};
        }
    };

    local *MordaX::Experiment::AB::flags = sub {
        MordaX::Experiment::AB::Flags::instance($_[0], 'MUTE_WARNINGS');
    };

    my $req = MordaX::Req->new();
    $req->{MordaContent} = 'touch';

    my $exp_data = {
        ok => 1,
        zen_type => 'mobile',
        zen_settings => $self->{get_static_data}{touch},
        debug_params => {},
        features => {},
        headers => {},
        params => {},
        params_for_static => {},
        should_load_with_anti_adblock => undef,
        should_use_zen_adb_host => 0,
        zen_api_host => undef,
        zen_client_host => undef,
        zen_loader_host => undef,
        zen_server_host => undef,
    };

    is_deeply(zen_params($req, {}), $exp_data);
}

1;
