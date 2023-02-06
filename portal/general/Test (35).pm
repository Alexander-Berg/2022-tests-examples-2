package MordaX::Block::BigB::Test;

use rules;

use Test::Most;
use base qw(Test::Class);

use MordaX::Block::BigB;
use MP::Logit;

sub _startup : Test(startup) {}

sub _setup : Test(setup) {}

sub test_decay_counter_value : Test(2) {
    my $self = shift;

    *_decay_counter_value = \&MordaX::Block::BigB::_decay_counter_value;

    my $updatetime = 3600 * 24 * 7;
    my $now = 3600 * 24 * 14;
    my $value = 2;
    my $decay_coef = 0.7;

    # С $decay_coef=0.7 за неделю затухание близко к 1 
    ok(1 > _decay_counter_value($value, $updatetime, $now, $decay_coef));
    ok(0.99 < _decay_counter_value($value, $updatetime, $now, $decay_coef));
}

sub test_get_mapping_of_services : Test(1) {
    my $self = shift;

    *get_mapping_of_services = \&MordaX::Block::BigB::get_mapping_of_services;

    no warnings qw(redefine);
    local *MordaX::Data_get::get_static_data = sub {
        return [
            {name => 'music'},
            {name => 'efir'},
        ]
    };

    my $out = {
        1808969537 => {name => 'efir'},
        3444712010 => {name => 'music'},
    };
    is_deeply(get_mapping_of_services({}), $out);

}

sub test_download_blender : Test(1) {
    my $self = shift;

    *download = \&MordaX::Block::BigB::download;

    no warnings qw(redefine once);
    local *MordaX::Experiment::AB::flags = sub { MordaX::Experiment::AB::Flags::instance($_[0], 'MUTE_WARNINGS'); };
    local *MordaX::Options::options = sub {
        return 1 if ($_[0] eq 'disable_bigb_protobuf_json');
    };
    local *alias_exists = sub {1};
    local *result_req_info = sub {{success => 1, response_content => 1}};
    local *MordaX::HTTP::new = sub {$self};
    local *MordaX::Utils::is_option_turned_by_host = sub {0};
    local *MP::Utils::parse_json = sub {
        return {
            data => [
                {
                    is_full => 1,
                    segment => [
                        {
                            id => 175,
                            name => 'krypta-user-age',
                        },
                        {
                            id => 100,
                            name => 'sonething',
                        },
                        {
                            id => 281,
                            name => 'krypta-marketing',
                        },
                        {
                            id => 328,
                            counter_id => 1071,
                            name => 'bt-counter',
                        },
                        {
                            id => 328,
                            counter_id => 1070,
                            name => 'bt-counter',
                        },
                    ]
                }
            ],
        };
    };
    local *MordaX::Data_get::get_static_data = sub {
        return if $_[1] ne 'bigb_keywords';

        return {
            keywords_blender => '174 175 216 281 543 547 614',
            counters_blender => '1071 1072'
        };
    };

    my $req = {};

    download($req);
    my $data_bass = [
        {
            id => 175,
            name => 'krypta-user-age',
        },
        {
            id => 281,
            name => 'krypta-marketing',
        },
        {
            id => 328,
            counter_id => 1071,
            name => 'bt-counter',
        },
    ];

    is_deeply($req->{TargetingInfo}{data_bass}, $data_bass);
}

sub test_have_promo_groups : Test(8) {
    my $self = shift;

    *have_promo_groups = \&MordaX::Block::BigB::have_promo_groups;

    no warnings qw(redefine);
    local *MordaX::Block::BigB::download = sub {};

    my $req = {
        TargetingInfoComplete => 1,
        TargetingInfo => {
            'promo-groups' => {
                '111:222' => 1,
                '333:444' => 1,
                '555:666' => 1,
            }
        }
    };

    is(have_promo_groups($req, ['111:222', '555:777']), 1);
    is(have_promo_groups($req, ['111:222', '555:666', '333:444']), 1);
    is(have_promo_groups($req, ['000:222', '555:777']), 0);
    is(have_promo_groups($req, '111:222'), 1);
    is(have_promo_groups($req, '000:222'), 0);
    is(have_promo_groups($req, ''), 0);
    is(have_promo_groups($req), 0);
    my $TargetingInfo_without_changes = {
            'promo-groups' => {
                '111:222' => 1,
                '333:444' => 1,
                '555:666' => 1,
            }
    };
    is_deeply($req->{TargetingInfo}, $TargetingInfo_without_changes);
}

