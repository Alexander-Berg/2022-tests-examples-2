package Test::Smoo::EventSettingsTargetings;
use parent 'Test::Class';

use Test::Most;
use MP::Logit qw(logit dmp);
use rules;

use Smoo::EventSettingsTargetings;
use Storable qw/dclone/;
use MP::Utils;
use utf8;

my $dbh;

sub start : Test(startup) {
    $dbh = Smoo::DB::instance();
    $dbh->begin_work();
    _init_db();
}

sub _init_db {
    my $res = $dbh->do('DELETE FROM settings');
    $res = $dbh->do('DELETE FROM settings_platforms');

    $res = $dbh->do(
        "INSERT INTO settings
        SET id=100, name='test', service='test', event_type='delayed', localize=?,
        ttl='10:00:00', ttv='03:00:00', ttp='01:00:00', push_approved=0, push_enabled=1, enabled=1",
        undef,
        '{"default": {"title": "Яндекс"}}'
    );

    $res = $dbh->do(
        "INSERT INTO settings_targetings
        SET id=1, settings_id=100, platform='test_appsearch_android', add_ri=0, no_notify=0, staff=1, receivers=?, apps=?,
        url='morda://', enabled=1",
        undef,
        "(app_version >= '5.3%' && app_version < '6.3') && topic=='other'",
        "has_yandex_metro_app=='0'"
    );

    $res = $dbh->do(
        "INSERT INTO settings_targetings
        SET id=2, settings_id=100, platform='test_appsearch_ios', add_ri=1, staff=0, receivers=?, apps=?,
        url='morda://?card=webcard', topic_push='assist_metro_push', topic_card='assist_metro_card',
        opt_in=1, exp='EXP-5,EXP-6', enabled=1",
        undef,
        "app_version >= '3.11'",
        "has_yandex_weather_app=='0'"
    );

    $res = $dbh->do(
        "
        INSERT INTO
            settings_platforms
        SET
            id        = 'test_appsearch_android',
            value     = ?,
            transport = 'Native',
            builder   = 'default'
        ",
        undef,
        "app_id LIKE 'ru.yandex.searchplugin%'",

    );

    $res = $dbh->do(
        "
        INSERT INTO
            settings_platforms
        SET
            id = 'test_appsearch_ios',
            value     = ?,
            transport = 'Xiva',
            builder = 'test_builder_ios'
        ",
        undef,
        "app_id=='ru.yandex.mobile' || app_id=='ru.yandex.mobile.inhouse'"
    );

    $res = $dbh->do(
        "
        INSERT INTO
            settings_platforms
        SET
            id = 'desktop_yabro',
            value     = ?,
            transport = 'Xiva',
            builder = 'default',
            project = 'mobyabro'
        ",
        undef,
        "app_id == 'YandexBrowser'"
    );
    $res = $dbh->do(
        "INSERT INTO settings_targetings
        SET id=3, settings_id=100, platform='desktop_yabro', add_ri=1, staff=0, receivers=?, apps='',
        url='https://yandex.ru/?desktop', topic_push='assist_metro_push', topic_card='assist_metro_card',
        opt_in=1, enabled=1, features=?",
        undef,
        "device_type == 'desktop'",
        '{"image": "https://ya.ru/image"}'
    );
}

sub end : Test(shutdown) {
    $dbh->rollback();
}

