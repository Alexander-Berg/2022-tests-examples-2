#!/usr/bin/perl
use 5.010;

use strict;
use warnings;

use common::sense;
use lib::abs;
use App::Prove;

my @files = @ARGV;
say "Changed files: ".join(';', @files ) ;
my %tests = map { $_ => 1 } grep { m/\.t$/ } grep { m/^t\// } @files;
say "Changed tests: ".join(';', keys %tests ) ;
my @files = grep { !m/^t\// }  @files;

#find #TESTme
my %c_tests;
my $docs = []; # DOC, help
for my $file ( @files ){
    # because we can delete file, too
    next unless -e $file;
    open( IN, $file );
    my $line = 1;
    while (my $str =  <IN>) {
        if ($str =~ m/^[^\-]*#TESTME ([\w\-\.\s]+)/) {
            my @t = split(m/\s+/, $1);
            #say " testme found: $1:: ", @t;
            for my $t ( @t ){
                $c_tests{ $t } = 1;
            }
        }
        if ($str =~ m/^.*DOC\s.+/ || $str =~ m/.*help.+\=\>.+/){
            $str =~ s/^\s+//;
            $str =~ s/\s+$//;
            $str =~ s/\s+/ /g;
            push @$docs, { file => $file, line => $line, doc => $str };
        }
        $line++;
    }
    close( IN );
}

for( keys %c_tests ){
    if (-e 't/'.$_) {
        say "TESTME t/$_";
        $tests{ 't/' . $_ } = 1;
    }
    elsif (-e 'tests/'.$_) {
        say "TESTME tests/$_";
        $tests{ 'tests/' . $_ } = 1;
    }
    else {
        say "Test doesn't exist ".$_;
        exit 1;
    }
}

my $parent_path = "..";

say "\n\e[1;31m======== CHECKING TESTS\e[0m";
my @testfiles = keys %tests;
if (scalar(@testfiles)) {
    my $app = App::Prove->new;
    chdir lib::abs::path("$parent_path");
    $app->process_args(keys %tests);
    exit 1 unless $app->run;
}

say "\n\e[1;34m======== CHECKING DOCS\e[0m";
if (scalar @$docs) {
    say "\e[1;34mNotice. Please, check documentation!\e[0m";
    for my $doc (@$docs) {
        say "\e[0;34m", $doc->{doc}, "\e[0m (\e[1;37m", $doc->{file}, ":", $doc->{line}, "\e[0m)";
    }
    say '';
}
else {
    say "\e[1;34mOK\e[0m";
}

exit(0);
