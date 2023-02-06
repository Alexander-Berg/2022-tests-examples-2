package DivCardV2::Base::Div::Text::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro 'c3';

use base qw(
  DivCardV2::Base::Div::IAction::Test
);

use MTH;
use Test::More;

use DivCardV2::Base::Constants;
use DivCardV2::Base::Utils qw(:args);

sub class {'DivCardV2::Base::Div::Text'}

sub short_constructor {'DivText'}

sub set_methods_startup : Test(startup) {
    my $self = shift;
    $self->next::method(@_);
    my $tests = $self->{set_methods_tests};
    $tests->{set_font_size} = {
        obj_key => 'font_size',
        tests   => $self->set_methods_tests_non_negative_integer(),
    };
    $tests->{set_line_height} = {
        obj_key => 'line_height',
        tests   => $self->set_methods_tests_non_negative_integer(),
    };
    $tests->{set_max_lines} = {
        obj_key => 'max_lines',
        tests   => $self->set_methods_tests_non_negative_integer(),
    };
    $tests->{set_letter_spacing} = {
        obj_key => 'letter_spacing',
        tests   => $self->set_methods_tests_number(),
    };
    $tests->{set_font_weight} = {
        obj_key => 'font_weight',
        tests   => $self->set_methods_tests_constant(DCV2_FW_BOLD),
    };
    $tests->{set_text_valign} = {
        obj_key => 'text_alignment_vertical',
        tests   => $self->set_methods_tests_constant(DCV2_VALIGN_TOP),
    };
    $tests->{set_text_halign} = {
        obj_key => 'text_alignment_horizontal',
        tests   => $self->set_methods_tests_constant(DCV2_HALIGN_LEFT),
    };
    $tests->{set_text_color} = {
        obj_key => 'text_color',
        tests   => $self->set_methods_tests_color(),
    };
    $tests->{set_text} = {
        obj_key => 'text',
        tests   => [
            @{ $self->set_methods_tests_non_empty_string() },
            {
                args     => [$self->class->new(text => 123)],
                expected => '123',
            },
            {
                args     => [$self->class->new()],
                expected => undef,
                errors   => 0,
            },
        ],
    };
    return;
}

sub to_struct_expected {
    my $struct = shift->next::method(@_);
    $struct->{type}                      = 'text';
    $struct->{font_size}                 = 5;
    $struct->{line_height}               = 0;
    $struct->{max_lines}                 = 3;
    $struct->{letter_spacing}            = 6;
    $struct->{font_weight}               = DCV2_FW_BOLD;
    $struct->{text_alignment_vertical}   = DCV2_VALIGN_TOP;
    $struct->{text_alignment_horizontal} = DCV2_HALIGN_LEFT;
    $struct->{text_color}                = '#ff0012';
    $struct->{text}                      = '0000000000';
    $struct->{images}                    = [
        { start => 4, url => 'http://ya.ru' },
    ];
    $struct->{ranges} = [
        { start => 2, end => 3, font_size => 5 },
    ];
    return $struct;
}

sub test_to_struct_pre_cb {
    my $obj = shift->next::method(@_);
    $obj->add_image(4 => 'http://ya.ru')->add_range(2 => 3, font_size => 5);
    return $obj;
}

sub test_to_struct : Tests {
    push @_, (
        font_size      => '5',
        line_height    => '0',
        max_lines      => '3',
        letter_spacing => '6',
        font_weight    => DCV2_FW_BOLD,
        text_valign    => DCV2_VALIGN_TOP,
        text_halign    => DCV2_HALIGN_LEFT,
        text_color     => '#FF0012',
        text           => '0000000000',
    );
    my $got = shift->next::method(@_);
    is_json_number($got->{font_size});
    is_json_number($got->{line_height});
    is_json_number($got->{max_lines});
    is_json_number($got->{letter_spacing});
    is_json_string($got->{font_weight});
    is_json_string($got->{text_alignment_vertical});
    is_json_string($got->{text_alignment_horizontal});
    is_json_string($got->{text_color});
    is_json_string($got->{text});
    is_json_number($got->{images}->[0]->{start});
    is_json_string($got->{images}->[0]->{url});
    is_json_number($got->{ranges}->[0]->{start});
    is_json_number($got->{ranges}->[0]->{end});
    is_json_number($got->{ranges}->[0]->{font_size});
    return $got;
}

sub test_set_text_extra : Tests {
    my ($self) = @_;
    my $obj = $self->class->new(text_color => '#ff0000');
    $obj->set_text(
        $self->class->new(text => 'xxx', text_color => '#00ff00') . 'x'
    );
    my $got      = $obj->to_struct();
    my $expected = {
        type       => 'text',
        text       => 'xxxx',
        text_color => '#ff0000',
        ranges     => [{
                start      => 0,
                end        => 3,
                text_color => '#00ff00',
        }],
    };
    is_deeply($got, $expected);
    return;
}

