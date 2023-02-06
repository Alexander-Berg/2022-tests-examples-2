package DivCardV2::Base::Div::Grid::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro 'c3';

use base qw(
  DivCardV2::Base::Div::IAction::Test
  DivCardV2::Base::Div::IContentAlignment::Test
  DivCardV2::Base::Div::IAddItems::Test
);

use Test::More;
use MTH;

use DivCardV2::Base::Div::Image;
use DivCardV2::Base::Utils qw(:all);

sub class {'DivCardV2::Base::Div::Grid'}

sub short_constructor { 'DivGrid' }

sub set_methods_startup : Test(startup) {
    my $self = shift;
    $self->next::method(@_);
    my $tests = $self->{set_methods_tests};
    $tests->{set_column_count} = {
        obj_key => 'column_count',
        tests   => $self->set_methods_tests_non_negative_integer(),
    };
    return;
}

sub to_struct_expected {
    my $struct = shift->next::method(@_);
    $struct->{type}         = 'grid';
    $struct->{column_count} = 5;
    return $struct;
}

sub test_to_struct : Tests {
    push @_, (
        column_count => "5",
    );
    my $got = shift->next::method(@_);
    is_json_number($got->{column_count});
    return $got;
}

sub test_to_struct_no_column_count : Tests {
    my ($self) = @_;
    my $grid = $self->class->new(
        border   => border(color => '#ffffff', radius => "3"),
        width    => size_fixed("3"),
        height   => size_wrap_content(),
        paddings => edge_insets(left => "5", top => "2"),
        margins  => edge_insets(right => "0", bottom => "1"),
    );
    $grid->add_item(DivCardV2::Base::Div::Image->new(image_url => 'http://ya.ru'));
    my $errors = 0;
    $grid->on_error_cb(sub { $errors++ });
    my $got = $grid->to_struct();
    is($got,    undef);
    is($errors, 1);
    return;
}

1;
