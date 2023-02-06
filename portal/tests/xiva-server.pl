#!/usr/bin/perl

=USAGE

./xiva-server.pl host=wxiva-dev4.yandex.net

=cut

use strict;
use utf8;
use warnings;
use Data::Dumper;
use IO::Socket::INET;
use lib::abs qw(../scripts);
use Time::HiRes qw(usleep sleep time);
use Xiva;

my $xiva = Xiva->new('debug' => 3,);
print("fail: cant init xiva"), exit 1 unless (defined($xiva));

if ($xiva->alive()) {
    #die "Alive!";
} else {
    print "fail: not alive";
    exit 1;
}

sub wait_connect ($;$) {
    my ($sock, $timeout) = @_;
    my $start = time;
    while (!$sock->connected()) {
        return "timeout($timeout)" if time - $start > $timeout;
        usleep(5000);
    }
    return !$sock->connected();
}

sub wait_data ($;$) {
    my ($sock, $timeout) = @_;
    my $start = time;
    while (!$sock->atmark) {
        return 1 if time - $start > $timeout;
        usleep(5000);
    }
    return 0;
}

sub test {
    my %argv = map { s/^-+//; split /=/, $_, 2 } grep {/\S=\S/} @ARGV;
    #warn Dumper \%argv;
    my %params = (
        'id'         => 'testing',
        'block'      => 'test',
        'key'        => 42,
        'time'       => (int time - 10),
        'message'    => 'testmessage' . rand(100500),
        'badmessage' => 'badmessage' . rand(100501),
        'host'       => '127.0.0.1',                    #'wxiva-dev4.yandex.net',
        'timeout'    => 3,
        'wait'       => 0.5,
        %argv,
    );
    $params{'channels'} //=
      $params{'block'} . ($params{'key'} ? "_$params{'key'}" : '') . ($params{'time'} ? ":$params{'time'}" : '');
    my $sock = IO::Socket::INET->new(
        PeerAddr => $params{'host'},
        PeerPort => $params{'port'} || 'http(80)',
        Proto    => 'tcp',
        Blocking => 0,
    );
    $sock->timeout($params{'timeout'});

    my %headers = (
        'Connection' => 'keep-alive',
        'Keep-Alive' => '30',
        'Host'       => $params{'host'},
    );
    my $s = "GET /?" . (join '&', map { $_ . '=' . $params{$_} } qw(id channels )) . " HTTP/1.1\n";
    $s .= join "", map {"$_: $headers{$_}\n"} keys %headers;
    $s .= "\n";
    return "not connected [$_]" if local $_ = wait_connect($sock, $params{'timeout'});
    #http://wxiva-dev4.yandex.net/?id=www&channels=weather_2:1297435365
    $sock->send($s);
    #my $sendedat = time;
    sleep($params{'wait'});    # must be here #min: 0.0001
    delete $params{'time'};
    $xiva->message(%params);
    {
        local $params{'key'}     = $params{'key'} + 100;
        local $params{'message'} = $params{'badmessage'};
        $xiva->message(%params);
    }
    my $channels = $xiva->request('list');
    my $start    = time;
    while ($sock->connected()) {
        last if time - $start > $params{'timeout'};
        my $data;
        die "no data " if wait_data($sock, $params{'timeout'});
        $sock->read($data, 1024 * 1024) if $sock->atmark;
        #warn "R[$data]" if $data;
        usleep(5000);
        return 'bad message from other key' if $data =~ /$params{'badmessage'}/;
        #warn(time - $sendedat),
        return undef if $data =~ /$params{'message'}/;
        Xiva::logit("strange data [$data]");
    }
    return 'no correct messages recieved';
}

if (!($_ = test())) {
} else {
    print "fail: test [$_]";
    exit 1;
}

print "ok";
