package MordaX::RankingServices::Test;

use rules;

use Test::Most;
use MordaX::Logit;
use base qw(Test::Class);

use MordaX::RankingServices;

sub _startup : Test(startup) {
}

sub _setup : Test(setup) {
    my $self = shift;

    $self->{req} = {
        TargetingInfo => {
            recently_services => {
                watch_common => {
                    music => {
                          "name" => "music",
                          "updatetime" => "1591127649",
                          "weight" => 78.3256640558061
                       },
                    zen => {
                          "name" => "zen",
                          "updatetime" => "1591031916",
                          "weight" => 52.5453582239229
                       },
                    mail => {
                          "name" => "mail",
                          "updatetime" => "1591132061",
                          "weight" => 41.246707514786
                    },
                },
            }
        }
    };

    $self->{list} = [
        {
            icon => 'lavka',
            position => 1,
            service => 'lavka',
            text => 'Лавка',
            url => 'https://eda.yandex/lavka/?utm_source=main_stripe_big_ranking',
            coef_weight => 1,
            weight => 1099
        },
        {
            icon => 'eda',
            position => 2,
            service => 'eda',
            text => 'Еда',
            url => 'https://eda.yandex/?utm_source=main_stripe_big_ranking',
            coef_weight => 1,
            weight => 1100
        },
        {
            icon => 'kinopoisk',
            service => 'kinopoisk_old',
            text => 'КиноПоиск',
            url => 'https://www.kinopoisk.ru/?utm_source=main_stripe_big_ranking',
            coef_weight => 1,
            weight => 1097
        },
        {
            icon => 'praktikum',
            service => 'praktikum',
            text => 'Практикум',
            coef_weight => 1,
            url => 'https://praktikum.yandex.ru/?utm_source=main_stripe_big_ranking'
		},
        {
            icon => 'music1',
            service => 'music',
            text => 'Музыка',
            url => 'https://music.yandex.ru/?utm_source=main_stripe_big_ranking',
            coef_weight => 1,
            weight => 1094
        },
    ];
}

sub test__replace_tail : Test(4) {
    my $self = shift;

    *_replace_tail = \&MordaX::RankingServices::_replace_tail;

    my $list = [
        {service => 'search'},
        {service => 'music'},
        {service => 'kinopoisk_old'}
    ];
    my $candidates = [
        {service => 'direct'},
        {service => 'praktikum'}
    ];

    my $order_services = {
        music => {
           "weight" => 10
        },
        kinopoisk_old => {
           "weight" => 9
        },
        praktikum => {
           "weight" => 11
        },
    };

    _replace_tail($list, $candidates, $order_services);
    is_deeply($list, [{service =>'search'}, {service => 'praktikum'}, {service => 'music'}]);

    $list = [
        {service => 'search'},
        {service => 'music'},
        {service => 'kinopoisk_old'}
    ];
    $candidates = [
        {service => 'direct'},
        {service => 'praktikum'},
        {service => 'mail'},
        {service => 'zen'}
    ];

    _replace_tail($list, $candidates, $order_services);
    is_deeply($list, [{service =>'praktikum'}, {service => 'music'}, {service => 'kinopoisk_old'}]);

    $list = [];
    $candidates = [
        {service => 'direct'},
        {service => 'praktikum'},
        {service => 'mail'},
        {service => 'zen'}
    ];

    _replace_tail($list, $candidates, {});
    is_deeply($list, $list);

    _replace_tail($list, $candidates, $order_services);
    is_deeply($list, []);
}

sub test__pinned_smoke : Test(1) {
    my $self = shift;

    *_pinned = \&MordaX::RankingServices::_pinned;

    my $list = [
        {
            name => 'lavka',
            position => 2,
        },
        {
            name => 'eda',
        },
        {
            name => 'music',
        },
    ];
    my $expect = [
        {
            name => 'eda',
        },
        {
            name => 'lavka',
            position => 2,
        },
        {
            name => 'music',
        },
    ];

    is_deeply(_pinned($list), $expect);
}

sub test__pinned_two_service : Test(1) {
    my $self = shift;

    *_pinned = \&MordaX::RankingServices::_pinned;

    my $list = [
        {
            name => 'lavka',
            position => 2,
        },
        {
            name => 'eda',
            position => 3,
        },
        {
            name => 'music',
        },
    ];
    my $expect = [
        {
            name => 'music',
        },
        {
            name => 'lavka',
            position => 2,
        },
        {
            name => 'eda',
            position => 3,
        },
    ];

    is_deeply(_pinned($list), $expect);
}