sub test_have_promo_groups_and : Test(11) {
    my $self = shift;

    no warnings qw(redefine);
    *have_promo_groups = \&MordaX::Block::BigB::have_promo_groups_and;

    local *MordaX::Block::BigB::download = sub {};

    my $req = {
        TargetingInfoComplete => 1,
        TargetingInfo => {
            'promo-groups' => {
                '111:222' => 1,
                '333:444' => 1,
                '555:666' => 1,
            }
        }
    };

    is(have_promo_groups($req, '111:222'), 1);
    is(have_promo_groups($req, '000:222'), 0);
    is(have_promo_groups($req, '111:222,000:222'), 1);
    is(have_promo_groups($req, '000:222,000:333'), 0);
    is(have_promo_groups($req, '111:222&333:444'), 1);
    is(have_promo_groups($req, '000:222,111:222&333:444'), 1);
    is(have_promo_groups($req, ' 000:222 , 111:222 & 333:444 '), 1);
    is(have_promo_groups($req, '111:222&000:444'), 0);

    is(have_promo_groups($req, ''), 0);
    is(have_promo_groups($req), 0);
    my $TargetingInfo_without_changes = {
            'promo-groups' => {
                '111:222' => 1,
                '333:444' => 1,
                '555:666' => 1,
            }
    };
    is_deeply($req->{TargetingInfo}, $TargetingInfo_without_changes);
}

sub test_process_counter_count_group : Test(1) {
    my $self = shift;

    no warnings qw(redefine);
    local *process_counter_count_group = \&MordaX::Block::BigB::process_counter_count_group;

    my $args = {
        counter_id => 1067,
        name       => 'zen',
        type       => 'visits_main_page_mobile',
        value      => '-0.01336487941'
    };
    my $targeting_info =  {
        recently_services => {
            visits_common => {
                realty => {
                    name   => 'realty',
                    weight => '1.977642298'
                }
            }
        }
    };
    my $result = {
        recently_services => {
            visits_common => {
                realty => {
                    name   => 'realty',
                    weight => '1.977642298'
                }
            },
            visits_main_page_mobile => {
                zen => {
                    name   => 'zen',
                    weight => '-0.01336487941'
                }
            }
        }
    };

    process_counter_count_group($targeting_info, $args);
    is_deeply($targeting_info, $result, 'process_counter_count_group');
}

sub test_process_counter_time_group : Test(1) {
    my $self = shift;

    no warnings qw(redefine);
    local *process_counter_time_group = \&MordaX::Block::BigB::process_counter_time_group;

    my $args = {
        counter_id => 1072,
        name       => 'disk',
        type       => 'visits_dacay_1_4_common',
        value      => 1614844022,
    };
    my $targeting_info = {
        recently_services => {
            visits_dacay_1_4_common => {
                disk => {
                    name   => 'disk',
                    weight => '0.9070225358',
                }
            }
        }
    };
    my $result = {
        recently_services => {
            visits_dacay_1_4_common => {
                disk => {
                    name       => 'disk',
                    updatetime => 1614844022,
                    weight     => '0.9070225358'
                }
            }
        }
    };

    process_counter_time_group($targeting_info, $args);
    is_deeply($targeting_info, $result, 'process_counter_time_group');
}


sub test_process_counter_item_recently_services : Test(1) {
    my $self = shift;

    no warnings qw(redefine);
    local *process_counter_item_recently_services = \&MordaX::Block::BigB::process_counter_item_recently_services;
    local *MordaX::Block::BigB::_get_service_by_int = sub {
        if ($_[1] == 3444712010) {
            return {
                name   => "music",
                weight => 60,
            };
        };

        return;
    };

    my $counter = {
        counter_id => 1071,
        key => [
            3444712010,
        ],
        value => [
            '1.999655128',
        ],
    };
    my $targeting_info = {};
    my $result = {
        recently_services => {
            visits_dacay_1_4_common => {
                music => {
                    name => 'music',
                    weight => '1.999655128',
                }
            }
        }
    };

    process_counter_item_recently_services({}, $targeting_info, $counter);
    is_deeply($targeting_info, $result, 'process_counter_item_recently_services');
}

