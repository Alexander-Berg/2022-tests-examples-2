#!/usr/bin/perl

use Test::Harness;

# run all test bu exclude some ones
use lib::abs;
use File::Spec;

my $path = lib::abs::path(".");
opendir(DIR, $path);
my @files = readdir(DIR);
closedir(DIR);
@files = grep {m/^\d+.*\.(pl|t)$/} @files;
my @skip_tests = (
    qw/
      19-rating-calc.pl
      14-history-report.pl
      13-tag-list.pl
      18-wadm-history.pl
      21-search.pl
      23-mime-lite.pl
      23-rss-monitoring.pl
      /
);
my %skip_test = map { $_ => 1 } @skip_tests;

my @tests = grep { !$skip_test{$_} } @files;
print "Skipped tests:\n" . join("\n", @skip_tests) . "\n-----------------------\n";

print "Running tests:\n" . join("\n", @tests) . "\n----------------------\n";
sleep(1);
runtests(@tests);

=old
runtests(qw/
03-changeLog.pl
05-widget-acessors.pl
06-history2.pl
08-history-db.pl
09-monitoring.pl
10-w-update.pl
12-wdgt-auth.pl
15-badresponse_dt.pl
16-dontwork_dt.pl
17-utils.pl
21-search.pl
22-ws-list.pl
24-auto-antivirus.pl
25-zerro-rss.pl
26-domain-list.pl
27-no-rss.pl
31-monitoring2.pl
32-test-no-rss.pl
    /);

=cut

#TODO
# rewirere 04-reasons.pl
print "Skipped tests:\n " . join("\n", @skip_tests) . "\n";

