package MordaX::Utils::Test;

use rules;

use Test::Most;
use base qw(Test::Class);

use MordaX::HTTP;

no  warnings 'experimental::smartmatch';

sub _startup : Test(startup) {
}

sub _setup : Test(setup) {
    my $self = shift;
}

sub test_shuffle_yuid : Test(6) {
    my $self = shift;

    *shuffle_yuid = \&MordaX::Utils::shuffle_yuid;

    ok(eq_set(shuffle_yuid({yandexuid_parsed => {ts => 1535382997}}, [1,2,3]), [1,2,3]));
    ok(eq_set(shuffle_yuid({yandexuid_parsed => {ts => 1535382997}}, []),           []));
    ok(eq_set(shuffle_yuid({yandexuid_parsed => {ts => undef}},      [1,2,3]), [1,2,3]));
    ok(eq_set(shuffle_yuid(undef,                                    [1,2,3]), [1,2,3]));

    ok(eq_array(
            shuffle_yuid({yandexuid_parsed => {ts => 1535382997}},[22,11,33]),
            shuffle_yuid({yandexuid_parsed => {ts => 1535382997}},[22,11,33]),
        )
    );

    ok(eq_set(
            shuffle_yuid(undef, [22,11,33]),
            shuffle_yuid(undef, [22,11,33]),
        )
    );
}

sub test_url_update_query : Test(6) {
    my $base = 'http://yandex.ru/';
    my %add  = (param => 'value_new', param2 => 'value2');

    is(MordaX::Utils::url_update_query($base), $base, $base);

    my $url1     = $base . '?param=value_old';
    my $correct1 = 'http://yandex.ru/?param=value_new&param2=value2';
    is(MordaX::Utils::url_update_query_slow($base, %add), $correct1, $correct1);
    is(MordaX::Utils::url_update_query_slow($url1, %add), $correct1, $correct1);

    # not sorted keys
    my @add  = (param => 'value_new', param2 => 'value2');
    $correct1 = 'http://yandex.ru/?param=value_new&param2=value2';
    is(MordaX::Utils::url_update_query_fast($base, @add), $correct1, $correct1);
    is(MordaX::Utils::url_update_query_fast($url1, @add), $correct1, $correct1);

    %add = (param => 'value_new');
    my $url2     = $base . '?param=value_old&param2=value2';
    my $correct2 = 'http://yandex.ru/?param=value_new&param2=value2';
    is(MordaX::Utils::url_update_query($url2, %add), $correct2, $correct2);
};

sub test_url_reduce_query : Test(3) {
    my $base = 'http://yandex.ru/';

    is(MordaX::Utils::url_reduce_query($base), $base, $base);

    my $url1 = $base . '?param1=value1';
    is(MordaX::Utils::url_reduce_query($url1, qw/param1/), $base, $base);

    my $url2 = $url1 . '&param2=value2';
    is(MordaX::Utils::url_reduce_query($url2, qw/param2/), $url1, $url1);
};

sub test_check_domain_key : Test(24) {
    my @tests = (
        ['all',        'ru',     1],
        ['all',        'com.tr', 1],
        ['ru',         'ru',     1],
        ['ee',         'ee',     1],
        ['all-com.tr', 'by',     1],
        ['all-com.tr', 'com.tr', 0],
        ['comtr',      'com.tr', 1],
        ['kub',        'ru',     1],
        ['kub',        'by',     1],
        ['kub',        'ua',     1],
        ['kub',        'kz',     1],
        ['kub',        'uz',     0],
        ['kubr-ua',    'ru',     1],
        ['kubr-ua',    'by',     1],
        ['kubr-ua',    'kz',     1],
        ['kubr-ua',    'ua',     0],
        ['kubru',      'kz',     1],
        ['kubru',      'ua',     1],
        ['kubru',      'by',     1],
        ['kubru',      'ru',     1],
        ['kubru',      'uz',     1],
        ['kubru',      'ee',     0],
        ['kubru',      'com.tr', 0],
        ['comtr',      'ru',     0],
    );

    for my $t (@tests) {
        ok((MordaX::Utils::check_domain_key(@$t[0,1]) ? 1 : 0) == $t->[2]);
    }
};

