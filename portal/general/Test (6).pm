package DivCardV2::Base::Div::IAction::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro;

use base qw(DivCardV2::Base::Div::Test);

use DivCardV2::Base::Utils qw(:all);

use Test::More;
use MTH;

sub class {'DivCardV2::Base::Div::IAction'}

sub set_methods_startup : Test(startup) {
    my $self = shift;
    $self->next::method(@_);
    my $tests = $self->{set_methods_tests};
    $tests->{set_action} = {
        obj_key => 'action',
        tests   => [
            { args => [], expected => undef },
            { args => [[]], expected => undef },
            { args => [undef], expected => undef },
            { args => ['xxx'], expected => undef },
            {
                args     => [action(log_id => 'xxx')],
                expected => { log_id => 'xxx' },
            },
            {
                args     => [url => 'http://ya.ru'],
                expected => undef,
                errors   => 1,
            },
            {
                args     => [log_id  => 12, url => 'https://ya.ru'],
                expected => { log_id => 12, url => 'https://ya.ru' },
            },
            {
                args => [
                    log_id => 130, url => 'https://ya.ru', payload => { 1 => 2 }
                ],
                expected => {
                    log_id  => 130,
                    url     => 'https://ya.ru',
                    payload => { 1 => 2 },
                },
            },
        ],
    };
    return;
}

sub to_struct_expected {
    my $struct = shift->next::method(@_);
    $struct->{action} = {
        log_id => 1,
        url    => 'http://ya.ru',
    };
    return $struct;
}

sub test_to_struct : Tests {
    push @_, (
        action => action(log_id => 1, url => 'http://ya.ru'),
    );
    my $got = shift->next::method(@_);
    is_json_string($got->{action}->{log_id});
    is_json_string($got->{action}->{url});
    return $got;
}

1;
