#!/usr/bin/env perl
use strict;
use warnings;

###########################################
# sudo -u www-data perl tests/lib-pfile.t
###########################################

use lib::abs qw(../lib);
use Pfile;

#current way
do {
    my $log_name = 'test_log';
    my $log_date = '20000118';

    my $fullpath = '/var/log/www/' . $log_name . '.' . $log_date;

    unlink($fullpath);
    my @strings;
    my $pid = fork();
    if ($pid) {
        push @strings, '2';
        push @strings, '2' x 32765;
    } else {
        # Test::More->builder->no_ending(1); # иначе prove ругается
        push @strings, '1';
        push @strings, '1' x 32765;
    }

    Pfile::PWrite_real($log_name, $log_date, \@strings);

    if ($pid) {
        exit();
    }
    check_result($fullpath, 'current way');
};  

#syswrite
do {
    my $log_name = 'test_log';
    my $log_date = '20000119';

    my $fullpath = '/var/log/www/' . $log_name . '.' . $log_date;
    
    sub PWrite_real_syswrite {
        my ($file_name, $log_date, $strings) = @_;
        my $handle = Pfile::POpen($file_name, $log_date)
            or die 'cant open';
        my $string = join '', @{ $strings };
        syswrite($handle, $string);
    }
    
    unlink($fullpath);
    my @strings;
    my $pid = fork();
    if ($pid) {
        push @strings, '2';
        push @strings, '2' x 32765;
    } else {
        push @strings, '1';
        push @strings, '1' x 32765;
    }

    PWrite_real_syswrite($log_name, $log_date, \@strings);

    if ($pid) {
        exit();
    }
    check_result($fullpath, 'syswrite way');
};

sub check_result {
    my ($fullpath, $method_name) = @_;
    open(my $file, '<', $fullpath) or die $!;
    my $str = <$file>;
    if ($str =~ /^(1{32766}|2{32766})/) {
        print "ok $method_name\n";
    } else {
        print "broken $method_name\n";
    }
}

# ok(1);
