package MordaX::Block::Services_new::Test;

use rules;
use base qw(Test::Class);

use MordaX::Block::Services_new;
use MordaX::Logit;
use MordaX::Options;
use Test::Most;
use testlib::TestRequest;

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

sub test_smart_sort_services_bigb_empty : Test(2) {
    my $self = shift;

    *smart_sort_services = \&MordaX::Block::Services_new::smart_sort_services;

    no warnings qw(redefine);
    local *MordaX::Experiment::AB::flags = sub {
        return $self;
    };
    sub get {}
    local *get_bool = sub {
        if (grep {$_[1] eq $_} @{$self->{flag} || []}) {
            return 1;
        }
        return 0;
    };
    local *MordaX::Block::Services_new::_get_count = sub {
        return 10;
    };


    # BigB пустой. Сортируем дефолт по весу
    $self->{req}{TargetingInfo} = {};
    $self->{flag} = ['services_new_without_sort_position'];

    my $list_exp = [
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
            icon => 'lavka',
            position => 1,
            service => 'lavka',
            text => 'Лавка',
            url => 'https://eda.yandex/lavka/?utm_source=main_stripe_big_ranking',
            coef_weight => 1,
            weight => 1099
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
            icon => 'music1',
            service => 'music',
            text => 'Музыка',
            url => 'https://music.yandex.ru/?utm_source=main_stripe_big_ranking',
            coef_weight => 1,
            weight => 1094
        },
        {
            icon => 'praktikum',
            service => 'praktikum',
            text => 'Практикум',
            coef_weight => 1,
            url => 'https://praktikum.yandex.ru/?utm_source=main_stripe_big_ranking'
        },
    ];
    is_deeply(smart_sort_services($self->{req}, $self->{list}), $list_exp);

    # BigB пустой. Сортируем дефолт по весу и позиции
    $self->{req}{TargetingInfo} = {};
    $self->{flag} = [];
    $list_exp = [
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
            icon => 'music1',
            service => 'music',
            text => 'Музыка',
            url => 'https://music.yandex.ru/?utm_source=main_stripe_big_ranking',
            coef_weight => 1,
            weight => 1094
        },
        {
            icon => 'praktikum',
            service => 'praktikum',
            text => 'Практикум',
            coef_weight => 1,
            url => 'https://praktikum.yandex.ru/?utm_source=main_stripe_big_ranking'
        },
    ];
    is_deeply(smart_sort_services($self->{req}, $self->{list}), $list_exp);
}