sub get_rules_for_push : Tests {
    my ($push, $got, $expected);
    $push = {
        settings_id => 99,
    };
    $got = Smoo::EventSettingsTargetings::get_rules_for_push($push);
    is_deeply $got, [] or expect $got;

    $push = {
        geo         => 2,
        settings_id => 99,
    };
    $got = Smoo::EventSettingsTargetings::get_rules_for_push($push);
    is_deeply $got, [] or expect $got;

    $push = {
        geo         => 1,
        settings_id => 100,
    };
    $got      = Smoo::EventSettingsTargetings::get_rules_for_push($push);
    $expected = [
        {
            receivers => "tag:geo=='1' && (app_id LIKE 'ru.yandex.searchplugin%') && (lang IN ('ru', 'en') || !lang) && yandex_staff && ((app_version >= '5.3%' && app_version < '6.3') && topic=='other') && has_yandex_metro_app=='0'",
            url              => 'morda://',
            icon             => undef,
            topic_card       => undef,
            topic_push       => undef,
            exp              => undef,
            platform         => 'test_appsearch_android',
            platform_builder => 'default',
            platform_project => 'searchapp',
            add_ri           => 0,
            no_notify        => 0,
            allow_no_geo     => undef,
            transport_sup    => 'Native',
            features         => {},
        },
        {
            receivers => "tag:geo=='1' && (app_id=='ru.yandex.mobile' || app_id=='ru.yandex.mobile.inhouse') && (lang IN ('ru', 'en') || !lang) && !yandex_staff && (app_version >= '3.11') && theme=='assist_metro_card_on' && theme=='assist_metro_push_on' && has_yandex_weather_app=='0'",
            exp              => 'EXP-5',
            url              => 'morda://?card=webcard',
            icon             => undef,
            topic_card       => 'assist_metro_card',
            topic_push       => 'assist_metro_push',
            platform         => 'test_appsearch_ios',
            platform_builder => 'test_builder_ios',
            platform_project => 'searchapp',
            add_ri           => 1,
            no_notify        => 1,
            allow_no_geo     => undef,
            transport_sup    => 'Xiva',
            features         => {},
        },
        {
            receivers => "tag:geo=='1' && (app_id=='ru.yandex.mobile' || app_id=='ru.yandex.mobile.inhouse') && (lang IN ('ru', 'en') || !lang) && !yandex_staff && (app_version >= '3.11') && theme=='assist_metro_card_on' && theme=='assist_metro_push_on' && has_yandex_weather_app=='0'",
            exp              => 'EXP-6',
            url              => 'morda://?card=webcard',
            icon             => undef,
            topic_card       => 'assist_metro_card',
            topic_push       => 'assist_metro_push',
            platform         => 'test_appsearch_ios',
            platform_builder => 'test_builder_ios',
            platform_project => 'searchapp',
            add_ri           => 1,
            no_notify        => 1,
            allow_no_geo     => undef,
            transport_sup    => 'Xiva',
            features         => {},
        },
        {
            receivers => "tag:geo=='1' && (app_id == 'YandexBrowser') && (lang IN ('ru', 'en') || !lang) && !yandex_staff && (device_type == 'desktop') && theme=='assist_metro_card_on' && theme=='assist_metro_push_on'",
            url              => 'https://yandex.ru/?desktop',
            icon             => undef,
            topic_card       => 'assist_metro_card',
            topic_push       => 'assist_metro_push',
            platform         => 'desktop_yabro',
            platform_builder => 'default',
            platform_project => 'mobyabro',
            add_ri           => 1,
            exp              => undef,
            no_notify        => 1,
            allow_no_geo     => undef,
            transport_sup    => 'Xiva',
            features         => {
                image => "https://ya.ru/image",
            },
        },
    ];
    is_deeply $got, $expected or explain $got;
}

sub _make_receivers_for_push : Tests {
    my ($got, $expected);
    $got = Smoo::EventSettingsTargetings::_make_receivers_for_push({});
    ok !$got or explain $got;

    my $s = {
        platform  => 'appsearch_android',
        staff     => 1,
        receivers => "(app_version >= '5.3%' && app_version < '6.3') && topic=='other'",
        apps      => "has_yandex_metro_app=='0'",
        opt_in    => 0,
        app_id    => "app_id LIKE 'ru.yandex.searchplugin%'",
    };
    $got = Smoo::EventSettingsTargetings::_make_receivers_for_push({ geo => 213 }, $s);
    $expected = "tag:geo=='213' && (app_id LIKE 'ru.yandex.searchplugin%') && (lang IN ('ru', 'en') || !lang) && yandex_staff && ((app_version >= '5.3%' && app_version < '6.3') && topic=='other') && has_yandex_metro_app=='0'";
    is $got, $expected;

    $s = {
        platform   => 'appsearch_android',
        staff      => 1,
        receivers  => "(app_version >= '5.3%' && app_version < '6.3')",
        apps       => "has_yandex_metro_app=='0'",
        topic_push => 'test_push',
        topic_card => 'test_card',
        opt_in     => 0,
        app_id     => "app_id LIKE 'ru.yandex.searchplugin%'",
    };
    $got = Smoo::EventSettingsTargetings::_make_receivers_for_push({ geo => 213 }, $s);
    $expected = "tag:geo=='213' && (app_id LIKE 'ru.yandex.searchplugin%') && (lang IN ('ru', 'en') || !lang) && yandex_staff && ((app_version >= '5.3%' && app_version < '6.3')) && theme!='test_card_off' && theme!='test_push_off' && has_yandex_metro_app=='0'";
    is $got, $expected;

    $s = {
        platform  => 'appsearch_ios',
        staff     => 0,
        receivers => "app_version >= '3.11'",
        apps      => "has_yandex_weather_app=='0'",
        opt_in    => 1,
        app_id    => "app_id=='ru.yandex.mobile' || app_id=='ru.yandex.mobile.inhouse'",
    };
    $got = Smoo::EventSettingsTargetings::_make_receivers_for_push({ geo => 213 }, $s);
    $expected = "tag:geo=='213' && (app_id=='ru.yandex.mobile' || app_id=='ru.yandex.mobile.inhouse') && (lang IN ('ru', 'en') || !lang) && !yandex_staff && (app_version >= '3.11') && has_yandex_weather_app=='0'";
    is $got, $expected;

    $s = {
        platform   => 'appsearch_ios',
        staff      => 0,
        receivers  => "app_version >= '3.11'",
        apps       => "has_yandex_weather_app=='0'",
        opt_in     => 1,
        topic_push => 'test_push',
        topic_card => 'test_card',
        app_id     => "app_id=='ru.yandex.mobile' || app_id=='ru.yandex.mobile.inhouse'",
    };
    $got = Smoo::EventSettingsTargetings::_make_receivers_for_push({ geo => 213 }, $s);
    $expected = "tag:geo=='213' && (app_id=='ru.yandex.mobile' || app_id=='ru.yandex.mobile.inhouse') && (lang IN ('ru', 'en') || !lang) && !yandex_staff && (app_version >= '3.11') && theme=='test_card_on' && theme=='test_push_on' && has_yandex_weather_app=='0'";
    is $got, $expected;
}

