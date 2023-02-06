package MordaX::Block::Video_translate::Test;

use rules;
use base qw(Test::Class);

use MordaX::Block::Video_translate;
use MordaX::Logit;
use Test::Most;

sub _startup : Test(startup) {
}

sub _setup : Test(setup) {
    my $self = shift;

    $self->{req} = {};
    $self->{all_tabs} = {};
}

sub test_GetData : Test(8) {
    my $self = shift;

    *GetData = \&MordaX::Block::Video_translate::GetData;

    my $tabs = [
        {
            title => 'Игры',
            type => 'games',
            url  => 'http://yandex.ru/games'
        },
        {
            title => 'Автомобили',
            type => 'auto',
            url  => 'http://yandex.ru/auto'
        },
        {
            title => 'Технологии',
            type => 'tech',
            url  => 'http://yandex.ru/tech'
        },
        {
            title => 'Кухня',
            type => 'kitchen',
            url  => 'http://yandex.ru/kitchen'
        },
    ];

    my $items = [
        {
            title => 'items1',
            url => 'url',
        },
        {
            title => 'items2',
            url => 'url',
        },
        {
            title => 'items3',
            url => 'url',
        },
        {
            title => 'items4',
            url => 'url',
        },
        {
            title => 'items5',
            url => 'url',
        },
    ];

    my $video_translate = {
        title_text => 'title',
        title_url => 'url',
        subtitle_text => 'subtitle',
        footer_text => 'footer_text',
        footer_url  => 'footer_url',
        large_feed_promo => 0,
        bk => 'test',
    };

    my $wait_video_translate_data = {
        title => 'title',
        url => 'url',
        subtitle => 'subtitle',
        footer => {
            text => 'footer_text',
            url  => 'footer_url'
        },
        show_url => 'test',
        click_url => 'test',
    };

    my $test_data = [
        {
            name => 'GetData: template=tabs',
            video_translate => {
                template => 'tabs',
                %$video_translate,
            },
            tabs => $tabs,
            items => $items,
            page => {},
            wait => {
                video_translate => {
                    show => 1,
                    data => {
                        %$wait_video_translate_data,
                        template => 'tabs',
                        tabs => [ 
                            {
                                title => 'Игры',
                                url  => 'http://yandex.ru/games',
                                items => $items,
                            },
                            {
                                title => 'Автомобили',
                                url  => 'http://yandex.ru/auto',
                                items => $items,
                            },
                            {
                                title => 'Технологии',
                                url  => 'http://yandex.ru/tech',
                                items => $items,
                            },
                            {
                                title => 'Кухня',
                                url  => 'http://yandex.ru/kitchen',
                                items => $items,
                            },
                        ],
                    }
                }
            },
        },
        {
            name => 'GetData: template=text',
            video_translate => {
                template => 'text',
                items_json => '[{ "bg": "https://yastatic.net/s3/home/div/bottomsheet/bender/first_item_br_test.png", "title": "Ищите прямо на русском", "url": "http://ya.ru", "bg_color": "#EBE4FF", "bg_color_dark": "#EBE4FF" },{ "bg": "https://yastatic.net/s3/home/div/bottomsheet/bender/first_item_br_test.png", "title": "Ищите прямо на русском", "url": "http://ya.ru", "bg_color": "#EBE4FF", "bg_color_dark": "#EBE4FF" }]',
                %$video_translate,
            },
            page => {},
            wait => {
                video_translate => {
                    show => 1,
                    data => {
                        %$wait_video_translate_data,
                        template => 'text',
                        items => [ 
                            {
                                bg => 'https://yastatic.net/s3/home/div/bottomsheet/bender/first_item_br_test.png',
                                title => 'Ищите прямо на русском',
                                url  => 'http://ya.ru',
                                bg_color => '#EBE4FF',
                                bg_color_dark => '#EBE4FF',
                            },
                            {
                                bg => 'https://yastatic.net/s3/home/div/bottomsheet/bender/first_item_br_test.png',
                                title => 'Ищите прямо на русском',
                                url  => 'http://ya.ru',
                                bg_color => '#EBE4FF',
                                bg_color_dark => '#EBE4FF',
                            },
                        ],
                    }
                }
            },
        },
        {
            name => 'GetData: template=image',
            video_translate => {
                template => 'image',
                items_json => '[{ "bg": "https://yastatic.net/s3/home/div/bottomsheet/bender/kote_test.png", "title": "Почему у кошек вертикальные зрачки?",     "subtitle": "Почему у кошек вертикальные зрачки?", "url": "http://ya.ru",     "time": "7:77" }, { "bg": "https://yastatic.net/s3/home/div/bottomsheet/bender/kote_test.png", "title": "Почему у кошек вертикальные зрачки?",     "subtitle": "Почему у кошек вертикальные зрачки?", "url": "http://ya.ru",     "time": "7:77" }]',
                %$video_translate,
            },
            page => {},
            wait => {
                video_translate => {
                    show => 1,
                    data => {
                        %$wait_video_translate_data,
                        template => 'image',
                        items => [ 
                            {
                                bg => 'https://yastatic.net/s3/home/div/bottomsheet/bender/kote_test.png',
                                title => 'Почему у кошек вертикальные зрачки?',
                                subtitle => 'Почему у кошек вертикальные зрачки?',
                                url  => 'http://ya.ru',
                                time => '7:77',
                            },
                            {
                                bg => 'https://yastatic.net/s3/home/div/bottomsheet/bender/kote_test.png',
                                title => 'Почему у кошек вертикальные зрачки?',
                                subtitle => 'Почему у кошек вертикальные зрачки?',
                                url  => 'http://ya.ru',
                                time => '7:77',
                            },
                        ],
                    }
                }
            },
        },
        {
            name => 'GetData: template=tabs, without items',
            video_translate => {
                template => 'tabs',
                %$video_translate,
            },
            tabs => $tabs,
            items => [],
            page => {},
            wait => {
                video_translate => {
                    show => 0,
                }
            },
        },
        {
            name => 'GetData: template=tabs, without tabs',
            video_translate => {
                template => 'tabs',
                %$video_translate,
            },
            tabs => [],
            items => $items,
            page => {},
            wait => {
                video_translate => {
                    show => 0,
                }
            },
        },
        {
            name => 'GetData: template=tabs, without video_translate',
            video_translate => {},
            tabs => $tabs,
            items => $items,
            page => {},
            wait => {
                video_translate => {
                    show => 0,
                }
            },
        },
        {
            name => 'GetData: template=image, without subtitle',
            video_translate => {
                template => 'image',
                items_json => '[{ "bg": "https://yastatic.net/s3/home/div/bottomsheet/bender/kote_test.png", "title": "Почему у кошек вертикальные зрачки?", "url": "http://ya.ru", "time": "7:77" }, { "bg": "https://yastatic.net/s3/home/div/bottomsheet/bender/kote_test.png", "title": "Почему у кошек вертикальные зрачки?", "url": "http://ya.ru", "time": "7:77" }]',
                %$video_translate,
            },
            page => {},
            wait => {
                video_translate => {
                    show => 0,
                }
            },
        },
        {
            name => 'GetData: template=text, without bg',
            video_translate => {
                template => 'text',
                items_json => '[{"title": "Ищите прямо на русском", "url": "http://ya.ru", "bg_color": "#EBE4FF", "bg_color_dark": "#EBE4FF" },{"title": "Ищите прямо на русском", "url": "http://ya.ru", "bg_color": "#EBE4FF", "bg_color_dark": "#EBE4FF" }]',
                %$video_translate,
            },
            page => {},
            wait => {
                video_translate => {
                    show => 0,
                }
            },
        },
    ];

    for my $d (@$test_data) {
        no warnings qw(redefine);
        local *MordaX::Block::Video_translate::_get_madm_data_video_translate = sub {
            return $d->{video_translate};
        };

        local *MordaX::Banners::instance = sub {
            return $self;
        };
        
        local *MordaX::Block::Video_translate::_get_tabs = sub {
            return $d->{tabs};
        };

        local *MordaX::Block::Video_translate::_get_items = sub {
            return $d->{items};
        };

        GetData($self, $self->{req}, $d->{page});
        is_deeply($d->{page}, $d->{wait}, $d->{name});
    }            
}

