#!/usr/bin/perl -w
use strict;
use lib::abs '../lib';

use authparser;
use Data::Dumper;
use Time::HiRes qw(usleep);
use URI::Escape;

my $etcpath = lib::abs::path('../etc');

require MordaX::Conf;
require MordaX::Auth;

my $logfilename = $ARGV[0] || '/var/log/nginx/access.log';
die "$logfilename not found" unless (-f $logfilename);

$| = 1;

my %Monthes = (
    'Jan' => 1,
    'Feb' => 2,
    'Mar' => 3,
    'Apr' => 4,
    'May' => 5,
    'Jun' => 6,
    'Jul' => 7,
    'Aug' => 8,
    'Sep' => 9,
    'Oct' => 10,
    'Nov' => 11,
    'Dec' => 12,
);

open ACCESSLOG, "<$logfilename" or die "Failed to open $logfilename: $!";
while (<ACCESSLOG>) {
    next unless ($_);
    chomp;
    s/^\s//go;
    s/\s$//go;
    my $sessionid = undef;
    if (/Session_id=([^;"]+)[;"]/) {
        $sessionid = uri_unescape($1);
        #print STDERR "Session_id: $sessionid\n";
    }
    next unless ($sessionid);
    my $domain = undef;
    if (/\.(yandex(-team)?\.(ru|ua|by|kz|com))/) {
        $domain = $1;
    }
    next unless (defined($domain));
    next if ($domain eq 'yandex-team.ru');
    my ($mday, $mon, $tmon, $year, $hour, $min, $sec);
    if (/^[^\[\[]+\[(\d{1,2})\/([a-zA-Z]+)\/(\d{4}):(\d{2}):(\d{2}):(\d{2})\s+/o) {
        $mday = $1;
        $tmon = $2;
        $year = $3;
        $hour = $4;
        $min  = $5;
        $sec  = $6;
        $mon  = $Monthes{$tmon} // 1;    # =)
    }

    my $req = {
        'INPUT_PROCESSED' => 1, 'LocalYear' => $year, 'LocalMon' => $mon, 'LocalDay' => $mday,
        'LocalHour' => $hour, 'LocalMin' => $min, 'LocalSec' => $sec,
        'SetupHash' => {'domain' => $domain,},
    };
    $req->{'_STATBOX_ID_SUFFIX_'} = 'test'; # HOME-37938
    my $auth = MordaX::Auth->new($req, 'dontauth' => 1,);
    $auth->check($req, {sessonid => $sessionid});

    my $parser = authparser::session->new();
    my $res    = $parser->parse($sessionid);

    compareauth($sessionid, $auth->{'AuthState'}, $res);

    usleep(10000);
}

close ACCESSLOG;

sub compareauth {
    my ($session, $auth, $res) = @_;

    unless (defined($res)) {
        print "Undefined authparser::session res for session \"$session\"\n";
        return undef;
    }
    unless (defined($auth)) {
        print "Undefined AuthState (got from blackbox) for session \"$session\". Semantic test res: \"$res\"\n";
    }

    if ($res == -1) {    # Invalid res
        unless ($auth eq 'NOAUTH') {
            print "Session_id: \"$session\", authparser: \"-1\" (invalid), blackbox: \"$auth\" (expected \"NOAUTH\")\n";
            return undef;
        }
    } elsif ($res == 0) {    # Noauth res
        unless ($auth eq 'NOAUTH') {
            print "Session_id: \"$session\", authparser: \"0\" (noauth), blackbox: \"$auth\" (expected \"NOAUTH\")\n";
            return undef;
        }
    } elsif ($res == 1) {    # Valid res
        unless ($auth eq 'AUTH') {
            print "Session_id: \"$session\", authparser: \"1\" (valid), blackbox: \"$auth\" (expected \"AUTH\")\n";
            return undef;
        }
    } elsif ($res == 2) {    # Valid rotten res
        unless (($auth eq 'EXPIRED') || ($auth eq 'NOAUTH')) {
            print
              "Session_id: \"$session\", authparser: \"2\" (expires), blackbox: \"$auth\" (expected \"EXPIRED\" or \"NOAUTH\")\n";
            return undef;
        }
    } else {
        print "Undocumented res \"$res\" for session \"$session\"\n";
        return undef;
    }
}