sub test__pinned_empty : Test(1) {
    my $self = shift;

    *_pinned = \&MordaX::RankingServices::_pinned;

    my $list = [
        {
            name => 'lavka',
        },
        {
            name => 'eda',
        },
        {
            name => 'music',
        },
    ];

    is_deeply(_pinned($list), $list);
}

sub test__pinned_double : Test(2) {
    my $self = shift;

    *_pinned = \&MordaX::RankingServices::_pinned;

    my $list = [
        {
            name => 'lavka',
            position => 3,
        },
        {
            name => 'eda',
            position => 3,
        },
        {
            name => 'music',
        },
    ];

    my $expect = [
        {
            name => 'music',
        },
        {
            name => 'eda',
            position => 3,
        },
        {
            name => 'lavka',
            position => 3,
        },
    ];

    no warnings qw(redefine);
    local *MordaX::RankingServices::logit = sub {
        is($_[0], 'interr', 'interr exists');
    };

    is_deeply(_pinned($list), $expect);
}

sub test__pinned_border : Test(2) {
    my $self = shift;

    *_pinned = \&MordaX::RankingServices::_pinned;

    my $list = [
        {
            name => 'lavka',
            position => 10,
        },
        {
            name => 'eda',
            position => 3,
        },
        {
            name => 'music',
        },
    ];

    my $expect = [
        {
            name => 'music',
        },
        {
            name => 'lavka',
            position => 10,
        },
        {
            name => 'eda',
            position => 3,
        },
    ];

    no warnings qw(redefine);
    local *MordaX::RankingServices::logit = sub {
        is($_[0], 'interr', 'interr exists');
    };

    is_deeply(_pinned($list), $expect);
}

sub test__pinned_zero : Test(1) {
    my $self = shift;

    *_pinned = \&MordaX::RankingServices::_pinned;

    my $list = [
        {
            name => 'lavka',
            position => 0,
        },
        {
            name => 'eda',
            position => 3,
        },
        {
            name => 'music',
        },
    ];

    my $expect = [
        {
            name => 'lavka',
            position => 0,
        },
        {
            name => 'music',
        },
        {
            name => 'eda',
            position => 3,
        },
    ];

    is_deeply(_pinned($list), $expect);
}

sub test__pinned_negative : Test(1) {
    my $self = shift;

    *_pinned = \&MordaX::RankingServices::_pinned;

    my $list = [
        {
            name => 'lavka',
            position => -1,
        },
        {
            name => 'music',
        },
        {
            name => 'eda',
        },
    ];

    my $expect = [
        {
            name => 'music',
        },
        {
            name => 'eda',
        },
        {
            name => 'lavka',
            position => -1,
        },
    ];

    is_deeply(_pinned($list), $expect);
}

sub test__pinned_double_2: Test(1) {
    my $self = shift;

    *_pinned = \&MordaX::RankingServices::_pinned;

    my $list = [
        {
            name => 'lavka',
            position => 1,
        },
        {
            name => 'music',
            position => 2,
        },
        {
            name => 'eda',
            position => 1,
        },
    ];

    my $expect = [
        {
            name => 'lavka',
            position => 1,
        },
        {
            name => 'eda',
            position => 1,
        },
        {
            name => 'music',
            position => 2,
        },
    ];

    is_deeply(_pinned($list), $expect);
}

sub test__pinned_double_3: Test(1) {
    my $self = shift;

    *_pinned = \&MordaX::RankingServices::_pinned;

    my $list = [
        {
            name => 'lavka',
            position => 2,
        },
        {
            name => 'music',
            position => 3,
        },
        {
            name => 'eda',
            position => 3,
        },
        {
            name => 'tv',
            position => 2,
        },
        {
            name => 'afisha',
        },
    ];

    my $expect = [
        {
            name => 'afisha',
        },
        {
            name => 'lavka',
            position => 2,
        },
        {
            name => 'tv',
            position => 2,
        },
        {
            name => 'music',
            position => 3,
        },
        {
            name => 'eda',
            position => 3,
        },
    ];

    is_deeply(_pinned($list), $expect);
}

sub test__pinned_order_without_pin : Test(1) {
    my $self = shift;

    *_pinned = \&MordaX::RankingServices::_pinned;

    my $list = [
        {
            name => 'music',
        },
        {
            name => 'eda',
        },
        {
            name => 'lavka',
        },
    ];

    my $expect = [
        {
            name => 'music',
        },
        {
            name => 'eda',
        },
        {
            name => 'lavka',
        },
    ];

    is_deeply(_pinned($list), $expect);
}
1;