sub test__get_tabs : Test(4) {
    my $self = shift;

    *_get_tabs = \&MordaX::Block::Video_translate::_get_tabs;

    my $all_tabs = [
        {
            title => 'Автомобили',
            type => 'auto',
            url  => 'http://yandex.ru/auto'
        },
        {
            title => 'Технологии',
            type => 'tech',
            url  => 'http://yandex.ru/tech'
        },
        {
            title => 'Кухня',
            type => 'kitchen',
            url  => 'http://yandex.ru/kitchen'
        },
        {
            title => 'Путешествие',
            type => 'travel',
            url  => 'http://yandex.ru/travel'
        },
        {
            title => 'Кошки',
            type => 'cat',
            url  => 'http://yandex.ru/cat'
        },
        {
            title => 'Игры',
            type => 'games',
            url  => 'http://yandex.ru/games'
        },
    ];

    my $test_data = [
        {
            name => 'get_tabs: one user tab',
            all_tabs => $all_tabs,
            users_tabs => [
                {
                    title => 'Игры',
                    type => 'games',
                    url  => 'http://yandex.ru/games'
                },
            ],
            wait => [
                {
                    title => 'Игры',
                    type => 'games',
                    url  => 'http://yandex.ru/games'
                },
                {
                    title => 'Автомобили',
                    type => 'auto',
                    url  => 'http://yandex.ru/auto'
                },
                {
                    title => 'Технологии',
                    type => 'tech',
                    url  => 'http://yandex.ru/tech'
                },
                {
                    title => 'Кухня',
                    type => 'kitchen',
                    url  => 'http://yandex.ru/kitchen'
                },
            ]
        },
        {
            name => 'get_tabs: zero user tab',
            all_tabs => $all_tabs,
            users_tabs => [],
            wait => [
                {
                    title => 'Автомобили',
                    type => 'auto',
                    url  => 'http://yandex.ru/auto'
                },
                {
                    title => 'Технологии',
                    type => 'tech',
                    url  => 'http://yandex.ru/tech'
                },
                {
                    title => 'Кухня',
                    type => 'kitchen',
                    url  => 'http://yandex.ru/kitchen'
                },
                {
                    title => 'Путешествие',
                    type => 'travel',
                    url  => 'http://yandex.ru/travel'
                },
            ]
        },
        {
            name => 'get_tabs: 4 user tab',
            all_tabs => $all_tabs,
            users_tabs => [
                {
                    title => 'Игры',
                    type => 'games',
                    url  => 'http://yandex.ru/games'
                },
                {
                    title => 'Кухня',
                    type => 'kitchen',
                    url  => 'http://yandex.ru/kitchen'
                },
                {
                    title => 'Автомобили',
                    type => 'auto',
                    url  => 'http://yandex.ru/auto'
                },
                {
                    title => 'Технологии',
                    type => 'tech',
                    url  => 'http://yandex.ru/tech'
                },
            ],
            wait => [
                {
                    title => 'Игры',
                    type => 'games',
                    url  => 'http://yandex.ru/games'
                },
                {
                    title => 'Кухня',
                    type => 'kitchen',
                    url  => 'http://yandex.ru/kitchen'
                },
                {
                    title => 'Автомобили',
                    type => 'auto',
                    url  => 'http://yandex.ru/auto'
                },
                {
                    title => 'Технологии',
                    type => 'tech',
                    url  => 'http://yandex.ru/tech'
                },
            ]
        },
        {
            name => 'get_tabs: more than 4 user tab',
            all_tabs => $all_tabs,
            users_tabs => [
                {
                    title => 'Игры',
                    type => 'games',
                    url  => 'http://yandex.ru/games'
                },
                {
                    title => 'Кухня',
                    type => 'kitchen',
                    url  => 'http://yandex.ru/kitchen'
                },
                {
                    title => 'Автомобили',
                    type => 'auto',
                    url  => 'http://yandex.ru/auto'
                },
                {
                    title => 'Технологии',
                    type => 'tech',
                    url  => 'http://yandex.ru/tech'
                },
                {
                    title => 'Кошки',
                    type => 'cat',
                    url  => 'http://yandex.ru/cat'
                },
            ],
            wait => [
                {
                    title => 'Игры',
                    type => 'games',
                    url  => 'http://yandex.ru/games'
                },
                {
                    title => 'Кухня',
                    type => 'kitchen',
                    url  => 'http://yandex.ru/kitchen'
                },
                {
                    title => 'Автомобили',
                    type => 'auto',
                    url  => 'http://yandex.ru/auto'
                },
                {
                    title => 'Технологии',
                    type => 'tech',
                    url  => 'http://yandex.ru/tech'
                },
            ]
        },
    ];

    for my $d (@$test_data) {
        no warnings qw(redefine);
        local *MordaX::Block::Video_translate::_get_madm_data_video_translate_tabs_all = sub {
            return $d->{all_tabs};
        };

        local *MordaX::Block::Video_translate::_get_madm_data_video_translate_tabs = sub {
            return $d->{users_tabs};
        };
        
        local *MordaX::Utils::shuffle = sub {
            return @_;
        };

        is_deeply(_get_tabs($self), $d->{wait}, $d->{name});
    }            
}

