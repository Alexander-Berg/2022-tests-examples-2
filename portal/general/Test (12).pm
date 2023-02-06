package DivCardV2::Base::Div::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro;

use base qw(Test::Class);

use MTH;

use Test::More;
use JSON::XS qw(decode_json);

use DivCardV2::Base::Constants;
use DivCardV2::Base::Utils qw(:all);

sub class {'DivCardV2::Base::Div'}

sub short_constructor { }

sub isa_tests {
    my ($self, $instance) = @_;
    my $isa = mro::get_linear_isa(ref $self);
    my $ok  = 1;
    for my $class ('DivCardV2::Base::Object',
        map { $_->class } grep { $_->can('class') } @$isa
    ) {
        $ok = isa_ok($instance, $class);
    }
    return $ok;
}

sub requier : Test(startup => no_plan) {
    my ($self) = @_;
    my $pkg = $self->class;
    use_ok($pkg);
    $self->isa_tests($pkg);
    return $pkg;
}

sub set_methods_tests_number {
    my ($self, $integer, $min, $max) = @_;
    my @tests = (
        {
            args     => [],
            expected => undef,
            errors   => 1,
        },
        (
            map { {
                    args     => [$_],
                    expected => undef,
                    errors   => 1,
            } } undef, '', qw(Inf -Inf NaN string)
        ),
    );
    if (defined $min) {
        push @tests, { args => [($min - 1)], expected => undef, errors => 1 };
    }
    if (defined $max) {
        push @tests, { args => [($max + 1)], expected => undef, errors => 1 };
    }
    $min //= -5;
    $max //= 5;
    ($min, $max) = ($max, $min) if $min > $max;
    if ($min <= 0 and 0 <= $max) {
        push @tests, { args => [0], expected => 0 };
    }
    else {
        push @tests, { args => [0], expected => undef, errors => 1 };
    }
    if ($integer and int($max) == $max) {
        $max += 0.5;
    }
    my $step = $integer ? int(($max - $min) / 3) + 0.5 : ($max - $min) / 7;
    for (my $n = $min; $n < $max; $n += $step) {
        next if $n == 0;
        last if $n eq $max;    # double precision
        push @tests, { args => [$n], expected => ($integer ? int($n) : $n) };
    }
    push @tests, { args => [$max], expected => ($integer ? int($max) : $max) };
    return \@tests;
}

sub set_methods_tests_non_negative_integer {
    return $_[0]->set_methods_tests_number(1, 0);
}

sub set_methods_tests_non_empty_string {
    my ($self, $str, $no_zero_test) = @_;
    $str //= 'some_string';
    return [
        { args => [], expected => undef },
        { args => [undef], expected => undef },
        { args => [''],    expected => undef },
        { args => [$str], expected => $str },
        ($no_zero_test ? () : ({ args => ['0'], expected => '0' })),
    ];
}

sub set_methods_tests_constant {
    my ($self, $good) = @_;
    return $self->set_methods_tests_non_empty_string($good, 1);
}

sub set_methods_tests_url {
    $_[0]->set_methods_tests_non_empty_string('https://yandex.ru', 1);
}

sub set_methods_tests_color {
    return [
        { args => [], expected => undef },
        { args => [undef],     expected => undef },
        { args => [''],        expected => undef },
        { args => ['#FF0102'], expected => '#ff0102' },
    ];
}

sub set_methods_tests_edge_insets {
    return [
        { args => [], expected => undef },
        { args => [[]], expected => undef },
        { args => [undef], expected => undef },
        { args => ['xxx'], expected => undef },

        {
            args     => [edge_insets(left => 5, top => 2)],
            expected => { left => 5, top => 2 },
        },
        {
            args     => [left => -5],
            expected => undef,
            errors   => 1,
        },
        {
            args     => [x => 1, y => 2],
            expected => undef,
        },
        {
            args     => [right  => 0, bottom => 1],
            expected => { right => 0, bottom => 1 },
        },
    ];
}

