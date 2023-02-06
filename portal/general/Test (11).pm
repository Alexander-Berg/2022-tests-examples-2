package DivCardV2::Base::Div::Tabs::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro 'c3';

use base qw(
  DivCardV2::Base::Div::Test
);

use Test::More;
use MTH;

use DivCardV2::Base::Constants;
use DivCardV2::Base::Utils qw(:all);
use DivCardV2::Base::Div::Image;

sub class {'DivCardV2::Base::Div::Tabs'}

sub short_constructor { 'DivTabs' }

sub set_methods_startup : Test(startup) {
    my $self = shift;
    $self->next::method(@_);
    my $tests = $self->{set_methods_tests};
    $tests->{set_title_paddings} = {
        obj_key => 'title_paddings',
        tests   => $self->set_methods_tests_edge_insets(),
    };
    $tests->{set_separator_paddings} = {
        obj_key => 'separator_paddings',
        tests   => $self->set_methods_tests_edge_insets(),
    };
    $tests->{set_selected_tab} = {
        obj_key => 'selected_tab',
        tests   => $self->set_methods_tests_non_negative_integer(),
    };
    $tests->{set_has_separator} = {
        obj_key => 'has_separator',
        tests   => $self->set_methods_tests_bool(),
    };
    $tests->{set_switch_tabs} = {
        obj_key => 'switch_tabs_by_content_swipe_enabled',
        tests   => $self->set_methods_tests_bool(),
    };
    $tests->{set_separator_color} = {
        obj_key => 'separator_color',
        tests   => $self->set_methods_tests_color(),
    };
    $tests->{set_tab_title_style} = {
        obj_key => 'tab_title_style',
        tests   => [
            { args => [], expected => undef },
            { args => [font_size => 'Inf'], expected => undef, errors => 1 },
            { args => [line_height => -1], expected => undef, errors => 1 },
            { args => [letter_spacing => ''], expected => undef, errors => 1 },
            {
                args => [
                    font_size       => "13",
                    line_height     => "15",
                    color_inactive  => '#FF0002',
                    bg_color_active => '#FF0003',
                ],
                expected => {
                    font_size               => 13,
                    line_height             => 15,
                    inactive_text_color     => '#ff0002',
                    active_background_color => '#ff0003',
                },
            },
        ],
        no_constructor => 1,
    };
    return;
}

sub to_struct_expected {
    my $struct = shift->next::method(@_);
    $struct->{type}           = 'tabs';
    $struct->{title_paddings} = {
        left => 5,
        top  => 2,
    };
    $struct->{separator_paddings} = {
        right  => 0,
        bottom => 1,
    };
    $struct->{selected_tab}    = 0;
    $struct->{has_separator}   = 1;
    $struct->{separator_color} = '#ff0012';
    $struct->{items}           = [
        {
            title => '123',
            div   => {
                type      => 'image',
                image_url => 'http://ya.ru',
            },
            title_click_action => {
                url    => 'http://ya.ru',
                log_id => '0',
            },
        },
    ];
    $struct->{switch_tabs_by_content_swipe_enabled} = 0;
    $struct->{tab_title_style}                      = {
        font_size               => 13,
        line_height             => 15,
        letter_spacing          => 0,
        font_weight             => DCV2_FW_REGULAR,
        paddings                => { left => 5, top => 2 },
        active_text_color       => '#ff0001',
        inactive_text_color     => '#ff0002',
        active_background_color => '#ff0003',
    };
    return $struct;
}

sub test_to_struct_pre_cb {
    my $obj = shift->next::method(@_);
    $obj->add_item(
        123 => DivCardV2::Base::Div::Image->new(image_url => 'http://ya.ru'),
        action(log_id => 0, url => 'http://ya.ru'),
    );
    $obj->set_tab_title_style(
        font_size       => "13",
        line_height     => "15",
        letter_spacing  => "0",
        font_weight     => DCV2_FW_REGULAR,
        paddings        => edge_insets(left => 5, top => 2),
        color_active    => '#FF0001',
        color_inactive  => '#FF0002',
        bg_color_active => '#FF0003',
    );
    return $obj;
}