sub test_process_counter_item_stateful_search_loggedin_without_enabled_flag : Test(1) {
    my $self = shift;

    no warnings qw(redefine);
    local *MordaX::Experiment::AB::flags = sub { $self };
    local *get = *get_bool = sub { undef };
    local *process_counter_item_stateful_search = \&MordaX::Block::BigB::process_counter_item_stateful_search;
    local *MordaX::Block::BigB::_get_search_theme_by_int = sub {
        return 'pregnancy' if $_[1] eq 1001;
        return 'travel' if $_[1] eq 1002;
        return 'career' if $_[1] eq 1003;
        return undef;
    };

    my $counters = [
        { counter_id => 2207, key => [1001, 1002, 1003, 1234], value => [1644924394, 1644924394, 1644924394, 1234] },
        { counter_id => 2208, key => [1001, 1002, 1003, 1234], value => [0, 25, 1, 1234] },
        { counter_id => 2209, key => [1001, 1002, 1003, 1234], value => [1644924394, 1644924394, 1644924394, 1234] },
        { counter_id => 2210, key => [1001, 1002, 1003, 1234], value => [0, 0, 1, 1234] },
        { counter_id => 2212, key => [1001, 1002, 1003, 1234], value => [0, 1, 1, 1234] },
        { counter_id => 1234, key => [1001], value => [888, 999] },
    ];

    my $targeting_info = {};
    for my $counter (@$counters) {
        process_counter_item_stateful_search({UID => 1}, $targeting_info, $counter);
    }

    my $expected = {};
    is_deeply($targeting_info, $expected, 'process_counter_item_stateful_search_loggedin_without_enabled_flag');
}

sub test_process_counter_item_stateful_search_loggedin : Test(1) {
    my $self = shift;

    my $test_flags = {
        stateful_search => 1,
    };

    no warnings qw(redefine);
    local *MordaX::Experiment::AB::flags = sub { $self };
    local *get = *get_bool = sub { $test_flags->{$_[1]} };
    local *process_counter_item_stateful_search = \&MordaX::Block::BigB::process_counter_item_stateful_search;
    local *MordaX::Block::BigB::_get_search_theme_by_int = sub {
        return 'pregnancy' if $_[1] eq 1001;
        return 'travel' if $_[1] eq 1002;
        return 'career' if $_[1] eq 1003;
        return undef;
    };

    my $counters = [
        { counter_id => 2207, key => [1001, 1002, 1003, 1234], value => [1644924394, 1644924394, 1644924394, 1234] },
        { counter_id => 2208, key => [1001, 1002, 1003, 1234], value => [0, 25, 1, 1234] },
        { counter_id => 2209, key => [1001, 1002, 1003, 1234], value => [1644924394, 1644924394, 1644924394, 1234] },
        { counter_id => 2210, key => [1001, 1002, 1003, 1234], value => [0, 0, 1, 1234] },
        { counter_id => 2212, key => [1001, 1002, 1003, 1234], value => [0, 1, 1, 1234] },
        { counter_id => 1234, key => [1001], value => [888, 999] },
    ];

    my $targeting_info = {};
    for my $counter (@$counters) {
        process_counter_item_stateful_search({UID => 1}, $targeting_info, $counter);
    }

    my $expected = {
        stateful_search => {
            pregnancy => {
                name => 'pregnancy',
                theme_id => 1001,
                search_query_cnt => 0,
                enabled => 0,
                refused => 0,
                update_time => 1644924394,
            },
            travel => {
                name => 'travel',
                theme_id => 1002,
                search_query_cnt => 25,
                enabled => 0,
                refused => 1,
                update_time => 1644924394,
            },
            career => {
                name => 'career',
                theme_id => 1003,
                search_query_cnt => 1,
                enabled => 1,
                refused => 1,
                update_time => 1644924394,
            },
        },
    };

    is_deeply($targeting_info, $expected, 'process_counter_item_stateful_search_loggedin');
}

