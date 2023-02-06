package MordaX::Experiment::AB::Tree::Primary::Size::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro;

use base qw(MordaX::Experiment::AB::Tree::Primary::Test);

use Test::More;
use MTH;

sub class {'MordaX::Experiment::AB::Tree::Primary::Size'}

sub not_need_one_arg_new_test {1}

sub new_tests_setup : Test(startup) {
    my $tests = shift->next::method(@_);
    push @$tests, ({
            name     => 'one arg "desktop"',
            args     => ['desktop'],
            errors   => 0,
            expected => ['desktop', undef],
        }, {
            name     => 'one arg "touch"',
            args     => ['touch'],
            errors   => 0,
            expected => ['touch', undef],
        },
    );
    return $tests;
}

sub test_as_string_one_node : Tests {
    my ($self) = @_;
    is($self->class->new("desktop")->as_string, 'size:desktop', 'as_string "desktop"');
    is($self->class->new("touch")->as_string,   'size:touch',   'as_string "touch"');
    return $self;
}

sub test_evaluate : Tests {
    my ($self) = @_;
    my @tests = ({
            size => 'desktop',
            req     => {
                MordaContent => undef,
            },
            result => 1
        }, {
            size => 'touch',
            req     => {
                MordaSize => 'touch',
                handler   => 'Handler::MordaX',
            },
            result => 1
        }, {
            size => 'desktop',
            req     => {
                MordaSize => 'touch',
                handler   => 'Handler::Api',
            },
            result => 0
        },
    );
    for my $test (@tests) {
        my $req = $test->{req};
        my $test_name =
          ($test->{result} ? 'true: ' : 'false: ')
          . $self->class
          . '->new('
          . explain_args($test->{size}) . ')'
          . '->evaluate('
          . explain_args($req) . ')';
        my $tree = $self->class->new($test->{size});
        is($tree->evaluate($req), $test->{result}, $test_name);
    }
    return $self;
}

1;
