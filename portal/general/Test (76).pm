package MordaX::Experiment::AB::Tree::Primary::Layout::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro;

use base qw(MordaX::Experiment::AB::Tree::Primary::Test);

use Test::More;
use MTH;

sub class {'MordaX::Experiment::AB::Tree::Primary::Layout'}

sub test_evaluate : Tests {
    my ($self) = @_;
    # Не надо указывать undef тут, они автоматически добавятся ниже, так же как
    # и точно не существующие контенты и лейауты
    my @tests = (
        {
            content => 'mob',      # morda content in req
            layout  => 'smart',    # layout in tree node
            result  => 1,          # result,
        },
        {
            content => 'mob',
            layout  => 'mobile',
            result  => 1,
        },
        {
            content => 'mob',
            layout  => 'phone',
            result  => 0,
        },
        {
            content => 'mob',
            layout  => 'touch',
            result  => 0,
        },
        {
            content => 'mob',
            layout  => 'desktop',
            result  => 0,
        },
        {
            content => 'tel',
            layout  => 'smart',
            result  => 0,
        },
        {
            content => 'tel',
            layout  => 'mobile',
            result  => 1,
        },
        {
            content => 'tel',
            layout  => 'phone',
            result  => 1,
        },
        {
            content => 'tel',
            layout  => 'touch',
            result  => 0,
        },
        {
            content => 'tel',
            layout  => 'desktop',
            result  => 0,
        },
        {
            content => 'touch',
            layout  => 'smart',
            result  => 0,
        },
        {
            content => 'touch',
            layout  => 'mobile',
            result  => 1,
        },
        {
            content => 'touch',
            layout  => 'phone',
            result  => 0,
        },
        {
            content => 'touch',
            layout  => 'touch',
            result  => 1,
        },
        {
            content => 'touch',
            layout  => 'desktop',
            result  => 0,
        },
        {
            content => 'big',
            layout  => 'smart',
            result  => 0,
        },
        {
            content => 'big',
            layout  => 'mobile',
            result  => 0,
        },
        {
            content => 'big',
            layout  => 'phone',
            result  => 0,
        },
        {
            content => 'big',
            layout  => 'touch',
            result  => 0,
        },
        {
            content => 'big',
            layout  => 'desktop',
            result  => 1,
        },
        {
            content => 'comtr',
            layout  => 'smart',
            result  => 0,
        },
        {
            content => 'comtr',
            layout  => 'mobile',
            result  => 0,
        },
        {
            content => 'comtr',
            layout  => 'phone',
            result  => 0,
        },
        {
            content => 'comtr',
            layout  => 'touch',
            result  => 0,
        },
        {
            content => 'comtr',
            layout  => 'desktop',
            result  => 1,
        },
        {
            content => 'videohub',
            layout  => 'smart',
            result  => 0,
        },
        {
            content => 'videohub',
            layout  => 'mobile',
            result  => 0,
        },
        {
            content => 'videohub',
            layout  => 'phone',
            result  => 0,
        },
        {
            content => 'videohub',
            layout  => 'touch',
            result  => 0,
        },
        {
            content => 'videohub',
            layout  => 'desktop',
            result  => 1,
        },
        {
            content => 'embedstream',
            layout  => 'smart',
            result  => 0,
        },
        {
            content => 'embedstream',
            layout  => 'mobile',
            result  => 0,
        },
        {
            content => 'embedstream',
            layout  => 'phone',
            result  => 0,
        },
        {
            content => 'embedstream',
            layout  => 'touch',
            result  => 0,
        },
        {
            content => 'embedstream',
            layout  => 'desktop',
            result  => 1,
        },
        {
            content => 'embedstream_touch',
            layout  => 'smart',
            result  => 0,
        },
        {
            content => 'embedstream_touch',
            layout  => 'mobile',
            result  => 1,
        },
        {
            content => 'embedstream_touch',
            layout  => 'phone',
            result  => 0,
        },
        {
            content => 'embedstream_touch',
            layout  => 'touch',
            result  => 1,
        },
        {
            content => 'embedstream_touch',
            layout  => 'desktop',
            result  => 0,
        },
        {
            content => 'videohub_touch',
            layout  => 'smart',
            result  => 0,
        },
        {
            content => 'videohub_touch',
            layout  => 'mobile',
            result  => 1,
        },
        {
            content => 'videohub_touch',
            layout  => 'phone',
            result  => 0,
        },
        {
            content => 'videohub_touch',
            layout  => 'touch',
            result  => 1,
        },
        {
            content => 'videohub_touch',
            layout  => 'desktop',
            result  => 0,
        },
    );
    # undef tests
    {
        my %content;
        my %layout;
        $content{ $_->{content} }++, $layout{ $_->{layout} }++ for @tests;
        push @tests, map { { content => $_, layout => undef, result => 0 } }
          keys %content;
        push @tests, map { { content => undef, layout => $_, result => 0 } }
          keys %layout;
        push @tests, map { { content => $_, layout => "NO_SUCH", result => 0 } }
          keys %content;
        push @tests, map { { content => "NO_SUCH", layout => $_, result => 0 } }
          keys %layout;
    }

    for my $test (@tests) {
        my $test_name = ($test->{result} ? 'true: ' : 'false: ')
          . $self->class . '->new(' . explain_args($test->{layout}) . ')'
          . '->evaluate(' . explain_args({ MordaContent => $test->{content} })
          . ')';
        my $tree = $self->class->new($test->{layout});
        my $req = { MordaContent => $test->{content} };
        is($tree->evaluate($req), $test->{result}, $test_name);
    }
    return $self;
}

1;
