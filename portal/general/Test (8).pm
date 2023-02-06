package DivCardV2::Base::Div::IContentAlignment::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro;

use base qw(DivCardV2::Base::Div::Test);

use DivCardV2::Base::Constants;

use Test::More;
use MTH;

sub class {'DivCardV2::Base::Div::IContentAlignment'}

sub set_methods_startup : Test(startup) {
    my $self = shift;
    $self->next::method(@_);
    my $tests = $self->{set_methods_tests};
    $tests->{set_content_valign} = {
        obj_key => 'content_alignment_vertical',
        tests   => $self->set_methods_tests_constant(DCV2_VALIGN_TOP),
    };
    $tests->{set_content_halign} = {
        obj_key => 'content_alignment_horizontal',
        tests   => $self->set_methods_tests_constant(DCV2_HALIGN_LEFT),
    };
    return;
}

sub to_struct_expected {
    my $struct = shift->next::method(@_);
    $struct->{content_alignment_vertical}   = DCV2_VALIGN_TOP;
    $struct->{content_alignment_horizontal} = DCV2_HALIGN_LEFT;
    return $struct;
}

sub test_to_struct : Tests {
    push @_, (
        content_valign => DCV2_VALIGN_TOP,
        content_halign => DCV2_HALIGN_LEFT,
    );
    my $got = shift->next::method(@_);
    is_json_string($got->{content_alignment_vertical});
    is_json_string($got->{content_alignment_horizontal});
    return $got;
}

1;
