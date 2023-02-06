#!/usr/bin/perl
# $Id$

=SYNOPSIS

 # 100 last commits:
 ./test_speed.pl from=HEAD~100
 # every 100 commits from last 1000
 ./test_speed.pl from=HEAD~1000 step=100
 # from this commit to now
 ./test_speed.pl from=82d31bc
 # range
 ./test_speed.pl from=82d31bc to=896c9ce
 # force commit list
 ./test_speed.pl revs=73ef41a,8cd15d4,HEAD,HEAD~1,HEAD~100
 ./test_speed.pl devs=-v4d1,-v4d4,-v4d7,-v4d11,-v4d11

 sudo apt-get install gnuplot

 gnuplot -p -e "set grid; set style data lines; plot 'graph.dat';" 
 gnuplot -e "set terminal png; set grid; set style data lines; plot 'graph.dat';" > graph.png

 plot.sh graph.dat
 plot.sh:
 gnuplot -e "set terminal png; set grid; set style data lines; plot '$1' using 1:2, '$1' using 1:3, '$1' using 1:4, '$1' using 1:5; " > $1.png
 gnuplot -e "set terminal png; set grid; set style data lines; plot '$1' using (column(0)):3 title 'want rate', '$1' using (column(0)):4 title 'conn rate', '$1' using (column(0)):5 title 'ms', '$1' using (column(0)):6 title 'resp rate', '$1' using (column(0)):7 title 'ms load'; " > $1.png


=cut

use strict;
use lib::abs;
use Cwd;
#use LWP::UserAgent;
#use URI::URL;
use HTTP::Tiny;
use Data::Dumper;
$Data::Dumper::Sortkeys = $Data::Dumper::Indent = $Data::Dumper::Terse = 1;
our %config;
my (%results, %revisions);

sub get_params_one(@) {    # p=x,p=y,p=z => p=x,p1=y,p2=z ; p>=z => p=z, p_mode='>'; p => p; -p => -p=1;
    local %_ = %{ref $_[0] eq 'HASH' ? shift : {}};
    for (@_) {             # PERL RULEZ # SORRY # 8-) #
        tr/+/ /, s/%([a-f\d]{2})/pack 'C', hex $1/gei for my ($k, $v) = /^([^=]+=?)=(.+)$/ ? ($1, $2) : (/^([^=]*)=?$/, /^-/);
        $_{"${1}_mode$2"} .= $3 if $k =~ s/^(.+?)(\d*)([=!><~@]+)$/$1$2/;
        $k =~ s/(\d*)$/($1 < 100 ? $1 + 1 : last)/e while defined $_{$k};
        $_{$k} = $v;       #lc can be here
    }
    wantarray ? %_ : \%_;
}

sub get_params(;$$) {      #v7
    my ($string, $delim) = @_;
    $delim ||= '&';
    read(STDIN, local $_ = '', $ENV{'CONTENT_LENGTH'}) if !$string and $ENV{'CONTENT_LENGTH'};
    local %_ =
      $string
      ? get_params_one split $delim, $string
      : (
        get_params_one(@ARGV), map { get_params_one split $delim, $_ } split(/;\s*/, $ENV{'HTTP_COOKIE'}),
        $ENV{'QUERY_STRING'},  $_
      );
    wantarray ? %_ : \%_;
}
sub printlog (@) { print join ' ', @_, "\n"; }
{
    my %fh;
    my $savetime = 0;

    sub file_append(;$@) {
        local $_ = shift;
        for (defined $_ ? $_ : keys %fh) { close($fh{$_}), delete($fh{$_}) if $fh{$_} and !@_; }
        return if !@_;
        unless ($fh{$_}) { return unless open $fh{$_}, '>>', $_; return unless $fh{$_}; }
        print {$fh{$_}} @_;
        if (time() > $savetime + 5) {
            close($fh{$_}), delete($fh{$_}) for keys %fh;
            $savetime = time();
        }
        return @_;
    }
    END { close($fh{$_}) for keys %fh; }
}