sub test_process_counter_item_stateful_search_loggedin_not_glued_counters : Test(1) {
    my $self = shift;

    my $test_flags = {
        stateful_search => 1,
        bigb_stateful_search_not_glued_counters => 1,
    };

    no warnings qw(redefine);
    local *MordaX::Experiment::AB::flags = sub { $self };
    local *get = *get_bool = sub { $test_flags->{$_[1]} };
    local *process_counter_item_stateful_search = \&MordaX::Block::BigB::process_counter_item_stateful_search;
    local *MordaX::Block::BigB::_get_search_theme_by_int = sub {
        return 'pregnancy' if $_[1] eq 1001;
        return 'travel' if $_[1] eq 1002;
        return 'career' if $_[1] eq 1003;
        return undef;
    };

    my $counters = [
        { counter_id => 2281, key => [1001, 1002, 1003, 1234], value => [1644924394, 1644924394, 1644924394, 1234] },
        { counter_id => 2282, key => [1001, 1002, 1003, 1234], value => [0, 25, 1, 1234] },
        { counter_id => 2283, key => [1001, 1002, 1003, 1234], value => [1644924394, 1644924394, 1644924394, 1234] },
        { counter_id => 2284, key => [1001, 1002, 1003, 1234], value => [0, 0, 1, 1234] },
        { counter_id => 2286, key => [1001, 1002, 1003, 1234], value => [0, 1, 1, 1234] },
        { counter_id => 1234, key => [1001], value => [888, 999] },
    ];

    my $targeting_info = {};
    for my $counter (@$counters) {
        process_counter_item_stateful_search({UID => 1}, $targeting_info, $counter);
    }

    my $expected = {
        stateful_search => {
            pregnancy => {
                name => 'pregnancy',
                theme_id => 1001,
                search_query_cnt => 0,
                enabled => 0,
                refused => 0,
                update_time => 1644924394,
            },
            travel => {
                name => 'travel',
                theme_id => 1002,
                search_query_cnt => 25,
                enabled => 0,
                refused => 1,
                update_time => 1644924394,
            },
            career => {
                name => 'career',
                theme_id => 1003,
                search_query_cnt => 1,
                enabled => 1,
                refused => 1,
                update_time => 1644924394,
            },
        },
    };

    is_deeply($targeting_info, $expected, 'process_counter_item_stateful_search_loggedin_not_glued_counters');
}

sub test_process_counter_item_stateful_search_withoutlogin : Test(1) {
    my $self = shift;

    my $test_flags = {
        stateful_search => 1,
    };

    no warnings qw(redefine);
    local *MordaX::Experiment::AB::flags = sub { $self };
    local *get = *get_bool = sub { $test_flags->{$_[1]} };
    local *process_counter_item_stateful_search = \&MordaX::Block::BigB::process_counter_item_stateful_search;
    local *MordaX::Block::BigB::_get_search_theme_by_int = sub {
        return 'pregnancy' if $_[1] eq 1001;
        return 'travel' if $_[1] eq 1002;
        return 'career' if $_[1] eq 1003;
        return undef;
    };

    my $counters = [
        { counter_id => 2289, key => [1001, 1002, 1003, 1234], value => [1644924394, 1644924394, 1644924394, 1234] },
        { counter_id => 2290, key => [1001, 1002, 1003, 1234], value => [0, 25, 1, 1234] },
        { counter_id => 2291, key => [1001, 1002, 1003, 1234], value => [1644924394, 1644924394, 1644924394, 1234] },
        { counter_id => 2292, key => [1001, 1002, 1003, 1234], value => [0, 0, 1, 1234] },
        { counter_id => 2294, key => [1001, 1002, 1003, 1234], value => [0, 1, 1, 1234] },
        { counter_id => 1234, key => [1001], value => [888, 999] },
    ];

    my $targeting_info = {};
    for my $counter (@$counters) {
        process_counter_item_stateful_search({}, $targeting_info, $counter);
    }

    my $expected = {
        stateful_search => {
            pregnancy => {
                name => 'pregnancy',
                theme_id => 1001,
                search_query_cnt => 0,
                enabled => 0,
                refused => 0,
                update_time => 1644924394,
            },
            travel => {
                name => 'travel',
                theme_id => 1002,
                search_query_cnt => 25,
                enabled => 0,
                refused => 1,
                update_time => 1644924394,
            },
            career => {
                name => 'career',
                theme_id => 1003,
                search_query_cnt => 1,
                enabled => 1,
                refused => 1,
                update_time => 1644924394,
            },
        },
    };

    is_deeply($targeting_info, $expected, 'process_counter_item_stateful_search_withoutlogin');
}