sub test_to_struct_no_text : Tests {
    my ($self) = @_;
    my $text = $self->class->new(
        border   => border(color => '#ffffff', radius => "3"),
        width    => size_fixed("3"),
        height   => size_wrap_content(),
        paddings => edge_insets(left => "5", top => "2"),
        margins  => edge_insets(right => "0", bottom => "1"),
    );
    my $errors = 0;
    $text->on_error_cb(sub { $errors++ });
    my $got = $text->to_struct();
    is($got,    undef);
    is($errors, 1);
    return;
}

sub test_to_struct_bad_image_start : Tests {
    my ($self) = @_;
    my $obj = $self->class->new(text => '0123456789')
      ->add_image(14, 'http://ya.ru')
      ->add_image(15, 'http://ya.ru')
      ->add_image(5,  'http://ya.ru')
      ->add_image(10, 'http://ya.ru');
    my $errors = 0;
    $obj->on_warning_cb(sub { $errors++ });
    my $got      = $obj->to_struct();
    my $expected = {
        text   => '0123456789',
        images => [
            { start => 10, url => 'http://ya.ru' },
            { start => 10, url => 'http://ya.ru' },
            { start => 5,  url => 'http://ya.ru' },
            { start => 10, url => 'http://ya.ru' },
        ],
        type => 'text',
    };
    is_deeply($got, $expected);
    is_json_number($_->{start}) for @{ $got->{images} };
    is($errors, 2);
    return;
}

sub test_to_struct_bad_range_positions : Tests {
    my ($self) = @_;
    my $obj = $self->class->new(text => '0123456789')
      ->add_range(14, 15, text_color => '#abc000')
      ->add_range(1,  2,  text_color => '#abc000')
      ->add_range(2,  15, text_color => '#abc000')
      ->add_range(2,  10, text_color => '#abc000')
      ->add_range(9,  10, text_color => '#abc000');
    my $errors = 0;
    $obj->on_warning_cb(sub { $errors++ });
    my $got      = $obj->to_struct();
    my $expected = {
        text   => '0123456789',
        ranges => [
            { start => 1, end => 2,  text_color => '#abc000' },
            { start => 2, end => 10, text_color => '#abc000' },
            { start => 2, end => 10, text_color => '#abc000' },
            { start => 9, end => 10, text_color => '#abc000' },
        ],
        type => 'text',
    };
    is_deeply($got, $expected);
    is_json_number($_->{start}) for @{ $got->{ranges} };
    is_json_number($_->{end})   for @{ $got->{ranges} };
    is($errors, 2);
    return;
}

sub test_add_image : Tests {
    my ($self) = @_;
    my $errors = 0;
    $self->class->on_error_cb(sub { $errors++ });
    my $obj = $self->class->new(text => '123');
    $obj->add_image()    # error #1 - no args
      ->add_image('xxx', 'http://ya.ru')    # error #2 - bad start
      ->add_image('Inf', 'http://ya.ru')    # error #3 - bad start
      ->add_image('',    'http://ya.ru')    # error #4 - bad start
      ->add_image(undef, 'http://ya.ru')    # error #6 - no start
      ->add_image(0)                        # error #7 - no url
                                            # error #8 - bad width
      ->add_image(0, 'http://ya.ru', width => 0)
      # error #9 - bad width
      ->add_image(0, 'http://ya.ru', width => size_wrap_content())
      # error #10 - bad height
      ->add_image(0, 'http://ya.ru', height => 0)
      # error #11 - bad height
      ->add_image(0,   'http://ya.ru', height => size_wrap_content())
      ->add_image(0,   'http://ya.ru')
      ->add_image("1", 'http://ya.ru', width  => size_fixed("3"))
      ->add_image(2.2, 'http://ya.ru', height => size_fixed(5, DCV2_SIZE_UNIT_SP))
      ->add_image(3, 'http://ya.ru',
        width  => size_fixed("3"),
        height => size_fixed(5),
      )
      ->add_image(-1,   'http://ya.ru')
      ->add_image(-2,   'http://ya.ru')
      ->add_image(-100, 'http://ya.ru');
    my $got      = $obj->_dev_to_struct->{images};
    my $expected = [
        { start => 0, url => 'http://ya.ru' },
        {
            start => 1,
            url   => 'http://ya.ru',
            width => { type => 'fixed', value => 3 },
        },
        {
            start  => 2,
            url    => 'http://ya.ru',
            height => { type => 'fixed', value => 5, unit => DCV2_SIZE_UNIT_SP },
        },
        {
            start  => 3,
            url    => 'http://ya.ru',
            width  => { type => 'fixed', value => 3 },
            height => { type => 'fixed', value => 5 },
        },
        { start => 3, url => 'http://ya.ru' },
        { start => 2, url => 'http://ya.ru' },
        { start => 0, url => 'http://ya.ru' },
    ];
    is_deeply($got, $expected);
    for my $i (@$got) {
        is_json_string($i->{url}, 'url is string');
        is_json_number($i->{start}, 'start is number');
        for my $k (grep { $i->{$_} } qw(width height)) {
            is_json_number($i->{$k}->{value}, "$k.value is number");
        }
    }
    is($errors, 10);
    return;
}