sub test_to_struct : Tests {
    push @_, (
        title_paddings     => edge_insets(left  => "5", top    => "2"),
        separator_paddings => edge_insets(right => "0", bottom => "1"),
        selected_tab       => '0',
        has_separator      => 'yes',
        switch_tabs        => '0',
        separator_color    => '#FF0012',
    );
    my $got = shift->next::method(@_);
    is_json_string($got->{items}->[0]->{title});
    is_json_string($got->{items}->[0]->{title_click_action}->{log_id});
    is_json_number($got->{title_paddings}->{left});
    is_json_number($got->{title_paddings}->{top});
    is_json_number($got->{separator_paddings}->{right});
    is_json_number($got->{separator_paddings}->{bottom});
    is_json_number($got->{selected_tab});
    is_json_number($got->{has_separator});
    is_json_number($got->{switch_tabs_by_content_swipe_enabled});
    is_json_string($got->{separator_color});
    is_json_number($got->{tab_title_style}->{font_size});
    is_json_number($got->{tab_title_style}->{line_height});
    is_json_number($got->{tab_title_style}->{letter_spacing});
    is_json_string($got->{tab_title_style}->{font_weight});
    is_json_number($got->{tab_title_style}->{paddings}->{left});
    is_json_number($got->{tab_title_style}->{paddings}->{top});
    is_json_string($got->{tab_title_style}->{active_text_color});
    is_json_string($got->{tab_title_style}->{inactive_text_color});
    is_json_string($got->{tab_title_style}->{active_background_color});
    return $got;
}

sub test_to_struct_no_items : Tests {
    my ($self) = @_;
    my $obj = $self->class->new(
        border   => border(color => '#ffffff', radius => "3"),
        width    => size_fixed("3"),
        height   => size_wrap_content(),
        paddings => edge_insets(left => "5", top => "2"),
        margins  => edge_insets(right => "0", bottom => "1"),
    );
    my $errors = 0;
    $obj->on_error_cb(sub { $errors++ });
    my $got = $obj->to_struct();
    is($got,    undef);
    is($errors, 1);
    return;
}

sub test_to_struct_bad_selected_tab : Tests {
    my ($self) = @_;
    my $obj = $self->class->new(
        selected_tab => 3,
    );
    $obj->add_item(
        123 => DivCardV2::Base::Div::Image->new(image_url => 'http://ya.ru'),
    );
    my $errors = 0;
    $obj->on_warning_cb(sub { $errors++ });
    my $got      = $obj->to_struct();
    my $expected = {
        selected_tab => 0,
        items        => [
            {
                title => '123',
                div   => {
                    type      => 'image',
                    image_url => 'http://ya.ru',
                },
            },
        ],
        type => 'tabs',
    };
    is_deeply($got, $expected);
    is_json_number($got->{selected_tab});
    is($errors, 1);
    return;
}

sub test_add_item : Tests {
    my ($self) = @_;
    my $errors = 0;
    $self->class->on_error_cb(sub { $errors++ });
    my $obj   = $self->class->new();
    my $image = DivImage(image_url => 'http://ya.ru');
    # error #1 - no args
    $obj->add_item()
      # error #2 - no item
      ->add_item("some title")
      # error #3 - no title
      ->add_item('', $image)
      # error #4 bad instance
      ->add_item('title' => action(log_id => 1))
      ->add_item(0, $image)
      ->add_item('title_2', $image, action(log_id => 1, url => 'http://ya.ru'));
    my $got      = $obj->_dev_to_struct->{items};
    my $expected = [
        {
            title => '0',
            div   => {
                type      => 'image',
                image_url => 'http://ya.ru',
            },
        },
        {
            title => 'title_2',
            div   => {
                type      => 'image',
                image_url => 'http://ya.ru',
            },
            title_click_action => {
                url    => 'http://ya.ru',
                log_id => '1',
            },
        },
    ];
    is_deeply($got, $expected);
    is_json_string($_->{title}) for @$got;
    is($errors, 4);
    return;
}

