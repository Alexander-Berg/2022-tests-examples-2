package MordaX::AppHost::Frontend::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro;

use base qw(MordaX::AppHost::Base::Test);

sub apphost_class { 'MordaX::AppHost::Frontend' }

sub graph_id { 'frontend' }

sub make_response { shift->next::method('frontend') }

sub set_tests {
    my $self  = shift;
    my $tests = $self->next::method(@_);
    $tests->{class_methods} = {
        type        => 'backend',
        answer_type => 'frontend',
        source_name => 'BACKEND',
    };
    $tests->{timeout} = {
        ok => [1, 50, 20, 10, 100, 500, 250, 5],
        not_ok => [0, 501, 600, 3600, -1],
    };
    $tests->{alias} = 'frontend';
    $tests->{ctx}   = {
        args => [
            { some_page_data => 'xxx', Requestid => 1 },
            'my_function',
        ],
        expected => {
            pagedata => {
                some_page_data => 'xxx',
                Requestid      => 1,
                handler        => 'my_function',
                jshandler      => 'my_function',
            },
        },
    };
    $tests->{encode_ctx}->{expected} = "\x{12}\x{2e}\x{0a}\x{07}\x{42}\x{41}\x{43}\x{4b}\x{45}\x{4e}\x{44}\x{12}\x{07}\x{62}\x{61}\x{63}\x{6b}\x{65}\x{6e}\x{64}\x{1a}\x{1a}\x{02}\x{0f}\x{00}\x{00}\x{00}\x{00}\x{00}\x{00}\x{00}\x{f0}\x{00}\x{7b}\x{22}\x{73}\x{6f}\x{6d}\x{65}\x{22}\x{3a}\x{22}\x{64}\x{61}\x{74}\x{61}\x{22}\x{7d}";
    return $tests;
}

sub config_setup  {
    my $self = shift;
    $self->mordax_config_mock(
        app_host => {
            frontend_addr    => "http://ya.ru",
            frontend_timeout => 50,
            frontend_retries => 1,
        },
    );
    return;
}

1;
