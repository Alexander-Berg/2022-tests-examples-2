package Test::Smoo::Event::Push;
use parent 'Test::Class';

use Test::Most;
use MP::Logit qw(logit dmp);
use rules;

use Smoo::Event::Push;
use utf8;

sub startup : Tests(startup) {
    my $test = shift;
    $test->{cases} = [
        {
            input => {
                l10n => {
                    "msg"   => "Пробки 9 баллов — город стоит",
                    "title" => "Яндекс",
                    "url"   => "viewport://?text=%D0%BF%D1%80%D0%BE%D0%B1%D0%BA%D0%B8&viewport_id=serp&aoff=1&lr=43",
                },
                push => {
                    name            => 'somepush',
                    id              => '123',
                    master_event_id => 'android',
                    ttl_sup         => '1200',
                    sup_content_id  => 'ef8d62e9e6eccfe6a866494f57a285143673e60b',
                    ttvp            => '01:00:00',
                },
                locale => 'ru',
                target => {
                    id => '14',
                    condition => "tag:geo=='[geo]' && topic=='other' && app_id LIKE 'ru.yandex.searchplugin%' && (lang IN ('ru', 'en') || !lang) && !yandex_staff && (app_version LIKE '5.3%')",
                    url              => "morda://?card=webcard%2Fassist",
                    exp_id           => "EXP-2",
                    platform         => 'android',
                    platform_builder => 'default',
                    platform_project => 'searchapp',
                    topic_push       => 'topic_push',
                    topic_card       => 'topic_card',
                    no_notify        => 1,
                    transport_sup    => 'Native',
                  },
            },
            output => {
                Default => {
                    body => "Пробки 9 баллов — город стоит",
                },
                Appsearch_ios => {
                    body => "Пробки 9 баллов — город стоит",
                },
                push => {
                    id                => 'smoo.somepush.123',
                    title             => "Яндекс",
                    body              => "Пробки 9 баллов — город стоит",
                    url               => "morda://?card=webcard%2Fassist",
                    content_id        => 'ef8d62e9e6eccfe6a866494f57a285143673e60b',
                    throttle_policies => {
                        content_id => 'smoo_content_id_policy',
                    },
                    android_features => {
                        soundType => 1,
                        ledType   => 1,
                    },
                    ios_features => {
                        soundType => 1,
                    },
                    exp_id  => 'EXP-2',
                    ttl_sup => 1200,
                    ttl     => 1 * 60 * 60,
                    topic_push => 'topic_push',
                    topic_card => 'topic_card',
                    transport_sup => 'Native',
                    platform_project => 'searchapp',
                    tag        => 'somepush',
                    icon       => '',
                },
            },
        },
        {
            input => {
                l10n => {
                    "msg"     => "Пробки 9 баллов — город стоит",
                    "msg_ios" => "Пробки 9 баллов — город стоит. Быстрее будет на метро",
                    "title"   => "Яндекс",
                    "url"     => "viewport://?text=%D0%BF%D1%80%D0%BE%D0%B1%D0%BA%D0%B8&viewport_id=serp&aoff=1&lr=43",
                },
                push => {
                    name            => 'somepush',
                    id              => '777',
                    master_event_id => 'ios',
                    ttl_sup         => '1400',
                    ttvp            => '02:00:00',
                },
                locale => 'ru',
                target => {
                    id => '14',
                    condition => "tag:geo=='[geo]' && (app_id=='ru.yandex.mobile' || app_id=='ru.yandex.mobile.inhouse') && (lang IN ('ru', 'en') || !lang) && yandex_staff && (app_version LIKE '2.6%')",
                    platform         => 'ios',
                    platform_builder => 'appsearch_ios',
                    platform_project => 'searchapp',
                    transport_sup    => 'Xiva',
                  },
            },
            output => {
                Default => {
                    body => "Пробки 9 баллов — город стоит",
                },
                Appsearch_ios => {
                    body => "Пробки 9 баллов — город стоит. Быстрее будет на метро",
                  },
                push => {
                    id                => 'smoo.somepush.777',
                    title             => "Яндекс",
                    body              => "Пробки 9 баллов — город стоит. Быстрее будет на метро",
                    url               => "viewport://?text=%D0%BF%D1%80%D0%BE%D0%B1%D0%BA%D0%B8&viewport_id=serp&aoff=1&lr=43",
                    content_id        => 'smoo.somepush.ios',
                    throttle_policies => {
                        content_id => 'smoo_content_id_policy',
                    },
                    ttl_sup => 1400,
                    transport_sup => 'Xiva',
                    platform_project => 'searchapp',
                    icon    => '',
                  },
            },
        },
        # Test for alter icon
        {
            input => {
                l10n => {
                    "msg"     => "Пробки 9 баллов — город стоит",
                    "msg_ios" => "Пробки 9 баллов — город стоит. Быстрее будет на метро",
                    "title"   => "Яндекс",
                    "url"     => "viewport://?text=%D0%BF%D1%80%D0%BE%D0%B1%D0%BA%D0%B8&viewport_id=serp&aoff=1&lr=43",
                },
                push => {
                    name            => 'somepush',
                    id              => '777',
                    master_event_id => 'ios_icon',
                    ttl_sup         => '1400',
                    ttvp            => '02:00:00',
                },
                locale => 'ru',
                target => {
                    id => '14',
                    condition => "tag:geo=='[geo]' && (app_id=='ru.yandex.mobile' || app_id=='ru.yandex.mobile.inhouse') && (lang IN ('ru', 'en') || !lang) && yandex_staff && (app_version LIKE '2.6%')",
                    platform         => 'ios',
                    platform_builder => 'appsearch_ios',
                    platform_project => 'searchapp',
                    icon             => 'http://my/super/icon.png',
                    transport_sup    => 'Native',
                  },
            },
            output => {
                Default => {
                    body => "Пробки 9 баллов — город стоит",
                },
                Appsearch_ios => {
                    body => "Пробки 9 баллов — город стоит. Быстрее будет на метро",
                  },
                push => {
                    id                => 'smoo.somepush.777',
                    title             => "Яндекс",
                    body              => "Пробки 9 баллов — город стоит. Быстрее будет на метро",
                    url               => "viewport://?text=%D0%BF%D1%80%D0%BE%D0%B1%D0%BA%D0%B8&viewport_id=serp&aoff=1&lr=43",
                    content_id        => 'smoo.somepush.ios_icon',
                    throttle_policies => {
                        content_id => 'smoo_content_id_policy',
                    },
                    ttl_sup => 1400,
                    icon => 'http://my/super/icon.png',
                    transport_sup => 'Native',
                    platform_project => 'searchapp',
                  },
            },
        },
        # Test new url schema
        {
            input => {
                l10n => {
                    "msg"     => "Пробки 9 баллов — город стоит",
                    "msg_ios" => "Пробки 9 баллов — город стоит. Быстрее будет на метро",
                    "title"   => "Яндекс",
                    "url"     => { default => "viewport://?text=%D0%BF%D1%80%D0%BE%D0%B1%D0%BA%D0%B8&viewport_id=serp&aoff=1&lr=43" },
                },
                push => {
                    name            => 'somepush',
                    id              => '777',
                    master_event_id => 'ios_urls',
                    ttl_sup         => '1400',
                    ttvp            => '02:00:00',
                },
                locale => 'ru',
                target => {
                    id => '14',
                    condition => "tag:geo=='[geo]' && (app_id=='ru.yandex.mobile' || app_id=='ru.yandex.mobile.inhouse') && (lang IN ('ru', 'en') || !lang) && yandex_staff && (app_version LIKE '2.6%')",
                    platform         => 'ios',
                    platform_builder => 'appsearch_ios',
                    transport_sup    => 'Native',
                    platform_project => 'searchapp',
                  },
            },
            output => {
                Default => {
                    body => "Пробки 9 баллов — город стоит",
                },
                Appsearch_ios => {
                    body => "Пробки 9 баллов — город стоит. Быстрее будет на метро",
                  },
                push => {
                    id                => 'smoo.somepush.777',
                    title             => "Яндекс",
                    body              => "Пробки 9 баллов — город стоит. Быстрее будет на метро",
                    url               => "viewport://?text=%D0%BF%D1%80%D0%BE%D0%B1%D0%BA%D0%B8&viewport_id=serp&aoff=1&lr=43",
                    content_id        => 'smoo.somepush.ios_urls',
                    throttle_policies => {
                        content_id => 'smoo_content_id_policy',
                    },
                    ttl_sup => 1400,
                    transport_sup => 'Native',
                    platform_project => 'searchapp',
                    icon => '',
                  },
            },
        },
        {
            input => {
                l10n => {
                    "msg"     => "Пробки 9 баллов — город стоит",
                    "msg_ios" => "Пробки 9 баллов — город стоит. Быстрее будет на метро",
                    "title"   => "Яндекс",
                    "url"     => { default => "viewport://?text=%D0%BF%D1%80%D0%BE%D0%B1%D0%BA%D0%B8&viewport_id=serp&aoff=1&lr=43" },
                },
                push => {
                    name            => 'somepush',
                    id              => '777',
                    master_event_id => 'ios_urls_default',
                    ttl_sup         => '1400',
                    ttvp            => '02:00:00',
                },
                locale => 'ru',
                target => {
                    id => '14',
                    condition => "tag:geo=='[geo]' && (app_id=='ru.yandex.mobile' || app_id=='ru.yandex.mobile.inhouse') && (lang IN ('ru', 'en') || !lang) && yandex_staff && (app_version LIKE '2.6%')",
                    platform         => 'ios',
                    platform_builder => 'appsearch_ios',
                    platform_project => 'searchapp',
                    transport_sup    => 'Native',
                  },
            },
            output => {
                Default => {
                    body => "Пробки 9 баллов — город стоит",
                },
                Appsearch_ios => {
                    body => "Пробки 9 баллов — город стоит. Быстрее будет на метро",
                  },
                push => {
                    id                => 'smoo.somepush.777',
                    title             => "Яндекс",
                    body              => "Пробки 9 баллов — город стоит. Быстрее будет на метро",
                    url               => "viewport://?text=%D0%BF%D1%80%D0%BE%D0%B1%D0%BA%D0%B8&viewport_id=serp&aoff=1&lr=43",
                    content_id        => 'smoo.somepush.ios_urls_default',
                    throttle_policies => {
                        content_id => 'smoo_content_id_policy',
                    },
                    ttl_sup => 1400,
                    transport_sup => 'Native',
                    platform_project => 'searchapp',
                    icon => '',
                  },
            },
        },
        # url-key ok
        {
            input => {
                l10n => {
                    "msg"     => "Пробки 9 баллов — город стоит",
                    "msg_ios" => "Пробки 9 баллов — город стоит. Быстрее будет на метро",
                    "title"   => "Яндекс",
                    "url"     => {
                        default => "viewport://?text=%D0%BF%D1%80%D0%BE%D0%B1%D0%BA%D0%B8&viewport_id=serp&aoff=1&lr=43",
                        mykey => 'http://example.com',
                    },
                },
                push => {
                    name            => 'somepush',
                    id              => '777',
                    master_event_id => 'ios_url_key',
                    ttl_sup         => '1400',
                    ttvp            => '02:00:00',
                },
                locale => 'ru',
                target => {
                    id => '14',
                    condition => "tag:geo=='[geo]' && (app_id=='ru.yandex.mobile' || app_id=='ru.yandex.mobile.inhouse') && (lang IN ('ru', 'en') || !lang) && yandex_staff && (app_version LIKE '2.6%')",
                    platform         => 'ios',
                    platform_builder => 'appsearch_ios',
                    url              => 'key:mykey',
                    transport_sup    => 'Native',
                    platform_project => 'searchapp',
                  },
            },
            output => {
                Default => {
                    body => "Пробки 9 баллов — город стоит",
                },
                Appsearch_ios => {
                    body => "Пробки 9 баллов — город стоит. Быстрее будет на метро",
                  },
                push => {
                    id                => 'smoo.somepush.777',
                    title             => "Яндекс",
                    body              => "Пробки 9 баллов — город стоит. Быстрее будет на метро",
                    url               => "http://example.com",
                    content_id        => 'smoo.somepush.ios_url_key',
                    throttle_policies => {
                        content_id => 'smoo_content_id_policy',
                    },
                    ttl_sup => 1400,
                    transport_sup => 'Native',
                    platform_project => 'searchapp',
                    icon => '',
                  },
            },
        },
        # url-key fail
        {
            input => {
                l10n => {
                    "msg"     => "Пробки 9 баллов — город стоит",
                    "msg_ios" => "Пробки 9 баллов — город стоит. Быстрее будет на метро",
                    "title"   => "Яндекс",
                    "url"     => {
                        default => "viewport://?text=%D0%BF%D1%80%D0%BE%D0%B1%D0%BA%D0%B8&viewport_id=serp&aoff=1&lr=43",
                        mykey => 'http://example.com',
                    },
                },
                push => {
                    name            => 'somepush',
                    id              => '777',
                    master_event_id => '888',
                    ttl_sup         => '1400',
                    ttvp            => '02:00:00',
                },
                locale => 'ru',
                target => {
                    id => '14',
                    condition => "tag:geo=='[geo]' && (app_id=='ru.yandex.mobile' || app_id=='ru.yandex.mobile.inhouse') && (lang IN ('ru', 'en') || !lang) && yandex_staff && (app_version LIKE '2.6%')",
                    platform         => 'ios',
                    platform_builder => 'appsearch_ios',
                    platform_project => 'searchapp',
                    url              => 'key:mykey2',
                    transport_sup    => 'Native',
                  },
            },
            output => {
                Default => {
                    body => "Пробки 9 баллов — город стоит",
                },
                Appsearch_ios => {
                    body => "Пробки 9 баллов — город стоит. Быстрее будет на метро",
                  },
                push => undef,
            },
        },
        # uniq_postfix
        {
            input => {
                l10n => {
                    "msg"     => "Пробки 9 баллов — город стоит",
                    "msg_ios" => "Пробки 9 баллов — город стоит. Быстрее будет на метро",
                    "title"   => "Яндекс",
                    "url"     => {
                        default => "viewport://?text=%D0%BF%D1%80%D0%BE%D0%B1%D0%BA%D0%B8&viewport_id=serp&aoff=1&lr=43",
                    },
                },
                push => {
                    name            => 'somepush',
                    id              => '777',
                    master_event_id => 'ios_postfix',
                    ttl_sup         => '1400',
                    ttvp            => '02:00:00',
                    data            => {
                        uniq_postfix => 'm123456',
                    },
                },
                locale => 'ru',
                target => {
                    id => '14',
                    condition => "tag:geo=='[geo]' && (app_id=='ru.yandex.mobile' || app_id=='ru.yandex.mobile.inhouse') && (lang IN ('ru', 'en') || !lang) && yandex_staff && (app_version LIKE '2.6%')",
                    platform         => 'ios',
                    platform_builder => 'appsearch_ios',
                    platform_project => 'searchapp',
                    transport_sup    => 'Native',
                  },
            },
            output => {
                Default => {
                    body => "Пробки 9 баллов — город стоит",
                },
                Appsearch_ios => {
                    body => "Пробки 9 баллов — город стоит. Быстрее будет на метро",
                  },
                push => {
                    id                => 'smoo.somepush_m123456.777',
                    title             => "Яндекс",
                    body              => "Пробки 9 баллов — город стоит. Быстрее будет на метро",
                    url               => "viewport://?text=%D0%BF%D1%80%D0%BE%D0%B1%D0%BA%D0%B8&viewport_id=serp&aoff=1&lr=43",
                    content_id        => 'smoo.somepush.ios_postfix',
                    throttle_policies => {
                        content_id => 'smoo_content_id_policy',
                    },
                    ttl_sup => 1400,
                    transport_sup => 'Native',
                    platform_project => 'searchapp',
                    icon => '',
                  },
            },
        },
        {
            input => {
                l10n => {
                    "msg"     => "Пробки 9 баллов — город стоит",
                    "msg_ios" => "Пробки 9 баллов — город стоит. Быстрее будет на метро",
                    "title"   => "Яндекс",
                    "url"     => {
                        default => "viewport://?text=%D0%BF%D1%80%D0%BE%D0%B1%D0%BA%D0%B8&viewport_id=serp&aoff=1&lr=43",
                    },
                },
                push => {
                    name            => 'somepush',
                    id              => '777',
                    master_event_id => 'launcher',
                    ttl_sup         => '1400',
                    ttvp            => '02:00:00',
                },
                locale => 'ru',
                target => {
                    id => '14',
                    condition => "tag:geo=='[geo]' && (app_id=='ru.yandex.launcher')",
                    platform         => 'yaphone_launcher',
                    platform_builder => 'yaphone_launcher',
                    platform_project => 'mobyabro',
                    transport_sup    => 'Native',
                  },
            },
            output => {
                Default => {
                    body => "Пробки 9 баллов — город стоит",
                },
                Yaphone_launcher => {
                    body => "Пробки 9 баллов — город стоит",
                    android_features => {
                        counter   => 5,
                        group     => 'phone-launcher-card',
                        priority  => 1,
                        timestamp => '1538503807000',
                    },
                },
                Appsearch_ios => {
                    body             => "Пробки 9 баллов — город стоит. Быстрее будет на метро",
                },
                push => {
                    id                => 'smoo.somepush.777',
                    title             => "Яндекс",
                    body              => "Пробки 9 баллов — город стоит",
                    url               => "viewport://?text=%D0%BF%D1%80%D0%BE%D0%B1%D0%BA%D0%B8&viewport_id=serp&aoff=1&lr=43",
                    content_id        => 'smoo.somepush.launcher',
                    throttle_policies => {
                        content_id => 'smoo_content_id_policy',
                    },
                    ttl_sup => 1400,
                    transport_sup => 'Native',
                    platform_project => 'mobyabro',
                    android_features => {
                        counter => 5,
                        group => 'phone-launcher-card',
                        priority => 1,
                    },
                    icon => '',
                  },
            },
        },
    ];
}