sub set_methods_tests_bool {
    state $json_true  = decode_json('[true]')->[0];
    state $json_false = decode_json('[false]')->[0];
    return [
        { args => [], expected => 0 },
        { args => [undef], expected => 0 },
        { args => [0],     expected => 0 },
        { args => [''],    expected => 0 },
        { args => [$json_false], expected => 0 },
        { args => [1],      expected => 1 },
        { args => ['true'], expected => 1 },
        { args => [$json_true], expected => 1 },
    ];
}

sub set_methods_startup : Test(startup) {
    my ($self) = @_;
    my %tests = (
        # NOTE: Так как большинство методов set_*, реализовано через
        #       DivCardV2::Base::Utils, то в данном месте не требуется такое
        #       детальное тестирование различных параметров, так как его уже
        #       покрывают тесты к модулю DivCardV2::Base::Utils
        set_border => {
            obj_key => 'border',
            tests   => [
                { args => [], expected => undef },
                { args => [[]], expected => undef },
                { args => [undef], expected => undef },
                { args => ['xxx'], expected => undef },
                {
                    args     => [border(color => '#fff')],
                    expected => { stroke => { color => '#fff' } },
                },
                {
                    args     => [color => '#fff', width => '-1'],
                    expected => undef,
                    errors   => 1,
                },
                {
                    args     => [radius         => 3, has_shadow => 1],
                    expected => { corner_radius => 3, has_shadow => 1 },
                },
            ],
        },
        set_width => {
            obj_key => 'width',
            tests   => [
                { args => [], expected => undef },
                { args => [[]], expected => undef },
                { args => [undef], expected => undef },
                { args => ['xxx'], expected => undef },
                {
                    args     => [size_fixed(3, DCV2_SIZE_UNIT_SP)],
                    expected => {
                        type  => 'fixed',
                        value => 3,
                        unit  => DCV2_SIZE_UNIT_SP
                    }
                },
                {
                    args     => [size_wrap_content()],
                    expected => { type => 'wrap_content' },
                },
                {
                    args     => [size_match_parent(5.2)],
                    expected => { type => 'match_parent', weight => 5.2 },
                },
            ],
        },
        set_width_fixed => {
            obj_key => 'width',
            tests   => [
                { args => [undef], expected => undef, errors => 1 },
                { args => ['xxx'], expected => undef, errors => 1 },
                { args => [-5],    expected => undef, errors => 1 },
                { args => [3], expected => { type => 'fixed', value => 3 }, },
            ],
            no_constructor => 1,
        },
        set_width_wrap_content => {
            obj_key => 'width',
            tests   => [
                { args => [undef], expected => { type => 'wrap_content' } },
            ],
            no_constructor => 1,
        },
        set_width_match_parent => {
            obj_key => 'width',
            tests   => [
                { args => ['xxx'], expected => undef, errors => 1 },
                { args => [-5],    expected => undef, errors => 1 },
                { args => [undef], expected => { type => 'match_parent' } },
                { args => [], expected => { type => 'match_parent' } },
                {
                    args     => [6.3],
                    expected => { type => 'match_parent', weight => 6.3 }
                },
            ],
            no_constructor => 1,
        },
        set_paddings => {
            obj_key => 'paddings',
            tests   => $self->set_methods_tests_edge_insets(),
        },
        set_margins => {
            obj_key => 'margins',
            tests   => $self->set_methods_tests_edge_insets(),
        },
        set_alpha => {
            obj_key => 'alpha',
            tests   => $self->set_methods_tests_number(0, 0, 1),
        },
        set_valign => {
            obj_key => 'alignment_vertical',
            tests   => $self->set_methods_tests_constant(DCV2_VALIGN_TOP),
        },
        set_halign => {
            obj_key => 'alignment_horizontal',
            tests   => $self->set_methods_tests_constant(DCV2_HALIGN_LEFT),
        },
        set_row_span => {
            obj_key => 'row_span',
            tests   => $self->set_methods_tests_non_negative_integer(),
        },
        set_column_span => {
            obj_key => 'column_span',
            tests   => $self->set_methods_tests_non_negative_integer(),
        },
        set_visibility_action => {
            obj_key => 'visibility_action',
            tests   => [
                { args => [], expected => undef },
                { args => [[]], expected => undef },
                { args => [undef], expected => undef },
                { args => ['xxx'], expected => undef },
                {
                    args     => [visibility_action(log_id => 'xxx')],
                    expected => { log_id => 'xxx' },
                },
                {
                    args     => [log_id => 'xxx', duration => -1],
                    expected => undef,
                    errors   => 1,
                },
                {
                    args     => [log_id => 'xxx', percentage => -1],
                    expected => undef,
                    errors   => 1
                },
                {
                    args     => [log_id  => 12, url => 'https://ya.ru'],
                    expected => { log_id => 12, url => 'https://ya.ru' },
                },
                {
                    args => [
                        log_id => 130, url => 'https://ya.ru', percentage => 78
                    ],
                    expected => {
                        log_id                => 130,
                        url                   => 'https://ya.ru',
                        visibility_percentage => 78,
                    },
                },
            ],
        },
    );
    for (grep {/width/} keys %tests) {
        my $tests = $tests{$_}->{tests};
        s/width/height/;
        $tests{$_} = { obj_key => 'height', tests => $tests };
    }
    $self->{set_methods_tests} = \%tests;
    return;
}

