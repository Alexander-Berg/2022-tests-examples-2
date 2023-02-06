package DivCardV2::Base::Action::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro;

use base qw(Test::Class);

use MTH;
use Test::More;

sub requier : Test(startup => no_plan) {
    my ($self) = @_;
    use_ok('DivCardV2::Base::Action', 'action');
    return;
}

sub scope_create : Test(setup) {
    my ($self) = @_;
    $self->{guard} = DivCardV2::Base::Action->scope();
    return;
}

sub scope_cleanup : Test(teardown) {
    my ($self) = @_;
    delete $self->{guard};
    return;
}

sub creation_no_log_id : Tests {
    my ($self) = @_;
    my $errors = 0;
    DivCardV2::Base::Action->on_error_cb(sub { $errors++ });
    my $obj = DivCardV2::Base::Action->new(url => "http://ya.ru");
    is($obj,    undef);
    is($errors, 1);
    return;
}

sub creation_bad_payload : Tests {
    my ($self) = @_;
    my $obj = DivCardV2::Base::Action->new(
        log_id  => 0,
        url     => "http://ya.ru",
        payload => [1, 2, 3],
    );
    isa_ok($obj, 'DivCardV2::Base::Object');
    isa_ok($obj, 'DivCardV2::Base::Action');
    my $got      = $obj->to_struct;
    my $expected = {
        log_id => "0",
        url    => "http://ya.ru",
    };
    is_deeply($got, $expected);
    is_json_string($got->{log_id});
    return;
}

sub creation_payload : Tests {
    my ($self) = @_;
    my $obj = DivCardV2::Base::Action->new(
        log_id  => 0,
        url     => "http://ya.ru",
        payload => { 1 => [2, 3] },
    );
    isa_ok($obj, 'DivCardV2::Base::Object');
    isa_ok($obj, 'DivCardV2::Base::Action');
    my $got      = $obj->to_struct;
    my $expected = {
        log_id  => "0",
        url     => "http://ya.ru",
        payload => { 1 => [2, 3] },
    };
    is_deeply($got, $expected);
    is_json_string($got->{log_id});
    return;
}

sub action_bad_payload : Tests {
    my ($self) = @_;
    my $obj = action(
        log_id  => 0,
        url     => "http://ya.ru",
        payload => [1, 2, 3],
    );
    isa_ok($obj, 'DivCardV2::Base::Object');
    isa_ok($obj, 'DivCardV2::Base::Action');
    my $got      = $obj->to_struct;
    my $expected = {
        log_id => "0",
        url    => "http://ya.ru",
    };
    is_deeply($got, $expected);
    is_json_string($got->{log_id});
    return;
}

sub action_payload : Tests {
    my ($self) = @_;
    my $obj = action(
        log_id  => 0,
        url     => "http://ya.ru",
        payload => { 1 => [2, 3] },
    );
    isa_ok($obj, 'DivCardV2::Base::Object');
    isa_ok($obj, 'DivCardV2::Base::Action');
    my $got      = $obj->to_struct;
    my $expected = {
        log_id  => "0",
        url     => "http://ya.ru",
        payload => { 1 => [2, 3] },
    };
    is_deeply($got, $expected);
    is_json_string($got->{log_id});
    return;
}

sub add_menu_item : Tests {
    my ($self) = @_;
    my $errors = 0;
    DivCardV2::Base::Action->on_error_cb(sub { $errors++ });
    my $obj = action(
        log_id => 0,
        url    => "http://ya.ru",
    );
    $obj->add_menu_item()    # error #1 - no args
      ->add_menu_item(undef, action(log_id => 1))    # error #2 - no text
      ->add_menu_item('xxx')                         # error #3 - no action
      ->add_menu_item('xxx', { log_id => 2 })        # error #4 - bad action
      ->add_menu_item(0, action(log_id => 3));
    my $got      = $obj->to_struct;
    my $expected = {
        log_id     => 0,
        url        => "http://ya.ru",
        menu_items => [
            {
                text   => 0,
                action => { log_id => 3 },
            },
        ],
    };
    is_deeply($got, $expected);
    is($errors, 4);
    is_json_string($got->{log_id});
    is_json_string($got->{menu_items}->[0]->{text});
    is_json_string($got->{menu_items}->[0]->{action}->{log_id});
    return;
}

sub add_menu_item_overload : Tests {
    my ($self) = @_;
    my $errors = 0;
    DivCardV2::Base::Action->on_error_cb(sub { $errors++ });
    my $obj = action(
        log_id => 0,
        url    => "http://ya.ru",
    );
    no warnings qw(void);
    # error 1 - not supported
    $obj <<= [0, action(log_id => 3)];
    # error 2 - bad args
    $obj << 0;
    # swap - no errors and no reaction
    [0, action(log_id => 3)] << $obj;
    # error 3 and 4 bad args
    $obj << [] << ['xxx'];
    $obj << [0, action(log_id => 3)] << ["item 1", action(log_id => 4)];
    my $got      = $obj->to_struct;
    my $expected = {
        log_id     => 0,
        url        => "http://ya.ru",
        menu_items => [
            {
                text   => 0,
                action => { log_id => 3 },
            },
            {
                text   => "item 1",
                action => { log_id => 4 },
            },
        ],
    };
    is_deeply($got, $expected);
    is($errors, 4);
    is_json_string($got->{log_id});
    is_json_string($got->{menu_items}->[0]->{text});
    is_json_string($got->{menu_items}->[0]->{action}->{log_id});
    is_json_string($got->{menu_items}->[1]->{text});
    is_json_string($got->{menu_items}->[1]->{action}->{log_id});
    return;
}

    1;
