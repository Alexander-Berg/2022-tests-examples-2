package Perl::Critic::Policy::Home::MP_Utils::RequireDefaultImport;

use strict;
use warnings FATAL => 'all';
no if $] >= 5.017011, warnings => 'experimental::smartmatch';
use utf8;
use v5.14;

use Perl::Critic::Utils qw( :severities  );
use base qw(Perl::Critic::Policy);

use constant DESC => 'Required use MP::Utils only with default import (no args at use)';
use constant EXPL => 'Replace with "use MP::Utils;"';

sub supported_parameters { () }

sub default_severity {$SEVERITY_MEDIUM}

sub default_themes {qw(home portability)}

sub applies_to { 'PPI::Statement::Include' }

sub violates {
    my ($self, $elem) = @_;
    return unless $elem->type eq 'use' and $elem->module eq 'MP::Utils';
    return unless $elem->arguments;
    return $self->violation(DESC, EXPL, $elem);
}


1;
