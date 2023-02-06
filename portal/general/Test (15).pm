package DivCardV2::Base::Utils::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro;

use base qw(Test::Class);

use Test::More;
use MTH;

use Scalar::Util qw(weaken);
use JSON::XS qw();

use DivCardV2::Base::Constants;
use DivCardV2::Base::Object;

sub requier : Test(startup => no_plan) {
    my ($self) = @_;
    use_ok('DivCardV2::Base::Utils', ':all');
    return;
}

sub scope_create : Test(setup) {
    my ($self) = @_;
    $self->{guard} = DCV2_BCLS->scope();
    weaken(my $_self = $self);
    DCV2_BCLS->on_warning_cb(sub {
            $_self->{warning_cb} ? $_self->{warning_cb}->(@_) : undef;
    });
    DCV2_BCLS->on_error_cb(sub {
            $_self->{error_cb} ? $_self->{error_cb}->(@_) : undef;
    });
    return;
}

sub scope_cleanup : Test(teardown) {
    my ($self) = @_;
    delete $self->{guard};
    return;
}

sub test_is_positive_number : Tests {
    no warnings qw(uninitialized);
    my ($self) = @_;
    my @ok  = (1, 2,     3.3, 0.2,  10.34);
    my @bad = (0, undef, -12, -0.1, 'string', 'Inf', 'NaN');
    ok(is_positive_number($_),      "is_positive_number($_)") for @ok;
    ok(not(is_positive_number($_)), "is_positive_number($_)") for @bad;
    return;
}

sub test_is_non_negative_number : Tests {
    no warnings qw(uninitialized);
    my ($self) = @_;
    my @ok  = (0,     1,   2,    3.3,      0.2,   10.34);
    my @bad = (undef, -12, -0.1, 'string', 'Inf', 'NaN');
    ok(is_non_negative_number($_),      "is_non_negative_number($_)") for @ok;
    ok(not(is_non_negative_number($_)), "is_non_negative_number($_)") for @bad;
    return;
}

sub test_is_negative_number : Tests {
    no warnings qw(uninitialized);
    my ($self) = @_;
    my @ok  = (-1, -2,    -3.3, -0.2, -10.34);
    my @bad = (0,  undef, 12,   0.1,  'string', 'Inf', 'NaN');
    ok(is_negative_number($_),      "is_negative_number($_)") for @ok;
    ok(not(is_negative_number($_)), "is_negative_number($_)") for @bad;
    return;
}

sub test_is_non_positive_number : Tests {
    no warnings qw(uninitialized);
    my ($self) = @_;
    my @ok  = (0,     -1, -2,  -3.3,     -0.2,  -10.34);
    my @bad = (undef, 12, 0.1, 'string', 'Inf', 'NaN');
    ok(is_non_positive_number($_),      "is_non_positive_number($_)") for @ok;
    ok(not(is_non_positive_number($_)), "is_non_positive_number($_)") for @bad;
    return;
}

sub test_is_size_fixed : Tests {
    no warnings qw(uninitialized);
    my ($self) = @_;
    my @ok  = (size_fixed(1), size_fixed(2));
    my @bad = (undef, [], {}, 'str', size_match_parent(), size_wrap_content());
    for (@ok) {
        ok(is_size_fixed($_), "is_size_fixed(" . explain_args($_) . ")");
    }
    for (@bad) {
        ok(not(is_size_fixed($_)), "is_size_fixed(" . explain_args($_) . ")");
    }
}

sub test_is_size_wrap_content : Tests {
    no warnings qw(uninitialized);
    my ($self) = @_;
    my @ok = (size_wrap_content());
    my @bad = (undef, [], {}, 'str', size_match_parent(), size_fixed(1));
    for (@ok) {
        ok(
            is_size_wrap_content($_),
            "is_size_wrap_content(" . explain_args($_) . ")"
        );
    }
    for (@bad) {
        ok(
            not(is_size_wrap_content($_)),
            "is_size_wrap_content(" . explain_args($_) . ")"
        );
    }
}

sub test_is_size_match_parent : Tests {
    no warnings qw(uninitialized);
    my ($self) = @_;
    my @ok  = (size_match_parent(), size_match_parent(15));
    my @bad = (undef, [], {}, 'str', size_wrap_content(), size_fixed(1));
    for (@ok) {
        ok(
            is_size_match_parent($_),
            "is_size_match_parent(" . explain_args($_) . ")"
        );
    }
    for (@bad) {
        ok(
            not(is_size_match_parent($_)),
            "is_size_match_parent(" . explain_args($_) . ")"
        );
    }
}