sub file_rewrite(;$@) {
    local $_ = shift;
    return unless open my $fh, '>', $_;
    print $fh @_;
    return 1;
}

sub http_get_code ($;$$) {
    my ($what, $lwpopt, $method) = @_;
    my $http = HTTP::Tiny->new();
    #printlog Data::Dumper::Dumper
    my $resp = $http->head($what);
    return $resp->{status}, $resp->{headers}{'content-length'};    #length $resp->{reason};

=old
    my $resp = ((
            LWP::UserAgent->new(
                %{$config{'lwp'} || {}},
                %{$lwpopt || {}}
              )
        )->request(
            HTTP::Request->new(
                ($method || 'GET'),
                URI::URL->new($what),
                HTTP::Headers->new('User-Agent' => $config{'useragent'} || $config{'crawler_name'})
              )
          )
    );
    printlog 'url=', $what;
    return $resp->code(), length $resp->as_string;
=cut

}

sub openproc($) {
    my ($proc) = @_;
    my $handle;
    return $handle if open($handle, $proc);
    return 0;
}

sub run($;$$) {    #v1
    my ($proc, $nologbody, $handler) = @_;
    return unless $proc;
    my $ret;
    printlog('run', "Starting [ $proc ]:");
    system($proc), return if $nologbody and !$handler;
    my $h = openproc("$proc $config{'stderr_redirect'}|") or return 1;
    while (<$h>) {
        s/\s*[\x0A\x0D]*$//;
        next unless length $_;
        printlog('run', $_) unless $nologbody;
        last if $handler and $ret = $handler->($_);
    }
    close($h);
    return $ret;
}

sub percent($$) {
    return undef unless $_[0];
    return sprintf '%.3f', ($_[0] - $_[1]) / ($_[0] / 100);
}

printlog 'stopping cron';
run 'sudo service cron stop';

my $params = get_params();

my ($devc) = lib::abs::path('..') =~ m{/opt/www/morda(-\w+)};

