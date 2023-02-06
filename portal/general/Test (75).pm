package MordaX::Experiment::AB::Tree::Primary::IPv6::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro;

use base qw(MordaX::Experiment::AB::Tree::Primary::Test);

use Test::More;
use MTH;

use MP::IPv6;

sub class {'MordaX::Experiment::AB::Tree::Primary::IPv6'}

sub test_evaluate : Tests {
    my ($self) = @_;
    my @tests = (
        {
            ip => '127.0.0.1',
            v6 => 0,
        },
        {
            ip => 'not ip',
            v6 => 0,
        },
        {
            ip => '::1',
            v6 => 1,
        },
    );
    for my $test (@tests) {
        my $ip_obj = MP::IPv6->new(ip => $test->{ip}, quiet => 1);
        my $req = { RemoteIp_Obj => $ip_obj };
        my $test_name = ($test->{v6} ? 'true: ' : 'false: ')
          . $self->class . '->new("ipv6")'
          . '->evaluate(' . explain_args($req) . ')';
        my $tree = $self->class->new("ipv6");
        is($tree->evaluate($req), $test->{v6}, $test_name);
    }
    return $self;
}

1;
