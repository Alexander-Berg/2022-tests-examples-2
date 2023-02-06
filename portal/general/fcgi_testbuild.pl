#!/usr/bin/perl

use strict;
use warnings;

use FCGI;
use IPC::Open3;
use Symbol qw{gensym};
use IO::Select;

use POSIX;


my $cmd = '/opt/www/testbuild/autobuild_instance.sh';

$| = 1;
my %req_params;

my $socket = FCGI::OpenSocket(':65080', 3);
my $request = FCGI::Request( \*STDIN, \*STDOUT, \*STDOUT, \%req_params, $socket );
while( $request->Accept() >= 0 ) {
	print "Content-Type: application/octet-stream\r\n\r\n";

	my ($stdout, $stderr) = gensym;
	my $pid;
	unless ( $pid = open3(undef, $stdout, $stderr, $cmd) ) {
		print "cannot open autobuild: $!";
		next;
	}

	my $sel = IO::Select->new();
	$sel->add($stdout);
	$sel->add($stderr);

	while( my @fhs = $sel->can_read(15) ) {
		for my $fh (@fhs) {
			my $line = <$fh>;
			unless (defined $line) {
				$sel->remove($fh);
				next;
			}

			print ">> $line";
		}
	}

	waitpid($pid, 0);
	my $child_exit_status = $? >> 8;
	print "\n--\nexit status: " . $child_exit_status . "\n";
}
FCGI::CloseSocket($socket);
