package MordaX::Experiment::AB::Tree::Primary::Cgi::Test;

use strict;
use warnings FATAL => 'all';
use v5.14;
use utf8;
use mro;

use base qw(MordaX::Experiment::AB::Tree::Primary::Test);

use Test::More;
use MTH;

sub class {'MordaX::Experiment::AB::Tree::Primary::Cgi'}

sub test_as_string_one_node : Tests {
    my ($self) = @_;
    is($self->class->new("uuid")->as_string, 'cgi.uuid', 'as_string "uuid"');
    is($self->class->new("did")->as_string,  'cgi.did',  'as_string "did"');
    return $self;
}

sub test_evaluate : Tests {
    my ($self) = @_;
    my $tree   = $self->class->new('app_version');
    my @tests  = (
        { Getargshash => undef, result => undef },
        { Getargshash => {}, result => undef },
        { Getargshash => { app_platform => 'android' }, result => undef },
        { Getargshash => { app_version  => '' },        result => '' },
        { Getargshash => { app_version  => 0 },         result => 0 },
        { Getargshash => { app_version  => '7020000' }, result => '7020000' },
    );
    for my $test (@tests) {
        my $req = { Getargshash => $test->{Getargshash} };
        my $test_name = $self->class . '->new("app_version")'
          . '->evaluate(' . explain_args($req) . ') is '
          . explain_args($test->{result});
        is($tree->evaluate($req), $test->{result}, $test_name);
    }
    return $self;
}

1;
