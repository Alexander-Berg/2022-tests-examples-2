package MordaX::Block::Stream::Test;

use rules;

use Test::Most;
use MordaX::Logit;
use base qw(Test::Class);

use MordaX::Block::Stream;

sub _startup : Test(startup) {
}

sub _setup : Test(setup) {
    my $self = shift;
}

sub test_get_data_stream_display : Test(2) {
    my $self = shift;

    *get_data_stream_display = \&MordaX::Block::Stream::get_data_stream_display;

    my $in = {};
    my $promo_id = '4a41b57961fa541e82db24b415397839';

    no warnings qw(redefine experimental::smartmatch);
    local *MordaX::Stream::is_on_channel = sub{1};
    local *MordaX::Data_get::get_static_data = sub {
        my ($req, $name, %args) = @_;
        if ($name eq 'promo_stream_display_count_2') {
            if ($args{text_key} eq 'storefront') {
                return {
                    category => 'storefront',
                    count => 2,
                    exp => 'stream_embed_autoplay',
                }
            }
            else {
                return {
                    category => 'sport',
                    count => 3,
                }
            }
        }
        elsif ($_[1] eq 'extra_stream_display') {
            return [
                {
                    category => 'sport',
                    content => 'all',
                    from => '2018-12-25',
                    geo  => 225,
                    promo_color => '#304bdd',
                    promo_position => 2,
                    promo_text => 'По подписке Яндекс.Плюс',
                    subtitle => 'Вселенная зовёт',
                    new_format => 1,
                    thumbnail => 'https://yastatic.net/s3/home/stream/storefront-promo/docwho.png',
                    till => '2019-04-28',
                    title => 'Сериал «Доктор Кто»',
                    url => 'https://www.kinopoisk.ru/film/252089/'
                }
            ];

        }
        elsif ($_[1] eq 'promo_stream_display') {
            return [
                {
                    category => 'storefront',
                    channel_id => 897,
                    content => 'embedstream',
                    content_id => '47e0453b74c0ee6da03c1d0db0a43a5b',
                    geo        => 225,
                    paid       => 1,
                    promo_position => 3,
                    subtitle => 'Музыкальный канал на Яндексе',
                    title => 'МУЗ-ТВ',
                    type => 'category',
                },
                {
                    category => 'storefront',
                    channel_id => 100000,
                    content => 'embedstream',
                    content_id => '4f9707904ed5698d97a948de0c01bdb9',
                    geo => 225,
                    paid => 1,
                    promo_position => 1,
                    subtitle => 'Прямой эфир',
                    title => 'Канал Яндекса «Семейные Комедии»',
                    type => 'category',
                },
                {
                    category => 'storefront',
                    channel_id => 405,
                    content => 'embedstream',
                    content_id => '4d1d6979385d28ebab8faae66cd97d72',
                    geo => 225,
                    paid => 1,
                    promo_position => 2,
                    subtitle => 'Прямой эфир',
                    title => 'Канал «Звезда»',
                    type => 'theme',
                },
                {
                    category => 'storefront',
                    channel_id => 23,
                    content => 'embedstream',
                    content_id => '4a41b57961fa541e82db24b415397829',
                    geo => 225,
                    paid => 1,
                    promo_position => 3,
                    subtitle => 'Прямой эфир',
                    title => 'Евроновости',
                    type => 'blogger',
                },
                {
                    category => 'sport',
                    channel_id => 23,
                    content => 'embedstream',
                    content_id => $promo_id,
                    geo => 225,
                    promo_position => 3,
                    subtitle => 'sport subtitle',
                    title => 'sport title',
                    type => '',
                },
                {
                    category => 'sport',
                    channel_id => 23,
                    content => 'embedstream',
                    content_id => '4a41b57961fa541e82db24b415397829',
                    geo => 225,
                    promo_position => 1,
                    subtitle => 'sport subtitle',
                    title => 'sport title',
                    type => '',
                },
            ]
        }
    };

    my $out_exp = {
        storefront  => [
            {
                content_id => '4f9707904ed5698d97a948de0c01bdb9',
                paid  => 1,
                subtitle => 'Прямой эфир',
                title  => 'Канал Яндекса «Семейные Комедии»',
                type => 'category',
            },
            {
                content_id => '4d1d6979385d28ebab8faae66cd97d72',
                paid => 1,
                subtitle => 'Прямой эфир',
                title => 'Канал «Звезда»',
                type => 'theme',
            }
        ],
        sport  => [
            {
                content_id => '4a41b57961fa541e82db24b415397829',
                subtitle => 'sport subtitle',
                title  => 'sport title',
                type => '',
            },
            {
                promo_color => '#304bdd',
                promo_text => 'По подписке Яндекс.Плюс',
                subtitle => 'Вселенная зовёт',
                new_format => 1,
                thumbnail => 'https://yastatic.net/s3/home/stream/storefront-promo/docwho.png',
                title => 'Сериал «Доктор Кто»',
                url => 'https://www.kinopoisk.ru/film/252089/',
            },
            {
                content_id => $promo_id,
                subtitle => 'sport subtitle',
                title  => 'sport title',
                type => '',
            }
        ]
    };
    my $out_exp_first = {
        storefront  => [
            {
                content_id => '4f9707904ed5698d97a948de0c01bdb9',
                paid  => 1,
                subtitle => 'Прямой эфир',
                title  => 'Канал Яндекса «Семейные Комедии»',
                type => 'category',
            },
            {
                content_id => '4d1d6979385d28ebab8faae66cd97d72',
                paid => 1,
                subtitle => 'Прямой эфир',
                title => 'Канал «Звезда»',
                type => 'theme',
            }
        ],
        sport  => [
         {
               content_id => $promo_id,
               subtitle => 'sport subtitle',
               title  => 'sport title',
               type => '',
           },
           {
               content_id => '4a41b57961fa541e82db24b415397829',
               subtitle => 'sport subtitle',
               title  => 'sport title',
               type => '',
           },
           {
               promo_color => '#304bdd',
               promo_text => 'По подписке Яндекс.Плюс',
               subtitle => 'Вселенная зовёт',
               new_format => 1,
               thumbnail => 'https://yastatic.net/s3/home/stream/storefront-promo/docwho.png',
               title => 'Сериал «Доктор Кто»',
               url => 'https://www.kinopoisk.ru/film/252089/',
           }
        ]
    };

    is_deeply(get_data_stream_display({}), $out_exp);
    is_deeply(get_data_stream_display({
        Getargshash => {
            king => $promo_id
        }
    }), $out_exp_first);
}