sub scope_create : Test(setup) {
    my ($self) = @_;
    $self->{guard} = $self->class->scope();
    return;
}

sub scope_cleanup : Test(teardown) {
    my ($self) = @_;
    delete $self->{guard};
    return;
}

sub simple_creation : Tests {
    my ($self) = @_;
    my $obj = $self->class->new();
    ok($obj, $self->class . '->new()');
    $self->isa_tests($obj);
    return $obj;
}

sub test_short_constructor : Tests {
    my ($self) = @_;
    my $sub = $self->short_constructor;
    return unless $sub;
    my $obj;
    eval {
        no strict 'refs';
        $obj = &{"$sub"}();
    };
    ok($obj, "$sub()")
      or return;
    $self->isa_tests($obj);
    return $obj;
}

sub creation_with_args : Tests {
    my ($self) = @_;
    # по факту все аргументы конструктора передаются в методы set_*
    my $tests = $self->{set_methods_tests};
    for my $method (grep { not $tests->{no_constructor} } keys %$tests) {
        my $key   = $tests->{$method}->{obj_key};
        my $param = $method =~ s/^set_//r;
        for my $test (@{ $tests->{$method}->{tests} }) {
            my $args = $test->{args};
            # аргумент в конструкторе может быть только один
            next if @$args != 1;
            my $errors     = 0;
            my $errors_exp = $test->{errors} // 0;
            $self->class->on_error_cb(sub { $errors++ });
            my $obj       = $self->class->new($param => $args->[0]);
            my $got       = $obj->_dev_to_struct->{$key};
            my $test_name = $self->class . '->new('
              . explain_args_hash($param => $args->[0])
              . ')';
            is_deeply($got, $test->{expected}, $test_name . ': deep test');
            is($errors, $errors_exp, $test_name . ': errors count');
            $self->isa_tests($obj);
        }
    }
    return;
}

sub to_struct_expected {
    return {
        border => {
            corner_radius => 3,
            stroke        => { color => '#ffffff' },
        },
        width => {
            type  => 'fixed',
            value => 3,
        },
        height   => { type => 'wrap_content' },
        paddings => {
            left => 5,
            top  => 2,
        },
        margins => {
            right  => 0,
            bottom => 1,
        },
        alpha                => 0.5,
        alignment_horizontal => DCV2_HALIGN_LEFT,
        alignment_vertical   => DCV2_VALIGN_TOP,
        row_span             => 2,
        column_span          => 2,
        visibility_action    => {
            log_id                => 130,
            url                   => 'https://ya.ru',
            visibility_percentage => 78,
        },
        background => [
            { type => 'solid',    color  => '#ff0011' },
            { type => 'gradient', colors => ['#ffab4e', '#fff'], angle => 127 },
        ],
    };
}