sub test_strip_messenger_text : Test(11) {
    my @tests = (
        ['Text',                       'Text', 'Just text'],
        ['Текст',                      'Текст', 'Just russian text'],
        ['__**```_____Текст⚡️⚡️',      'Текст', 'Russian text'],
        ['[```Text```](http://ya.ru)', 'Text', 'Text from link'],
        ['[[Text]](http://ya.ru)',     'Text', 'Text from double bracket link'],
        ['[[[Text]]]](http://ya.ru)',  'Text', 'Text from incorrect bracket link'],
        ['[Text](http://ya.ru/?m=())', 'Text', 'Text from empty bracket link'],
        ['```**__Text__**```',         'Text', 'Text tags'],
        ['***```**``Text__**```_____', 'Text', 'Text incorrect tags'],
        ['⚡️⚡️⚡️Text⚡️⚡️⚡️',         'Text', 'Emoji'],
        ['https://www.youtube.com/watch?v=NJyPtk3Dcfo', 'https://www.youtube.com/watch?v=NJyPtk3Dcfo', 'URL'],
    );

    for my $t (@tests) {
        is(MordaX::Utils::strip_messenger_text($t->[0]), $t->[1], $t->[2]);
    }
};

sub test_get_messenger_data : Test(10) {
    my @tests = (
        [{},                                              undef, 'Invalid input'],
        [1,                                               undef, 'Invalid input again'],
        [{Chats => []},                                   undef, 'Empty Chats'],
        [{Chats => 'hello'},                              undef, 'Invalid Chats'],
        [{Chats => [Messages => []]},                     undef, 'Empty Messages'],
        [{Chats => [Messages => 'chat closed']},          undef, 'Invalid Messages again'],
        [{Chats => [Messages => [{ServerMessage => 0}]]}, undef, 'Invalid Messages again and again'],
        [
            {
                Chats => [
                    {
                        Messages => [
                            {
                                ServerMessage => {
                                    ClientMessage => {
                                        Plain => {
                                            Text => 'Text0',
                                        },
                                    },
                                },
                            },
                        ],
                    },
                ],
            }, undef, 'One Text message',
        ],
        [
            {
                Chats => [
                    {
                        Messages => [
                            {
                                ServerMessage => {
                                    ClientMessage => {
                                        Plain => {
                                            Gallery => {
                                                Text => 'Text0'
                                            },
                                        },
                                    },
                                },
                            },
                        ],
                    },
                ],
            }, 'Text0', 'One Gallery message',
        ],
        [
            {
                Chats => [
                    {
                        Messages => [
                            {
                                ServerMessage => {
                                    ClientMessage => {
                                        Plain => {
                                            Text => {
                                                MessageText => 'Text0'
                                            },
                                        },
                                    },
                                },
                            },
                            {
                                ServerMessage => {
                                    ClientMessage => {
                                        Plain => {
                                            Text => {
                                                MessageText => 'Text1'
                                            },
                                        },
                                    },
                                },
                            },
                        ],
                    },
                ],
            }, 'Text1', 'Last Text message',
        ],
    );

    for my $t (@tests) {
        is((MordaX::Utils::get_messenger_data($t->[0])||[])->[0]{text}, $t->[1], $t->[2]);
    }
};

sub get_lists_diff : Test(5) {
    my @tests = (
        [['aba', 'caba'], ['caba'], ['aba'], 'first array has unique item'],
        [['caba'], ['aba', 'caba', 'cadabra'], ['aba', 'cadabra'], 'second array have unique items'],
        [['aba'], ['aba'], [], 'no unique items in arrays'],
        [['aba', 'aba'], ['caba'], ['aba', 'caba'], 'array with no unique items'],
        [[], [], [], 'empty arrays']
    );

    for my $t (@tests) {
        is_deeply(MordaX::Utils::get_lists_diff($t->[0], $t->[1]), $t->[2], $t->[3]);
    }
}

