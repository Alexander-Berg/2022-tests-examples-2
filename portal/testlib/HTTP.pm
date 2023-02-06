package testlib::HTTP;

use strict;
use warnings;
use utf8;
use v5.14;

use mro 'c3';

use base qw(MordaX::HTTP);

sub new { bless { handler => { aliases => {} }, responses => {} }, shift }

sub init { $_[0] }

sub alias_exists { !! $_[0]->{handler}->{aliases}->{ $_[1] } }

sub add {
    my ($self, %args) = (shift, @_);
    my $alias = $args{alias} // return;
    # alias already exists
    return if $self->{handler}->{aliases}->{$alias};
    $self->{handler}->{aliases}->{$alias} = \%args;
    return 1;
}

sub addreq { }

sub poke { }

sub spin { }

sub checktimeouts { }

sub stop_req_and_run { }

sub stop_req_and_log_error { }

sub run_next_try { }

sub stop_req { }

sub stop_req_info { }

sub timeout { }

sub dnsfail { }

sub crash { }

sub doretry { }

sub wait { }

sub done { }

sub result_req_info { $_[0]->{responses}->{ $_[1] } }

sub result { }

sub result_from_json { }

sub log_req_timings { }

sub timestart_delta { }

sub dump { }

sub testlib_get_request {
    $_[0]->{handler}->{aliases}->{ $_[1] };
}

sub testlib_set_response {
    $_[0]->{responses}->{ $_[1] } = $_[2];
}

1;
