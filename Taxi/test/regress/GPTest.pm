
=pod

=head1 NAME

GPTest - Generic functionality for Greenplum test tools

=head1 SYNOPSIS

  use GPTest;

  print $VERSION;

=head1 DESCRIPTION

GPTest is intended to contain generic functionality for the Greenplum test
tools written in Perl. At the moment the module contains the Greenplum
database VERSION.

=cut

package GPTest;

use strict;
use warnings;
use File::Basename qw(basename);

use Exporter;

our @ISA = 'Exporter';
our @EXPORT = qw($VERSION print_version);

our $VERSION = '6.8.1 build yandex0';

sub print_version
{
	print basename($0) . ' ' . $VERSION . "\n";
	exit(1);
}

1;
