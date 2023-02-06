package DivCardV2::Base::Div::Gallery::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro 'c3';

use base qw(
  DivCardV2::Base::Div::IAddItems::Test
);

use Test::More;
use MTH;

use DivCardV2::Base::Utils qw(:all);
use DivCardV2::Base::Constants;

sub class {'DivCardV2::Base::Div::Gallery'}

sub short_constructor { 'DivGallery' }

sub set_methods_startup : Test(startup) {
    my $self = shift;
    $self->next::method(@_);
    my $tests = $self->{set_methods_tests};
    $tests->{set_item_spacing} = {
        obj_key => 'item_spacing',
        tests   => $self->set_methods_tests_non_negative_integer(),
    };
    $tests->{set_scroll_mode} = {
        obj_key => 'scroll_mode',
        tests   => $self->set_methods_tests_constant(DCV2_SM_DEFAULT),
    };
    return;
}

sub to_struct_expected {
    my $struct = shift->next::method(@_);
    $struct->{type}         = 'gallery';
    $struct->{scroll_mode}  = DCV2_SM_DEFAULT;
    $struct->{item_spacing} = 5;
    return $struct;
}

sub test_to_struct : Tests {
    push @_, (
        item_spacing => "5",
        scroll_mode  => DCV2_SM_DEFAULT,
    );
    my $got = shift->next::method(@_);
    is_json_number($got->{item_spacing});
    is_json_string($got->{scroll_mode});
    return $got;
}

1;