sub test_add_item_overload : Tests {
    my ($self) = @_;
    no warnings qw(void);
    my $errors = 0;
    $self->class->on_error_cb(sub { $errors++ });
    my $obj   = $self->class->new();
    my $image = DivImage(image_url => 'http://ya.ru');
    # error 1 - not supported
    $obj <<= [some_title => $image];
    # error 2 - bad args
    $obj << 0;
    # swap - no errors and no reaction
    [some_title => $image] << $obj;
    # error 3 and 4 bad args
    $obj << [] << ['xxx'];
    $obj << [0, $image]
      << ['title_2', $image, action(log_id => 1, url => 'http://ya.ru')];
    my $got      = $obj->_dev_to_struct->{items};
    my $expected = [
        {
            title => '0',
            div   => {
                type      => 'image',
                image_url => 'http://ya.ru',
            },
        },
        {
            title => 'title_2',
            div   => {
                type      => 'image',
                image_url => 'http://ya.ru',
            },
            title_click_action => {
                url    => 'http://ya.ru',
                log_id => '1',
            },
        },
    ];
    is_deeply($got, $expected);
    is_json_string($_->{title}) for @$got;
    is($errors, 4);
    return;
}

sub test_mk_tab_title_style : Tests {
    my ($self) = @_;
    my @bad_args = (
        # bad font_size
        (
            map { [font_size => $_] }
              ('Inf', 'string', '-1', '-0.01')
        ),
        # bad line_height
        (
            map { [line_height => $_] }
              ('Inf', 'string', '-1', '-0.01')
        ),
        # bad letter_spacing
        (
            map { [letter_spacing => $_] }
              ('Inf', 'string', '')
        ),
    );
    for my $args (@bad_args) {
        my $test_name = $self->class . '->new()->_mk_tab_title_style('
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
        my $got = $obj->_mk_tab_title_style(@$args);
        is($got,    undef, "$test_name: in scalar content returns undef");
        is($errors, 1,     "$test_name: has errors");
        $errors = 0;
        my @got = $obj->_mk_tab_title_style(@$args);
        ok(
            ($#got == 0 and not defined $got[0]),
            "$test_name: in list content returns undef"
        );
        is($errors, 1, "$test_name: in list content has errors");
    }
    my $obj = $self->class->new();
    my $got = $obj->_mk_tab_title_style(
        font_size       => "13",
        line_height     => "15",
        letter_spacing  => "0",
        font_weight     => DCV2_FW_REGULAR,
        paddings        => edge_insets(left => 5, top => 2, right => 0, bottom => 1),
        color_active    => '#FF0001',
        color_inactive  => '#FF0002',
        bg_color_active => '#FF0003',
    );
    my $expected = {
        font_size               => 13,
        line_height             => 15,
        letter_spacing          => 0,
        font_weight             => DCV2_FW_REGULAR,
        paddings                => { left => 5, top => 2, right => 0, bottom => 1 },
        active_text_color       => '#ff0001',
        inactive_text_color     => '#ff0002',
        active_background_color => '#ff0003',
    };
    is_deeply($got, $expected);
    is_json_number($got->{font_size});
    is_json_number($got->{line_height});
    is_json_number($got->{letter_spacing});
    is_json_string($got->{font_weight});
    is_json_number($got->{paddings}->{left});
    is_json_number($got->{paddings}->{top});
    is_json_number($got->{paddings}->{right});
    is_json_number($got->{paddings}->{bottom});
    is_json_string($got->{active_text_color});
    is_json_string($got->{inactive_text_color});
    is_json_string($got->{active_background_color});
    return;
}

1;
