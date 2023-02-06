package Perl::Critic::Policy::Home::MP_Utils::ProhibitNonDirectImport;

use strict;
use warnings FATAL => 'all';
no if $] >= 5.017011, warnings => 'experimental::smartmatch';
use utf8;
use v5.14;

use File::Spec;
use lib::abs;

use Perl::Critic::Utils qw( :severities  );
use base qw(Perl::Critic::Policy);

use constant DESC => 'Usage of functions from MP::Utils without "use MP::Utils;" is prohibited';
use constant EXPL => '"%s" must be imported from MP::Utils';

use constant UPDIR    => File::Spec->updir();
use constant HOME_LIB => lib::abs::path(File::Spec->catfile(
        ((UPDIR) x (scalar(split '::', __PACKAGE__) + 1)), 'lib'
));
use constant MP_UTILS_PATH    => File::Spec->catfile(HOME_LIB, qw(MP Utils.pm));
use constant MP_UTILS_PP_PATH => File::Spec->catfile(HOME_LIB, qw(MP Utils PP.pm));

sub supported_parameters { () }

sub default_severity {$SEVERITY_HIGH}

sub default_themes {qw(home bugs)}

sub applies_to { qw(PPI::Statement::Include PPI::Token::Word) }

sub initialize_if_enabled {
    my ($self, $config) = @_;

    push @INC, HOME_LIB;
    my @functions = eval {
        require '' . MP_UTILS_PATH;
        @MP::Utils::EXPORT;
    };
    die "Failed to get \@EXPORT from MP::Utils $@" unless @functions;
    $self->{mp_functions} = { map { $_ => 1 } @functions };
    return 1;
}

sub violates {
    my ($self, $elem) = @_;

    my $current_location = $elem->location->[4];
    return if $current_location eq MP_UTILS_PP_PATH;

    state $location = '';
    state $use_mp_utils = 0;

    if ($current_location ne $location) {
        $use_mp_utils = 0;
        $location = $current_location;
    }

    if ($elem->isa('PPI::Statement::Include')) {
        return if $use_mp_utils;
        return unless $elem->type eq 'use' and $elem->module eq 'MP::Utils';
        $use_mp_utils = 1;
        return;
    }
    elsif ($elem->isa('PPI::Token::Word')) {
        return if $use_mp_utils;
        return unless $self->{mp_functions}->{ $elem->content };
        return $self->violation(DESC, sprintf(EXPL, $elem->content), $elem);
    }

    return;
}


1;
