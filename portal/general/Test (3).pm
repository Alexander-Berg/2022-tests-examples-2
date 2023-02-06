package DivCardV2::Base::Div::Container::Test;

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

use DivCardV2::Base::Constants;

sub class {'DivCardV2::Base::Div::Container'}

sub short_constructor { 'DivContainer' }

sub set_methods_startup : Test(startup) {
    my $self = shift;
    $self->next::method(@_);
    my $tests = $self->{set_methods_tests};
    $tests->{set_orientation} = {
        obj_key => 'orientation',
        tests   => $self->set_methods_tests_constant(DCV2_ORIENTATION_O),
    };
    return;
}

sub to_struct_expected {
    my $struct = shift->next::method(@_);
    $struct->{type}        = 'container';
    $struct->{orientation} = DCV2_ORIENTATION_O;
    return $struct;
}

sub test_to_struct : Tests {
    push @_, (
        orientation => DCV2_ORIENTATION_O,
    );
    my $got = shift->next::method(@_);
    is_json_string($got->{orientation});
    return $got;
}

1;