sub test_smart_sort_services_bigb_no_empty : Test(2) {
    my $self = shift;

    *smart_sort_services = \&MordaX::Block::Services_new::smart_sort_services;

    no warnings qw(redefine);
    local *MordaX::Experiment::AB::flags = sub {
        return $self;
    };
    sub get {}
    local *get_bool = sub {
        if (grep {$_[1] eq $_} @{$self->{flag} || []}) {
            return 1;
        }
        return 0;
    };
    local *MordaX::Block::Services_new::_get_count = sub {
        return 10;
    };

    # BigB не пустой. Сортируем дефолт по весу + вес Bigb
    $self->{flag} = ['services_new_without_sort_position'];

    my $list_exp = [
        {
            icon => 'music1',
            service => 'music',
            text => 'Музыка',
            url => 'https://music.yandex.ru/?utm_source=main_stripe_big_ranking',
            coef_weight => 1,
            weight => 1094
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
            icon => 'lavka',
            position => 1,
            service => 'lavka',
            text => 'Лавка',
            url => 'https://eda.yandex/lavka/?utm_source=main_stripe_big_ranking',
            coef_weight => 1,
            weight => 1099
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
    ];
    is_deeply(smart_sort_services($self->{req}, $self->{list}), $list_exp);

    # BigB не пустой. Сортируем дефолт по весу и позиции + вес Bigb
    $self->{flag} = [];
    $list_exp = [
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
            icon => 'music1',
            service => 'music',
            text => 'Музыка',
            url => 'https://music.yandex.ru/?utm_source=main_stripe_big_ranking',
            coef_weight => 1,
            weight => 1094
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
    ];
    is_deeply(smart_sort_services($self->{req}, $self->{list}), $list_exp);
}

sub test_smart_sort_services_threshold : Test(3) {
    my $self = shift;

    *smart_sort_services = \&MordaX::Block::Services_new::smart_sort_services;

    no warnings qw(redefine);
    local *MordaX::Experiment::AB::flags = sub {
        return $self;
    };
    local *get = sub {};
    local *get_bool = sub {
        if (grep {$_[1] eq $_} @{$self->{flag} || []}) {
            return 1;
        }
        return 0;
    };
    local *MordaX::Block::Services_new::_get_count = sub {
        return 3;
    };

    # BigB не пустой. Сортируем дефолт по весу + вес Bigb. Веса bigb меньше 5, 3 элемента в полоске
    # музыка и практикум уходят в хвост, и так как у них бигб веса меньше 5, фильтруются

    $self->{flag} = ['services_new_without_sort_position'];
    $self->{req}{TargetingInfo}{recently_services}{watch_common}{music}{weight} = 4;

    my $list_exp = [
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
            icon => 'lavka',
            position => 1,
            service => 'lavka',
            text => 'Лавка',
            url => 'https://eda.yandex/lavka/?utm_source=main_stripe_big_ranking',
            coef_weight => 1,
            weight => 1099
        },
        {
            icon => 'kinopoisk',
            service => 'kinopoisk_old',
            text => 'КиноПоиск',
            url => 'https://www.kinopoisk.ru/?utm_source=main_stripe_big_ranking',
            coef_weight => 1,
            weight => 1097
        },
    ];
    is_deeply(smart_sort_services($self->{req}, $self->{list}), $list_exp);

    # BigB не пустой. Сортируем дефолт по весу + вес Bigb. Веса bigb меньше 5, 3 элемента в полоске
    # музыка и практикум уходят в хвост, практикум фильтруется, музыка встает на место кинопоиска
    $self->{req}{TargetingInfo}{recently_services}{watch_common}{music}{weight} = 5;

    $list_exp = [
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
            icon => 'lavka',
            position => 1,
            service => 'lavka',
            text => 'Лавка',
            url => 'https://eda.yandex/lavka/?utm_source=main_stripe_big_ranking',
            coef_weight => 1,
            weight => 1099
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
    is_deeply(smart_sort_services($self->{req}, $self->{list}), $list_exp);

    # Добавляем в бигб практикум и кинопоиск, и делаем 2 элемента, чтобы хвост из элементов был длинее тела
    $self->{req} = {
        TargetingInfo => {
            recently_services => {
                watch_common => {
                    music => {
                          "name" => "music",
                          "updatetime" => "1591127649",
                          "weight" => 78.3256640558061
                    },
                    kinopoisk_old => {
                       "name" => "kinopoisk_old",
                       "updatetime" => "1591031916",
                       "weight" => 52.5453582239229
                    },
                    praktikum => {
                       "name" => "praktikum",
                       "updatetime" => "1591132061",
                       "weight" => 41.246707514786
                    },
                },
            }
        }
    };

    local *MordaX::Block::Services_new::_get_count = sub {
        return 2;
    };

    $list_exp = [
        {
            icon => 'music1',
            service => 'music',
            text => 'Музыка',
            url => 'https://music.yandex.ru/?utm_source=main_stripe_big_ranking',
            coef_weight => 1,
            weight => 1094
        },
        {
            icon => 'kinopoisk',
            service => 'kinopoisk_old',
            text => 'КиноПоиск',
            url => 'https://www.kinopoisk.ru/?utm_source=main_stripe_big_ranking',
            coef_weight => 1,
            weight => 1097
        },
    ];
    is_deeply(smart_sort_services($self->{req}, $self->{list}), $list_exp);
}

sub test_GetDataWithSmartSort_count : Test(2) {
    my $self = shift;

    *GetDataWithSmartSort = \&MordaX::Block::Services_new::GetDataWithSmartSort;

    no warnings qw(redefine);

    local *MordaX::Block::Common::Services_enabled::is_service_enabled = sub {
        return 1;
    };

    local *MordaX::Block::Services::GetOneServiceData = sub {
        return;
    };

    local *MordaX::Block::Services_new::smart_sort_services = sub {
        return $_[1];
    };

    local *MordaX::Block::Services_new::_get_count = sub {
        return 9;
    };

    local *MordaX::Data_get::get_static_data = sub {
        return [
            {
                icon => 'eda',
                service => 'eda',
                text => 'Еда',
                url => 'https://eda.yandex/?utm_source=main_stripe_big_ranking',
            },
            {
                icon => 'lavka',
                service => 'lavka',
                text => 'Лавка',
                url => 'https://eda.yandex/lavka/?utm_source=main_stripe_big_ranking',
            },
            {
                icon => 'music1',
                service => 'music',
                text => 'Музыка',
                url => 'https://music.yandex.ru/?utm_source=main_stripe_big_ranking',
            },
        ];
    };

    local *MordaX::Block::Services_new::logit = sub {
        is($_[0], 'warning');
    };

    is(GetDataWithSmartSort($self, {}, {}), undef, 'warning');
}

sub test_GetDataForV16 : Test(2) {
    my $self = shift;

    *GetDataForV16 = \&MordaX::Block::Services_new::GetDataForV16;

    no warnings qw(redefine);

    local *MordaX::Options::options = sub {
        return 1;
    };

    local *MordaX::Block::Services_new::get_services_v16 = sub {
        return [
            {service => 'market', position => 0, text => 'Маркет'},
            {service => 'video', position => 1, text => 'Видео'},
            {service => 'maps', position => 2, text => 'Карты'},
            {service => 'images', position => 3, text => 'Картинки'},
        ];
    };

    my $req = testlib::TestRequest::Req->new();
    my $page = {};
    GetDataForV16($self, $req, $page);

    is_deeply([map {$_->{service}} @{$page->{services_new}{list}}], ['market']);
    is_deeply([map {$_->{service}} @{$page->{services_new}{more}}], ['video', 'images', 'maps']);
}

sub test__get_more_last : Test(1) {
    my $self = shift;

    *_get_more_last = \&MordaX::Block::Services_new::_get_more_last;

    no warnings qw(redefine);
    local *MordaX::Block::Services::select = sub {
        return [
            {
                domain => 'ru',
                href => 'https://yandex.ru/soft/?from=prov_all',
                icon_id => 'soft',
                id => 'soft',
                tabs_more => '2',
                url => 'https://yandex.ru/soft/?from=prov_all'
            },
            {
                all_group => 'mobileBlock',
                domain => 'ru',
                href => '//mobile.yandex.ru/?from=desktop_morda_more',
                icon_id => 'mobile',
                id => 'mobile',
                tabs_more => '2',
                url => '//mobile.yandex.ru/?from=desktop_morda_more'
            },
            {
                domain => 'ru',
                href => '//yandex.ru/all',
                icon_id => 'all',
                id => 'all',
                pda => '//yandex.ru/all',
                tabs_more => '3',
                url => '//yandex.ru/all'
            },
        ];
    };

    local *MordaX::Block::Services_new::lang = sub {
        my %lang = (
            'tabs.soft' => 'Программы',
            'tabs.all' => 'Все&nbsp;сервисы',
            'tabs.mobile' => 'Для&nbsp;мобильного',
        );

        return $lang{$_[0]};
    };

    my $list_exp = [
        {
            url => '//mobile.yandex.ru/?from=desktop_morda_more',
            text => 'Для&nbsp;мобильного',
        },
        {
            url => 'https://yandex.ru/soft/?from=prov_all',
            text => 'Программы',
        },
        {
            url => '//yandex.ru/all',
            text => 'Все&nbsp;сервисы',
        },
    ];

    is_deeply(_get_more_last({}), $list_exp);
}

sub test__get_count : Test(12) {
    my $self = shift;

    no warnings qw(redefine once);
    local *MordaX::Experiment::AB::flags = sub { MordaX::Experiment::AB::Flags::instance($_[0], 'MUTE_WARNINGS'); };

    *_get_count = \&MordaX::Block::Services_new::_get_count;

    local *MordaX::Options::options = sub {
        return $self->{options}{$_[0]};
    };

    is(_get_count({}), MordaX::Block::Services_new::COUNT_DEFAULT - 1, 'COUNT_DEFAULT');

    local *MordaX::Block::Services_new::_get_promo = sub { return {text => 'text'}; };
    is(_get_count({}), MordaX::Block::Services_new::COUNT_DEFAULT - 2, 'not empty promo');

    local *MordaX::Block::Services_new::_get_promo = sub { return; };
    is(_get_count({}), MordaX::Block::Services_new::COUNT_DEFAULT - 1, 'empty promo');

    local *MordaX::Type::is_api_search_2 = sub { return 1; };
    is(_get_count({}), MordaX::Block::Services_new::COUNT_API_SEARCH - 1, 'COUNT_API_SEARCH');

    $self->{options}{services_new_count_api_search_2} = 78;
    is(_get_count({}), 77, 'option services_new_count_api_search_2');

    local *MordaX::Type::is_touch_only = sub { return 1; };
    is(_get_count({}), MordaX::Block::Services_new::COUNT_TOUCH - 1, 'COUNT_TOUCH');

    $self->{options}{services_new_count_touch_only} = 17;
    is(_get_count({}), 16, 'option services_new_count_touch_only');

    local *MordaX::Type::is_big = sub { return 1; };
    is(_get_count({}), MordaX::Block::Services_new::COUNT_BIG - 1, 'COUNT_BIG');

    $self->{options}{services_new_count_big} = 3;
    is(_get_count({}), 2, 'option services_new_count_big');

    local *MordaX::Type::is_dzen_search = sub { return 1; };
    is(_get_count({}), MordaX::Block::Services_new::COUNT_DZEN_SEARCH - 1, 'COUNT_DZEN_SEARCH');
    
    local *MordaX::Type::is_touch = sub { return 1; };
    $self->{options}{services_new_count_dzen_search_touch_only} = 15;
    is(_get_count({}), 14, 'option services_new_count_dzen_search_touch_only');

    local *MordaX::Type::is_touch = sub { return 0; };
    $self->{options}{services_new_count_dzen_search_big} = 9;
    is(_get_count({}), 8, 'option services_new_count_dzen_search_big');
}

sub TargetBlock {
    return 'services_new';
}

1;
