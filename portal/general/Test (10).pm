package DivCardV2::Base::Div::Separator::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro;

use base qw(DivCardV2::Base::Div::IAction::Test);

use Test::More;
use MTH;

use DivCardV2::Base::Constants;

sub class {'DivCardV2::Base::Div::Separator'}

sub short_constructor { 'DivSeparator' }

sub set_methods_startup : Test(startup) {
    my $self = shift;
    $self->next::method(@_);
    my $tests = $self->{set_methods_tests};
    $tests->{set_color} = {
        obj_key => 'delimiter_style',
        tests   => [
            { args => [], expected => undef },
            { args => [undef],     expected => undef },
            { args => [''],        expected => undef },
            { args => ['#FF0102'], expected => { color => '#ff0102' } },
        ],
    };
    $tests->{set_orientation} = {
        obj_key => 'delimiter_style',
        tests   => [
            { args => [], expected => undef },
            { args => [undef], expected => undef },
            { args => [DCV2_ORIENTATION_O], expected => undef, errors => 1 },
            {
                args     => [DCV2_ORIENTATION_H],
                expected => { orientation => DCV2_ORIENTATION_H },
            },
        ],
    };
    return;
}

sub to_struct_expected {
    my $struct = shift->next::method(@_);
    $struct->{type}                           = 'separator';
    $struct->{delimiter_style}->{color}       = '#ff0012';
    $struct->{delimiter_style}->{orientation} = DCV2_ORIENTATION_H;
    return $struct;
}

sub test_to_struct : Tests {
    push @_, (
        color       => '#FF0012',,
        orientation => DCV2_ORIENTATION_H,
    );
    my $got = shift->next::method(@_);
    is_json_string($got->{type});
    is_json_string($got->{delimiter_style}->{color});
    is_json_string($got->{delimiter_style}->{orientation});
    return $got;
}

1;