sub get_lists_intersection : Test(4) {
    my @tests = (
        [['aba', 'caba'], ['caba', 'cadabra'], ['caba'], 'arrays have intersecting items'],
        [['aba'], ['caba'], [], 'no intersecting items in arrays'],
        [['aba', 'aba'], ['caba'], [], 'array with no unique items'],
        [[], [], [], 'empty arrays']
    );

    for my $t (@tests) {
        is_deeply(MordaX::Utils::get_lists_intersection($t->[0], $t->[1]), $t->[2], $t->[3]);
    }
}

sub test_rotate_items : Test(80) {
    {
        my $in = [
            {type => 'a', order => 0},
            {type => 'b', order => 0},
            {type => 'c', order => 0},
        ];

        for (0..4) {
            my $out = MordaX::Utils::rotate_items($in);
            is(scalar(@$out), 1);
            ok($out->[0]{type} ~~ ['a', 'b', 'c']);
        }
    }
    {
        my $in = [
            {type => 'b', pos => 1},
            {type => 'a', pos => 0},
            {type => 'c', pos => 1},
            {type => 'e', pos => 2},
            {type => 'd', pos => 1},
            {type => 'f', pos => 2},
            {type => 'g', pos => 3},
            {type => 'h', pos => 4},
            {type => 'j', pos => 5},
            {type => 'i', pos => 4},
        ];

        for (0..9) {
            my $out = MordaX::Utils::rotate_items($in, 'pos');
            is(scalar(@$out), 6);
            ok($out->[0]{type} ~~ ['a']);
            ok($out->[1]{type} ~~ ['b', 'c', 'd']);
            ok($out->[2]{type} ~~ ['e', 'f']);
            ok($out->[3]{type} ~~ ['g']);
            ok($out->[4]{type} ~~ ['h', 'i']);
            ok($out->[5]{type} ~~ ['j']);
        }
    }
}

sub test_get_features : Test(2) {
    $|++;

    no warnings qw(redefine);

    local *MordaX::FcgiRequest::new = sub {
        return bless {}, shift;
    };

    local *MordaX::FcgiRequest::post_rawbody = sub {
        return '{"features":[{"enabled":false,"feature":"ya_plus2"},{"enabled":true,"feature":"account2"},{"enabled":true,"feature":"push_system_settings2"}]}'
    };

    local *MordaX::Utils::options = sub {return 0};
    local *MordaX::Type::is_api_search_2_only = sub {return 1};
    local *MordaX::Type::is_required_app_version = sub {return 1};
    local *MordaX::Type::is_yabrowser = sub {return 1};

    my $cgireq = MordaX::FcgiRequest->new;

    my @tests = (
        {
            req => {
                all_postargs => {
                    features => '[{"enabled":false,"feature":"ya_plus"},{"enabled":true,"feature":"account"},{"enabled":true,"feature":"push_system_settings"}]',
                }
            },
            expected => [
                {
                    enabled => bless( do{\(my $o = 0)}, 'JSON::PP::Boolean' ),
                    feature => 'ya_plus',
                },
                {
                    enabled => bless( do{\(my $o = 1)}, 'JSON::PP::Boolean' ),
                    feature => 'account',
                },
                {
                    enabled => bless( do{\(my $o = 1)}, 'JSON::PP::Boolean' ),
                    feature => 'push_system_settings',
                },
            ],
            name => 'old features format',
        },
        {
            req => {
                cgireq => $cgireq,
            },
            expected => [
                {
                    enabled => bless( do{\(my $o = 0)}, 'JSON::PP::Boolean' ),
                    feature => 'ya_plus2',
                },
                {
                    enabled => bless( do{\(my $o = 1)}, 'JSON::PP::Boolean' ),
                    feature => 'account2',
                },
                {
                    enabled => bless( do{\(my $o = 1)}, 'JSON::PP::Boolean' ),
                    feature => 'push_system_settings2',
                },
            ],
            name => 'new features format',
        }
    );

    for my $t (@tests) {
        is_deeply(MordaX::Utils::get_features($t->{req}), $t->{expected}, $t->{name} );
    }

}

1;