sub test_to_struct_pre_cb {
    my ($self, $obj) = @_;
    $obj->add_background_solid("#ff0011");
    $obj->add_background_gradient('#FFAb4e', '#fff', 127);
    return $obj;
}

sub test_to_struct : Tests {
    my $self = shift;
    my $obj  = $self->class->new(
        border            => border(color => '#ffffff', radius => "3"),
        width             => size_fixed("3"),
        height            => size_wrap_content(),
        paddings          => edge_insets(left => "5", top => "2"),
        margins           => edge_insets(right => "0", bottom => "1"),
        alpha             => "0.5",
        valign            => DCV2_VALIGN_TOP,
        halign            => DCV2_HALIGN_LEFT,
        row_span          => "2",
        column_span       => "2",
        visibility_action => visibility_action(
            log_id => 130, url => 'https://ya.ru', percentage => "78"
        ),
        @_,
    );
    $self->test_to_struct_pre_cb($obj);
    my $expected = $self->to_struct_expected();
    my $got      = $obj->to_struct();
    is_deeply($got, $expected);
    is_json_number($got->{border}->{corner_radius});
    is_json_string($got->{border}->{stroke}->{color});
    is_json_string($got->{width}->{type});
    is_json_number($got->{width}->{value});
    is_json_string($got->{height}->{type});
    is_json_number($got->{paddings}->{left});
    is_json_number($got->{paddings}->{top});
    is_json_number($got->{margins}->{right});
    is_json_number($got->{margins}->{bottom});
    is_json_number($got->{alpha});
    is_json_string($got->{alignment_horizontal});
    is_json_string($got->{alignment_vertical});
    is_json_number($got->{row_span});
    is_json_number($got->{column_span});
    is_json_string($got->{visibility_action}->{log_id});
    is_json_string($got->{visibility_action}->{url});
    is_json_number($got->{visibility_action}->{visibility_percentage});
    is_json_string($got->{background}->[0]->{type});
    is_json_string($got->{background}->[0]->{color});
    is_json_string($got->{background}->[1]->{type});
    is_json_string($got->{background}->[1]->{colors}->[0]);
    is_json_string($got->{background}->[1]->{colors}->[1]);
    is_json_number($got->{background}->[1]->{angle});
    return $got;
}

sub test_add_background_solid : Tests {
    my ($self) = @_;
    my $errors = 0;
    $self->class->on_error_cb(sub { $errors++ });
    my $obj = $self->class->new()
      ->add_background_solid()         # error #1 - no color
      ->add_background_solid(undef)    # error #2 - undef color
      ->add_background_solid('#FFAb4e')
      ->add_background_solid('#fff');
    my $expected = [
        { type => 'solid', color => '#ffab4e' },
        { type => 'solid', color => '#fff' },
    ];
    my $got = $obj->_dev_to_struct;
    is_deeply($got->{background}, $expected);
    is($errors, 2);
    return;
}