sub test_sub_bad_args {
    my ($self, $sub, $sub_name, $args) = @_;
    my $errors = 0;
    local $self->{error_cb} = sub { $errors++ };
    my $got       = $sub->(@$args);
    my $test_name = $sub_name
      . '('
      . (@$args % 2 ? explain_args(@$args) : explain_args_hash(@$args))
      . ')';
    is($got,    undef, $test_name . ': in scalar content returns undef');
    is($errors, 1,     $test_name . ': has errors');
    $errors = 0;
    my @got = $sub->(@$args);
    ok(
        ($#got == 0 and not defined $got[0]),
        $test_name . ': in list content returns undef'
    );
    is($errors, 1, $test_name . ': in list content has errors');
    return;
}

sub test_border : Tests {
    my ($self) = @_;
    for my $n ('Inf', 'string', '-1', '-0.01') {
        for my $arg (qw(width radius)) {
            my $args = [color => '#fff', $arg => $n];
            $self->test_sub_bad_args(\&border, 'border', $args);
        }
    }
    is(border(), undef, 'empty args returns undef');
    my $got      = border(radius => '2.1', has_shadow => 8);
    my $expected = {
        corner_radius => 2,
        has_shadow    => 1,
    };
    is_deeply($got, $expected);
    is_json_number($got->{$_}, "$_ is number") for qw(corner_radius has_shadow);
    $got = border(color => '#FFF');
    $expected = { stroke => { color => '#fff' } };
    is_deeply($got, $expected);
    $got      = border(color => '#fff', width => 2.2, radius => 1.1);
    $expected = {
        stroke        => { color => '#fff', width => 2 },
        corner_radius => 1
    };
    is_deeply($got, $expected);
    is_json_number($got->{corner_radius},   "corner_radius is number");
    is_json_number($got->{stroke}->{width}, "width is number");
    return;
}

sub test_edge_insets : Tests {
    my ($self) = @_;
    for my $n ('Inf', 'string', '-1', '-0.01') {
        for my $arg (qw(left right top bottom)) {
            my $args = [$arg => $n];
            $self->test_sub_bad_args(\&edge_insets, 'edge_insets', $args);
        }
    }
    is(edge_insets(), undef, 'empty args returns undef');
    my $got      = edge_insets(left => 2.1, top => "0");
    my $expected = {
        left => 2,
        top  => 0,
    };
    is_deeply($got, $expected);
    is_json_number($got->{$_}, "$_ is number") for keys %$got;
    $got      = edge_insets(left => 2.1, top => "0", right => 2.3, bottom => 1);
    $expected = {
        left   => 2,
        top    => 0,
        right  => 2,
        bottom => 1,
    };
    is_deeply($got, $expected);
    is_json_number($got->{$_}, "$_ is number") for keys %$got;
    return;
}

sub test_size_fixed : Tests {
    my ($self) = @_;
    for my $n (undef, 'Inf', 'string', '-1', '-0.01') {
        $self->test_sub_bad_args(\&size_fixed, 'size_fixed', [$n]);
    }
    my $got      = size_fixed("5");
    my $expected = {
        type  => 'fixed',
        value => 5,
    };
    is_json_number($got->{value}, "value is number");
    is_deeply($got, $expected);
    $got      = size_fixed(2.3, DCV2_SIZE_UNIT_SP);
    $expected = {
        type  => 'fixed',
        value => 2,
        unit  => DCV2_SIZE_UNIT_SP,
    };
    is_json_number($got->{value}, "value is number");
    is_deeply($got, $expected);
    return;
}

sub test_size_wrap_content : Tests {
    my ($self) = @_;
    my $expected = { type => 'wrap_content' };
    my $got      = size_wrap_content();
    is_deeply($got, $expected);
    return;
}

sub test_size_match_parent : Tests {
    my ($self) = @_;
    for my $n ('Inf', 'string', '-1', '-0.01', 0) {
        $self->test_sub_bad_args(\&size_match_parent, 'size_match_parent', [$n]);
    }
    my $got      = size_match_parent();
    my $expected = {
        type => 'match_parent',
    };
    is_deeply($got, $expected);
    $got      = size_match_parent(5.2);
    $expected = {
        type       => 'match_parent',
        weight => 5.2,
    };
    is_json_number($got->{weight}, "weight is number");
    is_deeply($got, $expected);
    return;
}

sub test_visibility_action : Tests {
    my ($self) = @_;
    my @bad_args = (
        # no log_id
        [],
        # no log_id
        [url => 'ya.ru'],
        # bad percentage
        (
            map { [log_id => 'xxx', percentage => $_] }
              ('Inf', 'string', '-1', '-0.01', 0, 0.1, 101, 150)
        ),
        # bad duration
        (
            map { [log_id => 'xxx', duration => $_] }
              ('Inf', 'string', '-1', '-0.01')
        ),
    );
    for my $args (@bad_args) {
        $self->test_sub_bad_args(\&visibility_action, 'visibility_action', $args);
    }
    my $got = visibility_action(log_id => 0);
    my $expected = { log_id => 0 };
    is_deeply($got, $expected);
    is_json_string($got->{log_id}, 'log_id is string');
    $got = visibility_action(log_id => 12, url => 'https://ya.ru');
    $expected = { log_id => 12, url => 'https://ya.ru' };
    is_deeply($got, $expected);
    is_json_string($got->{log_id}, 'log_id is string');
    $got = visibility_action(
        log_id     => 130,
        url        => 'https://ya.ru',
        percentage => "78.2",
        duration   => "30.2",
    );
    $expected = {
        log_id                => 130,
        url                   => 'https://ya.ru',
        visibility_percentage => 78,
        visibility_duration   => 30,
    };
    is_deeply($got, $expected);
    is_json_string($got->{log_id}, 'log_id is string');
    is_json_number($got->{$_}, "$_ is number")
      for qw(visibility_percentage visibility_duration);
    return;
}

1;
