#!/usr/bin/perl

use Test::More;
use common::sense;
use lib::abs qw(../lib ../scripts);

require_ok('export_hockey2015.pl');
my $data_file = lib::abs::path("./data/hockey2015-testing.json");

my $json = MP::Utils::parse_json_file($data_file);
ok($json);
ok($json->{events});
ok(scalar @{$json->{events}});

my $events = {map { $_->{id}, $_ } @{$json->{events}}};

subtest "STATUS DETECTION" => sub {
    #my $clone = MP::Utils::xclone( $events)
    for my $id (keys %$events) {
        my $e = $events->{$id};
        export_hockey2015::fillin_event_status($e);
    }

    subtest "STRANGE Status" => sub {
        my $expected = {
            m423891 => 'not_started',
            m423890 => 'canceled',
            m423889 => 'postponed',
            m423888 => 'suspended',
        };
        for my $m (keys %$expected) {
            is($events->{$m}->{m_status}, $expected->{$m}, "$m");
        }
    };
    subtest "Going on" => sub {
        my $expected = {
            m423887 => 'time1_goes',
            m423886 => 'time2_goes',
            m423885 => 'time3_goes',
            m423880 => 'overtime',
            m423879 => 'shootout',
            m423884 => 'timeout',
            m423883 => 'timeout',
            m423882 => 'timeout',
            m423881 => 'timeout',
        };

        for my $m (keys %$expected) {
            #is( $events->{$m}->{m_status}, 'in_progress' );
            is($events->{$m}->{m_status}, $expected->{$m})
        }
    };

    subtest "Finished" => sub {
        my $expected = {
            'm423878' => 3,
            'm423877' => 4,
            'm423876' => 5,
        };

        for my $m (keys %$expected) {
            is($events->{$m}->{m_status}, 'finished');
            ok($events->{$m}->{m_end_status});
            is($events->{$m}->{m_finished}, $expected->{$m});
        }
    };

    done_testing();
};

done_testing;