sub get_builder : Tests {
    is(ref Smoo::Event::Push::get_builder({ platform_builder => 'appsearch_ios' }), 'CODE');
    is(ref Smoo::Event::Push::get_builder({ platform_builder => 'yaphone_launcher' }), 'CODE');
    is(ref Smoo::Event::Push::get_builder({ platform_builder => 'default' }),       'CODE');
    is(ref Smoo::Event::Push::get_builder({ platform_builder => 'smth' }),          '');
    is(ref Smoo::Event::Push::get_builder({}), '');
}

sub make : Tests {
    my $test = shift;
    for my $case (@{$test->{cases}}) {
        my $input  = $case->{input};
        my $output = $case->{output}->{push};
        my $push = Smoo::Event::Push::make(
            push     => $input->{push},
            l10n     => $input->{l10n},
            target   => $input->{target},
            locale   => $input->{locale},
        );
        if ($push && $push->{android_features}) {
            delete $push->{android_features}->{timestamp};
        }
        is_deeply($push, $output) or note explain { got => $push, expected => $output };
    }
}

sub count_push_ttl : Tests {
    is (Smoo::Event::Push::count_ttvp_in_sec('01:00:00'), 1*60*60);
    is (Smoo::Event::Push::count_ttvp_in_sec('00:00:00'), 0);
    is (Smoo::Event::Push::count_ttvp_in_sec('00:00:15'), 15);
    is (Smoo::Event::Push::count_ttvp_in_sec('01:00:15'), 1*60*60+15);
    is (Smoo::Event::Push::count_ttvp_in_sec('00:30:15'), 30*60+15);
}