sub _appname_rule_part : Tests {
    my ($got, $expected);

    $got = Smoo::EventSettingsTargetings::_appname_rule_part();
    is $got, undef;

    $got = Smoo::EventSettingsTargetings::_appname_rule_part({
            platform => 'appsearch_android',
            app_id   => "app_id LIKE 'ru.yandex.searchplugin%'",
    });
    is $got, " && (app_id LIKE 'ru.yandex.searchplugin%')";

    $got = Smoo::EventSettingsTargetings::_appname_rule_part({
            platform => 'appsearch_ios',
            app_id   => "app_id=='ru.yandex.mobile' || app_id=='ru.yandex.mobile.inhouse'",
    });
    is $got, " && (app_id=='ru.yandex.mobile' || app_id=='ru.yandex.mobile.inhouse')";
}

sub _lang_rule_part : Tests {
    my ($got, $expected);

    $got = Smoo::EventSettingsTargetings::_lang_rule_part();
    is $got, " && (lang IN ('ru', 'en') || !lang)";
}

sub _staff_rule_part : Tests {
    my ($got, $expected);

    $got = Smoo::EventSettingsTargetings::_staff_rule_part();
    is $got, undef;

    $got = Smoo::EventSettingsTargetings::_staff_rule_part({staff => 1});
    is $got, " && yandex_staff";

    $got = Smoo::EventSettingsTargetings::_staff_rule_part({staff => 0});
    is $got, " && !yandex_staff";
}

sub _version_rule_part : Tests {
    my ($got, $expected);
    $got = Smoo::EventSettingsTargetings::_version_rule_part();
    is $got, undef;

    $got = Smoo::EventSettingsTargetings::_version_rule_part({ receivers=> "(android_os_level<'23' || !android_os_level || (app_version >= '5.3%' && app_version < '6.41')) && topic=='other'"});
    is $got, " && ((android_os_level<'23' || !android_os_level || (app_version >= '5.3%' && app_version < '6.41')) && topic=='other')";
}

sub _otherapps_rule_part : Tests {
    my ($got, $expected);

    $got = Smoo::EventSettingsTargetings::_otherapps_rule_part({});
    is $got, undef;

    $got = Smoo::EventSettingsTargetings::_otherapps_rule_part({ apps => "has_yandex_weather_app=='0'" });
    is $got, " && has_yandex_weather_app=='0'";
}

sub _topic_card_rule_part : Tests {
    my ($got, $expected);

    $got = Smoo::EventSettingsTargetings::_topic_card_rule_part({});
    is $got, undef;

    $got = Smoo::EventSettingsTargetings::_topic_card_rule_part({ topic_card => 'weather_card', opt_in => 1 });
    is $got, " && theme=='weather_card_on'";

    $got = Smoo::EventSettingsTargetings::_topic_card_rule_part({ topic_card => 'weather_card', opt_in => 0 });
    is $got, " && theme!='weather_card_off'";
}

