package DivCardV2::Base::Div::IAddItems::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro;

use base qw(DivCardV2::Base::Div::Test);

use DivCardV2::Base::Utils qw(:all);
use DivCardV2::Base::Div::Image;
use DivCardV2::Base::Div::Text;

use MTH;
use Test::More;

sub class {'DivCardV2::Base::Div::IAddItems'}

sub to_struct_expected {
    my $struct = shift->next::method(@_);
    $struct->{items} = [
        { type => 'image', image_url => 'http://ya.ru' },
    ];
    return $struct;
}

sub test_to_struct_pre_cb {
    my $obj = shift->next::method(@_);
    $obj->add_item(DivCardV2::Base::Div::Image->new(image_url => 'http://ya.ru'));
    return $obj;
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

sub test_add_item : Tests {
    my ($self) = @_;
    my $errors = 0;
    $self->class->on_error_cb(sub { $errors++ });
    my $obj = $self->class->new();
    # error #1 - no args
    $obj->add_item()
      # error #2 - bad instance
      ->add_item(action(log_id => 1))
      ->add_item(DivImage(image_url => 'http://ya.ru'));
    my $got      = $obj->_dev_to_struct->{items};
    my $expected = [
        { type => 'image', image_url => 'http://ya.ru' },
    ];
    is_deeply($got, $expected);
    is($errors, 2);
    return;
}

sub add_item_overload : Tests {
    my ($self) = @_;
    my $errors = 0;
    $self->class->on_error_cb(sub { $errors++ });
    my $obj = $self->class->new();
    no warnings qw(void);
    # error 1 - not supported
    $obj <<= DivImage(image_url => 'http://ya.ru');
    # swap - no errors and no reaction
    DivImage(image_url => 'http://ya.ru') << $obj;
    # error 2 and 3 bad args
    $obj << 0 << action(log_id => 1);
    $obj << DivImage(image_url => 'http://ya.ru') << DivText(text => 'xxx');
    my $got      = $obj->_dev_to_struct->{items};
    my $expected = [
        { type => 'image', image_url => 'http://ya.ru' },
        { type => 'text',  text      => 'xxx' },
    ];
    is_deeply($got, $expected);
    is($errors, 3);
    return;
}

1;

