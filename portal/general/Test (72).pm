package MordaX::Experiment::AB::Tree::Primary::Device::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro;

use base qw(MordaX::Experiment::AB::Tree::Primary::Test);

use Test::More;
use MTH;

sub class {'MordaX::Experiment::AB::Tree::Primary::Device'}

sub test_as_string_one_node : Tests {
    my ($self) = @_;
    is($self->class->new("Bro")->as_string, 'device.Bro', 'as_string "Bro"');
    is($self->class->new("csp")->as_string, 'device.csp', 'as_string "csp"');
    return $self;
}

sub test_evaluate : Tests {
    my ($self) = @_;
    my $tree   = $self->class->new('BrowserEngine');
    my @tests  = (
        { BrowserDesc => undef, result => undef },
        { BrowserDesc => {}, result => undef },
        { BrowserDesc => { x64           => 1 },       result => undef },
        { BrowserDesc => { BrowserEngine => '' },      result => '' },
        { BrowserDesc => { BrowserEngine => 0 },       result => 0 },
        { BrowserDesc => { BrowserEngine => 'Gecko' }, result => 'Gecko' },
    );
    for my $test (@tests) {
        my $req = { BrowserDesc => $test->{BrowserDesc} };
        my $test_name = $self->class . '->new("BrowserEngine")'
          . '->evaluate(' . explain_args($req) . ') is '
          . explain_args($test->{result});
        is($tree->evaluate($req), $test->{result}, $test_name);
    }
    return $self;
}

1;