my $try;
for my $dev ($params->{devs} ? split /[,;]+/, $params->{devs} : $devc) {

    %config = (
        dev => $dev,
        try => $try++,
#!    rep => 'svn+ssh://svn.yandex.ru/morda/trunk/',
#to   => 'HEAD',
#from => 'PREV',
        warm     => 50,    # warm requests
        rate     => 20,    #start rps from
        requests => 10,    #requests on one rps
#requests => 10,
        minlen     => 20000,                            #do not shoot while http body length <  (404)
                                                        #useragent  => 'tester', #del
        graph_data => 'graph.' . int(time) . '.dat',    #save results for graph to
#shooter => 'ab',
        noload_time => 500,                             # continue to detect minimum time if >
        shooter     => 'httperf',
        headers     => "User-Agent: msnbot\n",          # to disable banners

        fields => {
            'Document Length'      => 1,
            'Requests per second'  => 1,
            'Time per request'     => 1,
            'Time taken for tests' => 1,
            'Total transferred'    => 1,
            'HTML transferred'     => 1,
            'Transfer rate'        => 1,
#siege:
#        'Transaction rate' => 1,
#        'Response time'    => 1,
#httperf
            'Connection rate'          => 1,
            'Request rate'             => 1,
            'Reply time [ms] response' => 1,
        },

        graph_fields => {
            ab => [
                'Time per request',
                'Requests per second',
                'Document Length',
                'Time per request diff percent',
                'Requests per second diff percent',
            ],
            #siege => ['Transaction rate', 'Response time', 'Transaction rate diff percent', 'Response time diff percent'],
            httperf => [
                'Connection rate', 'Reply time [ms] response noload', 'Request rate', 'Reply time [ms] response',
                'Reply time [ms] response noload diff percent', 'Connection rate diff percent', 'Request rate diff percent',
#'Reply time [ms] response min diff percent',
            ],
        },
    );
    if (`hostname` =~ /\Qbang.yandex.net/) {    #special host params
#warn "run on bang";
        delete $config{dev};
        $config{url} = "http://bang.yandex.net/";
        #$config{url} = "http://bang.yandex.net/?edit=1";
        $config{requests} = 500;
        #$config{requests} = 1000;
        #$config{requests}    = 3000;
        #$config{requests}    = 5000;
        #$config{requests}    = 10000;
        $config{restart} = qq{
      sudo /usr/local/etc/rc.d/fastcgi-stop; 
      sudo /opt/www/morda/configurator/configurator.pl -t eto -deploy;
      sudo /usr/local/etc/rc.d/nginx reload; 
      sudo /usr/local/etc/rc.d/fastcgi-start
      };
        $config{noload_time} = 60;
    }

    $config{$_} = $params->{$_} for keys %$params;
#warn Dumper $params;;

#warn lib::abs::path($0); #todo: auto dev detect
#exit;
    $config{path}    //= "/opt/www/morda$config{dev}/";
    $config{proto}   //= "https";
    $config{domain}  //= "ru";
    $config{service} //= "www";
    $config{uri}     //= "/";
    $config{url}     //= "$config{proto}://$config{service}$config{dev}.wdevx.yandex.$config{domain}$config{uri}";
    $config{restart} //= "sudo $config{path}fastcgi.sh restart";
    if (!$config{dev}) {    #production
#    $config{rate} = 32;
#    $config{rate} = 64;
#    $config{rate} = 100;
#    $config{rate} = 115;
#    $config{rate} = 125;
        $config{rate} = 140;
#    $config{rate} = 160;
    }
    $config{'stderr_redirect'} //= '2>&1';    #'2>/dev/null';
    $config{revs} //= join ',', grep { length $_ } $config{from}, $config{to};

    #tune try 1
    $config{rate_step} //= 1;

    $config{rate_max} //= 250;
#$config{rate_step} //= 1;
    $config{rate_step} //= 2;
#$config{rate_step} //= 5;
#$config{razval}           = 300;
#$config{razval}           = 200;
    $config{razval} //= 100;                  #ms
    if (!$config{dev}) {                      #production
#    $config{rate} = 32;
        $config{warm} = 32 * 3;               # np
    }

    $config{git} = "git --git-dir=$config{path}.git --work-tree=$config{path}";

    do 'config.pl';

#warn Dumper  \%config;

    if ($config{from} and !$config{to}) {
        $config{to} = 'HEAD';
    }

    if ($config{from} and $config{to}) {
        my ($revision);
        #local $/ = '</logentry>';

        #if ($config{from} > $config{to} and $config{to} ne 'HEAD') {
        #    $config{'reverse'} //= 1;
        #    ($config{from}, $config{to}) = ($config{to}, $config{from});
        #}

        #run "svn log -r$config{from}:$config{to} --xml --stop-on-copy $config{rep}", 'silent', sub {
        my $order = 0;
        run "git log --oneline $config{from}..$config{to}", 'silent', sub {
            local ($_) = @_;
            ++$order;
            #printlog('skip', $order),
            next if $config{step} and $order != 1 and $order % $config{step};
            #printlog('go', $order);
            # TODO: dont skip last item

            if (m{^(\S+)}m) {
                $revision                       = $1;
                $revisions{$revision}{revision} = $revision;
                $revisions{$revision}{order}    = $order;
            }
            $revision and s{^(\S+)\s+(.+)\s*$}{$revisions{$revision}{message} = $2;}esmog;
            0;
        };
    }
    #my @revisions = sort { $a <=> $b } keys %revisions;
    my @revisions = sort { $revisions{$a}{order} <=> $revisions{$b}{order} } keys %revisions;
    @revisions = reverse @revisions if $config{'reverse'};
    printlog scalar @revisions, 'list:', join ' ', @revisions;
    $config{revs} = join ',', @revisions if @revisions;
    #$config{revs} ||= 0;
    $config{revs} ||= 'WORK';
    my $revprev;
    file_rewrite($config{graph_data});

    sub shoot ($) {
        my %shoot;
        my ($c, $r) = @_;
        $r ||= $config{requests};
        $r = $c if $c > $r;
        if ($config{shooter} eq 'ab') {
            $config{shooter_run} = qq{ab -r -n $r -c $c -H "Accept-Encoding: gzip,deflate"  -g graphg.dat $config{url}};
            #} elsif ($config{shooter} eq 'siege') {
            #    $config{shooter_run} = qq{siege -c $c --time=$config{time} -b $config{url}};
        } elsif ($config{shooter} eq 'httperf') {

            ($config{proto}, $config{server}, $config{uri}) = $config{url} =~ m{^(\w+)://([^/]+)(.*)$} unless $config{server};

            my $add;
            $add .= " --ssl " if $config{proto} ~~ 'https';

            $config{shooter_run} =
              qq{httperf --hog --num-conn $r --server $config{server} $add --uri $config{uri} --rate $c --add-header "$config{headers}"};
        }
        run $config{shooter_run},
          #'silent',
          undef, sub {
            local ($_) = @_;
            if (/^(\w+[\w\s\[\]]+):\s*?(\s\w+)?\s+([\d\.]+)/) {
                my $key = $1 . $2;
                if ($config{fields}{$key}) {
                    $shoot{$key} = $3;
                }
            }
            0;
          };
        return wantarray ? %shoot : \%shoot;
    }
  REV: for my $revision (split /[,;]+/, $config{revs}) {
        if ($revision and $revision ne 'WORK') {
            printlog "switching to [$revision]";
            #run "sudo -u morda svn switch $config{rep} -r $revision $config{path}";    #--quiet
            #run "sudo -u morda $config{git} checkout $revision";    #--quiet
            run "$config{git} checkout $revision";    #--quiet
        } else {
            $revision = 'WORK';
        }
        my $result = $results{$config{dev} . ($config{try} ? '-' . $config{try} : ())}{$revision} ||= {%{$revisions{$revision} || {}}};
        $result->{revision} = $revision;

        printlog "restarting $dev ", system $config{restart} if $revision ne 'WORK';

        my ($tries_ok, $tries);
        while (1) {
            my ($code, $len) = http_get_code($config{url});
            printlog "CODE=$code len=$len try=$tries_ok";
            if ($code == 200) {
                if (++$tries_ok >= 3) {
                    if ($len >= $config{minlen}) { last; }
                    else {
                        printlog "bad HTML rev [$revision] ($len < $config{minlen})";
                        next REV;
                    }
                } else {
                    next;    #no sleep on 200
                }
            }
            $result->{'cant start'} = 1, printlog('cant start, goto next rev'), next REV if ++$tries > 100;
            sleep 1;
        }

        if ($config{warm}) {
            printlog "warming [r=$config{warm}]";
            shoot $config{rate} * 2, $config{warm};
        }
        printlog "min time detect";
        for (1 .. 5) {
            local $config{requests} = 50;
            my %shoot = shoot 10;
            printlog Dumper \%shoot;
            next if $shoot{'Reply time [ms] response'} > $config{noload_time};
            $result->{'Reply time [ms] response noload'} = $shoot{'Reply time [ms] response'};
            last;
        }
        printlog "shooting";
        my $wantstop;
        for (my $c = $config{rate}; $c <= $config{rate_max}; $c += $config{rate_step}) {
            my %shoot = shoot $c;
            $result->{$_} = $shoot{$_} for grep { $result->{$_} < $shoot{$_} } 'Connection rate';
            if ($shoot{'Reply time [ms] response'} > $config{razval}) { ++$wantstop }
            else {
                $result->{rate} = $c;
                #$result->{rate} = $result->{'Request rate'};
                $wantstop = undef;
                $result->{$_} = $shoot{$_} for 'Reply time [ms] response', 'Request rate';
            }
            printlog 'now shoot', Dumper \%shoot;
            last if $wantstop > 3;
            if ($config{shooter} eq 'ab' and !$result->{'HTML transferred'}) {
                printlog "no html [$revision]";
                delete $result->{$_} for keys %{$config{fields}};
                next REV;
            }
        }
        if ($revprev) {
            my $percent =
              sub ($) { $result->{$_[0] . ' diff percent'} = percent($result->{$_[0]}, $revprev->{$_[0]}) if $result->{$_[0]}; };
            $percent->($_)
              for 'Time per request', 'Requests per second', 'Transaction rate', 'Response time', 'Connection rate', 'Request rate',
              'Reply time [ms] response', 'Reply time [ms] response noload';
        }
        $result->{dev} ||= $dev;
        if ($result->{$config{graph_fields}{$config{shooter}}->[0]}) {
            file_append $config{graph_data},
              (join "\t", map { $result->{$_} } 'dev', 'revision', 'rate', @{$config{graph_fields}{$config{shooter}} || []}), "\n";
        }
        printlog 'now', Dumper $result;
        $revprev = $result;
    }

}

printlog 'starting cron';
run 'sudo service cron start';
printlog '$result=', Dumper \%results;

__END__
dbg Time taken for tests:   38.150 seconds
dbg Complete requests:      100
dbg Failed requests:        99
dbg    (Connect: 0, Receive: 0, Length: 99, Exceptions: 0)
dbg Write errors:           0
dbg Total transferred:      8238366 bytes
dbg HTML transferred:       8168073 bytes
dbg Requests per second:    2.62 [#/sec] (mean)
dbg Time per request:       381.500 [ms] (mean)
dbg Time per request:       381.500 [ms] (mean, across all concurrent requests)
dbg Transfer rate:          210.89 [Kbytes/sec] received



ransactions:                    1029 hits
Availability:                 100.00 %
Elapsed time:                   9.13 secs
Data transferred:              28.88 MB
Response time:                  1.23 secs
Transaction rate:             112.67 trans/sec
Throughput:                     3.16 MB/sec
Concurrency:                  138.22
Successful transactions:        1029
Failed transactions:               0
Longest transaction:            2.44
Shortest transaction:           0.21


run Starting [ httperf --hog --num-conn 5000 --server bang.yandex.net --rate 128 ]:
run httperf: warning: open file limit > FD_SETSIZE; limiting max. # of open files to FD_SETSIZE
run httperf --hog --client=0/1 --server=bang.yandex.net --port=80 --uri=/ --rate=128 --send-buffer=4096 --recv-buffer=16384 --num-conns=5000 --num-calls=1
run Maximum connect burst length: 48
run Total: connections 5000 requests 5000 replies 5000 test-duration 39.140 s
run Connection rate: 127.7 conn/s (7.8 ms/conn, <=323 concurrent connections)
run Connection time [ms]: min 47.0 avg 361.3 max 2557.7 median 122.5 stddev 491.1
run Connection time [ms]: connect 11.9
run Connection length [replies/conn]: 1.000
run Request rate: 127.7 req/s (7.8 ms/req)
run Request size [B]: 68.0
run Reply rate [replies/s]: min 83.1 avg 127.9 max 183.8 stddev 29.8 (7 samples)
run Reply time [ms]: response 261.6 transfer 87.8
run Reply size [B]: header 695.0 content 75090.0 footer 0.0 (total 75785.0)
run Reply status: 1xx=0 2xx=5000 3xx=0 4xx=0 5xx=0
run CPU time [s]: user 0.69 system 18.16 (user 1.8% system 46.4% total 48.1%)
run Net I/O: 9463.0 KB/s (77.5*10^6 bps)
run Errors: total 0 client-timo 0 socket-timo 0 connrefused 0 connreset 0
run Errors: fd-unavail 0 addrunavail 0 ftab-full 0 other 0