sub test_add_range : Tests {
    my ($self) = @_;
    my $errors = 0;
    $self->class->on_error_cb(sub { $errors++ });
    my $obj = $self->class->new();
    # Детальное тестирование аргументов проводится в test_mk_range
    $obj->add_range('xxx', 10, font_size => "13")    # error #1 bad start
      ->add_range(10, 'xxx', font_size => "13")      # error #2 - bad end
      ->add_range(10, 15)                            # empty range
      ->add_range(2,  5, font_size => 5)
      ->add_range(4,  6, text_color => '#FFFFFF');
    my $got      = $obj->_dev_to_struct->{ranges};
    my $expected = [
        { start => 2, end => 5, font_size  => 5 },
        { start => 4, end => 6, text_color => '#ffffff' },
    ];
    is_deeply($got, $expected);
    is($errors, 2);
}

sub test_add_range_redefine : Tests {
    my ($self) = @_;
    $self->class->on_warning_quiet();
    my $obj = $self->class->new(
        text           => "Some text",
        font_size      => 10,
        text_color     => '#ffffff',
        letter_spacing => 1,
        font_weight    => DCV2_FW_REGULAR,
    );
    $obj->add_range(0, 2, letter_spacing => 2)
      ->add_range(0,   3,   text_color     => '#ff0000')
      ->add_range(100, 103, letter_spacing => 5)
      # Все цвета выше должны быть проигнорированы
      ->add_range(0, 100, text_color => '#000000', font_size => 5)
      ->add_range(0, 2,   text_color => '#ff0000', font_size => 3)
      ->add_range(3, 4,   font_size  => 3)
      ->add_range(0, 100, font_size  => 15)
      ->add_range(4, 5,   font_size  => 4)
      # Все размеры шрифта выше должны быть проигнорированы
      ->add_range(0, 100, font_size => 16);
    my $got      = $obj->to_struct();
    my $expected = {
        type           => 'text',
        text           => "Some text",
        font_size      => 16,
        text_color     => '#000000',
        letter_spacing => 1,
        font_weight    => DCV2_FW_REGULAR,
        ranges         => [
            { start => 0, end => 2, letter_spacing => 2 },
            { start => 0, end => 2, text_color     => '#ff0000' },
        ],
    };
    is_deeply($got, $expected);
}