sub test_add_background_gradient : Tests {
    my ($self) = @_;
    my $errors = 0;
    $self->class->on_error_cb(sub { $errors++ });
#<<<
    my $obj = $self->class->new()
      ->add_background_gradient()           # error #1 - no colors
      ->add_background_gradient(undef)      # error #2 - undef start_color
      ->add_background_gradient('#FFAb4e')  # error #3 - only start color
      ->add_background_gradient(undef,     '#fff')  # error #4 - only end color
      ->add_background_gradient('#FFAb4e', '#fff', -5)   # error #5 - bad angle
      ->add_background_gradient('#FFAb4e', '#fff', 368)  # error #6 - bad angle
      ->add_background_gradient('#FFAb4e', '#fff')
      ->add_background_gradient('#FFAb4e', '#fff', 0.5)
      ->add_background_gradient('#FFAb4e', '#fff', 127);
#>>>
    my $expected = [
        { type => 'gradient', colors => ['#ffab4e', '#fff'] },
        { type => 'gradient', colors => ['#ffab4e', '#fff'], angle => 0 },
        { type => 'gradient', colors => ['#ffab4e', '#fff'], angle => "127" },
    ];
    my $got = $obj->_dev_to_struct;
    is_deeply($got->{background}, $expected);
    is($errors, 6);
    for my $bg (grep { exists $_->{angle} } @{ $got->{background} }) {
        is_json_number($bg->{angle});
    }
    return;
}

sub test_add_background_image : Tests {
    my ($self) = @_;
    my $errors = 0;
    $self->class->on_error_cb(sub { $errors++ });
#<<<
    my $obj = $self->class->new()
      ->add_background_image()         # error #1 - no image url
      ->add_background_image(undef)    # error #2 - undef imegae url
      # error #3 bad alpha
      ->add_background_image('https://yastatic.net/1.png', alpha => 2.2)
      # error #4 bad alpha
      ->add_background_image('https://yastatic.net/1.png', alpha => -1)
      ->add_background_image('https://yastatic.net/1.png')
      ->add_background_image('https://yastatic.net/1.png',
        scale => DCV2_ISCALE_NO,
      )
      ->add_background_image('https://yastatic.net/1.png',
        valign => DCV2_VALIGN_TOP,
        halign => DCV2_HALIGN_LEFT,
        alpha  => "0.7"
      )
      ->add_background_image('https://yastatic.net/1.png',
        scale => DCV2_ISCALE_FILL,
        alpha => "0.2"
      );

#>>>
    my $expected = [
        {
            type      => 'image',
            image_url => 'https://yastatic.net/1.png',
        },
        {
            type      => 'image',
            image_url => 'https://yastatic.net/1.png',
            scale     => DCV2_ISCALE_NO,
        },
        {
            type                         => 'image',
            image_url                    => 'https://yastatic.net/1.png',
            content_alignment_vertical   => DCV2_VALIGN_TOP,
            content_alignment_horizontal => DCV2_HALIGN_LEFT,
            alpha                        => 0.7,
        },
        {
            type      => 'image',
            image_url => 'https://yastatic.net/1.png',
            alpha     => 0.2,
            scale     => DCV2_ISCALE_FILL,
        },
    ];
    my $got = $obj->_dev_to_struct;
    is_deeply($got->{background}, $expected);
    is($errors, 4);
    for my $bg (grep { exists $_->{alpha} } @{ $got->{background} }) {
        is_json_number($bg->{alpha});
    }
    return;
}

sub test_set_methods : Tests {
    my ($self) = @_;
    my $tests = $self->{set_methods_tests};
    for my $method (keys %$tests) {
        can_ok($self->class, $method) or next;
        my $key = $tests->{$method}->{obj_key};
        for my $test (@{ $tests->{$method}->{tests} }) {
            my $errors     = 0;
            my $errors_exp = $test->{errors} // 0;
            $self->class->on_error_cb(sub { $errors++ });
            my $args      = $test->{args};
            my $obj       = $self->class->new();
            my $ret       = $obj->$method(@$args);
            my $got       = $obj->_dev_to_struct->{$key};
            my $test_name = $self->class . '->' . $method . '('
              . explain_args(@$args)
              . ')';
            is_deeply($got, $test->{expected}, $test_name . ': deep test');
            is($errors, $errors_exp, $test_name . ': errors count');
            is($ret,    $obj,        $test_name . ': returns $self');
        }
    }
    return;
}

1;
