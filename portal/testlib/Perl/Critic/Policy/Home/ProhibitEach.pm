package Perl::Critic::Policy::Home::ProhibitEach;

use strict;
use warnings FATAL => 'all';
use utf8;
use v5.14;

use Perl::Critic::Utils qw( :severities  );
use base qw(Perl::Critic::Policy);

use constant DESC => 'Usage of "each" loop is prohibited';
use constant EXPL => 'Use "for keys" instead';

sub supported_parameters { () }

sub default_severity {$SEVERITY_HIGH}

sub default_themes {qw(home bugs)}

sub applies_to {qw(PPI::Token::Word)}

sub violates {
    my ($self, $elem) = @_;
    return unless $elem->content eq 'each';
    return $self->violation(DESC, EXPL, $elem);
}

1;
