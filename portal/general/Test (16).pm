package DivCardV2::Tmpl::Base::MethodFactory::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro;

use base qw(Test::Class);

use Test::More;
use MTH;

use Sub::Name;

sub requier : Test(startup => no_plan) {
    my ($self) = @_;
    use_ok('DivCardV2::Tmpl::Base::MethodFactory');
    return;
}

sub test_method_non_empty_string : Tests {
    my ($self) = @_;
    my $code = DivCardV2::Tmpl::Base::MethodFactory::_method_non_empty_string(
        'some_key'
    );
    my $method = eval "sub { $code }";
    is(ref($method), 'CODE', '_method_non_empty_string generates correct code');
    my $obj = \{};
    $method->($obj, '');
    is($$obj->{some_key}, undef);
    $method->($obj, 0);
    is_json_string($$obj->{some_key});
    is($$obj->{some_key}, 0);
    return;
}

sub test_check_non_empty_string : Tests {
    my ($self) = @_;
    my $code = DivCardV2::Tmpl::Base::MethodFactory::_check_non_empty_string(
        '$_[0]'
    );
    my $sub = eval "sub { return ($code) ? 1 : 0 }";
    is(ref($sub), 'CODE', '_check_non_empty_string generates correct code');
    ok($sub->($_)) for qw(1 0 sss ыы);
    ok(not($sub->($_))) for ('', undef);
    return;
}

# sub test_repr : Tests {
#     my ($self) = @_;
#     my $method = eval {
#         DivCardV2::Tmpl::Base::MethodFactory::repr(
#             "Base::Class", { some => 'data', here => [1] }
#         );
#     };
#     is(ref($method), 'CODE', 'repr generates sub');
#
#     *DivCardV2::Tmpl::Base::MethodFactory::Test::Cat::repr =
#       subname 'DivCardV2::Tmpl::Base::MethodFactory::Test::Cat::repr' => $method;
#
#     my $got      = DivCardV2::Tmpl::Base::MethodFactory::Test::Cat->repr();
#     my $expected = {
#         Template => {
#             base => 'Base::Class',
#             type => 'cat',
#             data => { some => 'data', here => [1] },
#         },
#     };
#     is_deeply($got, $expected, 'repr generates valid sub');
#     return;
# }

sub test_code2sub : Tests {
    my ($self) = @_;
    my $got = eval {
        DivCardV2::Tmpl::Base::MethodFactory::_code2sub(
            "use strict; not valid perl code !"
        );
        1;
    };
    is($got, undef, '_code2sub dies on bad code');
    $got = eval { DivCardV2::Tmpl::Base::MethodFactory::_code2sub(q{
        my ($num) = @_;
        $num++;
        return $num;
    }) };
    is(ref($got), 'CODE', '_code2sub turns to sub valid code');
    is($got->(1), 2,      '_code2sub generates valid sub');
    return;
}

sub test_self_key : Tests {
    my ($self) = @_;
    my @tests = (
        {
            varname  => '$self',
            key      => 'abcd-efg',
            expected => '${$self}->{"abcd-efg"}',
        },
        {
            varname  => '$_[0]',
            key      => "\"",
            expected => '${$_[0]}->{"\\""}',
        },
    );
    for my $test (@tests) {
        my $got = DivCardV2::Tmpl::Base::MethodFactory::_self_key(
            $test->{varname},
            $test->{key},
        );
        my $name = '_self_key('
          . explain_args($test->{varname}, $test->{key})
          . ')';
        is($got, $test->{expected}, $name);
    }
    return;
}

sub test_string_to_pp : Tests {
    my ($self) = @_;
    my @tests = qw(
      $self
      '"''"'''""'
      some_string
      0
      xxxx
      foo
    );

    for my $test (@tests) {
        my $got = DivCardV2::Tmpl::Base::MethodFactory::_string_to_pp($test);
        is(eval($got), $test, '_string_to_pp(' . explain_args($test) . ')');
    }
    return;
}

sub test_scalar_to_pp : Tests {
    my ($self) = @_;
    my @tests = (
        { some_data => 1, x => [1, 2, 3, 4, 5] },
        [1, 2, {}, { a => [1, 3, 54, undef] }],
        undef,
    );
    for my $test (@tests) {
        my $got = DivCardV2::Tmpl::Base::MethodFactory::_scalar_to_pp($test);
        is_deeply(
            eval($got), $test, '_scalar_to_pp(' . explain_args($test) . ')'
        );
    }
    return;
}

package DivCardV2::Tmpl::Base::MethodFactory::Test::Animal;

sub repr { return {} };

package DivCardV2::Tmpl::Base::MethodFactory::Test::Cat;

use base qw(DivCardV2::Tmpl::Base::MethodFactory::Test::Animal);

sub _type { 'cat' }

1;