sub test__get_exp_json : Test(5) {
    my $self = shift;

    my $test_flags = {
        stateful_search => 1,
        bigb_secondary_profile_policy => undef,
        bigb_secondary_profile_limit_puid => undef,
        bigb_secondary_profile_limit_yandexuid => 0,
    };

    no warnings qw(redefine);
    local *MordaX::Type::is_api_search_2_only = sub { 1 };
    local *MordaX::Experiment::AB::flags = sub { $self };
    local *get = *get_bool = sub { $test_flags->{$_[1]} };

    is(MordaX::Block::BigB::_get_exp_json({}), undef, 'test_exp_empty');

    $test_flags->{bigb_secondary_profile_policy} = 'SOME_POLICY';
    is(MordaX::Block::BigB::_get_exp_json({}), '{"EagleSettings":{"LoadSettings":{"CryptaSecondaryWeightMode":"SOME_POLICY"}}}');

    $test_flags->{bigb_secondary_profile_limit_puid} = 10;
    is(MordaX::Block::BigB::_get_exp_json({}), '{"EagleSettings":{"LoadSettings":{"CryptaSecondaryWeightMode":"SOME_POLICY","MaxSecondaryProfiles":10,"ProfileIdTypeLimits":[{"IdType":"PUID","Limit":10}]}}}');

    $test_flags->{bigb_secondary_profile_limit_yandexuid} = 11;
    is(MordaX::Block::BigB::_get_exp_json({}), '{"EagleSettings":{"LoadSettings":{"CryptaSecondaryWeightMode":"SOME_POLICY","MaxSecondaryProfiles":11,"ProfileIdTypeLimits":[{"IdType":"YANDEX_UID","Limit":11},{"IdType":"PUID","Limit":10}]}}}');

    $test_flags->{bigb_secondary_profile_limit_puid} = 0;
    is(MordaX::Block::BigB::_get_exp_json({}), '{"EagleSettings":{"LoadSettings":{"CryptaSecondaryWeightMode":"SOME_POLICY","MaxSecondaryProfiles":11,"ProfileIdTypeLimits":[{"IdType":"YANDEX_UID","Limit":11}]}}}');
}

sub test_process_promo_groups_values : Test(4) {
    my $self = shift;

    no warnings qw(redefine);
    local *process_promo_groups_values = \&MordaX::Block::BigB::process_promo_groups_values;

    #
    ### uint_values
    #

    my $targeting_info = {};
    my $profile_item = {
        keyword_id        => 549,
        source_uniq_index => 0,
        uint_values       => [
            1152,
            1281,
        ],
        update_time       => 1618660800,
    };
    my $result = {
        'promo-groups' => {
            '549:1152' => 1,
            '549:1281' => 1,
        },
    };

    process_promo_groups_values($targeting_info, $profile_item);
    is_deeply($targeting_info, $result, 'process_promo_groups_values uint_values');

    #
    ### pair_values
    #

    $targeting_info = {};
    $profile_item = {
        keyword_id  => 216,
        pair_values => [
            {
                first  => 591,
                second => 1
            },
            {
                first  => 623,
                second => 1
            },
        ],
        source_uniq_index => 0,
        update_time       => 1618660800,
    };
    $result = {
        'promo-groups' => {
            '216:591' => 1,
            '216:623' => 1,
        },
    };

    process_promo_groups_values($targeting_info, $profile_item);
    is_deeply($targeting_info, $result, 'process_promo_groups_values pair_values');

    #
    ### weighted_uint_values
    #

    $targeting_info = {};
    $profile_item = {
        keyword_id           => 546,
        source_uniq_index    => 0,
        update_time          => 1618660800,
        weighted_uint_values => [
            {
                first  => 1304,
                weight => 788412
            },
            {
                first  => 2052,
                weight => 541173
            },
        ],
    };
    $result = {
        'promo-groups' => {
            '546:1304' => 1,
            '546:2052' => 1,
        },
    };

    process_promo_groups_values($targeting_info, $profile_item);
    is_deeply($targeting_info, $result, 'process_promo_groups_values weighted_uint_values');

    #
    ### weighted_pair_values
    #

    $targeting_info = {};
    $profile_item = {
        keyword_id           => 217,
        source_uniq_index    => 0,
        update_time          => 1618660800,
        weighted_pair_values => [
            {
                first  => 70,
                second => 1,
                weight => 1000000,
            },
            {
                first  => 331,
                second => 1,
                weight => 1000000,
            },
        ],
    };
    $result = {
        'promo-groups' => {
            '217:70'  => 1,
            '217:331' => 1,
        },
    };

    process_promo_groups_values($targeting_info, $profile_item);
    is_deeply($targeting_info, $result, 'process_promo_groups_values weighted_pair_values');
}