sub test_mk_range : Tests {
    my ($self) = @_;
    my @bad_args = (
        # not numbers
        (
            map {
                [$_, 1, font_size => 5],
                  [0, $_, font_size => 5],
                  [0, 1, font_size      => $_],
                  [0, 1, letter_spacing => $_],
            } ('Inf', '', 'NaN', 'string')
        ),
        # bad non_negative_integer
        (
            map {
                [$_, 1, font_size => 5],
                  [0, $_, font_size => 5],
                  [0, 1, font_size => $_],
            } (-1, -0.1)
        ),
        # bad positive integer
        [0, 0, font_size => 5],
        # no start
        [undef, 1, font_size => 5],
        # no end
        [0, undef, font_size => 5],
    );
    for my $args (@bad_args) {
        my $test_name = $self->class . '->new()->_mk_range('
          . (
            join('', (explain($args)))
              =~ tr/ \t\r\n/ /sr
              =~ s/^\s*\[\s*|\s*\]\s*$//gr
          )
          . ')';
        my $obj    = $self->class->new();
        my $guard  = $obj->scope();
        my $errors = 0;
        $obj->on_error_cb(sub { $errors++ });
        my $got = $obj->_mk_range(@$args);
        is($got,    undef, "$test_name: in scalar content returns undef");
        is($errors, 1,     "$test_name: has errors");
        $errors = 0;
        my @got = $obj->_mk_range(@$args);
        ok(
            ($#got == 0 and not defined $got[0]),
            "$test_name: in list content returns undef"
        );
        is($errors, 1, "$test_name: in list content has errors");
    }
    my @warnings_args = (
        # start more than end
        [5, 2],
        # start equals end
        [5, 5],
    );
    for my $args (@warnings_args) {
        my $test_name = $self->class . '->new()->_mk_range('
          . (
            join('', (explain($args)))
              =~ tr/ \t\r\n/ /sr
              =~ s/^\s*\[\s*|\s*\]\s*$//gr
          )
          . ')';
        my $obj      = $self->class->new();
        my $guard    = $obj->scope();
        my $warnings = 0;
        $obj->on_warning_cb(sub { $warnings++ });
        my $got = $obj->_mk_range(@$args);
        is($got,      undef, "$test_name: in scalar content returns undef");
        is($warnings, 1,     "$test_name: has warnings");
        $warnings = 0;
        my @got = $obj->_mk_range(@$args);
        ok(
            ($#got == 0 and not defined $got[0]),
            "$test_name: in list content returns undef"
        );
        is($warnings, 1, "$test_name: in list content has warnings");
    }
    my $obj = $self->class->new();
    my $got = $obj->_mk_range("10.5", "15",
        font_size      => "13",
        letter_spacing => "0",
        font_weight    => DCV2_FW_REGULAR,
        text_color     => '#FF0001',
    );
    my $expected = {
        start          => 10,
        end            => 15,
        font_size      => 13,
        letter_spacing => 0,
        font_weight    => DCV2_FW_REGULAR,
        text_color     => '#ff0001',
    };
    is_deeply($got, $expected);
    is_json_number($got->{start});
    is_json_number($got->{end});
    is_json_number($got->{font_size});
    is_json_number($got->{letter_spacing});
    is_json_string($got->{font_weight});
    is_json_string($got->{text_color});
    return;
}

sub test_prop2range : Tests {
    my ($self) = @_;
    my @tests = (
        {
            args => [
                text => '01234',
            ],
            after_constructor => undef,
            expected          => {
                type => 'text',
                text => '01234',
            },
        },
        {
            args => [
                text      => '01234',
                font_size => 14,
            ],
            after_constructor => sub { $_[0]->add_range(0, 1, font_size => 5) },
            expected          => {
                ranges => [
                    { start => 0, end => 5, font_size => 14 },
                    { start => 0, end => 1, font_size => 5 },
                ],
                type => 'text',
                text => '01234',
            },
        },
        {
            args => [
                text           => '012',
                font_size      => 15,
                letter_spacing => 1,
                text_color     => '#FF0012',
                font_weight    => DCV2_FW_BOLD,
            ],
            after_constructor => undef,
            expected          => {
                text   => '012',
                type   => 'text',
                ranges => [
                    {
                        start          => 0,
                        end            => 3,
                        font_size      => 15,
                        letter_spacing => 1,
                        text_color     => '#ff0012',
                        font_weight    => DCV2_FW_BOLD,
                    },
                ],
            },
        },
        {
            args => [
                font_size      => 15,
                letter_spacing => 1,
                text_color     => '#FF0012',
                font_weight    => DCV2_FW_BOLD,
            ],
            after_constructor => undef,
            expected          => {
                type           => 'text',
                font_size      => 15,
                letter_spacing => 1,
                text_color     => '#ff0012',
                font_weight    => DCV2_FW_BOLD,
            },
        },
    );
    for my $test (@tests) {
        my $obj = $self->class->new(@{ $test->{args} });
        $test->{after_constructor}->($obj) if $test->{after_constructor};
        my $got = $obj->_prop2range->_dev_to_struct;
        is_deeply($got, $test->{expected});
    }
    return;
}

sub test_cat {
    my ($self) = @_;
    my $obj = $self->class->new(
        font_size      => 15,
        letter_spacing => 1,
        text_color     => '#FF0012',
        text           => '0123'
    );
    $obj->add_range(2, 3, font_size => 18);
    $obj->cat(
        $self->class->new(),
        "",
        '4567',
        $self->class->new(text => '89', letter_spacing => 2)
          ->add_range(0, 1, text_color => '#FF0012')
          ->add_image(1, 'http://ya.ru'),
        $self->class->new(text => 'XX'),
    );
    my $got      = $obj->to_struct();
    my $expected = {
        type   => 'text',
        text   => '0123456789XX',
        images => [
            { start => 9, url => 'http://ya.ru' },
        ],
        ranges => [
            {
                start          => 0,
                end            => 4,
                letter_spacing => 1,
                text_color     => '#ff0012',
            },
            {
                start     => 2,
                end       => 3,
                font_size => 18
            },
            {
                start          => 8,
                end            => 10,
                letter_spacing => 2,
            },
            {
                start      => 8,
                end        => 9,
                text_color => '#ff0012',
            },
        ],
    };
    is_deeply($got, $expected);
    return;
}

1;