sub test__get_items : Test(4) {
    my $self = shift;

    *_get_items = \&MordaX::Block::Video_translate::_get_items;

    my $all_items = {
        'auto' => [
            {
                title => 'auto1',
                url => 'url',
            },
            {
                title => 'auto2',
                url => 'url',
            },
            {
                title => 'auto3',
                url => 'url',
            },
            {
                title => 'auto4',
                url => 'url',
            },
            {
                title => 'auto5',
                url => 'url',
            },
        ],
        'tech' => [
            {
                title => 'tech1',
                url => 'url',
            },
            {
                title => 'tech2',
                url => 'url',
            },
            {
                title => 'tech3',
                url => 'url',
            },
            {
                title => 'tech4',
                url => 'url',
            },
        ],
        'kitchen' => [
            {
                title => 'kitchen1',
                url => 'url',
            },
            {
                title => 'kitchen2',
                url => 'url',
            },
            {
                title => 'kitchen3',
                url => 'url',
            },
            {
                title => 'kitchen4',
                url => 'url',
            },
            {
                title => 'kitchen5',
                url => 'url',
            },
            {
                title => 'kitchen6',
                url => 'url',
            },
        ],
    };

    my $test_data = [
        {
            name => 'get_items: simple',
            all_items => $all_items,
            tab => 'auto',
            wait => [
                {
                    title => 'auto1',
                    url => 'url',
                },
                {
                    title => 'auto2',
                    url => 'url',
                },
                {
                    title => 'auto3',
                    url => 'url',
                },
                {
                    title => 'auto4',
                    url => 'url',
                },
                {
                    title => 'auto5',
                    url => 'url',
                },
            ]
        },
        {
            name => 'get_items: less than 5',
            all_items => $all_items,
            tab => 'tech',
            wait => [
                {
                    title => 'tech1',
                    url => 'url',
                },
                {
                    title => 'tech2',
                    url => 'url',
                },
                {
                    title => 'tech3',
                    url => 'url',
                },
                {
                    title => 'tech4',
                    url => 'url',
                },
            ]
        },
        {
            name => 'get_items: more than 5',
            all_items => $all_items,
            tab => 'kitchen',
            wait => [
                {
                    title => 'kitchen1',
                    url => 'url',
                },
                {
                    title => 'kitchen2',
                    url => 'url',
                },
                {
                    title => 'kitchen3',
                    url => 'url',
                },
                {
                    title => 'kitchen4',
                    url => 'url',
                },
                {
                    title => 'kitchen5',
                    url => 'url',
                },
            ]
        },
        {
            name => 'get_items: tab does not exist',
            all_items => $all_items,
            tab => 'not_exists',
            wait => []
        },
    ];

    for my $d (@$test_data) {
        no warnings qw(redefine);
        local *MordaX::Block::Video_translate::_get_madm_data_video_translate_items = sub {
            return $d->{all_items};
        };

        is_deeply(_get_items($self, $d->{tab}), $d->{wait}, $d->{name});
    }            
}

sub TargetBlock {
    return 'video_translate';
}

sub get_flag_show_url {
    return $_[1];
}

sub get_flag_click_url {
    return $_[1];
}

1;