sub _topic_push_rule_part : Tests{
    my ($got, $expected);

    $got = Smoo::EventSettingsTargetings::_topic_push_rule_part({});
    is $got, undef;

    $got = Smoo::EventSettingsTargetings::_topic_push_rule_part({ topic_push => 'weather_push', opt_in => 1 });
    is $got, " && theme=='weather_push_on'";

    $got = Smoo::EventSettingsTargetings::_topic_push_rule_part({ topic_push => 'weather_push', opt_in => 0 });
    is $got, " && theme!='weather_push_off'";
}

sub _make_exp : Tests {
    my $got;
    $got = Smoo::EventSettingsTargetings::_make_exp({exp=>undef});
    is_deeply $got, [undef];

    $got = Smoo::EventSettingsTargetings::_make_exp({exp=>'EXP-5'});
    is_deeply $got, ["EXP-5"];

    $got = Smoo::EventSettingsTargetings::_make_exp({exp=>'EXP-5, EXP-6'});
    is_deeply $got, ["EXP-5", "EXP-6"];

    $got = Smoo::EventSettingsTargetings::_make_exp({exp=>'EXP-5,EXP-6'});
    is_deeply $got, ["EXP-5", "EXP-6"];

    $got = Smoo::EventSettingsTargetings::_make_exp({exp=>'EXP-1000;200;400,EXP-2000;300;500'});
    is_deeply $got, ["EXP-1000;200;400", "EXP-2000;300;500"];
}

# _get_settings_for_push
sub _get_settings_for_push : Tests {
    my $push = {
        settings_id => 99,
    };
    my $got = Smoo::EventSettingsTargetings::_get_settings_for_push($push);
    is_deeply $got, {} or explain $got;

    $push = {
        settings_id => 100,
    };
    $got = Smoo::EventSettingsTargetings::_get_settings_for_push($push);

    is_deeply [sort keys %$got], [1, 2, 3] or explain $got;
}

sub _get_settings_from_db : Tests {
    my $got = Smoo::DB2::get_targetings_settings({ settings_id => 99 })->{res};
    is_deeply $got, {} or explain $got;

    $got = Smoo::DB2::get_targetings_settings({ settings_id => 100 })->{res};
    my $expected = {
        1 => {
            id               => 1,
            settings_id      => 100,
            platform         => 'test_appsearch_android',
            platform_builder => 'default',
            platform_project => 'searchapp',
            add_ri           => 0,
            no_notify        => 0,
            staff            => 1,
            app_id           => "app_id LIKE 'ru.yandex.searchplugin%'",
            receivers        => "(app_version >= '5.3%' && app_version < '6.3') && topic=='other'",
            apps             => "has_yandex_metro_app=='0'",
            url              => 'morda://',
            icon             => undef,
            exp              => undef,
            topic_push       => undef,
            topic_card       => undef,
            opt_in           => 0,
            enabled          => 1,
            preview          => undef,
            descr            => '',
            transport_sup    => 'Native',
            div_card         => 0,
            add_card         => 0,
            features         => {},
          },
        2 => {
            id               => 2,
            settings_id      => 100,
            platform         => 'test_appsearch_ios',
            platform_builder => 'test_builder_ios',
            platform_project => 'searchapp',
            app_id           => "app_id=='ru.yandex.mobile' || app_id=='ru.yandex.mobile.inhouse'",
            add_ri           => 1,
            no_notify        => 1,
            staff            => 0,
            receivers        => "app_version >= '3.11'",
            apps             => "has_yandex_weather_app=='0'",
            url              => 'morda://?card=webcard',
            icon             => undef,
            topic_push       => 'assist_metro_push',
            topic_card       => 'assist_metro_card',
            opt_in           => 1,
            exp              => 'EXP-5,EXP-6',
            enabled          => 1,
            preview          => undef,
            descr            => '',
            transport_sup    => 'Xiva',
            div_card         => 0,
            add_card         => 0,
            features         => {},
        },
        3 => {
            id               => 3,
            settings_id      => 100,
            platform         => 'desktop_yabro',
            platform_builder => 'default',
            platform_project => 'mobyabro',
            app_id           => "app_id == 'YandexBrowser'",
            add_ri           => 1,
            no_notify        => 1,
            staff            => 0,
            receivers        => "device_type == 'desktop'",
            apps             => "",
            url              => 'https://yandex.ru/?desktop',
            icon             => undef,
            topic_push       => 'assist_metro_push',
            topic_card       => 'assist_metro_card',
            opt_in           => 1,
            exp              => undef,
            enabled          => 1,
            preview          => undef,
            descr            => '',
            transport_sup    => 'Xiva',
            div_card         => 0,
            add_card         => 0,
            features         => {
                image =>  "https://ya.ru/image",
            },
        },
    };
    is_deeply $got, $expected or explain $got;
}
1;