sub test_get_promo : Test(22) {
    my $self = shift;

    *get_promo = \&MordaX::Block::Stream::get_promo;

    no warnings qw(redefine experimental::smartmatch);

    local *MordaX::Data_get::get_static_data = sub {
        if ($_[1] eq 'stream_promo_api') {
            return {
                background          => "tina0520",
                bgcolor_1           => "#010101",
                button_text         => "Смотреть",
                card_from           => "2020-05-07 18:00",
                card_title          => "«Ешь, люби, тренируйся»",
                channel_id          => 1585050586,
                content_id          => "486dc0e16744730ba5e2685b7f136258",
                counter             => "TinaEatLoveTrain",
                domain              => "ru",
                from                => "2020-05-07 18:00",
                geos                => 225,
                locale              => "all",
                subtitle            => "Только в Яндекс.Эфире",
                text_color          => "#ffffff",
                till                => "2020-05-12 19:30",
                title               => "C Тиной Канделаки",
                title_color         => "#ffffff",
            };
        };
    };

    my $out = {
        'stream_promo_api' => {
            background    => "tina0520",
            bgcolor_1     => "#010101",
            button_text   => "Смотреть",
            card_from     => "2020-05-07 18:00",
            card_title    => "«Ешь, люби, тренируйся»",
            channel_id    => 1585050586,
            content_id    => "486dc0e16744730ba5e2685b7f136258",
            counter       => "TinaEatLoveTrain",
            open_stream   => 1,
            subtitle      => "Только в Яндекс.Эфире",
            text_color    => "#ffffff",
            title         => "C Тиной Канделаки",
            title_color   => "#ffffff",
        },
    };

    #
    # === Проверяем со свежим yandexuid, is_api_search=1 и is_stream_enabled=0
    #

    my $req = Req->new();
    $req->{Yandexuid_age} = 1;
    is(get_promo(), undef, "Yandexuid_age = 1");

    $req = Req->new();
    local *MordaX::Type::is_api_search = sub{1};
    is(get_promo(), undef, "is_api_search = 1");

    *MordaX::Type::is_api_search = sub{0};
    local *MordaX::Stream::is_stream_enabled = sub{0};
    is(get_promo(), undef, "is_stream_enabled = 0");

    *MordaX::Stream::is_stream_enabled = sub{1};

    #
    # === Проверяем stream_promo_api
    #

    local *MordaX::Type::is_api_search = sub{0};
    is(get_promo($req), undef, "is_api_search = 0");

    # Трансляция началась
    *MordaX::Type::is_api_search = sub{1};
    is_deeply(get_promo($req), $out->{stream_promo_api}, "stream_promo_api + stream started");
    # Начало больше, чем через 5 минут
    $req->{time} -= 6 * 60;
    $out->{stream_promo_api}{open_stream} = 0;
    $out->{stream_promo_api}{start_in} = "Начало через 6 минут";
    is_deeply(get_promo($req), $out->{stream_promo_api}, "stream_promo_api + stream starts in 6 min");
    # Начало больше, чем через 15 минут
    $req->{time} -= 10 * 60;
    $out->{stream_promo_api}{start_in} = "Трансляция в 18:00";
    delete $out->{stream_promo_api}{open_stream};
    is_deeply(get_promo($req), $out->{stream_promo_api}, "stream_promo_api + stream starts in 18:00");

    #
    # === Проверяем stream_promo_api с полем program_start_msk
    #

    local *MordaX::Data_get::get_static_data = sub {
        if ($_[1] eq 'stream_promo_api') {
            return {
                background          => "tina0520",
                bgcolor_1           => "#010101",
                button_text         => "Смотреть",
                card_from           => "2020-05-07 18:00",
                card_title          => "«Ешь, люби, тренируйся»",
                channel_id          => 1585050586,
                content_id          => "486dc0e16744730ba5e2685b7f136258",
                counter             => "TinaEatLoveTrain",
                domain              => "ru",
                from                => "2020-05-07 18:00",
                geos                => 225,
                locale              => "all",
                subtitle            => "Только в Яндекс.Эфире",
                text_color          => "#ffffff",
                till                => "2020-05-12 19:30",
                title               => "C Тиной Канделаки",
                title_color         => "#ffffff",
                program_start_msk   => "2020-05-07 18:30",
            };
        };
    };

    # Начало больше, чем через 15 минут
    $out->{stream_promo_api}{start_in} = "Трансляция в 18:30";
    is_deeply(get_promo($req), $out->{stream_promo_api}, "stream_promo_api + program_start_msk + stream starts in 18:30");
    # Начало больше, чем через 5 минут
    $req->{time} += 40 * 60;
    $out->{stream_promo_api}{open_stream} = 0;
    $out->{stream_promo_api}{start_in} = "Начало через 6 минут";
    is_deeply(get_promo($req), $out->{stream_promo_api}, "stream_promo_api + program_start_msk + stream starts in 6 min");
    # Трансляция началась
    $req->{time} += 10 * 60;
    $out->{stream_promo_api}{open_stream} = 1;
    delete $out->{stream_promo_api}{start_in};
    is_deeply(get_promo($req), $out->{stream_promo_api}, "stream_promo_api + program_start_msk + stream started");

    #
    # === Проверяем stream_promo_exp
    #

    *MordaX::Data_get::get_static_data = sub {
        if ($_[1] eq 'stream_promo_exp') {
            return {
                background   => "https://yastatic.net/morda-logo/i/stream_stream/box26112017.jpg",
                bk           => "stream_putin",
                channel_id   => 146,
                counter      => "ru_box261117",
                domain       => "ru",
                from         => "2020-05-07 18:00",
                geos         => "10933, 10939, 10842, 10853, 10174, 10897, 10904, 10926, 3, 11070, 11079, 11077, 11119, 11156, 11117, 11095, 11004, 10950, 11015, 10995, 977, 11029, 102444",
                locale       => "all",
                text_color   => "#ffffff",
                till         => "2020-06-08 20:30",
                title        => "Бой за титул чемпиона мира",
            };
        };
    };

    $out = {
        'stream_promo_exp' => {
            background    => "https://yastatic.net/morda-logo/i/stream_stream/box26112017.jpg",
            bk            => "stream_putin",
            channel_id    => 146,
            counter       => "ru_box261117",
            exp           => "other_stream_promo",
            text_color    => "#ffffff",
            title         => "Бой за титул чемпиона мира",
            v             => 2,
            open_stream   => 1,
        },
        'stream_promo' => {
            background_left    => "https://yastatic.net/s3/home/stream/pop-ups/marathon_pop-up2_left.png",
            background_right   => "https://yastatic.net/s3/home/stream/pop-ups/marathon_pop-up2_right.png",
            bk                 => "popup_stream_all_world_3/1",
            channel_id         => 1585050586,
            content_id         => "4d3c7102c21733a58b058173a2ad3073",
            counter            => "marathon20",
            geos_minus         => {
                                    171 => 1,
                                    187 => 1,
                                  },
            subtitle           => "Марафон российских звёзд<br> в поддержку медиков",
            text_color         => "#ffffff",
            title              => "Прорвёмся!",
            open_stream        => 1,
        },
    };

    *MordaX::Type::is_api_search = sub{0};
    $req = Req->new();
    # Трансляция началась
    is_deeply(get_promo($req), $out->{stream_promo_exp}, "stream_promo_exp + stream started");
    # Начало больше, чем через 5 минут
    $req->{time} -= 6 * 60;
    $out->{stream_promo_exp}{start_in} = "Начало через 6 минут";
    $out->{stream_promo_exp}{open_stream} = 0;
    is_deeply(get_promo($req), $out->{stream_promo_exp}, "stream_promo_exp + stream starts in 6 min");
    # Начало больше, чем через 15 минут
    $req->{time} -= 10 * 60;
    $out->{stream_promo_exp}{start_in} = "Трансляция в 18:00";
    delete $out->{stream_promo_exp}{open_stream};
    is_deeply(get_promo($req), $out->{stream_promo_exp}, "stream_promo_exp + stream starts in 18:00");

    #
    # === Проверяем stream_promo_exp с полем program_start_msk
    #

    $req = Req->new();
    *MordaX::Data_get::get_static_data = sub {
        if ($_[1] eq 'stream_promo_exp') {
            return {
                background          => "https://yastatic.net/morda-logo/i/stream_stream/box26112017.jpg",
                bk                  => "stream_putin",
                channel_id          => 146,
                counter             => "ru_box261117",
                domain              => "ru",
                from                => "2020-05-07 18:00",
                geos                => "10933, 10939, 10842, 10853, 10174, 10897, 10904, 10926, 3, 11070, 11079, 11077, 11119, 11156, 11117, 11095, 11004, 10950, 11015, 10995, 977, 11029, 102444",
                locale              => "all",
                program_start_msk   => "2020-05-07 18:30",
                text_color          => "#ffffff",
                till                => "2020-06-08 20:30",
                title               => "Бой за титул чемпиона мира",
            };
        };
    };

    # Начало больше, чем через 15 минут
    $out->{stream_promo_exp}{start_in} = "Трансляция в 18:30";
    is_deeply(get_promo($req), $out->{stream_promo_exp}, "stream_promo_exp + program_start_msk + stream starts in 18:30");
    # Начало больше, чем через 5 минут
    $req->{time} += 15 * 60;
    $out->{stream_promo_exp}{open_stream} = 0;
    $out->{stream_promo_exp}{start_in} = "Начало через 15 минут";
    is_deeply(get_promo($req), $out->{stream_promo_exp}, "stream_promo_exp + program_start_msk + stream starts in 15 min");
    # Трансляция началась
    $req->{time} += 10 * 60;
    $out->{stream_promo_exp}{open_stream} = 1;
    delete $out->{stream_promo_exp}{start_in};
    is_deeply(get_promo($req), $out->{stream_promo_exp}, "stream_promo_exp + program_start_msk + stream started");

    #
    # === Проверяем stream_promo
    #

    $req = Req->new();
    *MordaX::Data_get::get_static_data = sub {
        if ($_[1] eq 'stream_promo_exp') {
            return {
                background   => "https://yastatic.net/morda-logo/i/stream_stream/box26112017.jpg",
                bk           => "stream_putin",
                channel_id   => 146,
                counter      => "ru_box261117",
                domain       => "ru",
                exp          => "other_stream_promo",
                from         => "2020-05-07 18:00",
                geos         => "10933, 10939, 10842, 10853, 10174, 10897, 10904, 10926, 3, 11070, 11079, 11077, 11119, 11156, 11117, 11095, 11004, 10950, 11015, 10995, 977, 11029, 102444",
                locale       => "all",
                text_color   => "#ffffff",
                till         => "2020-06-08 20:30",
                title        => "Бой за титул чемпиона мира",
                v            => 2,
            };
        }
        elsif ($_[1] eq 'stream_promo') {
            return {
                background_left     => "https://yastatic.net/s3/home/stream/pop-ups/marathon_pop-up2_left.png",
                background_right    => "https://yastatic.net/s3/home/stream/pop-ups/marathon_pop-up2_right.png",
                bk                  => "popup_stream_all_world_3/1",
                channel_id          => 1585050586,
                content_id          => "4d3c7102c21733a58b058173a2ad3073",
                counter             => "marathon20",
                domain              => "all",
                from                => "2020-05-07 18:00",
                geos                => "10000, -171, -187",
                geos_minus          => {
                                            171 => 1,
                                            187 => 1,
                                       },
                locale              => "all",
                subtitle            => "Марафон российских звёзд<br> в поддержку медиков",
                text_color          => "#ffffff",
                till                => "2020-05-08 21:00",
                title               => "Прорвёмся!",
            };
        };
    };

    # Трансляция началась
    is_deeply(get_promo($req), $out->{stream_promo}, "stream_promo + stream started");
    # Начало больше, чем через 5 минут
    $req->{time} -= 6 * 60;
    $out->{stream_promo}{start_in} = "Начало через 6 минут";
    $out->{stream_promo}{open_stream} = 0;
    is_deeply(get_promo($req), $out->{stream_promo}, "stream_promo + stream starts in 6 min");
    # Начало больше, чем через 15 минут
    $req->{time} -= 10 * 60;
    $out->{stream_promo}{start_in} = "Трансляция в 18:00";
    delete $out->{stream_promo}{open_stream};
    is_deeply(get_promo($req), $out->{stream_promo}, "stream_promo + stream starts in 18:00");

    #
    # === Проверяем stream_promo с полем program_start_msk
    #

    $req = Req->new();
    *MordaX::Data_get::get_static_data = sub {
        if ($_[1] eq 'stream_promo_exp') {
            return {
                background   => "https://yastatic.net/morda-logo/i/stream_stream/box26112017.jpg",
                bk           => "stream_putin",
                channel_id   => 146,
                counter      => "ru_box261117",
                domain       => "ru",
                exp          => "other_stream_promo",
                from         => "2020-05-07 18:00",
                geos         => "10933, 10939, 10842, 10853, 10174, 10897, 10904, 10926, 3, 11070, 11079, 11077, 11119, 11156, 11117, 11095, 11004, 10950, 11015, 10995, 977, 11029, 102444",
                locale       => "all",
                text_color   => "#ffffff",
                till         => "2020-06-08 20:30",
                title        => "Бой за титул чемпиона мира",
                v            => 2,
            };
        }
        elsif ($_[1] eq 'stream_promo') {
            return {
                background_left     => "https://yastatic.net/s3/home/stream/pop-ups/marathon_pop-up2_left.png",
                background_right    => "https://yastatic.net/s3/home/stream/pop-ups/marathon_pop-up2_right.png",
                bk                  => "popup_stream_all_world_3/1",
                channel_id          => 1585050586,
                content_id          => "4d3c7102c21733a58b058173a2ad3073",
                counter             => "marathon20",
                domain              => "all",
                from                => "2020-05-07 18:00",
                geos                => "10000, -171, -187",
                geos_minus          => {
                                            171 => 1,
                                            187 => 1,
                                       },
                locale              => "all",
                subtitle            => "Марафон российских звёзд<br> в поддержку медиков",
                text_color          => "#ffffff",
                till                => "2020-05-08 21:00",
                title               => "Прорвёмся!",
                program_start_msk   => "2020-05-07 18:30",
            };
        };
    };

    # Начало больше, чем через 15 минут
    $out->{stream_promo}{start_in} = "Трансляция в 18:30";
    is_deeply(get_promo($req), $out->{stream_promo}, "stream_promo + program_start_msk + stream starts in 18:30");
    # Начало больше, чем через 5 минут
    $req->{time} += 15 * 60;
    $out->{stream_promo}{open_stream} = 0;
    $out->{stream_promo}{start_in} = "Начало через 15 минут";
    is_deeply(get_promo($req), $out->{stream_promo}, "stream_promo + program_start_msk + stream starts in 15 min");
    # Трансляция началась
    $req->{time} += 15 * 60;
    $out->{stream_promo}{open_stream} = 1;
    delete $out->{stream_promo}{start_in};
    is_deeply(get_promo($req), $out->{stream_promo}, "stream_promo + program_start_msk + stream started");

}

# ========================================================

package Req;

sub new {
    my ($class) = @_;
    my $defaults = {
        Yandexuid_age => 15 * 60 + 1,
        time          => 1588863600,
    };
    return bless $defaults, $class;
};

sub yabs {0};

# ========================================================

1;