sub icon : Tests {
    my $icon = "https://yastatic.net/s3/home/apisearch/alice_icon.png";
    # empty icon
    is_deeply(Smoo::Event::Push::_make_icon({}, {}), { icon => '' });
    # icon from target
    is_deeply(Smoo::Event::Push::_make_icon({}, { icon => $icon }), { icon => $icon });
    # icon from targer with i
    is_deeply(Smoo::Event::Push::_make_icon({}, { icon => $icon . ';i=1' }), { icon => $icon, i => 1 });
    # icon from event
    is_deeply(Smoo::Event::Push::_make_icon({ icon_key => $icon }, { icon => 'key:icon_key' }), { icon => $icon });
    # icon from event with i
    is_deeply(Smoo::Event::Push::_make_icon({ icon_key => $icon . ';i=2' }, { icon => 'key:icon_key' }), { icon => $icon, i => 2 });
    # no value for key
    is(Smoo::Event::Push::_make_icon({ some_key => $icon }, { icon => 'key:icon_key' }), undef);
}

sub expireat : Tests {
    is(Smoo::Event::Push::_make_expireat(), 0);
    is(Smoo::Event::Push::_make_expireat({ name => 'random' }), 0);
    is(Smoo::Event::Push::_make_expireat(
            { name => 'random' }, { platform => 'appsearch_ios' }, 10),
        0);
    is(Smoo::Event::Push::_make_expireat(
            { name => 'random' }, { platform => 'desktop_yabro' }, 10),
        (time + 10) * 1000);
    is(Smoo::Event::Push::_make_expireat(
            { name => 'weather_tomorrow' }, { platform => 'desktop_yabro' }, 10, 20),
        (time + 10 + 20) * 1000);
    is(Smoo::Event::Push::_make_expireat(
            { name => 'weather_tomorrow_alice' }, { platform => 'desktop_yabro' }, 10, 20),
        (time + 10 + 20) * 1000);
    is(Smoo::Event::Push::_make_expireat(
            { name => 'exp_weather_tomorrow_alice' }, { platform => 'desktop_yabro' }, 10, 20),
        (time + 10 + 20) * 1000);
}

sub make_featutes : Tests {
    is_deeply(Smoo::Event::Push::_make_features(), {});
    is_deeply(Smoo::Event::Push::_make_features({}, { platform => 'appsearch_ios' }), {});
    is_deeply(Smoo::Event::Push::_make_features({}, { platform => 'desktop_yabro' }), {});
    is_deeply(Smoo::Event::Push::_make_features({}, { platform => 'desktop_yabro', features => { image => "myimg" } }),
        { browser_features => { image => "myimg" } });
    is_deeply(Smoo::Event::Push::_make_features({ web => 'weblink' }, { platform => 'desktop_yabro', features => { fallbackLink => "key:web" } }),
        { browser_features => { fallbackLink => "weblink" } });
    is_deeply(Smoo::Event::Push::_make_features({ web => 'weblink' }, { platform => 'desktop_yabro', features => { fallbackLink => "key:newweb" } }),
        { browser_features => {} });
}
1;
