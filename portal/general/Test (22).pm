package Handler::Config::Test;

use rules;

use Test::Most;
use base qw(Test::Class);

#use MP::Logit qw(logit dmp);

use Handler::Config;

sub _redefine_object : Test(startup) {
    my $self = shift;

    $self->{Getargshash} = $self->{UserDevice} = {};
}

sub make_fixture : Test(setup) {
    my $self = shift;
}

sub test_modify_struct_by_path : Test(6) {
    my $self = shift;

    *modify_struct_by_path = \&Handler::Config::modify_struct_by_path;

    my $struct = {'one' => 'old'};
    modify_struct_by_path($struct, 0, 'one', 'new');
    is_deeply($struct, {'one' => 'new'});


    $struct = {'one' => {'two' => 'old'}};
    modify_struct_by_path($struct, 0, 'one.two', 'new');
    is_deeply($struct, {'one' => {two => 'new'}});

    $struct = {'one' => {'two' => 'old'}};
    modify_struct_by_path($struct, 0, 'one.tree', 'new');
    is_deeply($struct, {'one' => {'two' => 'old', tree => 'new'}});

    no warnings "redefine";
    local *MordaX::Utils::options = sub {0};
    my $error_type = '';
    local *Handler::Config::logit = sub {
        $error_type = $_[0];
    };
    $struct = {'one' => ['two' => 'old']};
    modify_struct_by_path($struct, 0, 'one', 'new');
    is_deeply($struct, {'one' => 'new'});
    is($error_type, 'interr');

    $struct = {'one' => {'two' => undef}};
    modify_struct_by_path($struct, 0, 'one.two', 'no undef');
    is_deeply($struct, {'one' => {'two' => 'no undef'}});
}

sub test_make_info_template : Test(2) {
    my $self = shift;

    *make_meta_info_template = \&Handler::Config::make_meta_info_template;

    no warnings "redefine";
    local *_is_tablet = sub {0};

    local *Handler::Config::make_web_view_pages = sub {return [] };
    like(make_meta_info_template({}), qr/"webViewPages":\[\]/);

    local *Handler::Config::make_web_view_pages = sub {return {'яндекс' => '№1'}};
    like(make_meta_info_template({}), qr/"webViewPages":\{"яндекс":"№1"\}/);
}

sub test_make_web_view_pages : Tests(3) {
    my $self = shift;

    *make_web_view_pages = \&Handler::Config::make_web_view_pages;

    no warnings qw(redefine once);
    local *MordaX::Experiment::AB::flags = sub { MordaX::Experiment::AB::Flags::instance($_[0], 'MUTE_WARNINGS'); };
    *MordaX::Utils::Api::get_args_country = sub($) {'ru'};
    local *header = sub{};

    is(@{make_web_view_pages($self)}, 3);

    $self->{UserDevice}{app_version}   = 7000500;
    $self->{UserDevice}{app_platform}  = 'android';
    is(@{make_web_view_pages($self)}, 6);

    $self->{UserDevice}{app_platform}  = 'apad';
    is(@{make_web_view_pages($self)}, 3);
}

sub test_is_tablet : Tests(5) {
    my $self = shift;

    local *_is_tablet = \&Handler::Config::_is_tablet;

    $self->{Getargshash}{app_platform} = 'apad';
    ok(_is_tablet($self));

    $self->{Getargshash}{app_platform} = 'ipad';
    ok(_is_tablet($self));

    $self->{Getargshash}{app_platform} = 'iphone';
    ok(_is_tablet($self) == 0);

    $self->{Getargshash}{app_platform} = '';
    $self->{isTablet} = 1;
    ok(_is_tablet($self));

    delete $self->{Getargshash}{app_platform};
    $self->{isTablet} = 1;
    ok(_is_tablet($self));
}

sub move_conditions {}

sub test_make_browser_flags_studies : Tests(2) {
    my $self = shift;

    *make_browser_flags_studies = \&Handler::Config::make_browser_flags_studies;

    my $config = {};
    make_browser_flags_studies($config, {});
    is_deeply($config, {browser_flags => {studies => []}}, 'empty input');

    $config = {};
    my $browser_flags = {
        'word_translation' => {
            'default_group_name' => 'default_enabled',
            'name' => 'word_translation',
        }
    };
    make_browser_flags_studies($config, $browser_flags);
    my $exp = {
        'browser_flags' => {
            'studies' => [
                {
                    'name' => 'word_translation',
                    'default_group_name' => 'default_enabled',
                    'salt' => '',
                },
            ],
        },
    };
    is_deeply($config, $exp, 'one flag in input');
}

sub test_validate_browser_pp_flags : Test(3) {
    my $self = shift;

    *validate_browser_pp_flags = \&Handler::Config::validate_browser_pp_flags;

    no warnings "redefine";

    my $input;
    $input->{json}->{value} = '{}';
    my $result = validate_browser_pp_flags($input);
    is($result, 'name required in json', 'ckeck name');

    $input->{json}->{value} = '{"name": "yandex"}';
    $result = validate_browser_pp_flags($input);
    is($result, 'default_group_name required in json', 'check default_group_name');

    $input->{json}->{value} = '{"name": "yandex", "default_group_name": "yandex"}';
    $result = validate_browser_pp_flags($input);
    is($result, undef, 'check valid input');
}

sub test_get_madm_browser_flags : Test(1) {
    my $self = shift;

    *get_madm_browser_flags = \&Handler::Config::get_madm_browser_flags;

    no warnings "redefine";
    local *Handler::Config::get_pp_flags = sub {
        return [
            {
                'app_platform' => 'android',
                'app_version_min' => '2000000',
                'domain' => 'all',
                'is_prod_android' => '1',
                'json' => '{"default_group_name": "yandex", "name": "second", "salt": 123}',
            },
            {
                'app_platform' => 'android',
                'app_version_min' => '1000000',
                'domain' => 'all',
                'is_prod_android' => '1',
                'json' => '{"default_group_name": "yandex", "name": "first"}',
            },
        ];
    };
    my $exp = {
        'second' => {
            'salt' => 123,
            'name' => 'second',
            'default_group_name' => 'yandex'
        },
        'first' => {
            'name' => 'first',
            'default_group_name' => 'yandex'
        },
    };

    my $result = get_madm_browser_flags({});
    is_deeply($result, $exp, 'check get_madm_browser_flags structure');
}

sub test_modify_browser_flags : Test(4) {
    my $self = shift;

    *modify_browser_flags = \&Handler::Config::modify_browser_flags;

    no warnings "redefine";

    local *MordaX::Experiment::AB::flags = sub {
        return $self;
    };
    local *browser_flags = sub {
        return {};
    };
    local *Handler::Config::get_madm_browser_flags = sub {
        return {};
    };

    #
    # empty input
    #

    my $input = {};
    modify_browser_flags({}, $input);
    is_deeply($input, {}, 'empty input');

    #
    # only code
    #

    $input = {
        name => 'default',
    };
    modify_browser_flags({}, $input);
    is_deeply($input, {name => 'default'}, 'only code');

    #
    # code + madm
    #

    *Handler::Config::get_madm_browser_flags = sub {
        return {
            name => 'madm',
        };
    };
    modify_browser_flags({}, $input);
    is_deeply($input, {name => 'madm'}, 'code + madm');

    #
    # code + madm + AB
    #

    *browser_flags = sub {
        return {
            name => 'AB',
        };
    };
    modify_browser_flags({}, $input);
    is_deeply($input, {name => 'AB'}, 'code + madm + AB');
}

1;