sub test_process_cryptaid2 : Test(1) {
    my $self = shift;

    no warnings qw(redefine);
    local *process_cryptaid2 = \&MordaX::Block::BigB::process_cryptaid2;

    my $targeting_info = {};
    my $data = {
        user_identifiers => {
            CryptaId                => 11195189868174090270,
        },
    };
    my $result = {
        cryptaid2 => 11195189868174090270,
    };

    process_cryptaid2($data, $targeting_info);
    is_deeply($targeting_info, $result, 'process_cryptaid2');
}

sub test_process_age_and_gender : Test(1) {
    my $self = shift;

    no warnings qw(redefine);
    local *process_age_and_gender = \&MordaX::Block::BigB::process_age_and_gender;

    my $profile_item = {
        keyword_id => 175,
        source_uniq_index => 0,
        update_time => 1618747200,
        weighted_uint_values => [
            {
                first => 1,
                weight => 2673,
            },
            {
                first => 2,
                weight => 864000,
            },
            {
                first => 4,
                weight => 581,
            },
            {
                first => 3,
                weight => 132746,
            },
            {
                first => 0,
                weight => 0,
            }
        ],
    };
    my $targeting_info = {};
    my $keyword_name = 'age';
    my $result = {
        age => [
            {
                id => 175,
                value => 1,
                weight => 2673,
            },
            {
                id => 175,
                value => 2,
                weight => 864000,
            },
            {
                id => 175,
                value => 4,
                weight => 581,
            },
            {
                id => 175,
                value => 3,
                weight => 132746,
            },
            {
                id => 175,
                value => 0,
                weight => 0,
            }
        ],
    };

    process_age_and_gender($targeting_info, $profile_item, $keyword_name);
    is_deeply($targeting_info, $result, 'process_age_and_gender');
}

sub test_process_market_cart : Test(1) {
    my $self = shift;

    no warnings qw(redefine);
    local *process_market_cart = \&MordaX::Block::BigB::process_market_cart;

    my $targeting_info = {};
    my $keyword_name = 'market_cart';
    my $profile_item = {
        keyword_id        => 1038,
        revision          => 0,
        source_uniq_index => 1,
        uint_values => [
            260000,
            1,
        ],
        update_time => 1618325411,
    };
    my $result = {
        market_cart => {
            count      => 1,
            total_cost => 260000,
        },
    };

    process_market_cart($targeting_info, $profile_item, $keyword_name);
    is_deeply($targeting_info, $result, 'process_age_and_gender');
}

sub test_process_other_roots : Test(1) {
    my $self = shift;

    no warnings qw(redefine);
    local *process_other_roots = \&MordaX::Block::BigB::process_other_roots;
    local *MordaX::Block::BigB::process_age_and_gender = sub {};
    local *MordaX::Block::BigB::process_market_cart = sub {};

    my $req = {};
    my $profile_item = {
        keyword_id => 294,
        source_uniq_index => 0,
        uint_values => [
            5,
            1
        ],
        update_time => 1618834611,
    };
    my $targeting_info = {};
    my $result = {
        clid_type => 5,
    };

    process_other_roots($req, $targeting_info, $profile_item);
    is_deeply($targeting_info, $result, 'process_other_roots');
}

1;
