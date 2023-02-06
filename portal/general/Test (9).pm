package DivCardV2::Base::Div::Image::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro 'c3';

use base qw(
    DivCardV2::Base::Div::IAction::Test
    DivCardV2::Base::Div::IContentAlignment::Test
);

use Test::More;
use MTH;

use DivCardV2::Base::Constants;
use DivCardV2::Base::Utils qw(:all);

sub class {'DivCardV2::Base::Div::Image'}

sub short_constructor { 'DivImage' }

sub set_methods_startup : Test(startup) {
    my $self = shift;
    $self->next::method(@_);
    my $tests = $self->{set_methods_tests};
    $tests->{set_image_url} = {
        obj_key => 'image_url',
        tests   => $self->set_methods_tests_url(),
    };
    $tests->{set_ph_color} = {
        obj_key => 'placeholder_color',
        tests   => $self->set_methods_tests_color(),
    };
    $tests->{set_scale} = {
        obj_key => 'scale',
        tests => $self->set_methods_tests_constant(DCV2_ISCALE_NO),
    };
    return;
}

sub to_struct_expected {
    my $struct = shift->next::method(@_);
    $struct->{type}                         = 'image';
    $struct->{image_url}                    = 'https://ya.ru/1.png';
    $struct->{placeholder_color}            = '#ff0012';
    $struct->{scale}                        = DCV2_ISCALE_NO;
    return $struct;
}

sub test_to_struct : Tests {
    push @_, (
        image_url      => 'https://ya.ru/1.png',
        ph_color       => '#FF0012',
        scale          => DCV2_ISCALE_NO,
    );
    my $got = shift->next::method(@_);
    is_json_string($got->{type});
    is_json_string($got->{image_url});
    is_json_string($got->{placeholder_color});
    is_json_string($got->{scale});
    return $got;
}

sub test_to_struct_no_image_url : Tests {
    my ($self) = @_;
    my $image = $self->class->new(
        border   => border(color => '#ffffff', radius => "3"),
        width    => size_fixed("3"),
        height   => size_wrap_content(),
        paddings => edge_insets(left => "5", top => "2"),
        margins  => edge_insets(right => "0", bottom => "1"),
    );
    my $errors = 0;
    $image->on_error_cb(sub { $errors++ });
    my $got = $image->to_struct();
    is($got,    undef);
    is($errors, 1);
    return;
}

1;
