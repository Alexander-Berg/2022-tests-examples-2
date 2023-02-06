package Stream::Schedule::Test;

use rules;

use Test::Most;
use base qw(Test::Class);

use Stream::Schedule;
use MP::Logit qw(dmp logit);

my %TimeZoneRussia = (
    '+0200' => 1,
    '+0300' => 1,
    '+0400' => 1,
    '+0500' => 1,
    '+0600' => 1,
    '+0700' => 1,
    '+0800' => 1,
    '+0900' => 1,
    '+1000' => 1,
    '+1100' => 1,
    '+1200' => 1,
);

sub _startup : Test(startup) {
}

sub _setup : Test(setup) {
    my $self = shift;

    $self->{programs} = {
        1 => [
                {
                    start_time => time - 30,
                    end_time   => time + 30,
                    content_id => 110,
                    title      => 'title1',
                    program_title  => 'program_title',
                    thumbnail => '//avatars.mds.yandex.net/',
                    meta => {},
                },
                {
                    start_time => time + 30,
                    end_time   => time + 60,
                    content_id => 111,
                    title      => 'title1',
                    program_title  => 'program_title',
                    thumbnail => '//avatars.mds.yandex.net/',
                    meta => {},
                },
        ],
        2 => [
                {
                    start_time => time - 30,
                    end_time   => time - 10,
                    content_id => 210,
                    title      => 'title1',
                    program_title  => 'program_title',
                    thumbnail => '//avatars.mds.yandex.net/',
                    meta => {},
                },
                {
                    start_time => time + 30,
                    end_time   => time + 60,
                    content_id => 211,
                    title      => 'title1',
                    program_title  => 'program_title',
                    thumbnail => '//avatars.mds.yandex.net/',
                    meta => {},
                },
        ],
        3 => [
                {
                    start_time => time - 30,
                    end_time   => time - 10,
                    content_id => 310,
                    title      => 'title1',
                    program_title  => 'program_title',
                    thumbnail => '//avatars.mds.yandex.net/',
                    meta => {},
                },
                {
                    start_time => time + 30,
                    end_time   => time + 60,
                    content_id => 311,
                    title      => 'title1',
                    program_title  => 'program_title',
                    thumbnail => '//avatars.mds.yandex.net/',
                    meta => {},
                },
        ],
        4 => [
                {
                    start_time => time - 30,
                    end_time   => time - 10,
                    content_id => 410,
                    title      => 'title1',
                    program_title  => 'program_title',
                    thumbnail => '//avatars.mds.yandex.net/',
                    meta => {},
                },
                {
                    start_time => time - 10,
                    end_time   => time + 30,
                    content_id => 411,
                    title      => 'title1',
                    program_title  => 'program_title',
                    thumbnail => '//avatars.mds.yandex.net/',
                    meta => {},
                },
                {
                    start_time => time + 30,
                    end_time   => time + 60,
                    content_id => 412,
                    title      => 'title1',
                    program_title  => 'program_title',
                    thumbnail => '//avatars.mds.yandex.net/',
                    meta => {},
                },
                {
                    start_time => time + 30 * 60 + 1,
                    end_time   => time + 30 * 60 + 10,
                    content_id => 413,
                    title      => 'title1',
                    program_title  => 'program_title',
                    thumbnail => '//avatars.mds.yandex.net/',
                    meta => {},
                },
        ],
        6 => [
                {
                    start_time => time - 30,
                    end_time   => time + 30,
                    content_id => 110,
                    title      => 'title1',
                    program_title  => 'program_title',
                    thumbnail => '//avatars.mds.yandex.net/',
                    meta => {},
                    unnecessary_field => 'something',
                },
        ]
    };

    $self->{programs}{orbital} = {map {$_ => [$self->{programs}{3}[1]]} keys %TimeZoneRussia};

    $self->{channels} = {
        1 => { 
            channel => 1,
            channel_id => 11,
            content_id => 1,
            thumbnail => '//avatars.mds.yandex.net/',
            title => 'Передача',
            type => "channel",
        },
        2 => { 
            channel => 1,
            channel_id => 22,
            content_id => 2,
            thumbnail => '//avatars.mds.yandex.net/',
            title => 'Передача',
            type => "channel",
        },
        3 => { 
            channel => 1,
            channel_id => 33,
            content_id => 3,
            thumbnail => '//avatars.mds.yandex.net/',
            title => 'Передача',
            type => "channel",
        },
    };
}

sub test_load_tv_stream_channel_programs : Test(9) {
    my $self = shift;

    *load_tv_stream_channel_programs = \&Stream::Schedule::load_tv_stream_channel_programs;

    no warnings 'redefine';
    local *Stream::Schedule::_get_programs = sub {
        my (undef, $url, $headers) = @_;

        my ($channel) = $url =~ /parent_id=(\d+)/;
        return $self->{programs}{$channel};
    };

    local *Stream::Schedule::logit = sub{};

    my $tv_stream_DATA = {};
    my $channel_programs = {};

    load_tv_stream_channel_programs($tv_stream_DATA, $channel_programs, $self->{channels}{1}, time, {});
    is_deeply($tv_stream_DATA->{channel_online_11}, $self->{programs}{1});
    is_deeply($tv_stream_DATA->{channel_online_region_11}, undef);
    is_deeply($tv_stream_DATA->{id_1}, $self->{channels}{1});

    load_tv_stream_channel_programs($tv_stream_DATA, $channel_programs, $self->{channels}{2}, time, {});
    is_deeply($tv_stream_DATA->{channel_online_22}, [$self->{programs}{2}[1]]);
    is_deeply($tv_stream_DATA->{channel_online_region_22}, undef);
    is_deeply($tv_stream_DATA->{id_2}, $self->{channels}{2});

    my $channel = {%{$self->{channels}{3}}};
    $channel->{orbital_channel} = 1;
    load_tv_stream_channel_programs($tv_stream_DATA, $channel_programs, $channel, time, {});
    is_deeply($tv_stream_DATA->{channel_online_33}, [$self->{programs}{3}[1]]);
    is_deeply($tv_stream_DATA->{channel_online_region_33}, $self->{programs}{orbital});
    is_deeply($tv_stream_DATA->{id_3}, $self->{channels}{3});
}

sub test__get_online_short_program : Test(6) {
    my $self = shift;

    *_get_online_short_program = \&Stream::Schedule::_get_online_short_program;

    is_deeply(_get_online_short_program($self->{programs}{1}), $self->{programs}{1});
    is_deeply(_get_online_short_program($self->{programs}{2}), [$self->{programs}{2}[1]]);
    is_deeply(_get_online_short_program([]), []);
    is_deeply(_get_online_short_program(undef), []);

    is_deeply(_get_online_short_program($self->{programs}{4}), [@{$self->{programs}{4}}[1 .. 2]]);

    my $programs = [@{ $self->{programs}{6}}];
    delete $programs->[0]{unnecessary_field};
    is_deeply(_get_online_short_program($self->{programs}{6}), $programs);
}

1;
