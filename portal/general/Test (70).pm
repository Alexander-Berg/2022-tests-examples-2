package MordaX::Experiment::AB::Tree::Primary::Content::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro;

use base qw(MordaX::Experiment::AB::Tree::Primary::Test);

use Test::More;
use MTH;

sub class {'MordaX::Experiment::AB::Tree::Primary::Content'}

sub not_need_one_arg_new_test {1}

sub new_tests_setup : Test(startup) {
    my $tests = shift->next::method(@_);
    push @$tests, (
        {
            name     => 'one arg "BIG"',
            args     => ['BIG'],
            errors   => 0,
            expected => ['big', undef],
        },
        {
            name     => 'one arg "touch"',
            args     => ['touch'],
            errors   => 0,
            expected => ['touch', undef],
        },
    );
    return $tests;
}

sub test_as_string_one_node : Tests {
    my ($self) = @_;
    is($self->class->new("BIG")->as_string, 'content:big', 'as_string "BIG"');
    is($self->class->new("touch")->as_string, 'content:touch', 'as_string "touch"');
    return $self;
}

sub test_evaluate : Tests {
    my ($self) = @_;
    my @tests = (
        {
            content => 'BIG',
            req => {
                MordaContent => 'big',
            },
            result => 1
        },
        {
            content => 'touch_only',
            req => {
                MordaContent => 'touch',
                handler      => 'Handler::MordaX',
            },
            result => 1
        },
        {
            content => 'touch_only',
            req => {
                MordaContent => 'touch',
                handler      => 'Handler::Api',
            },
            result => 0
        },
        {
            content => 'api_search_1',
            req => {
                MordaContent => 'touch',
                handler      => 'Handler::Api',
                api_search   => 1,
            },
            result => 1
        },
        {
            content => 'api_search_2',
            req => {
                MordaContent => 'touch',
                handler      => 'Handler::Api',
                api_search   => 2,
            },
            result => 1
        },
        {
            content => 'api_search_2_only',
            req => {
                MordaContent => 'touch',
                handler      => 'Handler::Api',
                api_search   => 2,
            },
            result => 1
        },
        {
            content => 'api_search_2_only',
            req => {
                MordaContent => 'touch',
                handler      => 'Handler::Api',
                api_search   => 2,
                real_api_name    => 'yabrowser',
                real_api_version => 2,
            },
            result => 0
        },
        {
            content => 'api_yabrowser_2',
            req => {
                MordaContent => 'touch',
                handler      => 'Handler::Api',
                api_search   => 2,
                real_api_name    => 'yabrowser',
                real_api_version => 2,
            },
            result => 1
        },
        {
            content => 'api_yabrowser_iphone',
            req => {
                MordaContent => 'touch',
                handler      => 'Handler::Api',
                api_search   => 2,
                real_api_name    => 'yabrowser',
                real_api_version => 2,
                Template         => 'api_yabrowser_iphone',
            },
            result => 1
        },
        {
            content => 'api_yabrowser_prod',
            req => {
                MordaContent => 'touch',
                handler      => 'Handler::Api',
                api_search   => 2,
                real_api_name    => 'yabrowser',
                real_api_version => 2,
                Getargshash => {app_id => 'com.yandex.browser'},
            },
            result => 1
        },
        {
            content => 'api_search_prod',
            req => {
                MordaContent => 'touch',
                handler      => 'Handler::Api',
                api_search   => 2,
                Getargshash  => {app_id => 'ru.yandex.searchplugin'},
            },
            result => 1
        },
        {
            content => 'api_launcher_0',
            req => {
                MordaContent => 'touch',
                handler      => 'Handler::Api',
                api_name     => 'launcher',
            },
            result => 1
        },
        {
            content => 'stream_big',
            req => {
                MordaContent => 'embedstream',
            },
            result => 1
        },
        {
            content => 'stream_touch',
            req => {
                MordaContent => 'embedstream_touch',
            },
            result => 1
        },
    );
    for my $test (@tests) {
        my $req = $test->{req};
        my $test_name = ($test->{result} ? 'true: ' : 'false: ')
          . $self->class . '->new(' . explain_args($test->{content}) . ')'
          . '->evaluate(' . explain_args($req) . ')';
        my $tree = $self->class->new($test->{content});
        is($tree->evaluate($req), $test->{result}, $test_name);
    }
    return $self;
}

1;
